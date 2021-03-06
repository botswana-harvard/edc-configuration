from copy import deepcopy

from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings

from edc_appointment.models import Holiday
from edc_consent.consent_type import ConsentType
from edc_content_type_map.models import ContentTypeMapHelper
from edc_export.helpers import ExportHelper
from edc_lab.lab_clinic_api.models import AliquotType, Panel
from edc_lab.lab_packing.models import Destination
from edc_lab.lab_profile.classes import site_lab_profiles
from edc_meta_data.models import RequisitionPanel
from edc_notification.models import NotificationHelper

from lis.labeling.models import LabelPrinter, ZplTemplate, Client

from .convert import Convert, localize
from .defaults import default_global_configuration
from .exceptions import AppConfigurationError
from .models import GlobalConfiguration

# from django.utils.timezone import make_aware


class BaseAppConfiguration(object):

    aliquot_type_model = None
    appointment_configuration = None
    consent_type_setup = None
    export_plan_setup = {}
    global_configuration = {}
    holidays_setup = {}
    lab_clinic_api_setup = None
    lab_setup = None
    labeling_setup = {}
    notification_plan_setup = {}
    panel_model = None
    profile_item_model = None
    profile_model = None

    def __init__(self, lab_profiles=None, use_site_lab_profiles=None):
        self.confirm_site_code_in_settings = True
        self.confirm_community_in_settings = True
        if True if use_site_lab_profiles is None else use_site_lab_profiles:
            lab_profiles = site_lab_profiles
        try:
            self.aliquot_type_model = lab_profiles.group_models.get('aliquot_type')
            self.profile_model = lab_profiles.group_models.get('profile')
            self.profile_item_model = lab_profiles.group_models.get('profile_item')
            self.panel_model = lab_profiles.group_models.get('panel')
        except AttributeError as e:
            if 'group_models' not in str(e):
                raise AttributeError(e)
        model_classes = [
            self.aliquot_type_model, self.profile_model, self.profile_item_model, self.panel_model]
        if None in model_classes:
            raise AppConfigurationError(
                'Not all required lab model classes were specified for '
                'in the configuration. Either pass \'lab_profiles=site_lab_profiles\' or '
                'explicitly declare the models on the class. Got {}.'.format(model_classes))

    def prepare(self):
        """Updates content type maps then runs each configuration method
        with the corresponding class attribute.

        Configuration methods update default data in supporting tables."""
        ContentTypeMapHelper().populate()
        ContentTypeMapHelper().sync()
        self.update_global()
        #self.update_or_create_consent_type()
        self.update_or_create_lab_clinic_api()
        self.update_or_create_lab()
        self.update_or_create_labeling()
        self.update_export_plan_setup()
        self.update_notification_plan_setup()
        self.update_holidays_setup()

    def update_or_create_lab_clinic_api(self):
        """Configure lab clinic api list models."""
        for item in self.lab_clinic_api_setup.get('aliquot_type'):
            try:
                aliquot_type = AliquotType.objects.get(name=item.name)
                aliquot_type.alpha_code = item.alpha_code
                aliquot_type.numeric_code = item.numeric_code
                aliquot_type.save()
            except AliquotType.DoesNotExist:
                AliquotType.objects.create(
                    name=item.name,
                    alpha_code=item.alpha_code,
                    numeric_code=item.numeric_code)
        # update / create panels
        for item in self.lab_clinic_api_setup.get('panel'):
            try:
                panel = Panel.objects.get(name=item.name)
                panel.panel_type = item.panel_type
                panel.save()
            except Panel.DoesNotExist:
                panel = Panel.objects.create(name=item.name, panel_type=item.panel_type)
            # add aliquots to panel
            aliquot_type = AliquotType.objects.get(alpha_code=item.aliquot_type_alpha_code)
            panel.aliquot_type.add(aliquot_type)

    def update_or_create_lab(self):
        """Updates profiles and supporting list tables for site
        specific lab module (e.g. bcpp_lab, mpepu_lab, ...)."""

        for setup_items in self.lab_setup.values():
            self.update_or_create_lab_destinations(setup_items)
            self.update_or_create_lab_aliquot_types(setup_items)
            self.update_or_create_lab_panels(setup_items)
            self.update_or_create_lab_profiles(setup_items)

    def update_or_create_lab_destinations(self, setup_items):
        """Updates / creates destination (shipping destination)."""
        for item in setup_items.get('destination', []):
            try:
                destination = Destination.objects.get(code=item.code)
                destination.name = item.name
                destination.address = item.address
                destination.tel = item.tel
                destination.email = item.email
                destination.save(update_fields=['name', 'address', 'tel', 'email'])
            except Destination.DoesNotExist:
                Destination.objects.create(
                    code=item.code,
                    name=item.name,
                    address=item.address,
                    tel=item.tel,
                    email=item.email)
            except MultipleObjectsReturned:
                Destination.objects.filter(code=item.code).delete()
                Destination.objects.create(
                    code=item.code,
                    name=item.name,
                    address=item.address,
                    tel=item.tel,
                    email=item.email)

    def update_or_create_lab_aliquot_types(self, setup_items):
        """Updates / creates aliquot_types."""
        for item in setup_items.get('aliquot_type'):
            try:
                aliquot_type = self.aliquot_type_model.objects.get(name=item.name)
                aliquot_type.alpha_code = item.alpha_code
                aliquot_type.numeric_code = item.numeric_code
                aliquot_type.save(update_fields=['alpha_code', 'numeric_code'])
            except self.aliquot_type_model.DoesNotExist:
                self.aliquot_type_model.objects.create(
                    name=item.name,
                    alpha_code=item.alpha_code,
                    numeric_code=item.numeric_code)

    def update_or_create_lab_panels(self, setup_items):
        """Updates / creates panels and links them to aliquot_types."""
        for item in setup_items.get('panel'):
            try:
                panel = self.panel_model.objects.get(name=item.name)
                panel.panel_type = item.panel_type
                panel.save(update_fields=['panel_type'])
            except self.panel_model.DoesNotExist:
                panel = self.panel_model.objects.create(
                    name=item.name,
                    panel_type=item.panel_type)
            # add aliquots to panel
            panel.aliquot_type.clear()
            aliquot_type = self.aliquot_type_model.objects.get(alpha_code=item.aliquot_type_alpha_code)
            panel.aliquot_type.add(aliquot_type)
            # create lab entry requisition panels based on this panel info
            try:
                requisition_panel = RequisitionPanel.objects.get(name=item.name)
                requisition_panel.aliquot_type_alpha_code = item.aliquot_type_alpha_code
                requisition_panel.save(update_fields=['aliquot_type_alpha_code'])
            except RequisitionPanel.DoesNotExist:
                requisition_panel = RequisitionPanel.objects.create(
                    name=item.name, aliquot_type_alpha_code=item.aliquot_type_alpha_code)

    def update_or_create_lab_profiles(self, setup_items):
        """ Updates / creates profiles."""
        for item in setup_items.get('profile'):
            aliquot_type = self.aliquot_type_model.objects.get(alpha_code=item.alpha_code)
            try:
                profile = self.profile_model.objects.get(name=item.profile_name)
                profile.aliquot_type = aliquot_type
                profile.save(update_fields=['aliquot_type'])
            except self.profile_model.DoesNotExist:
                self.profile_model.objects.create(name=item.profile_name, aliquot_type=aliquot_type)
        # add profile items
        for item in setup_items.get('profile_item'):
            profile = self.profile_model.objects.get(name=item.profile_name)
            aliquot_type = self.aliquot_type_model.objects.get(alpha_code=item.alpha_code)
            try:
                profile_item = self.profile_item_model.objects.get(profile=profile, aliquot_type=aliquot_type)
                profile_item.volume = item.volume
                profile_item.count = item.count
                profile_item.save(update_fields=['volume', 'count'])
            except self.profile_item_model.DoesNotExist:
                self.profile_item_model.objects.create(
                    profile=profile, aliquot_type=aliquot_type, volume=item.volume, count=item.count)

    def update_or_create_labeling(self):
        """Updates configuration in the :mod:`labeling` module."""

        for printer_setup in self.labeling_setup.get('label_printer', []):
            try:
                label_printer = LabelPrinter.objects.get(cups_printer_name=printer_setup.cups_printer_name,
                                                         cups_server_hostname=printer_setup.cups_server_hostname)
                label_printer.cups_server_ip = printer_setup.cups_server_ip
                label_printer.default = printer_setup.default
                label_printer.save(update_fields=['cups_server_ip', 'default'])
            except LabelPrinter.DoesNotExist:
                LabelPrinter.objects.create(
                    cups_printer_name=printer_setup.cups_printer_name,
                    cups_server_hostname=printer_setup.cups_server_hostname,
                    cups_server_ip=printer_setup.cups_server_ip,
                    default=printer_setup.default)
        for client_setup in self.labeling_setup.get('client', []):
            try:
                client = Client.objects.get(name=client_setup.hostname)
                client.label_printer = LabelPrinter.objects.get(
                    cups_printer_name=client_setup.printer_name,
                    cups_server_hostname=client_setup.cups_hostname)
                client.save(update_fields=['label_printer'])
            except Client.DoesNotExist:
                Client.objects.create(
                    name=client_setup.hostname,
                    label_printer=LabelPrinter.objects.get(
                        cups_printer_name=client_setup.printer_name,
                        cups_server_hostname=client_setup.cups_hostname))
        for zpl_template_setup in self.labeling_setup.get('zpl_template', []):
            try:
                zpl_template = ZplTemplate.objects.get(name=zpl_template_setup.name)
                zpl_template.template = zpl_template_setup.template
                zpl_template.default = zpl_template_setup.default
                zpl_template.save(update_fields=['template', 'default'])
            except ZplTemplate.DoesNotExist:
                ZplTemplate.objects.create(
                    name=zpl_template_setup.name,
                    template=zpl_template_setup.template,
                    default=zpl_template_setup.default)

    def update_global(self):
        """Creates or updates global configuration options in app_configuration.

        First ensures defaults exist, then, if user specification exists, overwrites the defaults or adds new.

        See sample app_configuration where there is an attribute like this:

            ...
            global_configuration = {
                'dashboard':
                    {'show_not_required': True,
                    'allow_additional_requisitions': False},
                'appointment':
                    {'allowed_iso_weekdays': '1234567',
                     'use_same_weekday': True,
                     'default_appt_type': 'default'},
                }
            ...

        """
        for category_name, category_configuration in self.configurations.items():
            for attr, value in category_configuration.items():
                try:
                    value, convert = value
                except (ValueError, TypeError):
                    value, convert = value, True
                convert = Convert(value, convert)
                string_value = convert.to_string()
                try:
                    global_configuration = GlobalConfiguration.objects.get(attribute=attr)
                    global_configuration.value = string_value
                    global_configuration.convert = convert.convert
                    global_configuration.save()
                except GlobalConfiguration.DoesNotExist:
                    GlobalConfiguration.objects.create(
                        category=category_name, attribute=attr, value=string_value, convert=convert.convert)

    @property
    def configurations(self):
        """Returns a dictionary of configurations to be used to update GlobalConfiguration model.

        Starts with the default_global_configuration and updates or adds any items changed
        by global_configurations."""

        configuration = deepcopy(default_global_configuration)
        for category, config in self.global_configuration.items():
            if configuration.get(category):
                for key, value in config.items():
                    configuration[category].update({key: value})
            else:
                configuration[category] = config
        return configuration

    def update_export_plan_setup(self):
        if self.export_plan_setup:
            ExportHelper.update_plan(self.export_plan_setup)

    def update_notification_plan_setup(self):
        if self.notification_plan_setup:
            notification_helper = NotificationHelper()
            notification_helper.update_plan(self.notification_plan_setup)

    def update_holidays_setup(self):
        """Updates holiday configurations in appointment__holiday module."""
        for holiday in self.holidays_setup:
            if not Holiday.objects.filter(holiday_name=holiday).exists():
                Holiday.objects.create(holiday_name=holiday, holiday_date=self.holidays_setup.get(holiday))
            else:
                updated_holiday = Holiday.objects.get(holiday_name=holiday)
                updated_holiday.holiday_date = self.holidays_setup.get(holiday)
                updated_holiday.save()

    def update_or_create_consent_type(self):
        for item in self.consent_type_setup:
            if settings.USE_TZ:
                item['start_datetime'] = localize(item.get('start_datetime'))
                item['end_datetime'] = localize(item.get('end_datetime'))
            try:
                consent_type = ConsentType.objects.get(
                    version=item.get('version'),
                    app_label=item.get('app_label'),
                    model_name=item.get('model_name'))
                consent_type.start_datetime = item.get('start_datetime')
                consent_type.end_datetime = item.get('end_datetime')
                consent_type.save()
            except ConsentType.DoesNotExist:
                ConsentType.objects.create(**item)
