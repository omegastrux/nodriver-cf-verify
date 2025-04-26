# This file is part of nodriver-cf-bypass.
# Copyright (c) 2025 KlozetLabs
#
# nodriver-cf-bypass is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# nodriver-cf-bypass is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with nodriver-cf-bypass. If not, see <https://www.gnu.org/licenses/>.



from nodriver import Tab, Element
import asyncio

class CFBypass:
    def __init__(self, _browser_tab: Tab, _debug: bool = False) -> None:
        self.BROWSER_TAB: Tab = _browser_tab
        self.DEBUG: bool = _debug
        self.INSTANCE_ID: str | None = None
    
    async def show_log(self, message: str) -> None:
        if not self.INSTANCE_ID:
            await self.get_instance_id()

        print(f"[CFBypass] {self.INSTANCE_ID}: {message}")

    async def get_instance_id(self) -> str | None:
        retries: int = 0
        max_retries: int = 5

        while retries < max_retries:
            retries += 1

            try:
                self.INSTANCE_ID = self.INSTANCE_ID = f"({self.BROWSER_TAB.target.target_id[-5:]}-{self.BROWSER_TAB.target.url.split("/")[2]})"
                
                if self.BROWSER_TAB.target.url:
                    return self.INSTANCE_ID

            except:
                pass

            await asyncio.sleep(0.3)

        return None


    async def is_cloudflare_presented(self) -> bool:
        try:
            obvious_script: str = "cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray"
            return bool([script.get("src") for script in await self.BROWSER_TAB.find_all("script") if obvious_script in str(script.get("src"))])
        except Exception as e:
            await self.show_log(e)
            return True

    async def find_cloudflare_iframe(self) -> Element | None:
        try:
            obvious_cloudflare_iframe_source: str = "challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/if/ov2/av0/rcv"
            
            iframes: list[Element] = [iframe for iframe in await self.BROWSER_TAB.find_all("iframe") if iframe.get("src")]

            for iframe in iframes:
                if obvious_cloudflare_iframe_source in iframe.get("src"):
                    return iframe
            
            return None

        except Exception as e:
            await self.show_log(e)
            return None

    async def bypass(self, _max_retries: int = 10, _interval_between_retries: float | int = 1,  _reload_page_after_n_retries = 0) -> bool:
        await self.show_log("Bypassing cloudflare...")

        retries: int = 0
        while retries < _max_retries:
            retries += 1

            await self.show_log(f"Trying... {retries}/{_max_retries}")
            
            if _reload_page_after_n_retries > 0 and retries % _reload_page_after_n_retries == 0 and retries > 0 and retries < _max_retries:
                await self.show_log(f"Reloading page...")
                await self.BROWSER_TAB.reload()

            await asyncio.sleep(delay = _interval_between_retries)

            iframe: Element | None = await self.find_cloudflare_iframe()
            try:
                await iframe.mouse_click()

            except AttributeError as e: # There is no cloudflare iframe on site.
                await self.show_log(e)
                if not await self.is_cloudflare_presented():
                    break

            except Exception as e: # The iframe could not be loaded on site.
                await self.show_log(e)

        if await self.is_cloudflare_presented():
            await self.show_log("Cloudflare could not be bypassed for an unknown reason.")

        else:
            await self.show_log("Cloudflare has been bypassed successfully.")

        return not await self.is_cloudflare_presented() # Return True if cloudflare was bypassed successfully.
