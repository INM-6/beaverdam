import sys

sys.path.insert(0, "./src")

from pathlib import Path
import glob
from tqdm import tqdm
import logging

from configparser import ConfigParser
from metadatasource import MongoDbDatabase
from metadatafiletools import load_metadata
from pluralize import pluralize


## INPUTS

# Name of configuration file
cfg_file_name = Path("config.toml")
db_extension = ".json"


## CODE


class BeaverDB:
    """Create or update a database from a directory of metadata files"""

    def __init__(self, fp_cfg):
        """Set up database and detect files to load

        Args:
            fp_cfg (Path): path to config file, including filename and extension
        """
        # Set up logging, with the log file in the same directory as the config file
        self._create_log(fp_cfg.parent)
        # Read config file
        self.cfg = ConfigParser(fp_cfg)
        # Set database
        self._set_database()
        # Get metadata file names
        self._find_files()

    def _create_log(self, directory):
        """Set up error logging

        Args:
            directory (Path): directory to place the log file in
        """
        log_file_name = Path("beaverdam.log")
        logging.basicConfig(
            filename=directory / log_file_name,
            encoding="utf-8",
            filemode="w",
            format="%(levelname)s:%(message)s",
            level=logging.INFO,
        )

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
        # Print entry status
        update_message = "{0} file{1} found in filesystem directory.".format(
            len(self.input_files), pluralize(len(self.input_files))
        )
        print(update_message)
        logging.info(update_message)
        # Store info to print exit status
        n_documents_deleted = 0
        n_new_documents = 0
        n_skipped_files = 0
        # For each file in the list of files, manipulate it if needed then add it to the
        # database
        for input_file in tqdm(self.input_files):
            # Load the file, if possible
            metadata_file = load_metadata(input_file)
            if metadata_file:
                # Get the ID for the file to use in the database
                db_record_id = input_file.stem

                # Convert the file to JSON if it isn't already
                json_file = metadata_file.to_json()
                # Add a meaningful _id tag for MongoDB
                json_file["_id"] = db_record_id

                # Update the database.  Note that some databases (e.g. MongoDB) have a
                # single function which updates a record -or- creates a new record if
                # the original one doesn't exist (in pymongo, this is update_one()).
                # However this doesn't work well when the _id field is included in the
                # new document.
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
                    logging.warning(
                        """The document with _id = {0} was updated, 
                        instead of id = {1}.""".format(
                            updated_document_id, db_record_id
                        )
                    )
            else:
                logging.error("File {0} skipped due to file problems.".format(input_file))
                n_skipped_files += 1

        # Report what happened
        update_message = (
            "Database updated!"
            + "\n{0} existing document{1} modified.".format(
                n_documents_deleted, pluralize(n_documents_deleted)
            )
            + "\n{0} new document{1} added.".format(
                n_new_documents, pluralize(n_new_documents)
            )
            + """\n{0} document{1} skipped due to file problems -- see beaverdam.log for details.""".format(
                n_skipped_files, pluralize(n_skipped_files)
            )
        )
        print(update_message)
        logging.info(update_message)


def build_database():
    user_database = BeaverDB(cfg_file_name)
    user_database.update_database()


build_database()
