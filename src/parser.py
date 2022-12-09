# Parse the provided config file and save the variables in a useful way

from tomlkit import (
    parse,
)  # change to tomllib once using Python 3.11
from collections import namedtuple


def parse_config(fp):
    """Parse configuration file

    Args:
        fp (str): path to config file
    """

    # Parse the config file
    with open(fp, "rb") as f:
        config_contents = parse(f.read())

    # Put each of the top-level dict entries into its own variable
    convert_config = namedtuple("convert_config", list(config_contents.keys()))
    config_values = convert_config(**config_contents)

    return config_values
