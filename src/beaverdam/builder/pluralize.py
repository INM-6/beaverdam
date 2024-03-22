def pluralize(number):
    """Decide whether or not to pluralize a string describing a nunber of items.

    Args:
        number (float or int): number of items you are describing

    Returns:
        plural (string):  's' if the string should be plural; '' if it shouldn't.
    """
    # Also see the solution here:  https://stackoverflow.com/a/65063284
    # which uses 's'[:i^1] or 's'[:i!=1]
    if 0 < number <= 1:
        return ""
    else:
        return "s"
