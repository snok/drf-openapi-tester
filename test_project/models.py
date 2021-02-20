from django.db import models


class Names(models.Model):
    custom_id_field = models.IntegerField(primary_key=True)

    class Meta:
        app_label = "test_project"
