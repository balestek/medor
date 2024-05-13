# coding: utf-8
import socket
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup as bs
from colorama import Fore, Style
from validators import domain as valid_domain, url as valid_url, ipv4, ipv6

from medor.utils import net
from medor.utils.tor import Tor
from medor.utils.util import (
    success,
    failure,
    warning,
    found,
    spinner,
)


class Bone:
    def __init__(
        self,
        item: str,
        onion: bool = False,
        proxy: str or None = None,
        webhook: str or None = None,
    ) -> None:
        self.item = item
        self.onion = onion
        self.proxy = proxy
        self.webhook = webhook
        self.medor_path = Path(__file__).parent
        self.webhook_token = ""
        self.webhook_url = ""
        self.domain = ""
        self.site_url = ""
        self.post_url = ""
        self.xmlrpc_url = ""
        self.net = None
        self.parse_input()

    def parse_input(self) -> None:
        # Parse the input to determine the type of item
        item = self.item
        input_type = ""
        if valid_domain(item):
            input_type = "domain"
        elif valid_url(item):
            parsed = urlparse(item)
            if (parsed.scheme == "https" or parsed.scheme == "http") and parsed.netloc:
                if (
                    (parsed.path == "" or parsed.path == "/")
                    and parsed.params == ""
                    and parsed.query == ""
                    and parsed.fragment == ""
                ):
                    input_type = "site"
                else:
                    input_type = "post"
        else:
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED} The entry provided doesn't seem to be formatted as a domain, url or post.\n"
                f"   Valid entry:\n"
                f"      a domain e.g. domain.tld\n"
                f"      a website url e.g. https://www.website.com\n"
                f"      a valid post url e.g. https://www.website.com/a-blog-post/\n",
            )
            exit()
        # Run the main logic
        self.run(input_type, item)

    def run(self, ptype: str, item: str) -> None:
        # Chaining main functions
        # Launch tor if the input is an onion service
        if self.onion:
            tor = Tor()
            tor.launch()
            tor_specs = tor.get_tor_ports()
        else:
            tor_specs = None
        self.net = net.Net(onion=self.onion, proxy=self.proxy, tor=tor_specs)
        # Update user agent and check proxy
        self.net.update_ua()
        if self.proxy and not self.onion:
            self.net.check_proxy(self.proxy)
        # Parse the input and create URLs used for the rest of the process
        self.domain, self.site_url, self.post_url, self.xmlrpc_url = self.parser(
            ptype, item
        )
        # Create a webhook with https://webhook.site if no alternative url is provided with --webhook
        if not self.webhook:
            self.webhook_token = self.create_webhook_token()
            self.webhook_url = f"https://webhook.site/{self.webhook_token}"
        else:
            self.webhook_url = self.webhook
        # Send a pingback request to xmlrpc.php
        self.ping_back(
            self.xmlrpc_url,
            self.post_url,
            self.webhook_url,
        )
        # Retrieve the IP if there is one with webhook.site API.
        if not self.webhook:
            self.get_ip(
                self.webhook_token,
                self.domain,
                self.site_url,
            )

    def parser(self, ptype: str, item: str) -> tuple:
        # Parse the input and create the urls
        spinner.start("Parsing and creating urls")
        site_url = ""
        domain = ""
        post_url = ""
        if ptype == "domain":
            domain = item
            site_url = self.find_domain_scheme(domain)
            post_url = self.find_post(site_url)
        if ptype == "site":
            site_url = item
            site_url = site_url.rstrip("/")
            self.net.valid_site_url(site_url)
            post_url = self.find_post(site_url)
            domain = ".".join(urlparse(site_url).netloc.split(".")[-2:])
        if ptype == "post":
            post_url = item
            site_url = f"{urlparse(post_url).scheme}://{urlparse(post_url).netloc}"
            domain = ".".join(urlparse(post_url).netloc.split(".")[-2:])
        xmlrpc_url = site_url + "/xmlrpc.php"
        self.test_url(xmlrpc_url)

        spinner.stop_and_persist(
            symbol=success,
            text=f"Urls parsed and created :\n"
            f"     domain : {domain}\n"
            f"     site_url : {site_url}\n"
            f"     post_url : {post_url}\n"
            f"     xmlrpc_url : {xmlrpc_url}\n",
        )
        return domain, site_url, post_url, xmlrpc_url

    def find_domain_scheme(self, domain: str) -> str:
        # Test the domain with different schemes to determine the right one
        schemes = (
            ["http://", "https://"]
            if self.onion
            else ["https://", "https://www.", "http://", "http://www."]
        )
        for scheme in schemes:
            try:
                url = scheme + domain
                res = self.net.connect(url)
                if res.status_code == 200:
                    return url
            except httpx.HTTPError:
                if scheme == "http://www.":
                    spinner.stop_and_persist(
                        symbol=failure,
                        text=f" {Fore.RED}Domain protocol for {domain} not found.\n"
                        f"   Use website URL or a post URL instead.",
                    )
                    exit()
                pass

    def find_post(self, url: str) -> str:
        # Gather the methods to find a WordPress post (REST API or RSS feed)
        post = self.find_post_rest(url)
        if not post:
            post = self.find_post_feed(url)
        if post:
            return post
        spinner.stop_and_persist(
            symbol=failure,
            text=f" {Fore.RED}medor can't find a post.\n"
            "   Find a post manually to use with medor.",
        )
        exit()

    def find_post_rest(self, url: str) -> str or None:
        # Find a post with the WordPress REST API
        wp_rest = "/wp-json/wp/v2/posts"
        if self.onion:
            wp_rest = "/index.php?rest_route=/wp/v2/posts"
        try:
            res = self.net.connect(url + wp_rest)
            if res.status_code == 200:
                post = res.json()[0]["link"]
                return post
            else:
                return None
        except:
            return None

    def find_post_feed(self, url: str) -> str or None:
        # Find a post with the WordPress RSS feed
        try:
            res = self.net.connect(url + "/feed/")
            if res.status_code == 200:
                soup = bs(res.text, "xml")
                post = soup.find("item").find("link").text
                return post
            else:
                return None
        except:
            return None

    def test_url(self, url):
        # Test if main urls are reachable
        try:
            res = self.net.connect(url, rtype="post")
            if res.status_code == 200:
                return
            else:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f" {Fore.RED}{url} is not accessible. medor won't work.",
                )
                exit()
        except Exception as e:
            spinner.stop_and_persist(
                symbol=failure,
                text=f" {Fore.RED}{url} is not accessible. medor won't work.\n"
                f"   {e}",
            )
            exit()

    def create_webhook_token(self) -> str:
        # Create a webhook with webhook.site
        spinner.start(f"Creating webhook")
        content = """{"expiry": 259200}"""
        try:
            res = self.net.connect(
                "https://webhook.site/token", rtype="post", content=content
            )
            if res.status_code == 429:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f" {Fore.RED}Your IP might have been blacklisted from webhook.site\n."
                    f"   Change your IP.",
                )
                exit()
            if res.status_code == 201:
                spinner.stop_and_persist(
                    symbol=success,
                    text="Webhook successfully created with webhook.site",
                )
                return res.json()["uuid"]
        except httpx.HTTPError as e:
            spinner.stop_and_persist(
                symbol=failure,
                text=f" {Fore.RED}Token creation failed (HTTP Error {e}).\n"
                f"   Try again later",
            )
            exit()

    def ping_back(self, xmlrpc_url: str, post_url: str, webhook_url: str) -> None:
        # Main feature of medor, send a pingback request to xmlrpc.php
        spinner.start(f"Posting request to xmlrpc.php")
        pingback_data = f"""<?xml version="1.0" encoding="utf-8"?>
    <methodCall>
    <methodName>pingback.ping</methodName>
    <params>
     <param>
      <value>
       <string>{webhook_url}</string>
      </value>
     </param>
     <param>
      <value>
       <string>{post_url}</string>
      </value>
     </param>
    </params>
    </methodCall>"""

        try:
            res = self.net.connect(xmlrpc_url, rtype="post", content=pingback_data)
            if res.status_code == 200:
                spinner.stop_and_persist(
                    symbol=success, text="Xmlrpc.php successfully reached"
                )
                if self.webhook:
                    spinner.stop_and_persist(
                        symbol=success,
                        text=f" {Fore.GREEN}Xmlrpc.php should have sent a response to:\n"
                        f"   {webhook_url}\n"
                        f"   Check there it got the response",
                    )
                    exit()
                else:
                    return
            else:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f" {Fore.RED}{xmlrpc_url}request has not been successful.\n"
                    f"   It might be protected or offline.",
                )
                exit()
        except httpx.HTTPError as e:
            spinner.stop_and_persist(
                symbol=failure,
                text=f" {Fore.RED}{xmlrpc_url} request has not been successful : {e}.\n"
                f"   It might be protected or offline.",
            )
            exit()

    def get_ip(self, token: str, domain, site_url) -> None:
        # Retrieve the IP from the webhook.site API and show the final result
        _headers = {"Accept": "application/json", "Content-Type": "application/json"}
        spinner.start(f"Retrieving real IP from the webhook")
        try:
            res = self.net.connect(
                f"https://webhook.site/token/{token}/request/latest",
                headers=_headers,
            )
        except httpx.HTTPError as e:
            spinner.stop_and_persist(
                symbol=failure, text=f" {Fore.RED}Webhook is not reachable : {e}."
            )
            exit()
        try:
            if not res.json()["ip"]:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED} No IP retrieved for {domain}.\n"
                    f"   Xmlrpc.php might be protected.",
                )
                exit()
            else:
                webhook_ip = res.json()["ip"]
        except:
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED} No IP retrieved for {domain}.\n"
                f"   Xmlrpc.php might be protected.",
            )
            exit()
        if not self.onion:
            waf_hostname = urlparse(site_url).hostname
            waf_ip = socket.gethostbyname(waf_hostname)
            if webhook_ip == waf_ip:
                spinner.stop_and_persist(
                    symbol=warning,
                    text=f" {Fore.RED}The website IP found with xmlrpc.php is the same as {site_url}: {webhook_ip}.\n"
                    f"   {site_url} is not behind WAF. No need of medor.",
                )
                exit()
            else:
                spinner.stop_and_persist(
                    symbol=found,
                    text=f" {Style.BRIGHT}The website IP found with xmlrpc.php is different from {site_url} ({waf_ip}):\n"
                    f"   Webhook url : https://webhook.site/#!/view/{token} (valid for 3 days).{Fore.RESET}\n\n"
                    f"   medor found the IP address {Fore.GREEN}{webhook_ip}{Style.RESET_ALL}.",
                )
                exit()
        elif self.onion:
            if ipv4(webhook_ip) or ipv6(webhook_ip):
                spinner.stop_and_persist(
                    symbol=found,
                    text=f" {Style.BRIGHT}A website IP has been found with xmlrpc.php for {site_url}:\n"
                    f"   Webhook url : https://webhook.site/#!/view/{token} (valid for 3 days).{Fore.RESET}\n\n"
                    f"   medor found the IP address {Fore.GREEN}{webhook_ip}{Style.RESET_ALL}.",
                )
                exit()
