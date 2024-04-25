# coding: utf-8
"""medor

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⡶⠿⠿⠿⠿⢶⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣠⣶⠿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠿⣶⣄⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⣰⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣆⠀⠀⠀
⠀⠀⣼⣿⣧⣤⣴⡶⠶⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣧⠀⠀
⠀⣼⡟⢻⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⣦⣀⣦⡀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⡇⢻⣧⠀
⢰⣿⠁⠈⢿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⢹⣿⡅⢿⣦⡀⠀⠀⠀⠀⠀⠘⣿⣿⣿⠃⠈⣿⡆
⣼⡏⠀⠀⠘⣿⣿⣿⣿⡄⠀⠀⠀⠀⢀⣼⣿⠃⢸⣿⣿⣦⡀⠀⠀⠀⠀⢹⣿⡟⠀⠀⢹⣧
⣿⡇⠀⠀⠀⢹⣿⣿⣿⣷⠀⠀⠀⣴⣿⣿⣿⣷⣿⣿⣿⣿⣿⣦⠀⠀⠀⢸⣿⠁⠀⠀⢸⣿        █▀▄▀█ █▀▀ █▀▄ █▀█ █▀█
⢻⣇⠀⠀⠀⠀⢻⣿⣿⣿⣇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⣿⠇⠀⠀⠀⣸⡟        █ ▀ █ ██▄ █▄▀ █▄█ █▀▄
⠸⣿⡀⠀⠀⠀⠈⣿⣿⠟⣩⣾⣿⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣧⡙⠀⠀⠀⢀⣿⠇  Find a WordPress website IP behind
⠀⢻⣧⠀⠀⠀⠀⢈⣵⠚⠁⠀⡿⠛⠋⠉⠀⠀⠀⠀⢻⣿⠟⣿⣿⣿⣿⣿⣦⡀⠀⣼⡟⠀     a WAF or behind Onion Services
⠀⠀⢻⣧⡀⠀⠀⠘⠿⣇⣀⣀⣠⠤⠖⠒⢦⡀⠀⠀⠘⠋⠀⣿⣿⣿⣿⣿⣿⣷⣾⡟⠀⠀
⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀              jm.balestek
⠀⠀⠀⠀⠈⠻⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⠟⠁
⠀⠀⠀⠀⠀⠀⠈⠙⠿⣶⣤⣀⡀⠀⠀⠀⠀⠸⡆⢀⣾⣿⣿⣿⣿⠿⠋⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠷⣶⣶⣶⣿⠾⠿⠟⠛⠉⠀

Usage:
    medor find <item> [--proxy=<proxy>] [--webhook=<webhook>]
    medor tor_path

Arguments:
    find <item>             Find <item> IP:
                                domain.tld for domain (e.g. website.com)
                                website URL for site (e.g. https://www.website.com)
                                post URL for post (e.g. https://www.website.com/a-blog-post/)
    tor_path                Setup tor path for onion services

Options:
    -h --help               Show this help
    -v --version            Show medor version
    -p --proxy=<proxy>      Optional. Proxy to use :
                                with authentication : scheme://user:password@ip:port
                                without authentication : scheme://ip:port
    -w --webhook=<webhook>  Optional. Custom webhook URL to send xmlrpc request to

"""

from colorama import Fore
from docopt import docopt

from medor.__about__ import __version__
from medor.utils.bone import Bone
from medor.utils.tor import Tor
from medor.utils.util import failure, medor_home


def main():
    args = docopt(__doc__, version="medor v" + __version__)
    medor_home()
    proxy = None
    onion = False
    webhook = None
    if args["--proxy"] == "":
        exit(
            f"{failure} {Fore.RED} You want to use a proxy (--proxy= or -p) but you haven't specified any.\n"
            """   Use --proxy=http://your-proxy-url"""
        )
    if args["--proxy"]:
        proxy = args["--proxy"]
    if args["find"] and ".onion" in args["<item>"]:
        if args["--proxy"]:
            exit(
                f"{failure} {Fore.RED} --proxy can't be used with onion services (.onion website)\n"
                f"Tor will be used instead"
            )
        onion = True
    if args["--webhook"]:
        webhook = args["--webhook"]
    if args["find"]:
        Bone(
            args["<item>"],
            proxy=proxy,
            onion=onion,
            webhook=webhook,
        )
    if args["tor_path"]:
        Tor().tor_setup()


if __name__ == "__main__":
    main()
