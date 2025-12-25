from django.db import models

class Skill(models.Model):

    title
    video_url

    required = models.ManyToManyField(
            'self',
            symmetrical=False,
            related_name='unlocks',
            blank=True
        )
