# edc-configuration

This prepares Edc specific variables from a oconfiguration file in the project.

A configuration file is read when the `urls.py` is loaded. The values are written to model `GlobalConfiguration` and a few other models such as `edc_consent.consent_type`, `edc_appointment`, `lis.labeling`, `edc.export`, `edc.notification`, and others.

Having this file keeps the values in these models static across multiple instances of the project. In our case we have many offline clients that must be configured identically.

Somewhere in your project create a configuration class based on `edc_configuration.BaseAppConfiguration`. See the configuration file of other projects for an example -- `microbiome.apps.mb.MicrobiomeConfiguration`.

in `urls.py` import the class and call prepare(). In most cases you need `site_lab_profiles` to instantiate.:

    from my_app import AppConfiguration
    from edc.lab_profiles import site_lab_profiles
    
    site_lab_profiles.autodiscover()
    AppConfiguration(lab_profiles=site_lab_profiles).prepare()

