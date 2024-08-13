"""Create an object for a source of metadata, and define how to access its information."""

import pandas as pd
from abc import ABC, abstractmethod
from pymongo import MongoClient
from tinydb import TinyDB, Query


class MetadataSource(ABC):
    """Store information about where to get metadata."""

    def __init__(self):
        pass

    @abstractmethod
    def set_fields(self):
        """Store name and access information for each metadata field."""

    @abstractmethod
    def query(self):
        """Get metadata from source."""
        # Should return a dataframe

    @abstractmethod
    def delete_single_record(self, document_id):
        """Delete a single record (document) from a collection, if it exists.

        Args:
            document_id (str): _id field for the document to be deleted

        Returns:
            (int) number of documents deleted (1 or 0)

        """

    @abstractmethod
    def insert_single_record(self, document_to_insert):
        """Insert a single record (document) into a collection.

        Args:
            document_to_insert (json): contents of the document to insert.  If
            the document doesn't have an _id field, one will be added automatically.

        Returns:
            (str) _id property of the inserted document

        """


class MongoDbDatabase(MetadataSource):
    """Use a MongoDB database as a metadata source."""

    def __init__(self, cfg):
        """Define database properties.

        Args:
            cfg (dict):  configuration information with keys:
                'address': string -- location of the server
                'port': int -- number of the port to access
                'db_name': string -- name of the MongoDB database
                'collection_name' -- string: name of the collection containing the
                documents you want to view

        """
        # Get database information
        self._address = cfg["address"]
        self._port = cfg["port"]
        self._db_name = cfg["db_name"]
        self._collection_name = cfg["collection_name"]

    def set_fields(self, field_dict):
        """Store name and access information for each metadata field.

        Args:
            field_dict (dict): keys = field names, vals = path to metadata field in
            database

        """
        self.fields = field_dict

    def get_field_name(self, requested_paths="all"):
        """Get list of field names from list of paths.

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

    def _get_client(self):
        """Get the client specified by the database information.

        Returns
            MongoDB client

        """
        return MongoClient(self._address, self._port)

    def _get_database(self):
        """Get the database specified by the database information.

        Returns
            MongoDB database

        """
        return getattr(self._get_client(), self._db_name)

    def _get_collection(self):
        """Get the collection specified by the database information.

        Returns
            MongoDB collection

        """
        return getattr(self._get_database(), self._collection_name)

    def get_path(self, requested_field_names="all"):
        """Get list of paths from list of field names.

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
        """Query a MongoDB database.

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

        # Query the database
        collection = self._get_collection()
        cursor = collection.find(query_input, projection=query_output)

        # Put projection values into a dataframe.  For each session, make a dict where
        # the keys are the field names and the vals are their values for that session.
        # Then add the whole dict to the dataframe at once.  Each column needs to have
        # dtype=object in order to be able to store iterables, e.g. lists.
        query_results = pd.DataFrame(
            columns=self.get_field_name(list(query_output.keys())), dtype=object
        )
        try:
            for doc in cursor:
                for proj_path in list(query_output.keys()):
                    # Get the value for each nested set of dict keys which are generated
                    # from the projection path
                    proj_val = doc
                    for ikey in proj_path.split("."):
                        try:
                            proj_val = proj_val[ikey]
                        except:
                            try:
                                proj_val = proj_val[int(ikey)]
                            except:
                                proj_val = None
                    # Insert the value into the correct row and column of the dataframe.
                    #
                    # Note that because some values may be lists, we have to do this
                    # individualy for each cell of the dataframe, rather than append an
                    # entire row at once.  This is because of how .loc and .at work.
                    # Here is an informative StackOverflow answer:
                    # https://stackoverflow.com/a/54447608
                    # and the documentation for .loc:
                    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.loc.html
                    query_results.loc[doc[index_id], self.get_field_name(proj_path)] = (
                        proj_val
                    )

        finally:
            self._get_client().close()
        return query_results

    def delete_single_record(self, document_id):
        """Delete a single record (document) from a collection, if it exists.

        Args:
            document_id (str): _id field for the document to be deleted

        Returns:
            (int) number of documents deleted (1 or 0)

        """
        collection = self._get_collection()
        deletion_result = collection.delete_one({"_id": document_id})
        return deletion_result.deleted_count

    def insert_single_record(self, document_to_insert):
        """Insert a single record (document) into a collection.

        Args:
            document_to_insert (json or bson): contents of the document to insert.  If
            the document doesn't have an _id field, one will be added automatically.

        Returns:
            (str) _id property of the inserted document

        """
        collection = self._get_collection()
        insertion_result = collection.insert_one(document_to_insert)
        return insertion_result.inserted_id

class TinyDbJson(MetadataSource):
    """Use a TinyDB JSON "database" as a metadata source.

    This avoids the need to install a separate database backend.
    """

    def __init__(self, cfg):
        """Define database properties.

        Args:
            cfg (dict):  configuration information with keys:
                'location': string -- location of the json file used as a database. This
                will eventually be created if it doesn't already exist.

        """
        # Get database information
        self._location = cfg["location"]

    def set_fields(self, field_dict):
        """Store name and access information for each metadata field.

        Args:
            field_dict (dict): keys = field names, vals = path to metadata field in
            json database

        """
        self.fields = field_dict

    def query(self, query_input={}, query_output={}):
        """Query a TinyDB json database.

        Args:
            query_input (dict or list of str):  requested queries.  If dict, should be a
            query formatted in TinyDB style.  If list, should be strings corresponding
            to the field names in self.fields.  Default is all fields.
                query_input = {
                    'Document.sections.TaskParameters.properties.dtp_filename.value': {"$in": ['Hex_VR2_LR100.dtp', 'Hex_2-4-6_and_3-5-7.dtp']},
                    'Document.sections.session.sections.Session.sections.Task.properties.ShortName.value': "land"
                }
            query_output (dict or str or list of str):  requested projections.  If dict,
            should be projections formatted in TinyDB style.  If string or list of
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

        # Query the database
        collection = self._get_collection()
        cursor = collection.find(query_input, projection=query_output)

        # Put projection values into a dataframe.  For each session, make a dict where
        # the keys are the field names and the vals are their values for that session.
        # Then add the whole dict to the dataframe at once.  Each column needs to have
        # dtype=object in order to be able to store iterables, e.g. lists.
        query_results = pd.DataFrame(
            columns=self.get_field_name(list(query_output.keys())), dtype=object
        )
        try:
            for doc in cursor:
                for proj_path in list(query_output.keys()):
                    # Get the value for each nested set of dict keys which are generated
                    # from the projection path
                    proj_val = doc
                    for ikey in proj_path.split("."):
                        try:
                            proj_val = proj_val[ikey]
                        except:
                            try:
                                proj_val = proj_val[int(ikey)]
                            except:
                                proj_val = None
                    # Insert the value into the correct row and column of the dataframe.
                    #
                    # Note that because some values may be lists, we have to do this
                    # individualy for each cell of the dataframe, rather than append an
                    # entire row at once.  This is because of how .loc and .at work.
                    # Here is an informative StackOverflow answer:
                    # https://stackoverflow.com/a/54447608
                    # and the documentation for .loc:
                    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.loc.html
                    query_results.loc[doc[index_id], self.get_field_name(proj_path)] = (
                        proj_val
                    )

        finally:
            self._get_client().close()
        return query_results

    def delete_single_record(self, document_id):
        """Delete a single record (document) from a collection, if it exists.

        Args:
            document_id (str): _id field for the document to be deleted

        Returns:
            number of documents deleted (1 or 0)

        """
        db = TinyDB(self._location)
        deletion_result = db.remove("_id" == document_id)
        return deletion_result.deleted_count

    def insert_single_record(self, document_to_insert):
        """Insert a single record (document) into a collection.

        Args:
            document_to_insert (json): contents of the document to insert.  If the
            document doesn't have an _id field, one will be added automatically.

        Returns:
            _id property of the inserted document

        """
        db = TinyDB(self._location)
        insertion_result = db.insert(document_to_insert)
        return insertion_result.inserted_id

def set_database(cfg) -> MetadataSource:
    """Create a database object.

    The default is a MongoDB database, for backwards compatability.

    Args:
        cfg (dict):  information about database.  This should contain a key 'type'
        defining the type of database (if not, a MongoDB database will be used); the
        other keys depend on the type of database.

    """
    # Set database information depending on the type of database used.  Use MongoDB
    # as the default database.
    if "type" in cfg:
        if cfg["type"] == "mongodb":
            return MongoDbDatabase(cfg)
        elif cfg["type"] == "tinydb":
            return TinyDbJson(cfg)
        else:
            return MongoDbDatabase(cfg)
    else:
        return MongoDbDatabase(cfg)
