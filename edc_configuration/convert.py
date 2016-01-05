from dateutil import parser
from decimal import Decimal, InvalidOperation

from django.utils.encoding import force_text


class ConvertError(Exception):
    pass


class Convert(object):

    def __init__(self, value, date_format=None, datetime_format=None, time_format=None):
        self.value = value
        self.date_format = date_format or '%Y-%m-%d'
        self.datetime_format = datetime_format or '%Y-%m-%d %H:%M'
        self.time_format = time_format or '%H:%M'

    def to_string(self):
        try:
            string_value = self.value.strftime(self.date_format)
            try:
                self.value.time()
                string_value = '{} {}'.format(string_value, self.value.strftime(self.time_format))
            except AttributeError:
                pass
        except AttributeError:
            string_value = str(self.value)
        return string_value or force_text(self.value)

    def to_boolean(self, string_value):
        if string_value.lower() in ['true', 'false', 'none']:
            return eval(string_value)
        else:
            raise ConvertError()

    def to_decimal(self, string_value):
        try:
            value = Decimal(string_value)
            if str(value) == string_value:
                return value
        except ValueError:
            pass
        except InvalidOperation:
            pass
        raise ConvertError()

    def to_int(self, string_value):
        try:
            value = int(string_value)
            if str(value) == string_value:
                return value
        except ValueError:
            pass
        raise ConvertError()

    def to_date(self, string_value):
        try:
            value = parser.parse(string_value)
            if value.strftime(self.date_format) == string_value:
                return value.date()
        except ValueError:
            pass
        except TypeError:
            pass
        raise ConvertError()

    def to_datetime(self, string_value):
        try:
            value = parser.parse(string_value)
            if value.strftime(self.datetime_format) == string_value:
                return value
        except ValueError:
            pass
        except TypeError:
            pass
        raise ConvertError()

    def to_value(self):
        """Converts a string representation of a value into its original datatype."""
        string_value = self.value.strip(' "')
        try:
            return self.to_boolean(string_value)
        except ConvertError:
            pass
        try:
            return self.to_decimal(string_value)
        except ConvertError:
            pass
        try:
            return self.to_int(string_value)
        except ConvertError:
            pass
        try:
            return self.to_date(string_value)
        except ConvertError:
            pass
        try:
            return self.to_datetime(string_value)
        except ConvertError:
            pass
        return string_value
