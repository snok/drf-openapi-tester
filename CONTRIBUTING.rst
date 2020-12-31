.. _contributing:

************
Contributing
************

This package is open to contributions. To contribute, please follow these steps:

1. Fork the upstream django-openapi-response-tester repository into a personal account.
2. Install poetry_, and install dev dependencies using ``poetry install``
3. Install pre-commit_ (for project linting) by running ``pre-commit install``.
4. Create a new branch for you changes
5. Push the topic branch to your personal fork.
6. Create a pull request to the django-openapi-response-tester repository with a detailed explanation of your changes.

.. _poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com/


Nice to know
------------
- To build docs locally, simply cd into ``/docs`` and run ``make html``. You can then navigate to ``file:///<your path>/django-openapi-response-tester/docs/build/html/index.html`` to browse them.
- Static files are gitignored, so to generate static assets locally, you should run ``manage.py collectstatic``.
- To publish a test-release, run

```
poetry config repositories.test https://test.pypi.org/legacy/
poetry config pypi-token.test ${{ secrets.TEST_PYPI_TOKEN }}
poetry publish --build --no-interaction --repository test
```
