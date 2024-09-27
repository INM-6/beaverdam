"""Create an object for a source of metadata, and define how to access its information."""

from abc import ABC, abstractmethod

import pandas as pd
from pymongo import MongoClient
from tinydb import Query, TinyDB


class MetadataSource(ABC):
    """Store information about where to get metadata."""

    @abstractmethod
    def __init__(self):
        pass

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
        # Make a pointer to the database
        self._collection = getattr(
            getattr(MongoClient(self._address, self._port), self._db_name),
            self._collection_name,
        )

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
        cursor = self._collection.find(query_input, projection=query_output)

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
            pass
        return query_results

    def delete_single_record(self, document_id):
        """Delete a single record (document) from a collection, if it exists.

        Args:
            document_id (str): _id field for the document to be deleted

        Returns:
            (int) number of documents deleted (1 or 0)

        """
        deletion_result = self._collection.delete_one({"_id": document_id})
        return deletion_result.deleted_count

    def insert_single_record(self, document_to_insert):
        """Insert a single record (document) into a collection.

        Args:
            document_to_insert (json or bson): contents of the document to insert.  If
            the document doesn't have an _id field, one will be added automatically.

        Returns:
            (str) _id property of the inserted document

        """
        insertion_result = self._collection.insert_one(document_to_insert)
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
        # Make a pointer to the database
        self._db = TinyDB(self._location)
        # TindyDB uses integers for document IDs, but Beaverdam uses strings.  The
        # simplest way to solve this is to keep the _id field expected by Beaverdam, and
        # query it for the value associated with the numeric TinyDB id -- set up a
        # lookup table for this as a dict with key=_id (string), val=id (int set by
        # TinyDB).
        self._record_ids = {}
        record_id_field_name = "_id"
        query_results = self._db.search(Query()[record_id_field_name].exists())
        for doc in query_results:
            self._record_ids[doc[record_id_field_name]] = doc.doc_id

    def query(self, query_input={}, query_output=[]):
        """Query a TinyDB json database.

        Args:
            query_input (dict or list of str):  requested queries.  If dict, should be a
            query formatted in TinyDB style (but this functionality isn't implemented
            yet).  Default is all fields.
                TODO:  implement TinyDB queries.  Ref:
                https://tinydb.readthedocs.io/en/latest/usage.html#queries
            query_output (str or list of str):  requested output fields.  Strings should
            correspond to the field names in self.fields.  Default is all fields.
                query_output = ["path.to.output.value"]

        Returns:
            query_results (dataframe): rows=documents and cols=projections

        """
        # TODO:  if the query inputs isn't a dict, convert it
        if not isinstance(query_input, dict):
            raise Exception("This function isn't defined yet.")

        # Use the document ID as the index in the output dataframe
        record_id_field_name = "_id"

        # Query the database
        query_results = self._db.search(Query()[record_id_field_name].exists())
        # Unlike MongoDB, TinyDB can only return the entire document, not a subset of
        # fields
        # https://stackoverflow.com/a/61548225
        # Extract the desired fields and put them into a dataframe.  For each document,
        # make a dict where the keys are the field names and the vals are their values.
        # Then add the whole dict to the dataframe at once.  Each column needs to have
        # dtype=object in order to be able to store iterables, e.g. lists.
        query_results_df = pd.DataFrame(columns=query_output, dtype=object)
        proj_paths = self.get_path(requested_field_names=query_output)
        # Make sure the document ID will be included in the output fields
        # proj_paths.insert(0, index_id)
        try:
            for doc in query_results:
                for proj_path in proj_paths:
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
                    query_results_df.loc[
                        doc[record_id_field_name], self.get_field_name(proj_path)
                    ] = proj_val
        finally:
            del query_results
        return query_results_df

    def delete_single_record(self, document_id):
        """Delete a single record (document) from a collection, if it exists.

        Args:
            document_id (str): _id field for the document to be deleted

        Returns:
            number of documents deleted (1 or 0)

        """
        # The document ID will only be a key in the lookup table of record IDs if the
        # record was already added.
        if document_id in self._record_ids:
            # Convert the provided document ID to the ID used by TinyDB
            tinydb_id = self._record_ids[document_id]
            if self._db.contains(doc_id=tinydb_id):
                deletion_result = self._db.remove(doc_ids=[tinydb_id])
            else:
                deletion_result = []
        else:
            deletion_result = []
        return len(deletion_result)

    def insert_single_record(self, document_to_insert):
        """Insert a single record (document) into a collection.

        Args:
            document_to_insert (json): contents of the document to insert.  If the
            document doesn't have an _id field, one will be added automatically.

        Returns:
            _id property of the inserted document

        """
        # Insert document into database
        insertion_result = self._db.insert(document_to_insert)
        # Store the TinyDB ID of the inserted document in the lookup table along with
        # the _id field of the original document.  If the document didn't have an _id
        # field, make this a string equal to the TinyDB ID.
        if "_id" in document_to_insert:
            self._record_ids[document_to_insert["_id"]] = insertion_result
        else:
            self._record_ids[str(insertion_result)] = insertion_result
        return insertion_result


def create_database(cfg) -> MetadataSource:
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
