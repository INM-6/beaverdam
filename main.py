import sys

sys.path.insert(0, "./src")
import parser
import core as bd
import presenter as bdp
import view_dash as bdv
import controller as bdc


## INPUTS

# Path to config file
fp_cfg = "config.toml"


## CODE


class BeaverApp:
    def __init__(self, fp_cfg):
        self.cfg = parser.parse_config(fp_cfg)
        self.core = bd.Core(self.cfg)
        self.presenter = bdp.Presenter(self.cfg)
        self.view = bdv.DashView()
        self.controller = bdc.Controller()

        self.presenter.set_core(self.core)
        self.controller.set_core(self.core)
        self.view.set_presenter(self.presenter)
        self.view.set_controller(self.controller)

    def run(self):
        self.view.launch_app()


def main():
    app = BeaverApp(fp_cfg)
    app.run()


main()
