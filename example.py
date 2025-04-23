import nodriver
from nodriver_cf_bypass import CFBypass

async def main() -> None:
    browser: nodriver.Browser = await nodriver.start()
    browser_tab: nodriver.Tab = await browser.get("https://2captcha.com/demo/cloudflare-turnstile-challenge")

    CFB: CFBypass = CFBypass(_browser_tab = browser_tab, _debug = True)
    result = await CFB.bypass(_max_tries = 10, _interval_between_tries = 1)

    if result:
        print("Cloudflare has been bypassed.")
        return

    print("Couldn't bypass cloudflare for some reason.")

nodriver.loop().run_until_complete(main())