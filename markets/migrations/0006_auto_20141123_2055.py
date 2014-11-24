# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0005_order_is_completed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='is_completed',
            new_name='is_successful',
        ),
    ]
