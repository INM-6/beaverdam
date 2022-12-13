"""Parse the provided config file and save the variables in a useful way"""

from tomlkit import (
    parse,
)  # change to tomllib once using Python 3.11
from collections import namedtuple


def parse_config(fp):
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

    return config_values
