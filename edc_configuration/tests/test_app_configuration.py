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

    global_configuration = {
        'appointment': {
            'allowed_iso_weekdays': ('2345', False),
            'use_same_weekday': False,
            'default_appt_type': 'clinic'},
        'protocol': {
            'start_datetime': study_start_datetime,
            'end_datetime': study_end_datetime}
    }

    consent_type_setup = [
        {'app_label': 'edc_testing',
         'model_name': 'testconsentmodel',
         'start_datetime': study_start_datetime,
         'end_datetime': study_end_datetime,
         'version': '1'}]

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
                 'profile': [ProfileTuple('Viral Load', 'WB'),
                             ProfileTuple('Genotyping', 'WB'),
                             ProfileTuple('ELISA', 'WB')],
                 'profile_item': [ProfileItemTuple('Viral Load', 'PL', 1.0, 3),
                                  ProfileItemTuple('Viral Load', 'BC', 0.5, 1),
                                  ProfileItemTuple('Genotyping', 'PL', 1.0, 4),
                                  ProfileItemTuple('Genotyping', 'BC', 0.5, 2),
                                  ProfileItemTuple('ELISA', 'PL', 1.0, 1),
                                  ProfileItemTuple('ELISA', 'BC', 0.5, 1)]}}

    labeling_setup = {
        'label_printer': [LabelPrinterTuple('Zebra_Technologies_ZTC_GK420t', 'localhost', '127.0.0.1', True)]
    }

    export_plan_setup = {}
