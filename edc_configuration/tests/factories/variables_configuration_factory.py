import factory

from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.core.bhp_variables.models import StudySpecific


class VariblesConfigurationFactory(BaseUuidModelFactory):
    FACTORY_FOR = StudySpecific
