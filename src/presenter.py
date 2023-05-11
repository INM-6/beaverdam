"""Prepare data for visualization
"""

import uuid


def remove_unselected_rows(data_table):
    """Remove rows of a dataframe that aren't contained in the selection-state column

    Args:
        data_table (DataTable): DataTable with data_table.df containing the dataframe to
        be filtered and data_table.selection_state_column_name giving the name of the
        column of the dataframe containing the selection state of each row.
    Returns:
        pretty_df (dataframe):  dataframe WITHOUT (1) the selection-state column and
        (2) any unselected rows
    """

    if data_table.selection_state_column_name in data_table.df.columns:
        # Drop any unselected rows.  Use the default of inplace=False so that df.drop
        # returns a new dataframe rather than modifying the original dataframe.
        pretty_df = data_table.df.drop(
            data_table.df[
                data_table.df[data_table.selection_state_column_name] == False
            ].index
        )
        # Remove column denoting selection state.  Use inplace=True so that df.drop
        # modifies the dataframe it's called on, rather than returning a new dataframe.
        pretty_df.drop([data_table.selection_state_column_name], axis=1, inplace=True)
    else:
        pretty_df = data_table.df.copy(deep=True)
    return pretty_df


def rename_df_columns(df, col_name_dict):
    """Rename the columns of a dataframe

    Args:
        df (dataframe): dataframe whose columns should be renamed
        col_name_dict (dict): dictionary containing keys=new names, vals=old names
    Returns:
        renamed_df (dataframe): dataframe with renamed columns
    """
    # Reverse the dict so keys=old names, vals=new names
    col_name_dict_reversed = {y: x for x, y in col_name_dict.items()}
    renamed_df = df.rename(columns=col_name_dict_reversed)
    return renamed_df


class Presenter:
    def __init__(self, cfg):
        """
        Args:
            cfg (namedtuple):  contains dicts for each heading of config file.  Example:

                cfg.headingName
                    {'key1': val1, 'key2': val2}
                cfg.headingName["key1"]
                    val1
                cfg.headingName["key2"]
                    val2

            Should contain headings:  plots, projections, queries
        """
        self.cfg = cfg

    def set_core(self, core_to_use):
        self.core = core_to_use
        # Load current info from core
        self.build()

    def build(self):

        # Make data table
        self.data_tables = [PrettyDataTable(self.core.data_table)]

        # Make graphs
        self.graphs = []
        for plot_info in self.cfg["plots"].values():
            if plot_info["plot_type"] == "pie":
                self.graphs.append(
                    PieChart(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            elif plot_info["plot_type"] == "bar":
                self.graphs.append(
                    BarGraph(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            elif plot_info["plot_type"] == "scatter":
                self.graphs.append(
                    ScatterPlot(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            else:
                pass

        # Make checklists
        self.checklists = []
        for ichecklist in self.cfg["filters"]["headings"]:
            self.checklists.append(
                FilterChecklist(metadata_source=self.core.db, display_name=ichecklist)
            )

    def update(self):
        for itable in self.data_tables:
            itable.update(self.core.data_table)
        for igraph in self.graphs:
            igraph.update(self.core.data_table)
        for ichecklist in self.checklists:
            ichecklist.update(self.core.data_table.filter_criteria)


class VisualizedObject:
    """General class for all output objects to visualize search results"""

    def __init__(self):
        """General attributes for all output objects"""
        # Set ID for UI element
        self.id = str(uuid.uuid4())


class PrettyDataTable(VisualizedObject):
    """Store data to display in a table"""

    def __init__(self, data_table, new_column_names={}):
        """Format a dataframe for display

        Args:
            data_table (DataTable): data_table.df is a dataframe containing data to be
            shown in the table; data_table.selection_state_column_name gives the name of
            the column indicating the selections state of each row
            new_column_names (opt; dict):  keys = new column names to display, vals =
            column names in df.  If a column name is not specified in the dict, the
            original column name will be retained.
        Returns:
            self.df (dataframe):  data to be shown in the table; column names are the
            same as column headers to display
        """
        super().__init__()

        self.build(data_table, new_column_names)

    def build(self, data_table, new_column_names={}):
        # Remove rows that won't be shown in data table
        self.df = remove_unselected_rows(data_table)
        # Rename columns to human-readable names
        self.df = rename_df_columns(self.df, new_column_names)

    def update(self, data_table, new_column_names={}):
        # Remove rows that won't be shown in data table
        self.df = remove_unselected_rows(data_table)
        # Rename columns to human-readable names
        self.df = rename_df_columns(self.df, new_column_names)


class DataFigure(VisualizedObject):
    """Store information to generate figures"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        """Store information to plot a figure from data

        Args:
            data_table (DataTable): object with data_table.df containing the dataframe
            with data to plot, and data_table.selection_state_column_names giving the
            name of the column indicating the selection state of each row
            col_to_plot (string or list of strings matching dataframe column labels):
            which columns of the dataframe contain data to plot
            col_labels (dict, optional): labels to use for each column of data, if you
            don't want to use the existing dataframe column labels. keys = new names to
            display, vals = column names in df. Defaults to {}.
            title (str): title of resulting figure.  Defaults to [].
        Returns:
            self.graph_type (str):  type of graph to plot
            self.df (dataframe):  dataframe containing data to plot and columns named
            with display names
            self.title (str):  title of plot
        """
        super().__init__()

        self.graph_type = "undefined"

        # Make sure the columns to plot are given as a list, even if only a single
        # string is given.  If you subset a column from a dataframe with a string, it
        # returns a series rather than a dataframe, and this screws up future
        # operations.
        if isinstance(col_to_plot, str):
            col_to_plot = [col_to_plot]
        self.col_to_plot = col_to_plot

        # Filter dataframe
        self.df = remove_unselected_rows(data_table)

        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(col_to_plot) > 0:
            # Make sure the column(s) are given as a list
            if isinstance(col_to_plot, list) is not True:
                col_to_plot = [col_to_plot]
            # Extract the columns
            self.df = self.df[col_to_plot].copy()
        else:
            pass

        # Rename columns
        self.col_labels = col_labels
        self.df = rename_df_columns(self.df, self.col_labels)

        # Set title
        self.title = title

    def update(self, data_table):
        # Filter dataframe
        self.df = remove_unselected_rows(data_table)

        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(self.col_to_plot) > 0:
            self.df = self.df[self.col_to_plot].copy()
        else:
            pass

        # Rename columns
        self.df = rename_df_columns(self.df, self.col_labels)


class PieChart(DataFigure):
    """Store information to generate pie charts"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        super().__init__(data_table, col_to_plot, col_labels, title)
        self.graph_type = "pie"


class BarGraph(DataFigure):
    """Store information to generate bar graphs"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        super().__init__(data_table, col_to_plot, col_labels, title)
        self.graph_type = "bar"


class ScatterPlot(DataFigure):
    """Store information to generate scatter plots"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        super().__init__(data_table, col_to_plot, col_labels, title)
        self.graph_type = "scatter"
        # Reset title
        self.title = " vs. ".join(self.title)


class FilterChecklist(VisualizedObject):
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
        # Find which selected options are in the current checklist and store them
        try:
            self.selected_options = selected_options[self.display_name]
        except:
            self.selected_options = []
