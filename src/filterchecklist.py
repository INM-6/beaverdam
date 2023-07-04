"""General class for checklists for filter criteria"""

import uielement as uielement


class FilterChecklist(uielement.UiElement):
    """Checklist containing filter criteria"""

    def __init__(self, filter_checklist_object):
        """Get and store checklist options and other properties

        Args:
            filter_checklist_object (FilterChecklist from Presenter module): title and
            options for the checklist
        """
        super().__init__(filter_checklist_object)

        # Set type of UI element
        self.id["type"] = "FilterChecklist"

        # Duplicate fields from filter_checklist_object [there's got to be a nicer way
        # to do this]
        self.checklist_options = filter_checklist_object.checklist_options
        self.field = filter_checklist_object.field
        self.title = filter_checklist_object.title

    def build(self):
        pass

    def update(self):
        pass
