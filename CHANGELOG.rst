.. _changelog:

*********
Changelog
*********

2.0.0 2020-09-14
----------------

**Breaking changes**

* New required setting, ``SCHEMA_LOADER``, was added.
* Existing setting, ``CASE``, was replaced by new setting, ``CASE_TESTER``, which now takes a callable case validation function rather than a string.

**General improvements**

* New optional setting, ``CASE_WHITELIST``, was added, allowing projects to exclude keys from case checking on a general basis.
* Excess schema iterations have been eliminated, and code made more consise by consolidating case checking, response checking, and response data checking into a single loop.
* Shared schema loading logic consolidated in a schema loading base class, making it easy to create new loading classes for currently unsupported swagger implementations. This also allows us to unify the API for the ``validate_response`` function, rather than having separate import paths per implementation.
* Upgraded demo project from Django 2.2.6 to Django 3.1
* Improved test suite, test coverage, and fixed a number of minor bugs

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
