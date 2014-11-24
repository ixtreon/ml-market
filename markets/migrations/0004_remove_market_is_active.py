# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0003_auto_20141121_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='market',
            name='is_active',
        ),
    ]
