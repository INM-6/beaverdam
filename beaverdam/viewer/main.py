import sys

sys.path.insert(0, "./src")

from pathlib import Path

from configparser import ConfigParser
from core import Core
from presenter import Presenter
from view_dash import DashView
from controller import Controller


## INPUTS

# Name of configuration file
cfg_file_name = Path("config.toml")


## CODE


class BeaverUI:
    """Define and configure modules to be included in the user interface"""

    def __init__(self, fp_cfg):
        """Link modules to each other and provide them with configuration information

        Args:
            fp_cfg (str): name of configuration file
        """
        # Read config file
        self.cfg = ConfigParser(fp_cfg)

        # Set modules
        self.core = Core(self.cfg)
        self.presenter = Presenter(self.cfg)
        self.view = DashView()
        self.controller = Controller()

        # Tell modules about each other
        self.presenter.set_core(self.core)
        self.controller.set_core(self.core)
        self.view.set_presenter(self.presenter)
        self.view.set_controller(self.controller)

    def run(self):
        """Launch the user interface"""
        self.view.launch_ui()


def main():
    """Create and run the main application"""
    user_interface = BeaverUI(cfg_file_name)
    user_interface.run()


main()