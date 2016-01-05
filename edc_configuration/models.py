from django.core.validators import RegexValidator
from django.db import models

from edc_base.model.models import BaseUuidModel

from .convert import Convert


class ConfigurationManager(models.Manager):

    def get_attr_value(self, attribute_name):
        """Returns the attribute value in its original datatype assuming it can be converted."""
        try:
            obj = self.get(attribute=attribute_name)
            return Convert(obj.value, convert=obj.convert).to_value()
        except self.model.DoesNotExist:
            return ''


class GlobalConfiguration(BaseUuidModel):
    """A model to store any configurations values for reference in the edc and other models.

    The manager method :func:`get_attr_value` will convert the stored string value to it's
    original datatype unless told not to (convert=False).

    Usage::
        GlobalConfiguration.objects.create(category=category_name,
            attribute=attribute_name, value=string_value)
        value = GlobalConfiguration.objects.get_attr_value(attribute_name)

    ..seealso:: func:`base_app_configuration.update_global`

    """
    category = models.CharField(max_length=50)

    attribute = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator('[a-z0-9_]',
                                   'Invalid attribute name, must be lower case separated by underscore.'), ])
    value = models.CharField(
        max_length=50,
        help_text='any string value or string representation of a value')

    convert = models.BooleanField(
        default=True,
        help_text=('If True, automatically convert string value to its datatype. '
                   'Type is autodetected in this order: Boolean, None, Decimal, Integer, '
                   'Date, Datetime otherwise String'))

    comment = models.CharField(max_length=100)

    objects = ConfigurationManager()

    class Meta:
        app_label = 'edc_configuration'
