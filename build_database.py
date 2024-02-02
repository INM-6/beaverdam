import sys

sys.path.insert(0, "./src")

from pathlib import Path
from configparser import ConfigParser
import glob
from tqdm import tqdm
from metadatasource import MongoDbDatabase
from metadatafiletools import load_metadata


## INPUTS

# Name of configuration file
cfg_file_name = "config.toml"
db_extension = ".json"


## CODE


class BeaverDB:
    """Create or update a database from a directory of metadata files"""

    def __init__(self, fp_cfg):
        """Set up database and detect files to load

        Args:
            fp_cfg (str): path to config file, including filename and extension
        """
        # Read config file
        self.cfg = ConfigParser(fp_cfg)
        # Set database
        self._set_database()
        # Get metadata file names
        self._find_files()

    def _set_database(self):
        """Create a database object"""
        # Set database information
        self.db = MongoDbDatabase(self.cfg.get_section("database"))

    def _find_files(self):
        """Detect metadata files to include in the database"""
        # Find metadata files
        input_file_info = self.cfg.get_section("raw_metadata")
        # Store file names
        input_file_directory = Path(input_file_info["directory"])
        self.input_files = list(
            input_file_directory.glob("*" + input_file_info["file_type"])
        )

    def update_database(self):
        """Add or update database information from each metadata file"""
        # Store info to print exit status
        n_documents_deleted = 0
        n_new_documents = 0
        # For each file in the list of files, manipulate it if needed then add it to the
        # database
        for input_file in tqdm(self.input_files):
            # Load the file
            metadata_file = load_metadata(input_file)
            # Get the ID for the file to use in the database
            db_record_id = input_file.stem

            # Convert the file to JSON if it isn't already
            json_file = metadata_file.to_json()
            # Add a meaningful _id tag for MongoDB
            json_file["_id"] = db_record_id

            # Update the database.  Note that some databases (e.g. MongoDB) have a
            # single function which updates a record -or- creates a new record if the
            # original one doesn't exist (in pymongo, this is update_one()).  However
            # this doesn't work well when the _id field is included in the new document.
            #
            # Delete existing document from database if present
            is_document_deleted = self.db.delete_single_record(db_record_id)
            # Insert the new document
            updated_document_id = self.db.insert_single_record(json_file)
            # Record what happened
            if is_document_deleted:
                n_documents_deleted += 1
            else:
                n_new_documents += 1

            # Check that the updated document has the same _id as you intended
            if updated_document_id != db_record_id:
                raise Exception(
                    "Oh no, something went wrong!  The document with _id = {0} was updated, instead of id = {1}.".format(
                        updated_document_id, db_record_id
                    )
                )

        # Report what happened
        print(
            "Database updated!  {0} existing documents modified, {1} new documents added.".format(
                n_documents_deleted, n_new_documents
            )
        )


def build_database():
    user_database = BeaverDB(cfg_file_name)
    user_database.update_database()


build_database()
