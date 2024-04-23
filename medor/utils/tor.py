# coding: utf-8
import os
import time
from pathlib import Path

import httpx
import stem
from colorama import Fore
from dotenv import load_dotenv, set_key
from stem import Signal, process, CircStatus
from stem.control import Controller
from stem.version import get_system_tor_version, Requirement

from medor.utils import net
from medor.utils.util import success, failure, warning, spinner


class Tor:
    def __init__(self):
        self.net = net.Net(onion=True, timeout=10.0)
        self.tor = None
        self.tor_controller = None
        load_dotenv()
        self.tor_path = os.getenv("tor_path")
        self.tor_port = os.getenv("tor_port")
        self.tor_controller_port = os.getenv("controller_port")

    def launch(self):
        # Chaining main functions to start Tor
        self.set_tor_path()
        self.ini_connection()
        self.tor_controller = self.tor_control()
        self.new_id()
        self.verify_tor()

    def ini_connection(self):
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

    def tor_process(self):
        # Launch tor process
        tor_process = process.launch_tor_with_config(
            config={
                "ControlPort": str(self.tor_controller_port),
                "SocksPort": str(self.tor_port),
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

    def start(self):
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

    def new_id(self):
        # Create a new tor identity before running medor functions
        spinner.start("Setting new tor circuits")
        recommended = self.tor_controller.get_info("status/version/recommended").split(
            ","
        )
        # Check if tor is up-to-date
        self.tor_recommended(recommended)
        # Check if a new identity can be set
        if self.tor_controller.is_newnym_available():
            self.tor_controller.signal(Signal.NEWNYM)
            spinner.stop_and_persist(symbol=success, text="Tor new circuits set")

    def shutdown(self):
        # Shut down tor process. Was previously used but take_ownership=True in tor_process() is more adapted
        spinner.start("Shutting down tor")
        self.tor_controller = self.tor_control()
        self.tor_controller.signal(Signal.SHUTDOWN)
        spinner.stop_and_persist(symbol=success, text="Tor shut down")
        exit()

    def verify_tor(self):
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

    def get_exit(self):
        # Get tor exit node IP
        for circ in self.tor_controller.get_circuits():
            if circ.status != CircStatus.BUILT:
                continue
            exit_fp, exit_nickname = circ.path[-1]
            exit_desc = self.tor_controller.get_network_status(exit_fp, None)
            exit_address = exit_desc.address if exit_desc else "unknown"
            return exit_address

    def tor_recommended(self, recommended):
        # Get stem recommended tor version and compare it to tor version
        present = str(get_system_tor_version(self.tor_path)).split(" ")[0]
        if present not in recommended:
            spinner.stop_and_persist(
                symbol=warning,
                text=f"{Fore.YELLOW}Update tor, highly recommended for security.",
            )
        return

    def check_env(self):
        # check if .env file exists and create it if not
        env_path = Path(__file__).parent.parent.joinpath(".env")
        if not env_path.exists():
            env_path.touch(mode=0o777)
            env_path.write_text(
                "tor_port=9050\n" "controller_port=9051\n" "tor_ip='127.0.0.1'\n"
            )

    def set_tor_path(self):
        # Set tor path and ports
        self.check_env()
        load_dotenv()
        tor_path = os.getenv("tor_path")
        # Launch setup if tor path is not set
        if not tor_path:
            self.tor_setup()
        else:
            self.tor_path = str(Path(tor_path))
        self.tor_port = os.getenv("tor_port")
        self.tor_controller_port = int(os.getenv("controller_port"))

    def tor_setup(self) -> None:
        # Setup tor path in .env file
        spinner.stop_and_persist(
            symbol=warning,
            text=f"{Fore.YELLOW}You have to install tor first. If you haven't, see README.md.\n"
            f"   https://github.com/balestek/medor?tab=readme-ov-file#install-tor",
        )
        tor_path = input(
            f"""➡️ Tor binary path or command:\n"""
            f"""       Linux and OSX : "tor"\n"""
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
        self.tor_path = str(Path(tor_path))
        self.tor_port = 9150
        self.tor_controller_port = 9151
        # Test if tor is working with the path
        try:
            test_tor = process.launch_tor_with_config(
                config={
                    "ControlPort": str(self.tor_controller_port),
                    "SocksPort": str(self.tor_port),
                },
                tor_cmd=self.tor_path,
                completion_percent=100,
                take_ownership=True,
            )
        except OSError as e:
            if ("Acting on config options left us in a broken state" in str(e)) or (
                "Invalid SocksPort configuration" in str(e)
            ):
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED} {e}\n"
                    f"""   It looks like tor is already running. Shut down the tor process and try again.\n"""
                    f"""       Linux : "sudo pkill tor" in the terminal\n"""
                    f"""       Windows : "End task" in the Task Manager or "taskkill /f /im tor.exe" in the terminal\n"""
                    f"""       OSX : kill tor in the Activity Monitor or in terminal, "killall tor".""",
                )
                set_key(
                    Path(__file__).parent.parent.joinpath(".env"), "tor_path", tor_path
                )
            else:
                spinner.stop_and_persist(
                    symbol=failure,
                    text=f"{Fore.RED} {e}\n"
                    f"""   Please, check tor path and try again.""",
                )
            exit()
        test_tor.terminate()
        time.sleep(1)
        # Set tor path in .env file
        set_key(Path(__file__).parent.parent.joinpath(".env"), "tor_path", tor_path)
        spinner.stop_and_persist(
            symbol=success, text=f"{Fore.GREEN}Tor path successfully set.\n"
        )
