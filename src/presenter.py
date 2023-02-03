"""Prepare data for visualization
"""


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
    # Make sure to explicitly make a deep copy of the df, otherwise changes to pretty_df
    # will be reflected in data_table.df
    # pretty_df = data_table.df.copy(deep=True)

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
    col_name_dict = {y: x for x, y in col_name_dict.items()}
    renamed_df = df.rename(columns=col_name_dict)
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
        self.update()

    def update(self):

        # TODO:  use loops for tables/charts/checklists to account for possibility of multiples

        self.data_tables = PrettyDataTable(self.core.data_table)
        self.graphs = PieChart(
            data_table=self.core.data_table,
            col_to_plot=self.cfg["plots"]["monkey_name"]["data_field"],
            title="Make nice plot titles",
        )
        self.checklists = FilterChecklist(
            self.core.db, self.cfg["filters"]["headings"][0]
        )


class PrettyDataTable:
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

        self.df = remove_unselected_rows(data_table)

        self.df = rename_df_columns(self.df, new_column_names)


class DataFigure:
    """Store information to generate figures"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        """Store information to plot a figure from data

        Args:
            data_table (DataTable): object with data_table.df containing the dataframe
            with data to plot, and data_table.selection_state_column_names giving the
            name of the column indicating the selection state of each row
            col_to_plot (list of strings matching dataframe column labels): which
            columns of the dataframe contain data to plot
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
        self.graph_type = "undefined"

        # Filter dataframe
        self.df = remove_unselected_rows(data_table)

        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(col_to_plot) > 0:
            self.df = self.df[[col_to_plot]].copy()
        else:
            pass

        # Rename columns
        self.df = rename_df_columns(self.df, col_labels)

        # Set title
        self.title = title


class PieChart(DataFigure):
    """Store information to generate pie charts"""

    def __init__(self, data_table, col_to_plot=[], col_labels={}, title=[]):
        super().__init__(data_table, col_to_plot, col_labels, title)
        self.graph_type = "pie"
        # TODO: Manipulate dataframe so that there is one column for categories and one for counts
        # Example:
        #   df:
        #           colName
        #       1   val1
        #       2   val1
        #       3   val2
        #   manipulated df:
        #       colName
        #       val1    2
        #       val2    1
        # self.df = pd.DataFrame(self.df.value_counts()).reset_index()


class FilterChecklist:
    """Information for lists of checkboxes to filter data"""

    def __init__(self, metadata_source, display_name, checklist_title=[]):
        """Set checklist properties and find options

        Args:
            metadata_source (MetadataSource):  information about where to find metadata
            display_name (str):  which metadata attribute the checklist represents
            checklist_title (str):  title for the checklist (optional; if not given,
            field_location will be used)
        """
        # Find options for the checklist
        checklist_query_results = metadata_source.query(query_output=display_name)
        self.checklist_options = (
            checklist_query_results[display_name].drop_duplicates().to_list()
        )

        # Set title for the checklist.  Default to field_location if checklist_title
        # isn't provided
        if len(checklist_title) > 0:
            self.title = checklist_title
        else:
            self.title = display_name
