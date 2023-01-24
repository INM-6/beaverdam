"""Query databases of metadata and filter the results.

:copyright:
:licence:
"""

import pandas as pd
from pymongo import MongoClient
import parser


class Core:
    def __init__(self, cfg):
        """Main code for the core/model of the app

        Args:
            cfg (dict):  contains dicts with information to configure each object that will be generated.  Keys should include:
                'database' -- information required to access the database
                'filters' -- which database fields to turn into checkboxes
        """

        # Define database info
        self.db = MongoDbDatabase(cfg["database"])
        self.db.set_fields(cfg["fields"])

        # Store information about fields to query and their display names
        # keys = display names, vals = access information for database (e.g. location)
        self.fields = cfg["fields"]

        # Query database for data table
        data_table = DataTable(self.db.query({}, list(self.fields.keys())))

        # query_request = MongoDbQueryIO()
        # query_request.set_query_input({})
        # query_request.set_query_output(cfg["projections"])
        # session_table = DataTable(self.db.query(query_request))

        # Initialize filter options
        filter_criteria = FilterCriteria(
            {}
            # {"Document.sections.subject.sections.Subject.properties.GivenName.value": ["Enya"]}
        )

        self.data_table = data_table
        self.filter_criteria = filter_criteria


class MetadataSource:
    """Store information about where to get metadata"""

    def __init__(self):
        pass

    def set_fields():
        """Store display name and access information for each metadata field"""
        pass

    def query():
        """Get metadata from source"""
        # Should return a dataframe
        pass


class MongoDbDatabase(MetadataSource):
    """Use a MongoDB database as a metadata source"""

    def __init__(self, cfg):
        """Define database properties

        Args:
            cfg (dict):  configuration information with keys:
                'address': string -- location of the server
                'port': int -- number of the port to access
                'db_name': string -- name of the MongoDB database
                'collection_name' -- string: name of the collection containing the documents
                you want to view
        """
        # Get database information
        self.address = cfg["address"]
        self.port = cfg["port"]
        self.db_name = cfg["db_name"]
        self.collection_name = cfg["collection_name"]

    def set_fields(self, field_dict):
        """Store display name and access information for each metadata field

        Args:
            field_dict (dict): keys = display names, vals = path to metadata field in
            database
        """
        self.fields = field_dict

    def get_display_name(self, requested_paths="all"):
        """Get list of display names from list of paths

        Args:
            requested_paths (str or list): string or list of strings, with each string
            corresponding to a path in the database.  Defaults to "all" to return all
            paths.
        """
        if requested_paths == "all":
            display_names = list(self.fields.keys())
        elif isinstance(requested_paths, str):
            display_names = [
                i_name
                for i_name in list(self.fields.keys())
                if self.fields[i_name] == requested_paths
            ][0]
        else:
            display_names = [
                i_name
                for i_name in list(self.fields.keys())
                if self.fields[i_name] in requested_paths
            ]
        return display_names

    def get_path(self, requested_display_names="all"):
        """Get list of paths from list of display names

        Args:
            requested_display_names (str or list): string or list of strings, with each
            string corresponding to a display name as defined in the config file.
            Defaults to "all" to return all display names.
        """
        if requested_display_names == "all":
            field_paths = list(self.fields.values())
        elif isinstance(requested_display_names, str):
            field_paths = self.fields[requested_display_names]
        else:
            field_paths = [
                self.fields[i_name] for i_name in requested_display_names
            ]
        return field_paths

    def query(self, query_input={}, query_output={}):
        """Query a MongoDB database

        Args:
            query_input (dict or list of str):  requested queries.  If dict, should be a
            query formatted in MongoDB style.  If list, should be strings corresponding
            to the display names in self.fields.  Default is all fields.
                Ref:  https://www.analyticsvidhya.com/blog/2020/08/query-a-mongodb-database-using-pymongo/
                query_input = {
                    'Document.sections.TaskParameters.properties.dtp_filename.value': {"$in": ['Hex_VR2_LR100.dtp', 'Hex_2-4-6_and_3-5-7.dtp']},
                    'Document.sections.session.sections.Session.sections.Task.properties.ShortName.value': "land"
                }
            query_output (dict or str or list of str):  requested projections.  If dict, should
            be projections formatted in MongoDB style.  If string or list of strings, strings
            should correspond to the display names in self.fields.  Default is all fields.
                query_output = {"path.to.output.value": 1}

        Returns:
            query_results (dataframe): rows=documents and cols=projections
        """
        # If either of the inputs are lists of display names, get the corresponding locations of the fields
        if isinstance(query_input, list):
            try:
                raise Exception("This function isn't defined yet.")
            except:
                raise Exception("Requested query inputs not defined.")
        if isinstance(query_output, list):
            try:
                output_paths = self.get_path(query_output)
                query_output = {ipath: 1 for ipath in output_paths}
            except:
                raise Exception("Requested query outputs not defined.")
        elif isinstance(query_output, str):
            output_paths = self.get_path(query_output)
            query_output = {output_paths: 1}

        # Use the projection ID as the index in the output dataframe
        index_id = "_id"

        # Extract only the paths of the projections, as strings
        # projection_paths = list(query_io.projections.values())

        # Set up pointers to the database
        client = MongoClient(self.address, self.port)  # "localhost",27017)#
        db = getattr(client, self.db_name)
        collection = getattr(db, self.collection_name)

        # Query the database
        cursor = collection.find(query_input, projection=query_output)

        # Put projection values into a dataframe.  For each session, make a dict where
        # the keys are the display names and the vals are their values for that
        # session.  Then add the whole dict to the dataframe at once.
        query_results = pd.DataFrame(
            columns=self.get_display_name(list(query_output.keys()))
        )
        try:
            for doc in cursor:
                row_to_add = {}
                for proj_path in list(query_output.keys()):
                    # Get the value for each nested set of dict keys which are generated
                    # from the projection path
                    proj_val = doc
                    for ikey in proj_path.split("."):
                        try:
                            proj_val = proj_val[ikey]
                        except:
                            proj_val = ["-"]
                    # Store the value to add to the dataframe; store a default
                    # placeholder if the value doesn't exist
                    if len(proj_val) > 0:
                        row_to_add[self.get_display_name(proj_path)] = proj_val[0]
                    else:
                        row_to_add[self.get_display_name(proj_path)] = "-"
                    # Append the row for this session to the dataframe and assign the
                    # index of the new row
                    query_results.loc[doc[index_id]] = row_to_add

        finally:
            client.close()
        return query_results


# class QueryIO:
#     """Store information about a desired query input and output"""

#     def __init__(self):
#         pass

#     def set_query_input(self, query_input):
#         """Which request you are sending for the query"""
#         pass

#     def set_query_output(self, query_output):
#         """What output information you desire from the query"""
#         pass


# class MongoDbQueryIO(QueryIO):
#     """Store desired queries and projections for a MongoDB database"""

#     def __init__(self):
#         super().__init__()

#     def set_query_input(self, requested_queries):
#         """Store requested queries

#         Args:
#             requested_queries (dict or str): If a dict:  criteria to meet for records to
#             be returned. If a string:  path to config file with a section named
#             'queries' containing the query information
#         """
#         # Format queries so the logical and/or will work.  The format should be:
#         # Ref:  https://www.analyticsvidhya.com/blog/2020/08/query-a-mongodb-database-using-pymongo/
#         # requested_queries = {
#         #     'Document.sections.TaskParameters.properties.dtp_filename.value': {"$in": ['Hex_VR2_LR100.dtp', 'Hex_2-4-6_and_3-5-7.dtp']},
#         #     'Document.sections.session.sections.Session.sections.Task.properties.ShortName.value': "land"
#         # }
#         self.queries = requested_queries  # Change this later

#     def set_query_output(self, requested_projections):
#         """Store requested projections

#         Args:
#             requested_projections (dict or str):
#                 If a dict:  specifies values to be returned with format:
#                     {"path.to.output.value": 1}
#                 If a string:  path to config file with a section named 'projections'
#                 containing lines with format:
#                     ShortName = "path.to.output.value"
#         """
#         if isinstance(requested_projections, str):
#             # veronica # check type of requested_projections
#             # If the input points to a config file, get the projections
#             requested_projections = requested_projections.projections
#         elif isinstance(requested_projections, dict):
#             # If the input is already in the correct format (assume anything dict is
#             # correct), then leave it as is
#             pass
#         else:
#             raise Exception("Requested projections not provided in correct format.")
#         self.projections = requested_projections


class DataTable(pd.DataFrame):
    """Store data and information about which data is currently selected by the user"""

    def __init__(self, df):
        selection_state_column_name = "selectionState"
        super(DataTable, self).__init__()
        # Store name of column indicating selection state of rows
        self.selection_state_column_name = selection_state_column_name
        # Check whether there is already a column for specifying whether the row is
        # selected.  If not, add one.
        if self.selection_state_column_name not in df.columns:
            df[selection_state_column_name] = True
        # Store dataframe
        self.df = df
        # Initialize place to store selection criteria -- will be a dict with key=column
        # name, val=allowable values
        self.selection_criteria = {}

    def filter(self, filter_criteria):
        """Identify rows that meet the filter criteria and mark them as selected

        Args:
        filter_criteria (FilterCriteria): dict of criteria, with key=column name,
        val=allowable values.  Sessions must meet at least one allowable val for all
        keys in the dict"""

        # Initialize list containing one list for each filter criterion
        is_row_selected = [[] for _ in range(len(self.df))]
        # For each criterion, find out if each row meets the criterion or not and add
        # this information as additional elements to each list inside the selected_rows
        # list.
        # NOTE: Replace isin by e.g. > == etc. to do more complicated comparisons
        for iCriteria, iVal in filter_criteria.criteria.items():
            is_row_selected = [
                x + [y] for x, y in zip(is_row_selected, self.df[iCriteria].isin(iVal))
            ]

        # Only accept rows where all criteria are met
        is_row_selected = [all(x) for x in is_row_selected]
        # Replace the column in the dataframe that denotes whether a row is selected or
        # not
        self.df[self.selection_state_column_name] = is_row_selected


class FilterCriteria:
    """Store and update selection criteria"""

    def __init__(self, criteria_dict={}):
        """Create a new object with a defined list of criteria
        Args:
        criteria_dict (dict):  keys=projection, vals=list of allowable options"""
        self.criteria = criteria_dict

    def update(self, new_criteria_dict):
        """Update existing criteria or add new ones"""
        # Check if criteria exists
        # If it exists, update with new val
        # If it does not exist, add it
        pass
