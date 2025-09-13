# This script must be run via Docker using the provided Dockerfile

import nodriver, time
from nodriver_cf_verify import CFVerify

async def main() -> None:
    config = nodriver.Config(headless = True, browser_executable_path = "/usr/bin/brave-browser") # Using Brave because Chrome couldn't be verified in headless mode
    config.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36") # Ensure the latest user-agent is set

    browser: nodriver.Browser = await nodriver.start(config = config)
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