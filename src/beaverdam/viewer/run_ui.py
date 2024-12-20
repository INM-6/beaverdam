"""Choose UI backend and frontend, then run the UI."""

from pathlib import Path

from beaverdam._core import ConfigParser, Core
from beaverdam.viewer.controller import Controller
from beaverdam.viewer.dash_view import DashView
from beaverdam.viewer.presenter import Presenter

## INPUTS

# Name of configuration file
cfg_file_name = Path("config.toml")


class BeaverUI:
    """Define and configure modules to be included in the user interface."""

    def __init__(self, fp_cfg):
        """Link modules to each other and provide them with configuration information.

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
        """Launch the user interface."""
        self.view.launch_ui()


def run_ui(cfg_file_name):
    """Create and run the main application.

    Args:
        cfg_file_name (str): relative path and name of configuration file

    """
    cfg_file_name = Path(cfg_file_name)
    user_interface = BeaverUI(cfg_file_name)
    user_interface.run()


if __name__ == "__main__":
    # Edit the name and RELATIVE (to this file) location of the config file
    # appropriately.
    #
    # An alternative approach is to define cfg_file_name in the configurations section
    # of launch.json if you are using VSCode, e.g.:
    #    env: {"cfg_file_name": "config_countries.toml"}
    # Then access this variable here using e.g.:
    #    import os
    #    cfg_file_name = os.environ.get("cfg_file_name")
    cfg_file_name = Path(__file__).parents[3] / "config_countries.toml"
    # Generate the UI
    run_ui(cfg_file_name)
