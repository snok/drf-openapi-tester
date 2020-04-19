.. _publish:

*******
Publish
*******

This site is intended for the contributors of ``django-swagger-tester``.

PyPi
----

Publishing ``django-swagger-tester`` is done via Github workflows.

A publish to test-pypi is done every time a branch is merged into master (this means that the job will fail if the version already exists, but that's fine).

To publish to pypi, the push-to-pypi jobs is triggered by creating a ``release`` in the Github UI. See previous releases for formatting.


Read the docs
-------------

Read the docs documentation can be built locally by entering the ``docs`` folder and writing ``make html``.

The docs can be viewed in the browser by accessing ``~/django-swagger-tester/docs/build/html/index.html``.
