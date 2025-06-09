import nodriver, time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    browser: nodriver.Browser = await nodriver.start()
    browser_tab: nodriver.Tab = await browser.get("https://nowsecure.nl")

    start: float = time.perf_counter()

    cf_verify: CFVerify = CFVerify(_browser_tab=browser_tab, _debug=True)
    result: bool = await cf_verify.verify(_max_retries=10, _interval_between_retries=1, _reload_page_after_n_retries=0)

    duration: float = (time.perf_counter() - start)

    if result:
        print(f"Cloudflare was successfully verified in {duration:.2f} seconds.")
        return
    
    print(f"Failed to verify Cloudflare. Elapsed time: {duration:.2f} seconds.")

nodriver.loop().run_until_complete(main())
