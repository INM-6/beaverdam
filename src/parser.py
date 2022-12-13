"""Parse the provided config file and save the variables in a useful way"""
# NOTE:  check out YACS:  https://github.com/rbgirshick/yacs

from tomlkit import (
    parse,
)  # change to tomllib once using Python 3.11
from collections import namedtuple


def parse_config(fp, required_fields=[]):
    """Parse configuration file

    Args:
        fp (str): path to config file
    Returns:
        config_values (namedtuple):  contains dicts for each heading of config file (see example)

    Example:

        TOML file (input to parse_config()):
            [heading]
            key1 = val1
            key2 = val2
        config_values (output of parse_config()):
            config_values.heading
                {'key1': val1, 'key2': val2}
            config_values.heading["key1"]
                val1
            config_values.heading["key2"]
                val2
    """

    # Parse the config file
    with open(fp, "rb") as f:
        config_contents = parse(f.read())

    # Put each of the top-level dict entries into its own variable
    convert_config = namedtuple("convert_config", list(config_contents.keys()))
    config_values = convert_config(**config_contents)

    # Check for required fields
    is_section_missing = [item not in config_values._fields for item in required_fields]
    if any(is_section_missing):
        missing_sections = [
            required_fields[i] for i, val in enumerate(is_section_missing) if is_section_missing[i]
        ]
        raise Exception("Config file is missing section(s): " + ", ".join(missing_sections))

    return config_values
