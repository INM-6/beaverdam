import uuid

# Define classes for different types of user interface elements.
#
# The classes can inherit from each other.  Each class inherits properties of its
# superclass(es), and can have new properties.
#
# Every instance of a class has to have a unique identifier (ID) that is automatically
# generated if one isn't provided.
#
# Some properties are used to actually build the element ("contents"), and
# others describe characteristics of the element that can be used e.g. to select
# elements of certain types ("properties").
#
# The properties of an element are stored in a dict so that new ones can be added easily
# and accessed by the get_properties() function, without having to rewrite stuff in
# multiple places.  Subclasses inherit all properties of their parent classes, and can
# add new properties.
#
# Here is a rough proposal for the properties:
#   id:  unique identifier (will be generated if not provided)
#   type:  FilterChecklist, DataTable, DataFigure
#   field:  name of the df column(s) represented by the UiElement.  Must match the name assigned in the config file.
#   style:  pie, bar, scatter

def rename_df_columns(df, col_name_dict={}):
    """Rename the columns of a dataframe
    
    Columns not contained in col_name_dict will not be renamed.

    Args:
        df (dataframe): dataframe whose columns should be renamed
        col_name_dict (dict; opt): dictionary containing keys=new names, vals=old names
    Returns:
        renamed_df (dataframe): dataframe with renamed columns
    """
    # Reverse the dict so keys=old names, vals=new names
    col_name_dict_reversed = {y: x for x, y in col_name_dict.items()}
    renamed_df = df.rename(columns=col_name_dict_reversed)
    return renamed_df


class UiElement:
    """General class for all UI elements"""

    def __init__(self):
        """Initialize any fields that all UiElements should contain

        Args:
            UIelement (structure, optional): use this to manually define the ID for an
            element by providing some kind of structure with an "id" field that can be
            accessed by UIelement.id. Defaults to [], to auto-generate an ID.
        """        
        self.properties = {}
        self.contents = {}
        
        # Unique identifier for the element
        self.properties["id"] = str(uuid.uuid4())
        # What type of object it is
        self.properties["type"] = "undefined"

    def get_properties(self):
        """Return an object's properties

        Returns:
            properties (dict): everything in self.properties
        """
        return self.properties
    
    def get_contents(self):
        """Return the data and labels etc. for the resulting figure

        Returns:
            contents (dict): everything in self.contents
        """
        return self.contents
    
    def update(self):
        """Update the element with new data"""
        pass


class FilterChecklist(UiElement):
    """Checklist containing filter criteria"""

    def __init__(self, metadata_source, field, checklist_title=[], selected_options=[]):
        """Store checklist options and other properties

        Args:
            metadata_source (MetadataSource):  information about where to find metadata
            field (str):  which metadata attribute the checklist represents
            checklist_title (str):  title for the checklist (optional; if not given,
            field_location will be used)
            selected_options (list):  which checklist options are selected (optional; if
            not given, no options will be selected)
        """
        super().__init__()

        # Properties
        self.properties["type"] = "FilterChecklist"
        self.properties["field"] = [field]

        # Set title for the checklist.  Default to field_location if checklist_title
        # isn't provided
        if len(checklist_title) > 0:
            self.contents["title"] = checklist_title
        else:
            self.contents["title"] = field
        # Find all options for the checklist
        checklist_query_results = metadata_source.query(query_output=field)
        self.contents["checklist_options"] = (
            checklist_query_results[field].drop_duplicates().to_list()
        )
        # Find which options are selected
        try:
            self.contents["selected_options"] = selected_options#[self.field]
        except:
            self.contents["selected_options"] = []

    def update(self, new_selected_options):
        """Update which options are selected in the checklist

        Args:
            new_selected_options (list):  which options are selected
        """
        self.contents["selected_options"] = new_selected_options

class DataTable(UiElement):
    """Data tables"""

    def __init__(self, data_table, new_column_names={}):
        """Store data table options and other properties

        Args:
            data_table (DataTableCore): data_table.df is a dataframe containing data to
            be shown in the table; data_table.selection_state_column_name gives the name
            of the column indicating the selections state of each row
            new_column_names (opt; dict):  keys = new column names to display, vals =
            column names in df.  If a column name is not specified in the dict, the
            original column name will be retained.
        """
        super().__init__()

        # Properties
        self.properties["type"] = "DataTable"

        # Contents
        self.contents["df"] = rename_df_columns(
            data_table.get_selected_rows(), 
            new_column_names
            )

    def update(self, new_data_table, new_column_names={}):
        """Update data table contents

        Args:
            data_table (DataTableCore): data_table.df is a dataframe containing data to
            be shown in the table; data_table.selection_state_column_name gives the name
            of the column indicating the selections state of each row
            new_column_names (opt; dict):  keys = new column names to display, vals =
            column names in df.  If a column name is not specified in the dict, the
            original column name will be retained.
        """
        self.contents["df"] = rename_df_columns(
            new_data_table.get_selected_rows(), 
            new_column_names
            )

class DataFigure(UiElement):
    """General class for figures"""

    def __init__(self, data_table, field, style="undefined"):
        """Set common DataFigure properties

        Args:
            data_table (DataTableCore): object with data_table.df containing the
            dataframe with data to plot, and data_table.selection_state_column_names
            giving the name of the column indicating the selection state of each row
            field (string or list of strings matching dataframe column labels):
            which columns of the dataframe contain data to plot
        """
        super().__init__()
        
        # Properties
        self.properties["type"] = "DataFigure"
        self.properties["field"] = [field] if isinstance(field, str) else field
        self.properties["style"] = style

        # Contents
        self.contents["df"] = data_table.get_selected_rows().filter(
            items=self.properties["field"]
            )
        
    def update(self, new_data_table):
        """Update the data shown in the figure

        Args:
            data_table (DataTableCore): object with data_table.df containing the
            dataframe with data to plot, and data_table.selection_state_column_names
            giving the name of the column indicating the selection state of each row
        """
        self.contents["df"] = new_data_table.get_selected_rows().filter(
            items=self.properties["field"]
            )


class PieChart(DataFigure):
    """Create pie chart"""

    def __init__(self, data_table, field, title):
        """Store pie chart options and other properties

        Args:
            graph_object (PieChart class from Presenter module): title and options for
            the graph
        """
        super().__init__(data_table, field, "pie")
        self.contents["title"] = title


class BarGraph(DataFigure):
    """Create bar graph"""

    def __init__(self, data_table, field, title):
        """Store bar graph options and other properties

        Args:
            graph_object (BarGraph class from Presenter module): title and options for
            the graph
        """
        super().__init__(data_table, field, "bar")
        self.contents["title"] = title


class ScatterPlot(DataFigure):
    """Scatterplot figure"""

    def __init__(self, data_table, field, title):
        """Get and store figure options and other properties

        Args:
            graph_object (ScatterPlot class from Presenter module): title and options for
            the graph
        """
        super().__init__(data_table, field, "scatter")
        self.contents["title"] = title
