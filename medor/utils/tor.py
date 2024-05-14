# coding: utf-8
import os
import time
from pathlib import Path

import httpx
import stem
from colorama import Fore
from dotenv import load_dotenv, find_dotenv, set_key
from stem import Signal, process, CircStatus
from stem.control import Controller
from stem.version import get_system_tor_version, Requirement

from medor.utils import net
from medor.utils.util import success, failure, warning, spinner


class Tor:
    def __init__(self) -> None:
        self.net = None
        self.tor = None
        self.tor_controller = None
        load_dotenv()
        self.tor_path = None
        self.tor_port = "9250"
        self.tor_controller_port = "9251"
        self.tor_browser = None

    def launch(self) -> None:
        # Chaining main functions to start Tor
        self.config_tor()
        if not self.tor_browser:
            self.ini_connection()
        self.new_id()
        self.net = net.Net(onion=True, timeout=10.0, tor = self.get_tor_ports())
        self.verify_tor()

    def ini_connection(self) -> None:
        # Check if Tor is already running
        spinner.start("Initializing tor")
        try:
            self.tor_controller = self.tor_control()
            if self.tor_controller.get_info("status/circuit-established") == "1":
                spinner.stop_and_persist(symbol=success, text="Tor initialized")
                return
        except stem.SocketError:
            # Try to start if not
            try:
                self.start()
            except stem.SocketError as e:
                spinner.stop_and_persist(
                    symbol=warning,
                    text=f"{Fore.RED}Tor might already be running. Kill tor process.",
                )
                exit()

    def tor_process(self) -> stem.process:
        # Launch tor process
        tor_process = process.launch_tor_with_config(
            config={
                "ControlPort": self.tor_controller_port,
                "SocksPort": self.tor_port,
            },
            tor_cmd=self.tor_path,
            completion_percent=100,
            take_ownership=True,
        )
        return tor_process

    def tor_control(self) -> stem.control.Controller:
        # Create tor controller
        controller = Controller.from_port(port=int(self.tor_controller_port))
        controller.authenticate()
        return controller

    def start(self) -> None:
        # Start tor process and its controller
        if get_system_tor_version(self.tor_path) >= Requirement.TORRC_CONTROL_SOCKET:
            try:
                self.tor = self.tor_process()
                self.tor_controller = self.tor_control()
            except OSError as e:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED}Tor might be already running. Shut down tor process\n"
                    f"   {e}\n",
                )
                exit()
        else:
            spinner.stop_and_persist(
                symbol=failure, text=f"{Fore.RED}Please, update tor.\n"
            )
            exit()

    def new_id(self) -> None:
        # Create a new tor identity before running medor functions
        spinner.start("Setting new tor circuits")
        recommended = self.tor_controller.get_info("status/version/recommended").split(
            ","
        )
        # Check if tor is up-to-date
        if not self.tor_browser:
            self.tor_recommended(recommended)
        # Check if a new identity can be set
        if self.tor_controller.is_newnym_available():
            self.tor_controller.signal(Signal.NEWNYM)
            spinner.stop_and_persist(symbol=success, text="Tor new circuits set")

    def verify_tor(self) -> None:
        # Check if tor is active with check.torproject.org
        spinner.start("Checking Tor Exit IP")
        try:
            res = self.net.connect("https://check.torproject.org/api/ip")
            if res.status_code == 200:
                is_tor = res.json()["IsTor"]
                ip = res.json()["IP"]
                if is_tor:
                    spinner.stop_and_persist(
                        symbol=success, text=f"Tor is ok. Exit IP: {ip}"
                    )
                    return
            else:
                raise httpx.HTTPError
        except httpx.HTTPError:
            # Check if tor is active with stem if check.torproject.org is not reachable
            real_ip = self.net.get_real_ip()
            exit_node = self.get_exit()
            if real_ip != exit_node:
                spinner.stop_and_persist(
                    symbol=success, text=f"Tor exit check. Exit IP: {exit_node}"
                )
                return
            else:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED}Can't verify tor exit IP. Exiting.",
                )
                exit()
        spinner.stop_and_persist(
            symbol=failure, text=f"{Fore.RED}Tor is not active. Exiting"
        )
        exit()

    def get_exit(self) -> str or None:
        # Get tor exit node IP
        for circ in self.tor_controller.get_circuits():
            if circ.status != CircStatus.BUILT:
                continue
            exit_fp, exit_nickname = circ.path[-1]
            exit_desc = self.tor_controller.get_network_status(exit_fp, None)
            exit_address = exit_desc.address if exit_desc else "unknown"
            return exit_address

    def tor_recommended(self, recommended) -> None:
        # Get stem recommended tor version and compare it to tor version
        present = str(get_system_tor_version(self.tor_path)).split(" ")[0]
        if present not in recommended:
            spinner.stop_and_persist(
                symbol=warning,
                text=f"{Fore.YELLOW}Update tor, highly recommended for security.",
            )
        return

    def check_env(self) -> None:
        # check if .env file exists and create it if not
        env_path = Path(__file__).parent.parent.joinpath(".env")
        if not env_path.exists():
            env_path.touch(mode=0o777)

    def check_tor_browser(self) -> bool or None:
        # Check if tor browser is running
        try:
            controller = Controller.from_port(port=9151)
            controller.authenticate()
            self.tor_port = "9150"
            self.tor_controller_port = "9151"
            self.tor_controller = controller
            spinner.stop_and_persist(
                symbol=success, text=f"Tor browser detected. medor will use it."
            )
            return True
        except Exception:
            return None

    def check_tor_process(self, tor_path) -> None:
        # Test if tor is working with the provided path
        try:
            self.tor_path = tor_path
            # self.tor_port = "9250"
            # self.tor_controller_port = "9251"
            test_tor = process.launch_tor_with_config(
                config={
                    "ControlPort": self.tor_controller_port,
                    "SocksPort": self.tor_port,
                },
                tor_cmd=self.tor_path,
                completion_percent=100,
                take_ownership=True,
            )
            test_tor.terminate()
            # wait a bit for tor to exit cleanly
            time.sleep(1)
            # Set tor path in .env file
            set_key(Path(__file__).parent.parent.joinpath(".env"), "tor_path", tor_path)
            spinner.stop_and_persist(
                symbol=success, text=f"{Fore.GREEN}Tor path successfully set.\n"
            )
        except OSError as e:
            if (
                ("Acting on config options left us in a broken state" in str(e))
                or ("Invalid SocksPort configuration" in str(e))
                or ("Failed to bind one of the listener ports" in str(e))
            ):
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED} {e}\n"
                    f"""   It looks like tor is already running. Shut down the tor process and try again.\n"""
                    f"""       Linux : "sudo pkill tor" in the terminal\n"""
                    f"""       Windows : "End task" in the Task Manager or "taskkill /f /im tor.exe" in the terminal\n"""
                    f"""       OSX : kill tor in the Activity Monitor or in terminal, "killall tor".""",
                )
            else:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED} {e}\n"
                    f"""   Please, check tor path and try again.""",
                )
            exit()

    def tor_setup(self) -> None:
        # Setup tor path
        spinner.stop_and_persist(
            symbol=warning,
            text=f"{Fore.YELLOW}You have to start Tor Browser and connect it to Tor, or to install Tor first. If you haven't, see README.md.\n"
            f"   https://github.com/balestek/medor?tab=readme-ov-file#darknet--onion-services",
        )
        tor_path = input(
            f"""➡️ If you installed Tor enter its binary path or command:\n"""
            f"""       Linux and OSX : "tor" on debian/ubuntu or full path\n"""
            f"""       Windows: full path to tor.exe. E.g. """
            + r"C:\Tor\tor.exe"
            + "\n"
            f"""   Enter the path: """
        )
        if len(tor_path) == 0:
            spinner.stop_and_persist(
                symbol=failure,
                text=f"{Fore.RED}You should enter a path.",
            )
            exit()
        self.check_tor_process(str(Path(tor_path)))

    def config_tor(self) -> None:
        self.check_env()
        if self.check_tor_browser():
            self.tor_browser = True
            return
        load_dotenv()
        tor_path = os.getenv("tor_path")
        if not tor_path:
            self.tor_setup()
        else:
            self.tor_path = tor_path

    def get_tor_ports(self) -> tuple:
        return self.tor_port, self.tor_controller_port, self.tor_browser
