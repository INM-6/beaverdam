from abc import ABC, abstractmethod
from pathlib import Path
import tempfile
import sys
import os
import logging

import odml  # handling odml files; install with pip not conda
import json  # handling JSON files; built in, don't need to install separate package


class MetadataFile(ABC):
    """Generic class to store all types of metadata files and control their manipulation"""

    def __init__(self, file_name: Path):
        """Load the file

        Args:
            file_name (Path): path containing the file path, file name, and extension
        """
        self.file_name = file_name
        self._load_file()

    @abstractmethod
    def _load_file(self):
        """Load the raw data from the file using the given file_name"""

    @abstractmethod
    def to_json(self):  # return json dict
        """Convert the metadata file to json format"""


class JsonMetadata(MetadataFile):
    """Control handling of json files"""

    def __init__(self, file_name):
        super().__init__(file_name)

    def _load_file(self):
        """Load raw data from json file"""
        with open(self.file_name, "r") as f:
            # Since the data is already in json format, we can put it directly in
            # self.json
            self.json = json.load(f)

    def to_json(self):
        # The metadata is already in json format, so just return it
        return self.json


class OdmlMetadata(MetadataFile):
    """Control handling of odML files"""

    def __init__(self, file_name):
        super().__init__(file_name)

    def _load_file(self, suppress_validations=True):
        """Load raw data from odML file

        Args:
            suppress_warnings (bool): if True, won't print validation warnings
            (optional; defaults to True)
        """
        error_suppressor = _ErrorSuppressor(suppress_validations)
        error_suppressor.turn_on()
        self.file_contents = odml.load(self.file_name)
        error_suppressor.turn_off()

    def to_json(self, suppress_validations=True):
        """Convert odML data to json

        Args:
            suppress_warnings (bool): if True, won't print validation warnings
            (optional; defaults to True)

        Returns:
            (json): json-serialized metadata
        """
        error_suppressor = _ErrorSuppressor(suppress_validations)
        # Save a temporary json file
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_file_path = Path(temp_dir_name) / Path(self.file_name.stem + ".json")
            error_suppressor.turn_on()
            odml.save(self.file_contents, str(temp_file_path), "JSON")
            error_suppressor.turn_off()

            # Load JSON output
            with open(temp_file_path, "r") as f:
                self.json = json.load(f)

        # Convert the odML structure to nice names for json
        self._flatten_json_section_lists()
        return self.json

    def _flatten_json_section_lists(self):
        """Convert the default odML-to-json section names into more meaningful names.
        Because odML sections and properties contain lists, converting to json results
        in a lot of useless heirarchical levels named e.g. 01, 02 when the lists get
        expanded.  Replace the list items with logically-named json sections which take
        their name from the "name" property of the "sections" and "properties" elements
        of the odML, and values from the "value" elements of "properties".
        """

        # Define function to flatten section lists
        def change_list(input_section):
            # Go through each item in the list stored in the dict entry having key
            # "sections"
            for x in input_section["sections"]:
                change_list(x)

                # Un-list the properties sections to new dict items with keys = property
                # names
                if "properties" in x:
                    x["__properties"] = {}
                    for item in x["properties"]:
                        new_key = item["name"]
                        x["__properties"].update({new_key: item})

                    # Delete the original properties list
                    del x["properties"]
                    # Rename the key without the underscores
                    x["properties"] = x.pop("__properties")

                # Un-list the sections to new dict items with keys = section names
                new_key = x["name"]
                if "__sections" not in input_section:
                    input_section["__sections"] = {}
                input_section["__sections"].update({new_key: x})

            # Delete the original section list
            del input_section["sections"]
            # Rename the key without the underscores
            if "__sections" in input_section:
                input_section["sections"] = input_section.pop("__sections")
            return input_section

        # Flatten list items in JSON so Mongo will query them more easily
        self.json["Document"] = change_list(self.json["Document"])


class _ErrorSuppressor(ABC):
    """Class to handle supression of errors/warnings.

    odML Validations are checks that run automatically when a document is loaded or
    saved, and print warnings or errors if the document doesn't meet odML
    specifications.  The odML package doesn't include a way to turn these off.  Printing
    validation warnings when loading odML documents to build the database gets really
    annoying and clutters the terminal.  This class turns warnings on and off.

    Description of odML validation:
    https://github.com/G-Node/python-odml/blob/98fa2e658313c299c4d237e3b8e7dc16f6727e60/doc/advanced_features.rst#L19

    Validation errors are reported with the Validation.report() method starting on line
    174:
    https://github.com/G-Node/python-odml/blob/98fa2e658313c299c4d237e3b8e7dc16f6727e60/odml/validation.py#L100

    I used the method of suppressing errors described here:
    https://stackoverflow.com/a/2125776
    I found that odML warnings only required blocking stderr, not stdout.
    """

    def __init__(self, has_effect=True) -> None:
        """Initialize error suppressor

        Args:
            has_effect (bool, optional): whether or not the object can suppress errors.
            Really only used to avoid multiple if/else statements.  Defaults to True.
        """
        super().__init__()
        self.has_effect = has_effect

    def turn_on(self):
        """Suppress warnings and errors"""
        if self.has_effect:
            # sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

    def turn_off(self):
        """Re-allow display of warnings and errors"""
        if self.has_effect:
            # sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


def load_metadata(file_name: Path) -> MetadataFile:
    """Load metadata from any file type

    Args:
        file_name (Path): path to the file, including filename and extension

    Returns:
        MetadataFile: some flavour of a MetadataFile object, depending on the input file
        type.  Returns None if there is a problem with the file or the file doesn't
        exist.
    """
    # Create the correct type of file object depending on the extension.  If there is a
    # problem, report this in the log file.
    try:
        if file_name.suffix == ".odml":
            return OdmlMetadata(file_name)
        elif file_name.suffix == ".json":
            return JsonMetadata(file_name)
        else:
            logging.error(
                """File {0} skipped, because Beaverdam doesn't know how to treat 
                {1} files yet.\n""".format(
                    file_name, file_name.suffix
                )
            )
            return None
    except Exception as e:
        logging.error("Problem with file {0}:\n".format(file_name) + e.args[0])
        return None
