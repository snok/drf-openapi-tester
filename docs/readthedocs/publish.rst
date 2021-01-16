.. _publish:

*******
Publish
*******

This page is intended for the contributors of ``django-openapi-tester``.

PyPi
----

Publishing ``django-openapi-tester`` is done via Github workflows. A publish to test-pypi is performed *before* we push to pypi, meaning the workflow will never fail against pypi.

To publish, create a ``release`` in the Github UI. See previous releases for formatting.

Read the docs
-------------

Read the docs documentation can be built locally by entering the ``docs`` folder and writing ``make html``.

The docs can be viewed in the browser by accessing ``~/django-openapi-tester/docs/build/html/index.html``.
