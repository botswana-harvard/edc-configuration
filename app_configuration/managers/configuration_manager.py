from django.db import models

from edc.utils import string_to_datatype


class ConfigurationManager(models.Manager):

    def get_attr_value(self, attribute_name):
        """Returns the attribute value in its original datatype assuming it can be converted."""
        try:
            obj = self.get(attribute=attribute_name)
            string_value = obj.value.strip(' "')
            return string_to_datatype(string_value) if obj.convert else string_value
        except self.model.DoesNotExist:
            return ''
