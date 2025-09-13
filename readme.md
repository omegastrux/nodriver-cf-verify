# nodriver-cf-verify

A lightweight, asynchronous extension for **nodriver** and **zendriver** that detects and verifies Cloudflare Turnstile challenges.


## 🚀 Description

`nodriver-cf-verify` is a lightweight plugin for the **nodriver** and **zendriver** projects.

It automatically detects whether a webpage is protected by a Cloudflare Turnstile challenge and attempts to verify it using the browser automation interfaces provided by **nodriver** or **zendriver**.

This extension is particularly useful for automating headless access to pages protected by Cloudflare's JavaScript or iframe-based Turnstiles.


## ✅ Features

- Detects Cloudflare protection scripts.
- Locates the embedded Turnstile iframe.
- Simulates a click on the challenge.
- Works asynchronously using `asyncio`.
- Supports retrying with configurable intervals.
- Provides support for the `nodriver` and `zendriver` libraries.
- Can be run easily in Docker containers for isolated environments.


## ⚙️ Requirements

- Python 3.9+
- `nodriver`
- `zendriver` (optional, if preferred over `nodriver`)
- `asyncio` (standard library)


## 📦 Installation

Install the required dependencies using pip (this will install `nodriver` and `zendriver`):
- pip install -r requirements.txt

Make sure `nodriver` or `zendriver` is available in your environment.

You can also install it manually:
- pip install nodriver
- pip install zendriver (optional, if preferred over `nodriver`)


## 🐳 Quick Start with Docker

You can run `nodriver-cf-verify` quickly using Docker. Follow these steps:


### 1️⃣ Build the Docker image

From the root of your project (where the `Dockerfile` is located):

```bash
docker build -t nodriver-cf-verify .
```

- `-t nodriver-cf-verify` sets the image name.
- `.` uses the current directory as the build context.


### 2️⃣ Run the container interactively

```bash
docker run -it --rm nodriver-cf-verify
```

- `-it` interactive mode (needed if running a browser in headful mode).
- `--rm` removes the container after it exits.
- This will execute the example script [`docker_example.py`](./docker_example.py) included in the project.


### 3️⃣ Run the container in detached mode (background)

```bash
docker run -d --name cf-verify nodriver-cf-verify
```

- `-d` detached mode (runs in background).
- `--name cf-verify` assigns a name to the container.


### 4️⃣ Optional: Open a shell inside the container

```bash
docker exec -it cf-verify bash
```

- Useful for debugging, checking installed binaries, or testing scripts manually.


### 5️⃣ Notes

- The container includes **Brave browser** pre-installed and configured.
- Ensure your scripts reference `CHROME_BIN=/usr/bin/brave-browser` if needed. However, this may not always work, so it's recommended to use `browser_executable_path` in the *nodriver* / *zendriver* options instead.
- For headless automation, you can run the container as-is. For headful mode, make sure your environment supports GUI or use `Xvfb`.


## 💻 Example Usage with `nodriver` library

```python
import nodriver, time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    browser: nodriver.Browser = await nodriver.start()
    browser_tab: nodriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    cf_verify: CFVerify = CFVerify(_browser_tab = browser_tab, _debug = True)
    success: bool = await cf_verify.verify(_max_retries = 15, _interval_between_retries = 1, _reload_page_after_n_retries = 0)

    duration: float = (time.perf_counter() - start)

    if not success:
        print(f"Failed to verify Cloudflare. Elapsed time: {duration:.2f} seconds.")
        return

    print(f"Cloudflare was successfully verified in {duration:.2f} seconds.")

nodriver.loop().run_until_complete(future = main())
```


## 💻 Example Usage with `zendriver` library

```python
import zendriver, asyncio, time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    browser: zendriver.Browser = await zendriver.start()
    browser_tab: zendriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    cf_verify: CFVerify = CFVerify(_browser_tab = browser_tab, _debug = True)
    success: bool = await cf_verify.verify(_max_retries = 15, _interval_between_retries = 1, _reload_page_after_n_retries = 0)

    duration: float = (time.perf_counter() - start)

    if not success:
        print(f"Failed to verify Cloudflare. Elapsed time: {duration:.2f} seconds.")
        return

    print(f"Cloudflare was successfully verified in {duration:.2f} seconds.")

asyncio.run(main = main())
```


## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
The full license text is available at: <https://www.gnu.org/licenses/agpl-3.0.txt>

This project is an **independent, unofficial extension** that makes use of:
- **nodriver** – <https://github.com/ultrafunkamsterdam/nodriver> (AGPL-3.0)
- **zendriver** – <https://github.com/cdpdriver/zendriver> (AGPL-3.0)

We are not affiliated with, endorsed by, or sponsored by the authors of *nodriver* or *zendriver*.

All source code for this project is provided in compliance with Section 13 of the AGPL-3.0 license.


## 📝 NOTICE

**This project uses the following open-source software:**

- **nodriver** – <https://github.com/ultrafunkamsterdam/nodriver>
  Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0)
- **zendriver** – <https://github.com/cdpdriver/zendriver>
  Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0)

No modifications have been made to the source code of *nodriver* or *zendriver*.
This project interacts with them solely through their public APIs.

We are not affiliated with the *nodriver* or *zendriver* projects or their authors.


## ⚠️ Disclaimer

The authors are not responsible for any misuse of this project. Use at your own risk. This code is provided for educational and research purposes only. Ensure your usage complies with all applicable laws and terms of service.


## 📬 Contact

Built by [OMEGASTRUX](https://github.com/omegastrux).
If you have questions, ideas, or feedback — open an issue or reach out.