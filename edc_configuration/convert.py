import pytz
import re

from dateutil import parser
from decimal import Decimal, InvalidOperation

from django.utils.encoding import force_text
from django.utils import timezone
from django.test.utils import override_settings


class ConvertError(Exception):
    pass


def localize(datetime_obj):
    try:
        default_timezone = timezone.get_default_timezone_name()
        aware_datetime = pytz.timezone(default_timezone).localize(datetime_obj)
    except ValueError as e:
        if 'Not naive datetime' not in str(e):
            raise ValueError(e)
        aware_datetime = datetime_obj
    return aware_datetime


class Convert(object):

    def __init__(self, value, convert=None, time_format=None):
        self.value = value
        self.convert = False if convert is False else True
        self.time_format = time_format or '%H:%M'

    def to_value(self):
        """Converts a string representation of a value into its original datatype.

        For dates and datetimes always returns a time zone aware datetime."""
        string_value = self.value.strip(' "')
        if self.convert:
            try:
                return self.to_time(string_value)
            except ConvertError:
                pass
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
                return self.to_datetime(string_value)
            except ConvertError:
                pass
            # raise ConvertError('Cannot convert string to value. Got \'{}\''.format(self.value))
        return string_value

    def to_string(self):
        try:
            string_value = self.value.isoformat()
            try:
                self.value.time()
                string_value = '{} {}'.format(string_value, self.value.strftime(self.time_format))
            except AttributeError:
                pass
        except AttributeError:
            string_value = str(self.value)
        return string_value or force_text(self.value)

    def to_time(self, string_value):
        if re.match('^[0-9]{1,2}\:[0-9]{2}$', string_value):
            return string_value
        else:
            raise ConvertError()

    def to_boolean(self, string_value):
        if string_value.lower() in ['true', 'false', 'none']:
            return eval(string_value)
        else:
            raise ConvertError()

    def to_decimal(self, string_value):
        if '.' in string_value:
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

    @override_settings(USE_TZ=True)
    def to_datetime(self, string_value):
        """Returns a timezone aware date.

        If you want a naive date, then you will need to convert it to naive yourself."""
        try:
            value = parser.parse(string_value)
            value = localize(value)
            return value
        except ValueError:
            pass
        except TypeError:
            pass
        raise ConvertError()
