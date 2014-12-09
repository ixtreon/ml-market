# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('msr_maker', '0004_auto_20141209_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supply',
            name='amount',
            field=models.DecimalField(max_digits=7, decimal_places=2, default=0),
        ),
    ]
