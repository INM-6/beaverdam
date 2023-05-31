import uuid


class UiElement:
    """General class for all UI elements"""

    def __init__(self, UIelement=[]):
        """Assign an identifier to the new element

        Args:
            UIelement (structure, optional): use this to manually define the ID for an
            element by providing some kind of structure with an "id" field that can be
            accessed by UIelement.id. Defaults to [], to auto-generate an ID.
        """
        # Set ID of element
        if hasattr(UIelement, "id"):
            self.id = {"index": UIelement.id, "type": "undefined"}
        else:
            self.id = {"index": str(uuid.uuid4()), "type": "undefined"}

    def build(self):
        # Create the element
        pass
