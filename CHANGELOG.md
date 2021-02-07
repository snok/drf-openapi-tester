# Changelog


## v1.0.0 2020-02-07

* Now supports `anyOf`
* Adds `additionalProperties` support
* Adds validation for remaining OpenAPI features, including
    * `format`
    * `enum`
    * `pattern`
    * `multipleOf`
    * `uniqueItems`
    * `minLength` and `maxLength`
    * `minProperties` and `maxProperties`
    * `minimum`, `maximum`, `exclusiveMinimum`, and `exclusiveMaximum`

## v0.1.0 2020-01-26

* Package refactored and renamed from `django-swagger-tester` to `drf-openapi-tester`
* Adds `inflection` for case checking
* Adds `prance` for schema validation
* Adds enum validation
* Adds format validation
* Adds support for `oneOf` and `allOf`
