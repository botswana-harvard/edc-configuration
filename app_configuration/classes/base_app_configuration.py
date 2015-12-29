from __future__ import print_function

from django.core.exceptions import MultipleObjectsReturned

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.export.helpers import ExportHelper
from edc.lab.lab_clinic_api.models import AliquotType, Panel
from edc.lab.lab_packing.models import Destination
from edc.lab.lab_profile.classes import site_lab_profiles
from edc.notification.helpers import NotificationHelper
from edc.subject.entry.models import RequisitionPanel
from edc.utils import datatype_to_string
from edc_appointment.models import Holiday
from edc_consent.models.consent_type import ConsentType

from lis.labeling.models import LabelPrinter, ZplTemplate, Client

from .defaults import default_global_configuration

from ..models import GlobalConfiguration


class BaseAppConfiguration(object):

    appointment_configuration = None
    consent_catalogue_list = None
    consent_catalogue_setup = None
    lab_clinic_api_setup = None
    lab_setup = None
    study_site_setup = None
    study_variables_setup = None
    export_plan_setup = {}
    notification_plan_setup = {}
    labeling_setup = {}
    holidays_setup = {}

    def __init__(self):
        self.confirm_site_code_in_settings = True
        self.confirm_community_in_settings = True

    def prepare(self):
        """Updates content type maps then runs each configuration method with the corresponding class attribute.

        Configuration methods update default data in supporting tables."""
        ContentTypeMapHelper().populate()
        ContentTypeMapHelper().sync()
        self.update_global()
        self.update_or_create_consent_type()
        self.update_or_create_study_variables()
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
            # panel.aliquot_type.clear()
            aliquot_type = AliquotType.objects.get(alpha_code=item.aliquot_type_alpha_code)
            panel.aliquot_type.add(aliquot_type)

    def update_or_create_lab(self):
        """Updates profiles and supporting list tables for site specific lab module (e.g. bcpp_lab, mpepu_lab, ...).

        The supporting model classes Panel, AliquotType, Profile and ProfileItem
        are fetched from the global site_lab_profiles."""

        for setup_items in self.lab_setup.itervalues():
            destination = site_lab_profiles.group_models.get('destination')
            aliquot_type_model = site_lab_profiles.group_models.get('aliquot_type')
            panel_model = site_lab_profiles.group_models.get('panel')
            profile_model = site_lab_profiles.group_models.get('profile')
            profile_item_model = site_lab_profiles.group_models.get('profile_item')
            # update / create destination (shipping destination)
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
            # update / create aliquot_types
            for item in setup_items.get('aliquot_type'):
                try:
                    aliquot_type = aliquot_type_model.objects.get(name=item.name)
                    aliquot_type.alpha_code = item.alpha_code
                    aliquot_type.numeric_code = item.numeric_code
                    aliquot_type.save(update_fields=['alpha_code', 'numeric_code'])
                except aliquot_type_model.DoesNotExist:
                    aliquot_type_model.objects.create(name=item.name,
                                                      alpha_code=item.alpha_code,
                                                      numeric_code=item.numeric_code)
            # update / create panels
            for item in setup_items.get('panel'):
                try:
                    panel = panel_model.objects.get(name=item.name)
                    panel.panel_type = item.panel_type
                    panel.save(update_fields=['panel_type'])
                except panel_model.DoesNotExist:
                    panel = panel_model.objects.create(name=item.name,
                                                       panel_type=item.panel_type)
                # add aliquots to panel
                panel.aliquot_type.clear()
                aliquot_type = aliquot_type_model.objects.get(alpha_code=item.aliquot_type_alpha_code)
                panel.aliquot_type.add(aliquot_type)
                # create lab entry requisition panels based on this panel info
                try:
                    requisition_panel = RequisitionPanel.objects.get(name=item.name)
                    requisition_panel.aliquot_type_alpha_code = item.aliquot_type_alpha_code
                    requisition_panel.save(update_fields=['aliquot_type_alpha_code'])
                except RequisitionPanel.DoesNotExist:
                    requisition_panel = RequisitionPanel.objects.create(
                        name=item.name, aliquot_type_alpha_code=item.aliquot_type_alpha_code)
            # create profiles
            for item in setup_items.get('profile'):
                aliquot_type = aliquot_type_model.objects.get(alpha_code=item.alpha_code)
                try:
                    profile = profile_model.objects.get(name=item.profile_name)
                    profile.aliquot_type = aliquot_type
                    profile.save(update_fields=['aliquot_type'])
                except profile_model.DoesNotExist:
                    profile_model.objects.create(name=item.profile_name, aliquot_type=aliquot_type)
            # add profile items
            for item in setup_items.get('profile_item'):
                profile = profile_model.objects.get(name=item.profile_name)
                aliquot_type = aliquot_type_model.objects.get(alpha_code=item.alpha_code)
                try:
                    profile_item = profile_item_model.objects.get(profile=profile, aliquot_type=aliquot_type)
                    profile_item.volume = item.volume
                    profile_item.count = item.count
                    profile_item.save(update_fields=['volume', 'count'])
                except profile_item_model.DoesNotExist:
                    profile_item_model.objects.create(
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
                    default=printer_setup.default,
                )
        for client_setup in self.labeling_setup.get('client', []):
            try:
                client = Client.objects.get(name=client_setup.hostname)
                client.label_printer = LabelPrinter.objects.get(cups_printer_name=client_setup.printer_name,
                                                                cups_server_hostname=client_setup.cups_hostname)
                client.save(update_fields=['label_printer'])
            except Client.DoesNotExist:
                Client.objects.create(
                    name=client_setup.hostname,
                    label_printer=LabelPrinter.objects.get(cups_printer_name=client_setup.printer_name,
                                                           cups_server_hostname=client_setup.cups_hostname),
                )
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
                    default=zpl_template_setup.default,
                )

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
        configurations = [default_global_configuration]
        try:
            configurations.append(self.global_configuration)
        except AttributeError:
            pass   # maybe attribute does not exist
        for configuration in configurations:
            for category_name, category_configuration in configuration.iteritems():
                for attr, value in category_configuration.iteritems():
                    string_value = datatype_to_string(value)
                    string_value = string_value.strip(' "')
                    try:
                        global_configuration = GlobalConfiguration.objects.get(attribute=attr)
                        global_configuration.value = string_value
                        global_configuration.save()
                    except GlobalConfiguration.DoesNotExist:
                        GlobalConfiguration.objects.create(category=category_name, attribute=attr, value=string_value)

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
