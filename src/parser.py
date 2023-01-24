"""Parse the provided config file and save the variables in a useful way"""

import tomli  # import tomllib in Python 3.11


def parse_config(fp, sections_to_extract="all"):
    """Parse configuration file

    Args:
        fp (str): path to config file
        sections_to_extract (string or list of strings):  [optional] which sections to
        get out of file.  Default is all sections.
    Returns:
        config_values (dict):  dict with keys obtained from the headings of the config
        file, and vals containing contains dicts of keys/vals obtained from the section
        of the config file under each heading (see example)

    Example:

        TOML file -- input to parse_config()
            [heading]
            key1 = val1
            key2 = val2
        config_values -- output of parse_config(fp) -or- parse_config(fp, "heading")
            config_values['heading']
                {'key1': val1, 'key2': val2}
            config_values['heading']['key1']
                val1
    """

    # Parse the config file
    try:
        with open(fp, "rb") as f:
            config_contents = tomli.load(f)
    except:
        raise Exception("File " + fp + " cannot be read.")

    # If no requested sections are provided, get all the sections in the config file
    if sections_to_extract == "all":
        sections_to_extract = list(config_contents.keys())
    # If only one requested section is present, and it's not already in a list, put it
    # into a list
    if isinstance(sections_to_extract, str):
        sections_to_extract = [sections_to_extract]
    # Check if the requested section(s) are present
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
    # Extract desired section(s)
    cfg = {}
    for key in sections_to_extract:
        cfg[key] = config_contents[key]

    return cfg
