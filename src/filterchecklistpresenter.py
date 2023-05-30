"""Information to create checklists in a user interface"""

import uielementpresenter as uiobj


class FilterChecklistPresenter(uiobj.UIElementPresenter):
    """Information for lists of checkboxes to filter data"""

    def __init__(
        self, metadata_source, display_name, checklist_title=[], selected_options=[]
    ):
        """Set checklist properties and find options

        Args:
            metadata_source (MetadataSource):  information about where to find metadata
            display_name (str):  which metadata attribute the checklist represents
            checklist_title (str):  title for the checklist (optional; if not given,
            field_location will be used)
            selected_values (list):  which checklist options are selected (optional; if
            not given, no options will be selected)
        """
        super().__init__()

        # Store display name for access later
        self.display_name = display_name

        # Find options for the checklist
        checklist_query_results = metadata_source.query(query_output=display_name)
        self.checklist_options = (
            checklist_query_results[display_name].drop_duplicates().to_list()
        )
        try:
            self.selected_options = selected_options[self.display_name]
        except:
            self.selected_options = []

        # Set title for the checklist.  Default to field_location if checklist_title
        # isn't provided
        if len(checklist_title) > 0:
            self.title = checklist_title
        else:
            self.title = display_name

    def update(self, selected_options):
        """Update checklist with currently selected options

        Args:
            selected_options (dict): dict with key=column, name, val=selected values
        """
        # Find which selected options are in the current checklist and store them
        try:
            self.selected_options = selected_options[self.display_name]
        except:
            self.selected_options = []
