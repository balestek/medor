# coding: utf-8
from colorama import Fore, Style
from halo import Halo

success = "🦴".encode("utf-8")
failure = "❌"
warning = "⚠️"
spinner = Halo()


def medor_home():
    print(
        f"""
         |\\_/|
         | ʘ ʘ   █▀▄▀█ █▀▀ █▀▄ █▀█ █▀█
         |   <>  █ ▀ █ ██▄ █▄▀ █▄█ █▀▄
         |  _︿ ------____   | |
         |               `--' |   
     ____|_       ___|   |___.' 
    /_/_____/____/_______| jm.balestek
    
    """
    )


def found(ip):
    return f"""
                      |\\_/|
                      | ^ ^
       _              |   <>
    ((| |)) ____------|  _🦴 {Fore.GREEN}{Style.BRIGHT}{ip}{Style.RESET_ALL}{Fore.RESET}
      | '--'              |
      '.___|   |___      _|____
           |_______\\____\\_____\\_\\  
           
    """


def not_found():
    return f"""
                      |\\_/|
                      | x x
       _              | ' <>
      | |   ____------|  _︿
      | '--'              |
      '.___|   |___      _|____
           |_______\\____\\_____\\_\\
           
            """
