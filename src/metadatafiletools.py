from abc import ABC, abstractmethod
from pathlib import Path
import tempfile

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

    def _load_file(self):
        """Load raw data from odML file"""
        self.file_contents = odml.load(self.file_name)

    def to_json(self):
        """Convert odML data to json

        Returns:
            (json): json-serialized metadata
        """
        try:
            # See if you can get the session name from the odML contents.  This might
            # only work for odMLs from the Vision4Action project, but we start with it
            # here because right now that's the main use case
            json_file_name_stem = self.get_session_name()
        except:
            # If the file doesn't have a session name, just use the original filename
            # for the json
            json_file_name_stem = self.file_name.stem

        # Save a temporary json file
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_file_path = Path(temp_dir_name) / Path(json_file_name_stem + ".json")
            odml.save(self.file_contents, str(temp_file_path), "JSON")

            # Load JSON output
            with open(temp_file_path, "r") as f:
                self.json = json.load(f)

        # Convert the odML structure to nice names for json
        self._flatten_json_section_lists()
        return self.json

    def get_session_name(self):
        """Get session name from Vision4Action odML data"""
        # Find session name in odML
        session_name = (
            self.file_contents["session"]["Session"].properties["Name"].values
        )
        if isinstance(session_name, list):
            if len(session_name) > 1:
                raise ValueError("Ambiguous session names found in odML file.")
            session_name = session_name[0]
        elif isinstance(session_name, str):
            # If session_name is already a single string, do nothing
            pass
        else:
            raise ValueError("Unknown session name in odML file.")
        return session_name

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

                # Un-list the properties sections to new dict items with keys = property names
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


def load_metadata(file_name: Path) -> MetadataFile:
    """Load metadata from any file type

    Args:
        file_name (Path): path to the file, including filename and extension

    Raises:
        Exception: if the file type isn't found

    Returns:
        MetadataFile: some flavour of a MetadataFile object, depending on the input file
        type
    """
    # Create the correct type of file object depending on the extension
    if file_name.suffix == ".odml":
        return OdmlMetadata(file_name)
    elif file_name.suffix == ".json":
        return JsonMetadata(file_name)
    else:
        raise Exception(
            "Beaverdam doesn't know how to treat " + file_name.suffix + " files yet."
        )
