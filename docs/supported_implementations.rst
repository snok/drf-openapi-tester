Supported Implementations
-------------------------

As long as we can load your OpenAPI schema, we can test your API responses.
How we load your OpenAPI schema, however, will depend on what package(s) you're
using to host/generate your schema.

We currently have pre-made schema-loader classes created for:

- Schemas rendered dynamically using `drf-yasg`_
- Schemas rendered dynamically using `drf-spectacular`_
- Any implementation which generates a static yaml or json file (e.g., like `DRF`_)

We believe this should cover most cases, but if you're using another method to
generate your documentation and would like to use this package, feel free to
add an issue, or create a PR. Adding a new implementation is as easy as adding
the required logic needed to load the OpenAPI schema.

Take a look here_ for inspiration.

.. _here: https://github.com/snok/django-openapi-tester/blob/master/openapi_tester/loaders.py#L418
.. _drf-yasg: https://github.com/axnsan12/drf-yasg
.. _drf-spectacular: https://github.com/tfranzel/drf-spectacular
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
