import factory

from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.subject.consent.models import ConsentCatalogue


class CatalogueConfigurationFactory(BaseUuidModelFactory):
    FACTORY_FOR = ConsentCatalogue
