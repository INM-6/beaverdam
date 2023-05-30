"""Dash reset button"""

import resetbutton as resetbutton
from dash import html

class DashResetButton(resetbutton.ResetButton):
    """Button to clear all filter criteria"""

    def __init__(self):
        """Set type of UI element, so it's compatible with other UI elements"""
        super().__init__()

    def build(self):
        """Build plot for user interface

        Returns:
            html.Div containing button
        """

        # Build the button
        return html.Div(
            children=[
                html.Button("Reset", id=self.id, n_clicks=0),
            ]
        )