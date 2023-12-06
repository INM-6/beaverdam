"""Create an object for a source of metadata, and define how to access its information
"""

from pymongo import MongoClient
import pandas as pd


class MetadataSource:
    """Store information about where to get metadata"""

    def __init__(self):
        pass

    def set_fields():
        """Store name and access information for each metadata field"""
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
                'collection_name' -- string: name of the collection containing the
                documents you want to view
        """
        # Get database information
        self.__address = cfg["address"]
        self.__port = cfg["port"]
        self.__db_name = cfg["db_name"]
        self.__collection_name = cfg["collection_name"]

    def set_fields(self, field_dict):
        """Store name and access information for each metadata field

        Args:
            field_dict (dict): keys = field names, vals = path to metadata field in
            database
        """
        self.fields = field_dict

    def get_field_name(self, requested_paths="all"):
        """Get list of field names from list of paths

        Args:
            requested_paths (str or list): string or list of strings, with each string
            corresponding to a path in the database.  Defaults to "all" to return all
            paths.
        """
        if requested_paths == "all":
            field_names = list(self.fields.keys())
        elif isinstance(requested_paths, str):
            field_names = [
                i_name
                for i_name in list(self.fields.keys())
                if self.fields[i_name] == requested_paths
            ][0]
        else:
            field_names = [
                i_name
                for i_name in list(self.fields.keys())
                if self.fields[i_name] in requested_paths
            ]
        return field_names

    def get_path(self, requested_field_names="all"):
        """Get list of paths from list of field names

        Args:
            requested_field_names (str or list): string or list of strings, with each
            string corresponding to a field name as defined in the config file.
            Defaults to "all" to return all field names.
        """
        if requested_field_names == "all":
            field_paths = list(self.fields.values())
        elif isinstance(requested_field_names, str):
            field_paths = self.fields[requested_field_names]
        else:
            field_paths = [self.fields[i_name] for i_name in requested_field_names]
        return field_paths

    def query(self, query_input={}, query_output={}):
        """Query a MongoDB database

        Args:
            query_input (dict or list of str):  requested queries.  If dict, should be a
            query formatted in MongoDB style.  If list, should be strings corresponding
            to the field names in self.fields.  Default is all fields.
                Ref:  https://www.analyticsvidhya.com/blog/2020/08/query-a-mongodb-database-using-pymongo/
                query_input = {
                    'Document.sections.TaskParameters.properties.dtp_filename.value': {"$in": ['Hex_VR2_LR100.dtp', 'Hex_2-4-6_and_3-5-7.dtp']},
                    'Document.sections.session.sections.Session.sections.Task.properties.ShortName.value': "land"
                }
            query_output (dict or str or list of str):  requested projections.  If dict,
            should be projections formatted in MongoDB style.  If string or list of
            strings, strings should correspond to the field names in self.fields.
            Default is all fields.
                query_output = {"path.to.output.value": 1}

        Returns:
            query_results (dataframe): rows=documents and cols=projections
        """
        # TODO:  if the query inputs isn't a dict, convert it
        if not isinstance(query_input, dict):
            raise Exception("This function isn't defined yet.")

        # If the query output isn't already in the format pymongo likes, convert it
        if not isinstance(query_output, dict):
            # If the query output is given as a string, convert to a list
            query_output = (
                [query_output] if isinstance(query_output, str) else query_output
            )
            # Get the corresponding locations of the fields
            output_paths = self.get_path(query_output)
            query_output = {ipath: 1 for ipath in output_paths}

        # Use the projection ID as the index in the output dataframe
        index_id = "_id"

        # Set up pointers to the database
        client = MongoClient(self.__address, self.__port)
        db = getattr(client, self.__db_name)
        collection = getattr(db, self.__collection_name)

        # Query the database
        cursor = collection.find(query_input, projection=query_output)

        # Put projection values into a dataframe.  For each session, make a dict where
        # the keys are the field names and the vals are their values for that session.
        # Then add the whole dict to the dataframe at once.
        query_results = pd.DataFrame(
            columns=self.get_field_name(list(query_output.keys()))
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
                    if isinstance(proj_val, list):
                        if len(proj_val) > 0:
                            val_to_add = proj_val[0]
                        else:
                            val_to_add = "-"
                    else:
                        try:
                            val_to_add = proj_val
                        except:
                            val_to_add = "-"
                    # Insert the value into the row you are adding to the dataframe
                    row_to_add[self.get_field_name(proj_path)] = val_to_add
                    # Append the row for this session to the dataframe and assign the
                    # index of the new row
                    query_results.loc[doc[index_id]] = row_to_add

        finally:
            client.close()
        return query_results
