"""Beaverdam queries databases of metadata and visualizes the results.

:copyright:
:licence:
"""

# Import external packages
import pandas as pd
from pymongo import MongoClient


class MetadataSource:
    """Store information about where to get metadata"""

    def __init__(self):
        pass

    def Query():
        """Get metadata from source"""
        # Should return a dataframe
        pass


class MongoDbDatabase(MetadataSource):
    """Use a MongoDB database as a metadata source"""

    def __init__(self, address, port, db_name, collection_name):
        """Define database properties

        Args:
            address (string): location of the server
            port (int): number of the port to access
            db_name (string): name of the MongoDB database
            collection_name (string): name of the collection containing the documents
            you want to view
        """
        self.address = address
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

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
        client = MongoClient(self.address, self.port)
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
            df[filter_col_name] = 1
        self.df = df

    def filter(self, filter_criteria):
        """Identify rows that meet the filter criteria and mark them as selected
        
        Args:
        filter_criteria (FilterCriteria): dict of criteria -- sessions must meet at least one allowable val for all keys in the dict"""
        pass


class FilterCriteria:
    """Store and update selection criteria"""

    def __init__(self, criteria_dict={}):
        """Create a new object with a defined list of criteria
        Args:
        criteria_dict (dict):  keys=projection, vals=allowable options"""
        self.criteria = criteria_dict

    def update(self, new_criteria_dict):
        """Update existing criteria or add new ones"""
        # Check if criteria exists
        # If it exists, update with new val
        # If it does not exist, add it
        pass
