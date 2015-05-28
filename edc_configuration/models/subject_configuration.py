from django.apps import apps
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from edc_base.model.models import BaseUuidModel
from edc_appointment.choices import APPT_STATUS, APPT_TYPE
from edc_appointment.constants import NEW
try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})


class SubjectConfiguration(SyncMixin, BaseUuidModel):
    """Store subject specific defaults."""

    subject_identifier = models.CharField(
        max_length=36)

    default_appt_type = models.CharField(
        max_length=10,
        default='clinic',
        choices=APPT_TYPE,
        help_text=''
    )

    def __unicode__(self):
        return self.subject_identifier

    def natural_key(self):
        return (self.subject_identifier, )

    def save(self, *args, **kwargs):
        self.update_new_appointments()
        super(SubjectConfiguration, self).save(*args, **kwargs)

    def update_new_appointments(self):
        Appointment = apps.get_model('appointment', 'Appointment')

        """Updates \'NEW\' appointments for this subject_identifier to reflect this appt_status."""
        if NEW not in [x[0] for x in APPT_STATUS]:
            raise ImproperlyConfigured(
                'SubjectConfiguration save() expects APPT_STATUS choices tuple '
                'to have a \'{0}\' option. Not found. Got {1}'.format(NEW, APPT_STATUS))
        for appointment in Appointment.objects.filter(
                registered_subject__subject_identifier=self.subject_identifier, appt_status__iexact=NEW):
            appointment.appt_type = self.default_appt_type
            appointment.raw_save()

    class Meta:
        app_label = 'subject_config'
        db_table = 'bhp_subject_config_subjectconfiguration'
