"""General class for user interfaces"""


class View:
    """Define the user interface's source of information and what actions it can initiate"""

    def __init__(self):
        pass

    def set_presenter(self, presenter):
        """Set the source of information to create the user interface

        Args:
            presenter (Presenter): contains data and formatting information for
            checklists, plots, and tables
        """
        self.presenter = presenter

        # Get information about the elements that can be included in the UI
        self.ui_elements = presenter.get_elements()

    def set_controller(self, controller):
        """Set the source of functions to execute on interaction with the frontend

        Args:
            controller (Controller): contains function logic and connection to Core
        """
        self.controller = controller
