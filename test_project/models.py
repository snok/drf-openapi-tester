from django.db import models


class Names(models.Model):
    custom_id_field = models.IntegerField(primary_key=True)
    name = models.CharField(
        max_length=254,
        choices=(("mo", "Moses"), ("moi", "Moishe"), ("mu", "Mush")),
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "test_project"
