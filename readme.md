# nodriver-cf-bypass

A lightweight async extension for `nodriver` to detect and bypass Cloudflare Turnstile challenges.


## 🚀 Description

`nodriver-cf-bypass` is a simple plugin for the `nodriver` project.
It automatically detects if a webpage is protected by a Cloudflare Turnstile challenge and attempts to bypass it using the browser automation interface provided by nodriver.

This extension is useful when automating headless access to pages protected by Cloudflare's JS-based or iframe-based turnstiles.


## ✅ Features

- Detects Cloudflare protection scripts
- Locates the embedded Turnstile iframe
- Simulates a click on the challenge
- Works asynchronously using `asyncio`
- Supports retrying with configurable intervals


## ⚙️ Requirements

- Python 3.9+
- `nodriver`
- `asyncio` (standard lib)


## 📦 Installation

Install the required dependencies using pip:
- pip install -r requirements.txt

Make sure `nodriver` is available in your environment.  

You can also install it manually:
- pip install nodriver


## 💻 Example Usage

```python
    import nodriver
    from nodriver_cf_bypass import CFBypass

    async def main() -> None:
        browser: nodriver.Browser = await nodriver.start()
        browser_tab: nodriver.Tab = await browser.get("https://2captcha.com/demo/cloudflare-turnstile-challenge")

        CFB: CFBypass = CFBypass(_browser_tab = browser_tab, _debug = True)
        result = await CFB.bypass(_max_retries = 10, _interval_between_retries = 1, _reload_page_after_n_retries = 0)

        if result:
            print("Cloudflare has been bypassed.")
            return None

        print("Couldn't bypass cloudflare for some reason.")

    nodriver.loop().run_until_complete(main())
```


## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
You can read the full license text here: https://www.gnu.org/licenses/agpl-3.0.txt

This project is an **independent, unofficial extension** based on:
- `nodriver` – https://github.com/ultrafunkamsterdam/nodriver (AGPL-3.0)

We are not affiliated with or endorsed by the original `nodriver` authors.
All source code is provided openly to comply with AGPL-3.0 section 13.


## 📝 NOTICE

This software is based on or makes use of:

- `nodriver` — https://github.com/ultrafunkamsterdam/nodriver
  Licensed under the GNU Affero General Public License v3.0

No changes were made to nodriver's source code.
This extension communicates externally using nodriver’s public API.


## 📬 Contact

Built by [KlozetLabs](https://github.com/KlozetLabs).
If you have questions, ideas, or feedback — open an issue or reach out.
