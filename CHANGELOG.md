# Changelog

## v1.3.0 WIP

* Updated handling of byte format to test for base64 string
* Added format validators to handle the following keywords: "uuid", "base64", "email", "uri", "url", "ipv4", "ipv6" and "time"
  validator

## v1.2.0 2020-02-14

* Added validation of writeOnly keys
* Updated openAPI keyword (anyOf, oneOf, allOf) logic
* Resolve minor issues with error formatting (unable to handle bytes)

## v1.1.0 2020-02-12

* Fixed allOf deep object merging
* Fixed handling of non-string path parameters
* Fixed error messages
* Fixed handling of 0 as a float format value

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
