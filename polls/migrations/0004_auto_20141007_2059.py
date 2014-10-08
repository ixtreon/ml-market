# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20141007_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='real_outcome',
            field=models.OneToOneField(related_name='ans', blank=True, null=True, to='polls.Outcome'),
        ),
    ]
