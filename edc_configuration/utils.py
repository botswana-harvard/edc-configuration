from dateutil import parser
from decimal import Decimal, InvalidOperation


def string_to_datatype(string_value):
    """Converts a string representation of a value into its original datatype."""
    string_value = string_value.strip(' "')
    # try to return as boolean or none
    retval = string_value
    if string_value.lower() in ['true', 'false', 'none']:
        retval = eval(string_value)
        return retval
    # try to return as a decimal
    try:
        value = Decimal(string_value)
        if str(value) == string_value:
            retval = value
    except ValueError:
        pass
    except InvalidOperation:
        pass
    # try to return as an integer
    try:
        value = int(string_value)
        if str(value) == string_value:
            retval = value
    except ValueError:
        pass
    # try to return as date
    try:
        value = parser.parse(string_value)
        if value.strftime('%Y-%m-%d') == string_value:
            retval = value.date()
    except ValueError:
        pass
    except TypeError:
        pass
    # try to return as datetime
    try:
        value = parser.parse(string_value)
        if value.strftime('%Y-%m-%d %H:%M') == string_value:
            retval = value
    except ValueError:
        pass
    except TypeError:
        pass
    # otherwise return string value
    return retval
