"""Main functionality to build and update a database."""

import logging
import os
from pathlib import Path

from tqdm import tqdm

from beaverdam._core import ConfigParser
from beaverdam._core.metadatasource import create_database
from beaverdam.builder.metadatafiletools import load_metadata
from beaverdam.builder.pluralize import pluralize


class BeaverDB:
    """Create or update a database from a directory of metadata files."""

    def __init__(self, fp_cfg):
        """Set up database and detect files to load.

        Args:
            fp_cfg (Path): path to config file, including filename and extension

        """
        # Set up logging, with the log file in the same directory as the config file
        self._create_log(fp_cfg.parent)
        # Read config file
        self.cfg = ConfigParser(fp_cfg)
        # Set database
        self.db = create_database(self.cfg.get_section("database"))
        # Get metadata file names
        self._find_files()

    def _create_log(self, directory):
        """Set up error logging.

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

    def _find_files(self):
        """Detect metadata files to include in the database."""
        # Get information from config file
        input_file_info = self.cfg.get_section("raw_metadata")
        # Recursively search parent directory and store the locations of files having
        # the requested extension.  I used os.walk() because it's backwards-compatible -
        # on Python 3.12 and higher, you could use Path.walk().
        self.input_files = []
        for dirpath, _dirnames, filenames in os.walk(input_file_info["directory"]):
            filepaths = [
                Path(dirpath, x)
                for x in filenames
                if x.endswith(input_file_info["file_type"])
            ]
            self.input_files.extend(filepaths)

    def update_database(self):
        """Add or update database information from each metadata file."""
        # Print entry status
        update_message = "{0} file{1} found in filesystem directory.".format(
            len(self.input_files), pluralize(len(self.input_files))
        )
        print(update_message)
        logging.info(update_message)
        # Store info to print exit status
        n_records_modified = 0
        n_new_records = 0
        n_skipped_files = 0

        def update_record(db_record_id, json_contents):
            # Update a single record in the database.  Note that some databases (e.g.
            # MongoDB) have a single function which updates a record -or- creates a new
            # record if the original one doesn't exist (in pymongo, this is
            # update_one()).  However this doesn't work well when the _id field is
            # included in the new document.
            #
            # Delete existing record from database if present
            is_record_deleted = self.db.delete_single_record(db_record_id)
            # Insert the new record
            self.db.insert_single_record(json_contents)

            # Return what happened
            if is_record_deleted:
                return "record_modified"
            else:
                return "record_added"

        # For each file in the list of files, manipulate it if needed then add it to the
        # database
        for input_file in tqdm(self.input_files):
            # Load the file, if possible
            metadata_file = load_metadata(input_file)
            if metadata_file:
                # Get the name of the file
                file_name = input_file.stem

                # Convert the file to JSON if it isn't already
                json_file = metadata_file.to_json()
                # For a regular JSON, add it as a record to the database.  For a JSON
                # array, assign each element an ID corresponding to its location in the
                # array then add the element as a record to the database.
                if isinstance(json_file, list):
                    # Find the total number of records.
                    # A better solution, if `math` is imported, is
                    # math.log10(len(json_file))
                    n_digits_max = len(str(len(json_file)))
                    for idx, json_array_item in enumerate(json_file):
                        # Assign a meaningful _id tag
                        db_record_id = (
                            file_name + "_" + str(idx + 1).zfill(n_digits_max)
                        )
                        json_array_item["_id"] = db_record_id
                        # Update the record
                        update_result = update_record(db_record_id, json_array_item)
                        # Store what happened
                        if update_result == "record_modified":
                            n_records_modified += 1
                        elif update_result == "record_added":
                            n_new_records += 1
                else:
                    # Add a meaningful _id tag to represent the record in the database, if
                    # it doesn't already exist
                    if "_id" not in json_file:
                        db_record_id = file_name
                        json_file["_id"] = db_record_id
                    else:
                        db_record_id = json_file["_id"]
                    # Update the record
                    update_result = update_record(db_record_id, json_file)
                    # Store what happened
                    if update_result == "record_modified":
                        n_records_modified += 1
                    elif update_result == "record_added":
                        n_new_records += 1
                    else:
                        pass
            else:
                logging.error(
                    "File {0} skipped due to file problems.".format(input_file)
                )
                n_skipped_files += 1

        # Report what happened
        update_message = (
            "Database updated!"
            + "\n{0} existing record{1} modified.".format(
                n_records_modified, pluralize(n_records_modified)
            )
            + "\n{0} new record{1} added.".format(
                n_new_records, pluralize(n_new_records)
            )
            + """\n{0} record{1} skipped due to file problems -- see beaverdam.log for details.""".format(
                n_skipped_files, pluralize(n_skipped_files)
            )
        )
        print(update_message)
        logging.info(update_message)


def build_database(cfg_file_name):
    """Create or update a database.

    Args:
        cfg_file_name (str): relative path and name of configuration file

    """
    cfg_file_name = Path(cfg_file_name)
    user_database = BeaverDB(cfg_file_name)
    user_database.update_database()


if __name__ == "__main__":
    # Edit the name and RELATIVE (to this file) location of the config file
    # appropriately.
    #
    # An alternative approach is to define cfg_file_name in the configurations section
    # of launch.json if you are using VSCode, e.g.:
    #    env: {"cfg_file_name": "config_countries.toml"}
    # Then access this variable here using e.g.:
    #    import os
    #    cfg_file_name = os.environ.get("cfg_file_name")
    cfg_file_name = Path(__file__).parents[3] / "config_countries.toml"
    # Build the database
    build_database(cfg_file_name)
