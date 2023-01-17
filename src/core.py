"""Query databases of metadata and filter the results.

:copyright:
:licence:
"""

import pandas as pd
from pymongo import MongoClient
import parser

class MetadataSource:
    """Store information about where to get metadata"""

    def __init__(self):
        pass

    def query():
        """Get metadata from source"""
        # Should return a dataframe
        pass


class MongoDbDatabase(MetadataSource):
    """Use a MongoDB database as a metadata source"""

    def __init__(self, config_file_path):
        """Define database properties

        Args:
            config_file_path (string):  path to configuration file.  Configuration file 
            should contain a section with the heading 'database' and contents:
                address (string): location of the server
                port (int): number of the port to access
                db_name (string): name of the MongoDB database
                collection_name (string): name of the collection containing the documents
                you want to view
        """
        # Read configuration file and store database information
        cfg = parser.parse_config(config_file_path, 'database')
        self.address = str(cfg.database["address"])
        self.port = int(cfg.database["port"])
        self.db_name = cfg.database["db_name"]
        self.collection_name = cfg.database["collection_name"]

    def set_queries(self, requested_queries):
        """Store requested queries

        Args:
            requested_queries (dict or str): If a dict:  criteria to meet for records to 
            be returned. If a string:  path to config file with a section named 
            'queries' containing the query information
        """
        # Format queries so the logical and/or will work.  The format should be:
        # Ref:  https://www.analyticsvidhya.com/blog/2020/08/query-a-mongodb-database-using-pymongo/
        # requested_queries = {
        #     'Document.sections.TaskParameters.properties.dtp_filename.value': {"$in": ['Hex_VR2_LR100.dtp', 'Hex_2-4-6_and_3-5-7.dtp']},
        #     'Document.sections.session.sections.Session.sections.Task.properties.ShortName.value': "land"
        # }
        self.queries = requested_queries  # Change this later

    def set_projections(self, requested_projections):
        """Store requested projections

        Args:
            requested_projections (dict or str):
                If a dict:  specifies values to be returned with format:
                    {"path.to.output.value": 1}
                If a string:  path to config file with a section named 'projections' 
                containing lines with format:
                    ShortName = "path.to.output.value"
        """
        if isinstance(requested_projections, str):
            # If the input points to a config file, get the projections and convert them
            # to the appropriate format
            cfg = parser.parse_config(requested_projections, 'projections')
            requested_projections = dict.fromkeys(list(cfg.projections.values()), 1)
        elif isinstance(requested_projections, dict):
            # If the input is already in the correct format (assume anything dict is
            # correct), then leave it as is
            pass
        else:
            raise Exception(
            "Requested projections not provided in correct format."
        )
        self.projections = requested_projections

    def query(self, requested_queries, requested_projections):
        """Query a MongoDB database

        Args:
            requested_queries (dict): criteria to meet for records to be returned
            requested_projections (dict?): which information to return from a record

        Returns:
            query_results: Pandas dataframe with rows=documents and cols=projections
        """
        # Use the projection ID as the index in the output dataframe
        index_id = "_id"

        # Extract only the paths of the projections, as strings
        projection_paths = list(requested_projections.keys())

        # Set up pointers to the database
        client = MongoClient(self.address, self.port)  # "localhost",27017)#
        db = getattr(client, self.db_name)
        collection = getattr(db, self.collection_name)

        # Query the databaase
        cursor = collection.find(requested_queries, projection=requested_projections)

        # Put projection values into a dataframe.  For each session, make a dict where
        # the keys are the requested projections and the vals are their values for that
        # session.  Then add the whole dict to the dataframe at once.
        # query_results = Table(pd.DataFrame(columns=projection_paths))
        query_results = pd.DataFrame(columns=projection_paths)
        try:
            for doc in cursor:
                row_to_add = {}
                for proj_path in projection_paths:
                    proj_val = doc
                    # Get the value for each nested set of dict keys which are generated
                    # from the projection path
                    for ikey in proj_path.split("."):
                        try:
                            proj_val = proj_val[ikey]
                        except:
                            proj_val = ["-"]
                    # Store the value to add to the dataframe; store a default
                    # placeholder if the value doesn't exist
                    if len(proj_val) > 0:
                        row_to_add[proj_path] = proj_val[0]
                    else:
                        row_to_add[proj_path] = "-"
                    # Append the row for this session to the dataframe and assign the
                    # index of the new row
                    # query_results.df.loc[doc[index_id]] = row_to_add
                    query_results.loc[doc[index_id]] = row_to_add

        finally:
            client.close()
        return query_results


class Table(pd.DataFrame):
    """Store data and information about which data is currently selected by the user"""

    def __init__(self, df):
        filter_col_name = "selectionState"
        super(Table, self).__init__()
        # Check whether there is already a column for specifying whether the row is
        # selected.  If not, add one.
        if filter_col_name not in df.columns:
            df[filter_col_name] = True
        self.df = df

    def filter(self, filter_criteria):
        """Identify rows that meet the filter criteria and mark them as selected

        Args:
        filter_criteria (FilterCriteria): dict of criteria, with key=column name,
        val=allowable values.  Sessions must meet at least one allowable val for all
        keys in the dict"""
        filter_col_name = "selectionState"

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
        self.df[filter_col_name] = is_row_selected


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
