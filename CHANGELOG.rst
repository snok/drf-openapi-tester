.. _changelog:

*********
Changelog
*********

2.0.0 2020-09-14
----------------

**Breaking changes**

* ``SCHEMA_LOADER`` has been added as a new required setting. This breaks backwards compatibility from version 1.
* ``CASE`` setting has been reworked, and replaced by ``CASE_TESTER`` which now takes a callable from ``django_swagger_tester.case_testers``.

**Improvements**

* ``CASE_WHITELIST`` was added to settings, allowing projects to whitelist keys from case checking on a general basis.
* Schema loader classes were added, making it easier to create new implementations
* Performance has been improved by consolidating case checking, response checking, and response data checking into a single loop.
* Upgraded demo project from Django 2.2.6 to Django 3.1


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
