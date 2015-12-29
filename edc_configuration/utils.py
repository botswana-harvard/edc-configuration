from dateutil import parser
from decimal import Decimal, InvalidOperation

from django.utils.encoding import force_text


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


def datatype_to_string(value):
    """Converts a value of Boolean, Decimal, Integer, Date or datetime or other into a string."""
    string_value = None
    if value is True:  # store booleans, None as a text string
        string_value = 'True'
    if value is False:
        string_value = 'False'
    if value is None:
        string_value = 'None'
    else:
        try:
            string_value = value.strftime('%Y-%m-%d')
            if not parser.parse(string_value) == value:
                raise ValueError
        except ValueError:
            pass
        except AttributeError:
            pass
        try:
            string_value = value.strftime('%Y-%m-%d %H:%M')
            if not parser.parse(string_value) == value:
                raise ValueError
        except ValueError:
            pass
        except AttributeError:
            pass
    return string_value or force_text(value)
