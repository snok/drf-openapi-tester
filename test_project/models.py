from django.db import models


class Names(models.Model):
    custom_id_field = models.IntegerField(primary_key=True, max_length=20)

    class Meta:
        app_label = "test_project"
