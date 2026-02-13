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