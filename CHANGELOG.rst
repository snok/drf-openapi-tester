.. _changelog:

*********
Changelog
*********

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
