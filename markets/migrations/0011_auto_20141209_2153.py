# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0010_account_is_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='funds',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='buy_offer',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='current_price',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='sell_offer',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
        migrations.AlterField(
            model_name='position',
            name='amount',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
        migrations.AlterField(
            model_name='position',
            name='contract_price',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
    ]
