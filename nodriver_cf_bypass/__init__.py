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
        self.DEBUG = _debug

    async def is_cloudflare_presented(self) -> bool:
        try:
            obvious_cloudflare_script_source: str = "cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray"
            script_sources: list[str] = [script.get("src") for script in await self.BROWSER_TAB.find_all("script") if script.get("src")]

            for source in script_sources:
                if obvious_cloudflare_script_source in source:
                    return True

            return False

        except Exception as e:
            print(e) if self.DEBUG else None
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
            print(e) if self.DEBUG else None
            return None

    async def bypass(self, _max_tries: int = 10, _interval_between_tries: float | int = 1) -> bool:
        print("[CFBypass] Bypassing cloudflare...") if self.DEBUG else None

        tries: int = 0
        while tries < _max_tries and await self.is_cloudflare_presented():
            tries += 1
            print(f"[CFBypass] Trying... {tries}/{_max_tries}") if self.DEBUG else None

            await asyncio.sleep(delay = _interval_between_tries)

            iframe = await self.find_cloudflare_iframe()
            try:
                await iframe.mouse_click()
            except Exception as e:
                print(e) if self.DEBUG else None
        
        if self.DEBUG:
            if await self.is_cloudflare_presented():
                print("[CFBypass] Cloudflare could not be bypassed for an unknown reason.")
            
            else:
                print("[CFBypass] Cloudflare has been bypassed successfully.")

        return not await self.is_cloudflare_presented() # Return True if cloudflare was bypassed successfully.
