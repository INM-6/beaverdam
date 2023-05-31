"""Dash checklists for filter criteria"""

import filterchecklist as filterchecklist
from dash import dcc, html


class DashFilterChecklist(filterchecklist.FilterChecklist):
    """Checklist containing filter criteria"""

    def __init__(self, filter_checklist_object):
        """Get and store checklist options and other properties

        Args:
            filter_checklist_object (FilterChecklist from Presenter module): title and
            options for the checklist
        """
        super().__init__(filter_checklist_object)

    def build(self):
        """Build checklist for the user interface

        Returns:
            html.Div containing checklist title and options
        """

        # Build the checklist elements
        return html.Div(
            children=[
                html.Div(children=self.title),
                html.Div(
                    children=dcc.Checklist(
                        options=self.checklist_options,
                        value=[],
                        id=self.id,
                        labelStyle={"display": "block"},
                    )
                ),
            ]
        )

    def update(self, new_values):
        """Update checklist"""
        self.values = new_values
