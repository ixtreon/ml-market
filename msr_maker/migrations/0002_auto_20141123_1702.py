# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('msr_maker', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Trade',
        ),
        migrations.RenameField(
            model_name='supply',
            old_name='outcome_id',
            new_name='outcome',
        ),
        migrations.AddField(
            model_name='supply',
            name='amount',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
