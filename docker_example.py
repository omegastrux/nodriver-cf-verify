import zendriver
import asyncio
import time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    # Explicitly bind to the containerized Brave browser binary path
    config = zendriver.Config(headless=True, browser_executable_path="/usr/bin/brave-browser")
    # Inject a clean User-Agent header string
    config.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

    browser: zendriver.Browser = await zendriver.start(config=config)
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
        return

    print(f"Cloudflare was successfully verified in {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())