# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0006_auto_20141123_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcome',
            name='buy_offer',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='outcome',
            name='sell_offer',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
            preserve_default=True,
        ),
    ]
