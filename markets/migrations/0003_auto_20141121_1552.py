# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0002_market_is_active'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Outcomes',
            new_name='Event',
        ),
        migrations.RenameField(
            model_name='outcome',
            old_name='set',
            new_name='event',
        ),
    ]
