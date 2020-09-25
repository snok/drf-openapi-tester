from django.db import models


class Schema(models.Model):
    hash = models.CharField(max_length=50, unique=True)


class Url(models.Model):
    """
    Holds references to specific API urls.
    """

    url = models.CharField(max_length=2048)


class Method(models.Model):
    """
    Holds references to the particular method of an API url.
    """

    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    method = models.CharField(max_length=6, choices=METHOD_CHOICES)


class ValidatedResponse(models.Model):
    """
    Holds response validation results for specific endpoints and methods.
    """

    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    status_code = models.IntegerField()
    response_hash = models.CharField(max_length=50)
    schema_hash = models.ForeignKey(Schema, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    valid = models.BooleanField()
    error_message = models.TextField(null=True)
