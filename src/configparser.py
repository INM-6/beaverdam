"""Parse the provided config file and save the variables in a useful way"""

from pathlib import Path
import tomli  # import tomllib in Python 3.11


class ConfigParser:
    """Parse configuration file and store parameters"""

    def __init__(self, fp, sections_to_extract="all"):
        """Parse configuration file

        Args:
            fp (str or Path): path to config file
            sections_to_extract (string or list of strings):  [optional] which sections
            to get out of file.  Default is all sections.
        Returns:
            self.contents (dict):  dict with keys obtained from the headings of the
            config file, and vals containing contains dicts of keys/vals obtained from
            the section of the config file under each heading (see example)

        Example:

            TOML file -- the file pointed to by fp
                [heading]
                key1 = val1
                key2 = val2
            self.contents -- output of ConfigParser(fp) -or- ConfigParser(fp, "heading")
                self.contents['heading']
                    {'key1': val1, 'key2': val2}
                self.contents['heading']['key1']
                    val1
        """

        # Parse the config file
        if isinstance(fp, str):
            fp = Path(fp)
        try:
            with open(fp, "rb") as f:
                config_contents = tomli.load(f)
        except:
            raise Exception("File " + str(fp.name) + " cannot be read.")

        # If no requested sections are provided, get all the sections in the config file
        if sections_to_extract == "all":
            sections_to_extract = list(config_contents.keys())
        # If only one requested section is present, and it's not already in a list, put
        # it into a list
        if isinstance(sections_to_extract, str):
            sections_to_extract = [sections_to_extract]

        # Check if the requested section(s) are present
        self._check_for_missing_sections(config_contents, sections_to_extract)

        # Extract desired section(s)
        self.contents = {}
        for key in sections_to_extract:
            self.contents[key] = config_contents[key]

    def get_section(self, section_name):
        """Return the contents of one or more sections of the config file

        Args:
            section_name (string | list of strings):  names of the section(s) to
            extract

        Returns:
            section_contents (? | dict):  contents of the requested
            section(s) as:
                - ? -- if one section is requested, and that section contains a single
                  value -- the value will be returned (whatever it is)
                - dict -- if multiple sections are requested
        """

        # Check that requested section(s) exist
        self._check_for_missing_sections(self.contents, section_name)

        section_contents = None
        # If one section is requested, return its contents
        if isinstance(section_name, str):
            section_contents = self.contents[section_name]
        else:
            section_contents = {iname: self.contents[iname] for iname in section_name}

        return section_contents

    def _check_for_missing_sections(self, dict_to_check, requested_sections):
        """Check a dictionary to make sure all requested sections are present

        Args:
            dict_to_check (dict): dictionary whose sections you want to check the
            existance of
            requested_sections (str | list of str): sections you want to make sure are
            contained in dict_to_check

        Returns:
            Exception if a requested section is not present as a key in dict_to_check
        """

        # Make sure that requested sections are a list
        requested_sections = (
            [requested_sections]
            if isinstance(requested_sections, str)
            else requested_sections
        )

        is_section_missing = [
            item not in list(dict_to_check.keys()) for item in requested_sections
        ]
        if any(is_section_missing):
            missing_sections = [
                x for (x, y) in zip(requested_sections, is_section_missing) if y
            ]
            raise Exception(
                "Config file is missing requested section(s): "
                + ", ".join(missing_sections)
            )
