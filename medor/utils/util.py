# coding: utf-8
from colorama import Fore, Style
from halo import Halo

from medor.__about__ import __version__ as version

success = "🦴".encode("utf-8")
failure = "❌"
warning = "⚠️"
found = "✔️"
spinner = Halo()


def medor_home():
    print(
        f"""{Style.BRIGHT}{Fore.GREEN}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⡶⠿⠿⠿⠿⢶⣶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣠⣶⠿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠿⣶⣄⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣴⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⣰⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣆⠀⠀⠀
⠀⠀⣼⣿⣧⣤⣴⡶⠶⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣧⠀⠀
⠀⣼⡟⢻⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⣦⣀⣦⡀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⡇⢻⣧⠀
⢰⣿⠁⠈⢿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⢹⣿⡅⢿⣦⡀⠀⠀⠀⠀⠀⠘⣿⣿⣿⠃⠈⣿⡆
⣼⡏⠀⠀⠘⣿⣿⣿⣿⡄⠀⠀⠀⠀⢀⣼⣿⠃⢸⣿⣿⣦⡀⠀⠀⠀⠀⢹⣿⡟⠀⠀⢹⣧
⣿⡇⠀⠀⠀⢹⣿⣿⣿⣷⠀⠀⠀⣴⣿⣿⣿⣷⣿⣿⣿⣿⣿⣦⠀⠀⠀⢸⣿⠁⠀⠀⢸⣿{Fore.RESET}        █▀▄▀█ █▀▀ █▀▄ █▀█ █▀█{Fore.GREEN}
⢻⣇⠀⠀⠀⠀⢻⣿⣿⣿⣇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⣿⠇⠀⠀⠀⣸⡟{Fore.RESET}        █ ▀ █ ██▄ █▄▀ █▄█ █▀▄{Fore.GREEN}
⠸⣿⡀⠀⠀⠀⠈⣿⣿⠟⣩⣾⣿⣿⣿⣿⡿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣧⡙⠀⠀⠀⢀⣿{Fore.RESET}  Find a WordPress website IP behind{Fore.GREEN}
⠀⢻⣧⠀⠀⠀⠀⢈⣵⠚⠁⠀⡿⠛⠋⠉⠀⠀⠀⠀⢻⣿⠟⣿⣿⣿⣿⣿⣦⡀⠀⣼⡟⠀{Fore.RESET}   a WAF or behind Onion Services{Fore.GREEN}
⠀⠀⢻⣧⡀⠀⠀⠘⠿⣇⣀⣀⣠⠤⠖⠒⢦⡀⠀⠀⠘⠋⠀⣿⣿⣿⣿⣿⣿⣷⣾⡟⠀⠀
⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀  {Fore.RESET}     {Style.RESET_ALL}jm balestek - v{version}{Style.BRIGHT}{Fore.GREEN}
⠀⠀⠀⠀⠈⠻⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⠟⠁
⠀⠀⠀⠀⠀⠀⠈⠙⠿⣶⣤⣀⡀⠀⠀⠀⠀⠸⡆⢀⣾⣿⣿⣿⣿⠿⠋⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠷⣶⣶⣶⣿⠾⠿⠟⠛⠉{Style.RESET_ALL}⠀                    ⠀⠀⠀⠀⠀
        """
    )
