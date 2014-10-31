# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('amount', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('contract_price', models.DecimalField(default=0, max_digits=7, decimal_places=2)),
                ('order', models.ForeignKey(to='markets.Order')),
                ('outcome', models.ForeignKey(to='markets.Outcome')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='datum',
            old_name='setId',
            new_name='set_id',
        ),
        migrations.RemoveField(
            model_name='market',
            name='exp_date',
        ),
        migrations.RemoveField(
            model_name='market',
            name='last_reveal_date',
        ),
        migrations.RemoveField(
            model_name='market',
            name='last_revealed_id',
        ),
        migrations.RemoveField(
            model_name='market',
            name='reveal_interval',
        ),
        migrations.RemoveField(
            model_name='order',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='order',
            name='claim',
        ),
        migrations.RemoveField(
            model_name='order',
            name='price',
        ),
        migrations.AddField(
            model_name='dataset',
            name='active_datum_start',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 31, 1, 7, 36, 165445), verbose_name='Date last challenge was started'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='is_active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='reveal_interval',
            field=models.IntegerField(default=7, verbose_name='Interval between challenges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='is_processed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
