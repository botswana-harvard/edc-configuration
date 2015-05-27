import ast

from dateutil import parser

from django.db import models


class ConfigurationManager(models.Manager):

    def get_attr_value(self, attribute_name):
        """Returns the attribute value in its original datatype assuming it can be converted."""
        string_value = self.get(attribute=attribute_name).value.strip(' "')
        try:
            return parser.parse(string_value)
        except ValueError:
            try:
                return ast.literal_eval(string_value)
            except (ValueError, SyntaxError):
                pass
        return string_value
