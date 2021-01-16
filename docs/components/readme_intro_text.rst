
Django OpenAPI Tester is a simple test utility. Its aim is to make it easy for
developers to catch and correct documentation errors in their OpenAPI schema.

Maintaining good documentation is hard, and ensuring complete correctness is
harder. By testing that your **actual** API responses against your schema,
you can *know* that your schema reflects reality.

To illustrate; given this example response:


.. code-block:: python

    {
      "id": 0,
      "name": "doggie",
      "status": "available",
      "photoUrls": ["string"],
      "category": {
        "id": 0,
        "name": "string"
      }
    }

your brain shouldn't have to manually scan this OpenAPI response schema for
possible documentation errors

.. code-block:: yaml

  responses:
    '200':
      description: successful operation
      schema:
        type: object
        required:
        - name
        - photoUrls
        properties:
          id:
            type: integer
            format: int64
          category:
            type: object
            properties:
              id:
                type: integer
                format: int64
              name:
                type: string
            xml:
              name: Category
          name:
            type: string
            example: doggie
          photoUrl:
            type: array
            xml:
              wrapped: true
            items:
              type: string
              xml:
                name: photoUrl
          status:
            type: string
            description: pet status in the store
            enum:
            - available
            - pending
            - sold
        xml:
          name: Pet

when automated tests can simply tell you that ``photoUrls`` is missing an ``s``.

Not only that, but when you come back and change your API next year, your test
suite should not allow you to deploy your changes without remembering to
update your documentation.
