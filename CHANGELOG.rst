.. _changelog:

*********
Changelog
*********

2.2.0 2020-12-18
----------------

**New Features**

* Added ``PARAMETERIZED_I18N_NAME`` package setting.

2.1.3 2020-12-18
----------------

**Improvements**

* Support added for split files in the StaticSchemaLoader class by @askoretskiy
* Django APITestCase class added by @Goldziher

2.1.2 2020-10-06
----------------

**Improvements**

* Fixed minor settings bug

2.1.1 2020-09-27
----------------

**Improvements**

* Fixed djangorestframework-camel-case hard dependency
* Fixed cache bug

2.1.0 2020-09-24
----------------

**New Features**

* Added DRF-spectacular implementation
* Added response validation middleware
* Added response validation APIView

2.0.1 2020-09-15
----------------

* Fixed bug causing ``received`` parameter in the ``validate_response`` error output to display as an OrderedDict.
* Fixed bug causing error handling for undocumented paths to fail.

2.0.0 2020-09-14
----------------

**Breaking changes**

Version 2.0.0 introduces new required package settings, which means existing implementations will need to set up their ``SWAGGER_TESTER`` settings again before package functions will run.

Specifically:

* New required setting, ``SCHEMA_LOADER``, was added.
* Existing setting, ``CASE``, was replaced by new setting, ``CASE_TESTER``, which now takes a callable case validation function rather than a string.

**Non-breaking changes**

* New optional setting, ``CASE_PASSLIST``, was added, allowing projects to exclude keys from case checking on a general basis.
* Excess schema iterations have been eliminated, and code made more consise by consolidating case checking, response checking, and response data checking into a single loop.
* Shared schema loading logic consolidated in a schema loading base class, making it easy to create new loading classes for currently unsupported swagger implementations. This also allows us to unify the API for the ``validate_response`` function, rather than having separate import paths per implementation.
* Upgraded demo project from Django 2.2.6 to Django 3.1
* Improved test suite, test coverage, and fixed a number of minor bugs from v1

1.0.4 2020-07-14
----------------

**Improvements**

* Improves various error messages

1.0.3 2020-05-13
----------------

**Improvements**

* Added support for nullable arrays and objects.
* Added custom error hint for nullable arrays and objects.
* Added multi-line hints to response error messages.

1.0.2 2020-04-24
----------------

**Improvements**

* Improved handling of missing ``json`` response attribute.
* Made errors more concise, added error hints, and added ``verbose`` error messages.
* Further improved robustness of our route handling.


1.0.1 2020-04-21
----------------

**Improvements**

* Added handling of 204 HTTP responses.
* Improved exception handling for missing request bodies.
* Improved robustness of our route handling.


1.0.0 2020-04-20
----------------

* Initial release
* Added input validation for static schemas and drf_yasg-generated schemas
* Added response validation for static schemas and drf_yasg-generated schemas
* Added case checking, which is run for response- and input-validation.
