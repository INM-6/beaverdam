import sys

sys.path.insert(0, "./src")
import parser
import core as bd
import presenter as bdp
import view_dash as bdv
import controller as bdc


## INPUTS

# Name of configuration file
cfg_file_name = "config.toml"


## CODE


class BeaverUI:
    """Define and configure modules to be included in the user interface"""

    def __init__(self, fp_cfg):
        """Link modules to each other and provide them with configuration information

        Args:
            fp_cfg (str): name of configuration file
        """
        # Read config file
        self.cfg = parser.parse_config(fp_cfg)

        # Set modules
        self.core = bd.Core(self.cfg)
        self.presenter = bdp.Presenter(self.cfg)
        self.view = bdv.DashView()
        self.controller = bdc.Controller()

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
