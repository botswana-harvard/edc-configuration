from datetime import datetime

from edc_configuration.base_app_configuration import BaseAppConfiguration
from edc_lab.lab_profile.classes import ProfileItemTuple, ProfileTuple

from lis.labeling.classes import LabelPrinterTuple
from lis.specimen.lab_aliquot_list.classes import AliquotTypeTuple
from lis.specimen.lab_panel.classes import PanelTuple

from edc_testing.models import TestAliquotType, TestPanel, TestProfile, TestProfileItem

study_start_datetime = datetime(2013, 10, 18, 10, 30, 0)
study_end_datetime = datetime(2016, 10, 17, 16, 30, 0)


class TestAppConfiguration(BaseAppConfiguration):

    aliquot_type_model = TestAliquotType
    panel_model = TestPanel
    profile_model = TestProfile
    profile_item_model = TestProfileItem

    appointment_configuration = {
        'allowed_iso_weekdays': '1234567',
        'use_same_weekday': True,
        'default_appt_type': 'default'}

    study_variables_setup = {
        'protocol_number': 'TEST',
        'protocol_code': '000',
        'protocol_title': 'TEST',
        'research_title': 'Test Project',
        'study_start_datetime': study_start_datetime,
        'minimum_age_of_consent': 16,
        'maximum_age_of_consent': 64,
        'gender_of_consent': 'MF',
        'subject_identifier_seed': '10000',
        'subject_identifier_prefix': '000',
        'subject_identifier_modulus': '7',
        'subject_type': 'subject',
        'machine_type': 'SERVER',
        'hostname_prefix': 's030',
        'device_id': '99'}

    consent_catalogue_setup = {
        'name': 'test',
        'content_type_map': 'testconsentwithmixin',
        'consent_type': 'study',
        'version': 1,
        'start_datetime': study_start_datetime,
        'end_datetime': study_end_datetime,
        'add_for_app': 'edc_testing'}

    consent_type_setup = [
        {'app_label': 'edc_testing',
         'model_name': 'testconsentmodel',
         'start_datetime': study_start_datetime,
         'end_datetime': study_end_datetime,
         'version': '1'}]

    study_site_setup = [{
        'site_name': 'test_site',
        'site_code': '10'}]

    lab_clinic_api_setup = {
        'panel': [PanelTuple('Research Blood Draw', 'TEST', 'WB'),
                  PanelTuple('Viral Load', 'TEST', 'WB'),
                  PanelTuple('Microtube', 'STORAGE', 'WB')],
        'aliquot_type': [AliquotTypeTuple('Whole Blood', 'WB', '02'),
                         AliquotTypeTuple('Plasma', 'PL', '32'),
                         AliquotTypeTuple('Buffy Coat', 'BC', '16')]}

    lab_setup = {'test': {
                 'panel': [PanelTuple('Research Blood Draw', 'TEST', 'WB'),
                           PanelTuple('Viral Load', 'TEST', 'WB'),
                           PanelTuple('Microtube', 'STORAGE', 'WB')],
                 'aliquot_type': [AliquotTypeTuple('Whole Blood', 'WB', '02'),
                                  AliquotTypeTuple('Plasma', 'PL', '32'),
                                  AliquotTypeTuple('Buffy Coat', 'BC', '16')],
                 'profile': [ProfileTuple('Viral Load', 'WB'), ProfileTuple('Genotyping', 'WB'), ProfileTuple('ELISA', 'WB')],
                 'profile_item': [ProfileItemTuple('Viral Load', 'PL', 1.0, 3),
                                  ProfileItemTuple('Viral Load', 'BC', 0.5, 1),
                                  ProfileItemTuple('Genotyping', 'PL', 1.0, 4),
                                  ProfileItemTuple('Genotyping', 'BC', 0.5, 2),
                                  ProfileItemTuple('ELISA', 'PL', 1.0, 1),
                                  ProfileItemTuple('ELISA', 'BC', 0.5, 1)]}}

    labeling = {'label_printer': [LabelPrinterTuple('Zebra_Technologies_ZTC_GK420t', 'localhost', '127.0.0.1', True), ],
                }

    consent_catalogue_list = [consent_catalogue_setup]

    export_plan_setup = {}
