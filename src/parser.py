"""Parse the provided config file and save the variables in a useful way"""
# NOTE:  check out YACS:  https://github.com/rbgirshick/yacs

from tomlkit import (
    parse,
)  # change to tomllib once using Python 3.11
from collections import namedtuple


def parse_config(fp, sections_to_extract="all"):
    """Parse configuration file

    Args:
        fp (str): path to config file
        sections_to_extract (string or list of strings):  [optional] which sections to
        get out of file.  If not provided, defaults to all sections
    Returns:
        config_values (namedtuple):  contains dicts for each heading of config file (see
        example)

    Example:

        TOML file -- input to parse_config()
            [heading]
            key1 = val1
            key2 = val2
        config_values -- output of parse_config(fp) -or- parse_config(fp, "heading")
            config_values.heading
                {'key1': val1, 'key2': val2}
            config_values.heading["key1"]
                val1
            config_values.heading["key2"]
                val2
    """

    # Parse the config file
    try:
        with open(fp, "rb") as f:
            config_contents = parse(f.read())
    except:
        raise Exception("File " + fp + " cannot be read.")

    # If no requested sections are provided, get all the sections in the config file
    if sections_to_extract == "all":
        sections_to_extract = list(config_contents.keys())
    # If only one requested section is present, and it's not already in a list, put it
    # into a list
    if isinstance(sections_to_extract, str):
        sections_to_extract = [sections_to_extract]
    # Check if the requested section is present
    is_section_missing = [
        item not in list(config_contents.keys()) for item in sections_to_extract
    ]
    if any(is_section_missing):
        missing_sections = [
            sections_to_extract[i]
            for i, val in enumerate(is_section_missing)
            if is_section_missing[i]
        ]
        raise Exception(
            "Config file is missing requested section(s): "
            + ", ".join(missing_sections)
        )

    # Make sure items in each field will be a dict
    list_of_dicts = []
    for isection in sections_to_extract:
        list_of_dicts.append(dict(config_contents[isection]))

    # Put each of the top-level dict entries into its own variable
    convert_config = namedtuple("convert_config", sections_to_extract)
    config_values = convert_config._make(list_of_dicts)

    return config_values
