# nodriver-cf-verify

A low-level, asynchronous Python extension designed to unify Cloudflare Turnstile challenge verification across both `nodriver` and `zendriver` runtimes.

## System Architecture and Design Choices

The library is split into decoupled sub-components handling driver abstractions, execution logging, target analysis, and DOM interaction.

### 1. Dynamic Driver Runtime Binding (`CFLibUtil`)
Due to type handling discrepancies and known upstream compilation faults (such as missing encoding declarations in `nodriver.network`), the library uses a fallback utility class. It dynamically imports available drivers at runtime, handles syntax exceptions, and binds `Browser`, `Tab`, and `Element` instances into global type unions.

### 2. Context Isolation and Instance Tracking (`CFUtil`, `CFLogger`)
To support concurrent multi-tab processing, each verification routine generates a contextual `instance_id`. This identifier tracks tasks using mutated slices of the unique Chrome DevTools Protocol (CDP) `target_id` combined with sanitized domain string extractions.

### 3. High-Performance DOM Querying (`CFHelper`)
Standard framework node lookups (like `find_all`) suffer from high latency when executing inside complex single-page applications. This extension bypasses framework overhead by evaluating raw asynchronous JavaScript operations directly inside the runtime to map loaded script sources and instantly read volatile input states:
```javascript
// Used for challenge discovery
[...document.querySelectorAll('script[src]')].map(script => script.src)

// Used for deterministic verification
[...document.querySelectorAll('input#cf-chl-widget-{unique_id}_response')].filter(element => element.value !== '').length == 1;
```

### 4. Overhead Mitigation (Bypassing OpenCV Dependencies)
The native upstream `nodriver` implementation includes a built-in `tab.cf_verify()` routing. However, that mechanism relies on visual template matching powered by the `opencv-python` package to locate challenge coordinates on screen. This dependency introduces significant CPU overhead and forces the inclusion of heavy native binary compilation layers, which inflates deployment footprints inside minimal container runtimes.

This extension mitigates that overhead completely by operating strictly within the logical layer of the DOM. By substituting computer vision analysis with deterministic state checks and automated CDP coordinate lookups, the execution loop remains lightweight and eliminates the need for any image-processing binaries.

### 5. Concurrent Synchronization & Background Processing (`CLICK_LOCK`)
To support parallel processing across multiple tabs or browser instances without race conditions, the engine utilizes a module-level `asyncio.Lock()` (`CLICK_LOCK`). All tabs can evaluate Cloudflare states concurrently in the background. The lock is acquired only for a fraction of a second when a tab needs to call `tab.activate()` and trigger the CDP `mouse_click()` event, guaranteeing that mouse interactions are sent to an active viewport without conflicting between parallel routines.

## Core Component Specification

- **CFLibUtil**: Resolves cross-environment dependency injection and initializes unified type bindings.
- **CFLogger**: Provides isolated asynchronous execution tracing using high-precision timestamp matching.
- **CFUtil**: Handles execution of low-level JS payloads and provides cross-driver compatibility wrappers for data objects returned via CDP.
- **CFHelper**: Evaluates active page signatures against known Cloudflare challenge platform endpoints, isolates target iframe elements using strict ID/class attribute heuristics with reduced lookup timeouts (`timeout=1`), and executes deterministic token validation via DOM-isolated JavaScript queries.
- **CFVerify**: Implements the main state machine loop governing retries, automated page refresh triggers, thread-safe tab focus synchronization (`CLICK_LOCK`), and explicit coordinate-based cursor emulation (`mouse_click`).

## Requirements
- Python 3.9+
- Active installation of nodriver or zendriver

## Installation
```bash
pip install git+https://github.com/omegastrux/nodriver-cf-verify.git
```

## Recommended Browser Arguments

When running multiple tabs concurrently or processing background verification tasks, Chromium may throttle JavaScript timers or suspend background tab rendering. Passing the following startup flags ensures maximum verification speed and eliminates coordinate resolution failures on background tabs:

```python
RECOMMENDED_BROWSER_ARGS = [
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-component-update"
]
```

## API Implementation Examples

### Standard Execution Loop (nodriver)

```python
import nodriver
import asyncio
import time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    # Initialize the core browser context with performance args
    browser: nodriver.Browser = await nodriver.start(
        browser_args=[
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-component-update"
        ]
    )
    browser_tab: nodriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    # Pass the active tab reference and execute verification sequence
    cf_verify: CFVerify = CFVerify(_browser_tab=browser_tab, _debug=True)
    success: bool = await cf_verify.verify(
        _max_retries=15, 
        _interval_between_retries=1, 
        _reload_page_after_n_retries=5
    )

    duration: float = (time.perf_counter() - start)

    if not success:
        print(f"Verification failure. State unresolved after {duration:.2f} seconds")
        return

    print(f"Verification successful. Complete in {duration:.2f} seconds")

    await browser.stop()

if __name__ == "__main__":
    nodriver.loop().run_until_complete(main())
```

### Alternative Execution Loop (zendriver)

```python
import zendriver
import asyncio
import time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    browser: zendriver.Browser = await zendriver.start(
        browser_args=[
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-component-update"
        ]
    )
    browser_tab: zendriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    cf_verify: CFVerify = CFVerify(_browser_tab=browser_tab, _debug=True)
    success: bool = await cf_verify.verify(
        _max_retries=15, 
        _interval_between_retries=1, 
        _reload_page_after_n_retries=0
    )

    duration: float = (time.perf_counter() - start)

    if not success:
        print(f"Verification failure. State unresolved after {duration:.2f} seconds")
        return

    print(f"Verification successful. Complete in {duration:.2f} seconds")

    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Concurrent Multi-Tab Execution (`asyncio.gather`)

```python
import zendriver
import asyncio
import time
from nodriver_cf_verify import CFVerify

async def verify_tab(tab: zendriver.Tab, tab_idx: int) -> bool:
    print(f"[Tab {tab_idx}] Starting verification...")
    return await CFVerify(tab, _debug=True).verify(
        _max_retries=10,
        _interval_between_retries=1
    )

async def main() -> None:
    urls = [
        "https://nowsecure.nl",
        "https://nowsecure.nl",
        "https://nowsecure.nl",
        "https://nowsecure.nl"
    ]

    browser: zendriver.Browser = await zendriver.start(
        browser_args=[
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-component-update"
        ]
    )

    tabs = []
    for url in urls:
        tabs.append(await browser.get(url, new_tab=True))

    start = time.perf_counter()

    # Execute parallel verification across all tabs
    tasks = [verify_tab(tab, idx + 1) for idx, tab in enumerate(tabs)]
    results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - start
    success_count = sum(1 for res in results if res is True)

    print(f"Verified {success_count}/{len(urls)} tabs in {duration:.2f} seconds")
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Containerized Deployment via Docker

The repository provides an automated deployment architecture via a `Dockerfile` based on the official `python:3.12-slim` image. To minimize the container footprint while bypassing native headless anti-bot flags, the image provisions system dependencies strictly with standard Debian `chromium` and `Xvfb` (X Virtual Framebuffer).

Headless environments or privacy-focused browsers using dynamic canvas noise (like Brave's Farbling) can cause Cloudflare Turnstile scripts to stall on initial loading checks. To resolve this inside headless server environments, the container executes standard Chromium in non-headless mode (`headless=False`) rendered inside an isolated Xvfb virtual display memory layer.

### Docker Execution Example

The following minimal script demonstrates how to initialize `zendriver` inside the containerized Xvfb environment:

```python
import zendriver
import asyncio
import time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    # Explicitly bind to the containerized Chromium binary path inside Xvfb
    browser: zendriver.Browser = await zendriver.start(
        browser_executable_path="/usr/bin/chromium",
        headless=False,
        browser_args=[
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-component-update"
        ]
    )
    browser_tab: zendriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    cf_verify: CFVerify = CFVerify(_browser_tab=browser_tab, _debug=True)
    success: bool = await cf_verify.verify(
        _max_retries=15, 
        _interval_between_retries=1,
        _reload_page_after_n_retries=0
    )

    duration: float = (time.perf_counter() - start)

    if not success:
        print(f"Failed to verify Cloudflare. Elapsed time: {duration:.2f} seconds")
        await browser.stop()
        return

    print(f"Cloudflare was successfully verified in {duration:.2f} seconds")
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Execution Instructions

Build the local container image using the present directory context:
```bash
docker build -t nodriver-cf-verify .
```

Run the container in interactive mode with host IPC memory sharing:
```bash
docker run -it --rm --ipc=host nodriver-cf-verify
```

Deploy the container to run persistently in a detached background state:
```bash
docker run -d --name cf-verify --ipc=host nodriver-cf-verify
```

## Verification Loop Behavior
The `verify()` method runs an iterative control loop processing the following execution steps:

1. Evaluates page signatures via `CFHelper.is_cloudflare_presented`. If no challenge signature is identified, execution returns early with a success code.
2. Locates target iframes matching validation criteria. If the signature exists but the iframe element is missing from the active DOM context, the loop skips the current tick and retries.
3. Executes `CFHelper.is_cloudflare_verified` via direct JS evaluation against the target element `input#cf-chl-widget-{unique_id}_response`. If the value attribute is non-empty, the challenge is marked as resolved and execution terminates with a true status.
4. Acquires the shared `CLICK_LOCK` to safely bring the tab into foreground focus (`tab.activate()`), then fires an isolated coordinate pointer injection (`mouse_click()`) directly into the target frame boundaries.
5. Catches positional frame exception faults, logging rendering pipeline errors and enforcing isolated fallback runtime delays before recycling the iteration.
6. If the loop completes all iterations without an early return, the method executes a final evaluation check. If `is_cloudflare_presented` still returns true, it logs a verification failure and returns false; otherwise, it confirms successful verification and returns true.

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](./LICENSE) file for exact upstream terms and distribution copy guidelines.

## Open Source Compliance and Notices

This project actively consumes and interfaces with external open-source dependencies under strict compliance with Section 13 of the AGPL-3.0 licensing directive. For exhaustive legal mapping, see the accompanying upstream [NOTICE](./NOTICE) resource.

- **Integration Boundary**: This extension communicates with external logic strictly via public API abstraction layers.
- **Codebase Integrity**: No core modifications, adaptations, or deep overrides have been introduced into the source files of the `nodriver` or `zendriver` projects.
- **Entity Affiliation**: This framework represents an isolated development project and holds no legal affiliation, partnership, authorization, or sponsorship with the original authors of the dependent web driver packages.

## Disclaimer

This framework is distributed solely for educational objectives, legal penetration testing operations, and authorized security research scenarios. The developer assumes zero liability, assumes no structural responsibility, and denies any legal accountability for systemic misuse, service disruptions, financial damage, or breaches of external third-party terms of service caused by automated execution loops generated via this software. All execution risk remains bound entirely to the end user.