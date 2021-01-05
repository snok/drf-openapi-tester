.. _publish:

*******
Publish
*******

This site is intended for the contributors of ``django-openapi-tester``.

PyPi
----

Publishing ``django-openapi-tester`` is done via Github workflows.

A publish to test-pypi is done every time a branch is merged into master (this means that the job will fail if the version already exists, but that's fine).

To publish to pypi, the push-to-pypi jobs is triggered by creating a ``release`` in the Github UI. See previous releases for formatting.

.. Note::

    Our ``README.rst`` and ``index.rst`` uses embedded html. This is not allowed by PyPi, and so we currently maintain a separate PYPI_README.rst that also needs to be updated to reflect changes.

Read the docs
-------------

Read the docs documentation can be built locally by entering the ``docs`` folder and writing ``make html``.

The docs can be viewed in the browser by accessing ``~/django-openapi-tester/docs/build/html/index.html``.
