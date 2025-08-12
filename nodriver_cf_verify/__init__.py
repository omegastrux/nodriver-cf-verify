# This file is part of nodriver-cf-verify.
# Copyright (c) 2025 OMEGASTRUX
#
# nodriver-cf-verify is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# nodriver-cf-verify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with nodriver-cf-verify. If not, see <https://www.gnu.org/licenses/>.



from nodriver import Tab, Element
from datetime import datetime
from typing import Optional, Any
import asyncio

class CFLogger:
    def __init__(self, _class_name: str, _debug: bool = False) -> None:
        self.debug: bool = _debug
        self.class_name: str = _class_name

    async def log(self, _message: str) -> None:
        """
        Simple logger for CFVerify
        """

        if not self.debug:
            return

        print(f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) [{self.class_name}]: {_message}")


class CFUtil:
    def __init__(self, _browser_tab: Tab, _debug = False) -> None:
        self.debug: bool = _debug
        self.browser_tab: Tab = _browser_tab
        self.cf_logger: CFLogger = CFLogger(_class_name = self.__class__.__name__, _debug = self.debug)

    async def create_instance_id(self, _max_retries: int = 10) -> Optional[str]:
        """
        CFUtil method for creating the instance_id from target_id and url.
        """

        for retry_count in range(1, _max_retries + 1):
            target_id: Optional[str] = self.browser_tab.target.target_id
            target_url: Optional[str] = self.browser_tab.target.url

            if not target_id or not target_url:
                await asyncio.sleep(0.05)
                continue

            instance_id: Optional[str] = f"{target_id[-5:]}-{target_url.split('/')[2]}"
            await self.cf_logger.log(f"Created instance_id: {instance_id}")
            return instance_id

        await self.cf_logger.log(f"instance_id could not be created.")

    async def run_js(self, javascript: str, return_value: bool = True) -> Any:
        result: Any = await self.browser_tab.evaluate(expression = javascript)

        if not return_value:
            return

        if isinstance(result, list):
            return [value['value'] for value in result]

        return result

class CFHelper:
    def __init__(self, _browser_tab: Tab, _debug: bool = False) -> None:
        self.debug: bool = _debug
        self.browser_tab: Tab = _browser_tab

        self.cf_util: CFUtil = CFUtil(self.browser_tab, _debug = self.debug)
        self.cf_logger: CFLogger = CFLogger(_class_name = self.__class__.__name__, _debug = self.debug)

    async def is_cloudflare_presented(self, _max_retries: int = 5, _interval_between_retries: float = 0.1) -> bool:
        """
        Checks if Cloudflare challenge script is present on the page.
        """

        obv_things: list[str] = ["challenges.cloudflare.com", "cdn-cgi/challenge-platform", "turnstile/v0/api.js"]
        urls: list[str] = []

        for i in range(_max_retries):
            for i in range(5):
                try:
                    if "turnstile" in await self.browser_tab.evaluate("document.title"):
                        return True

                    # Using javascript instead if find_all, because it's a lot faster than method used in nodriver
                    urls: list[str] = await self.cf_util.run_js("[...document.querySelectorAll('script[src]')].map(script => script.src)", return_value = True)
                    if not urls:
                        continue

                    break

                except Exception as e:
                    await self.cf_logger.log(f"Error occured while fetching urls from site: {e}")

                await asyncio.sleep(0.1)

            if len(urls) == 0:
                await self.cf_logger.log(f"No urls were fetched from site.")
                continue

            for thing in obv_things:
                for url in urls:
                    if thing in url:
                        return True

            await asyncio.sleep(delay = _interval_between_retries)

        return False

    async def find_cloudflare_iframe(self) -> Optional[Element]:
        """
        Searches for an iframe likely related to Cloudflare challenge.
        Returns the iframe element if found, otherwise None.
        """
        
        try:
            iframes: list[Element] = [iframe for iframe in await self.browser_tab.find_all("iframe") if iframe.attrs.get("src")]

            for iframe in iframes:
                iframe_id: str = iframe.attrs.get("id", "").lower()
                iframe_class: str = iframe.attrs.get("class", "").lower()

                if "cf-" in iframe_id or "turnstile" in iframe_id or "cf-" in iframe_class:
                    await self.cf_logger.log(
                        f"Found potential Cloudflare iframe with {'id=' + iframe_id if iframe_id else ''}"
                        f"{' and ' if iframe_id and iframe_class else ''}"
                        f"{'class=' + iframe_class if iframe_class else ''}"
                    )
                    return iframe

        except Exception as e:
            await self.cf_logger.log(f"Error occurred: {e}")


class CFVerify:
    def __init__(self, _browser_tab: Tab, _debug: bool = False) -> None:
        """
        Initializes CFVerify with the given browser tab and debug flag.
        Raises ValueError if arguments are of incorrect types.
        """

        if not isinstance(_browser_tab, Tab):
            raise ValueError(f"_browser_tab parameter must be an instance of Tab.")

        if not isinstance(_debug, bool):
            raise ValueError(f"_debug parameter must be a bool.")

        self.debug: bool = _debug
        self.browser_tab: Tab = _browser_tab
        self.instance_id: Optional[str] = None

        self.cf_util: CFUtil = CFUtil(_browser_tab = self.browser_tab, _debug = self.debug)
        self.cf_helper: CFHelper = CFHelper(_browser_tab = self.browser_tab, _debug = self.debug)
        self.cf_logger: CFLogger = CFLogger(self.__class__.__name__, _debug = self.debug)

    async def log(self, message: str) -> None:
        """
        Logs a message prefixed by the instance ID.
        If the instance ID is not set, it attempts to create it before logging.
        """

        if not self.instance_id:
            self.instance_id = await self.cf_util.create_instance_id()

        await self.cf_logger.log(f"<{self.instance_id}>: {message}")

    async def verify(self, _max_retries = 10, _interval_between_retries = 1, _reload_page_after_n_retries = 0) -> bool:
        """
        Attempts to verify Cloudflare challenge by retrying up to _max_retries times.
        Optionally reloads the page every _reload_page_after_n_retries attempts.
        """
        
        await self.log("Verifying cloudflare has started.")

        for retry_count in range(1, _max_retries + 1):
            await self.log(f"Trying to verify cloudflare. Attempt {retry_count} of {_max_retries}.")

            await asyncio.sleep(delay = _interval_between_retries)

            if retry_count < _max_retries and _reload_page_after_n_retries > 0 and retry_count % _reload_page_after_n_retries == 0:
                await self.log(f"Reloading page... Attempt {retry_count} of {_max_retries}, reload interval {_reload_page_after_n_retries}.")
                await self.browser_tab.reload()
                continue

            if not await self.cf_helper.is_cloudflare_presented():
                await self.log(f"Cloudflare is not presented on site. No verify needed.")
                return True

            iframe: Optional[Element] = await self.cf_helper.find_cloudflare_iframe()

            if not iframe:
                await self.log("No cloudflare iframe found.")

                if not await self.cf_helper.is_cloudflare_presented():
                    await self.log("Cloudflare has been verified successfully (no iframe required).")
                    return True

                continue

            try:
                await iframe.mouse_click()
                await self.log("Cloudflare iframe has been clicked.")

            except Exception as e:
                await self.log(f"Error while clicking iframe: {e}")

                if "could not find position for" in str(e):
                    await self.log(f"Cloudflare iframe could not load properly.")
                    continue

                if not await self.cf_helper.is_cloudflare_presented():
                    await self.log("Cloudflare has been verified successfully despite error.")
                    return True

        if await self.cf_helper.is_cloudflare_presented():
            await self.log("Cloudflare could not be verified for an unknown reason.")
            return False

        await self.log("Cloudflare has been verified successfully.")
        return True
