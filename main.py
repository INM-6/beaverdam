import sys

sys.path.insert(0, "./src")
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
        self.model = bd.Core(fp_cfg)
        self.presenter = bdp.Presenter(fp_cfg)
        self.view = bdv.DashView()
        self.controller = bdc.Controller()

        self.presenter.set_model(self.model)
        self.controller.set_model(self.model)
        self.view.set_presenter(self.presenter)
        self.view.set_controller(self.controller)

    def run(self):
        self.view.launch_app()


def main():
    app = BeaverApp(fp_cfg)
    app.run()


main()
