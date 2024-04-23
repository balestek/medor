# coding: utf-8
import importlib
import os
from pathlib import Path
from random import choice
from re import match

import httpx
from bs4 import BeautifulSoup as bs
from colorama import Fore
from dotenv import load_dotenv
from validators import url as valid_url, validator

from medor.utils import uas
from medor.utils.util import success, failure, warning, spinner


class Net:
    def __init__(
        self,
        onion: bool = False,
        proxy: str or None or dict[str, str] = None,
        timeout: float = 5.0,
    ):
        self.medor_path = Path(__file__).parent
        self.onion = onion
        self.uas = uas.uas
        self.proxy = proxy
        self.timeout = timeout
        self._headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Referrer": "https://google.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
        }
        self.onion_pattern = r"^https?://[a-z2-7]{16,56}\.onion/?$"
        load_dotenv()
        self.tor_ip = os.getenv("tor_ip")
        self.tor_port = os.getenv("tor_port")

    def connect(self, url, rtype="get", headers=None, content=None) -> httpx.Response:
        # Request to URLs function
        # Randomize the User-Agent if no header is provided
        if not headers:
            headers = self.rand_headers()
        # Build the socks5 proxy url for onion requests and set a longer timeout as onion requests are slower
        if self.onion:
            self.proxy = f"socks5://{self.tor_ip}:{self.tor_port}"
            self.timeout = 15.0
        with httpx.Client(headers=headers, proxy=self.proxy, timeout=self.timeout) as c:
            # Make the request, get/post logic
            if rtype == "get":
                res = c.get(url)
            if rtype == "post":
                res = c.post(url, content=content)
        return res

    def valid_site_url(self, url: str) -> None:
        # Check if the url is a valid url. Onion validation is checked elsewhere, to change
        if self.onion and not self.valid_onion(url):
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED}{url} is not a valid onion url.\n"
                     "   Check the url.",
            )
            exit()
        if valid_url(url):
            try:
                res = self.connect(url)
                if res.status_code == 200:
                    return
                else:
                    spinner.stop_and_persist(
                        symbol=failure,
                        text=f"{Fore.RED}{url} request is not successful.\n"
                             "   Check the url.",
                    )
                    exit()
            except httpx.HTTPError as e:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED}{url} request is not successful : {e}.\n"
                         "   Check the url.",
                )
                exit()
        else:
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED}{url} doesn't seem to be well formatted as a valid url.\n"
                     "   Check the url.",
            )
            exit()

    @validator
    def valid_onion(self, url):
        # Pattern matching for onion urls
        check = match(self.onion_pattern, url)
        return check

    def update_ua(self) -> None:
        # Update the User-Agents list
        spinner.start("Updating User-Agents list")
        ua = self.get_ua()
        if ua is None:
            ua = self.get_ua_failover()
        if ua is None:
            spinner.stop_and_persist(
                symbol=warning, text=f"{Fore.YELLOW}User-Agents can't be updated"
            )
        else:
            with open(Path(self.medor_path, "uas.py"), "w", encoding="utf-8)") as f:
                f.write(ua)
            importlib.reload(uas)
            spinner.stop_and_persist(symbol=success, text=f"User-Agents checked")

    def get_ua(self) -> str or None:
        # Get User-Agents from microlinkhq/top-user-agents
        try:
            res = self.connect(
                "https://cdn.jsdelivr.net/gh/microlinkhq/top-user-agents@master/src/desktop.json"
            )
            if res.status_code == 200:
                ua = f"uas = " + res.text
                return ua
        except:
            return None

    def get_ua_failover(self) -> str or None:
        # Get User-Agents from useragents.me if micrilinkhq/top-user-agents is down
        matches = [
            "latest-windows-desktop-useragents",
            "latest-mac-desktop-useragents",
            "latest-linux-desktop-useragents",
        ]
        try:
            res = self.connect("https://www.useragents.me/")
            soup = bs(res.text, "lxml")
            ua = []
            for h2 in soup.select("body div h2"):
                h2id = h2.get("id")
                if h2id in matches:
                    textareas = h2.parent.find_all("textarea")
                    for content in textareas:
                        ua.append(content.text)
            return f"uas = " + str(ua)
        except:
            return None

    def rand_headers(self):
        # Randomize the User-Agent
        self._headers["User-Agent"] = choice(self.uas)
        return self._headers

    def check_proxy(self, proxy):
        # Check if the proxy if the proxy IP is different from the real IP
        spinner.start("Checking proxy connection")
        real_ip = self.get_real_ip()
        try:
            res = self.connect("https://api64.ipify.org")
            if res.status_code == 200:
                if proxy and (res.text == real_ip):
                    spinner.stop_and_persist(
                        symbol=failure,
                        text=f"{Fore.RED}Proxy check failed:\n"
                             f"   Your proxy IP ({proxy}) is the same as your real ip ({real_ip}).",
                    )
                    exit()
        except httpx.HTTPError as e:
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED}Proxy {proxy} check failed : {e}.\n"
                     f"   Check the proxy url or if https://api64.ipify.org is online.",
            )
            exit()
        spinner.stop_and_persist(symbol="🦴".encode("utf-8"), text="Proxy checked")

    def get_real_ip(self):
        # Get user IP with ipify to compare with the proxy IP
        return httpx.get("https://api64.ipify.org").text
