"""General class for reset button"""

import uielement as uielement

class ResetButton(uielement.UiElement):
    """Button to clear all filter criteria"""

    def __init__(self):
        """Set type of UI element, so it's compatible with other UI elements"""
        super().__init__()
        # Set type of UI element
        self.id["type"] = "ResetButton"

    def build(self):
        pass