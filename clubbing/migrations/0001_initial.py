# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-21 16:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Emoji',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('char_coded', models.TextField()),
                ('image_url', models.TextField()),
                ('image_source', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Riddle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seconds_spent', models.IntegerField()),
                ('unicode_chars', models.TextField()),
                ('more_chars_considered', models.TextField()),
                ('reshared', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clubbing.Riddle')),
            ],
        ),
        migrations.CreateModel(
            name='ShownRiddle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_shown', models.DateTimeField(verbose_name='time shown')),
                ('hints_used', models.TextField()),
                ('riddle_shown', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.Riddle')),
            ],
        ),
        migrations.CreateModel(
            name='ShownTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_shown', models.DateTimeField(verbose_name='time shown')),
            ],
        ),
        migrations.CreateModel(
            name='Solve',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_spent', models.IntegerField()),
                ('solve_time', models.DateTimeField(verbose_name='time solved')),
                ('attempts_count', models.IntegerField(default=0)),
                ('difficult_feedback', models.IntegerField(null=True)),
                ('riddle_show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.ShownRiddle')),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=30)),
                ('source', models.CharField(max_length=30)),
                ('language', models.CharField(default='English', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cookie_id', models.CharField(max_length=200)),
                ('auth_token', models.CharField(max_length=200)),
                ('auth_identifier', models.CharField(max_length=200)),
                ('auth_type', models.CharField(max_length=20)),
                ('first_seen', models.DateTimeField(verbose_name='first time seen')),
                ('last_seen', models.DateTimeField(verbose_name='last time seen')),
                ('page_count', models.IntegerField(default=0)),
                ('campaign_id', models.CharField(max_length=200)),
                ('campaign_source', models.CharField(max_length=20)),
                ('referrer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clubbing.User')),
            ],
        ),
        migrations.AddField(
            model_name='showntitle',
            name='riddler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.User'),
        ),
        migrations.AddField(
            model_name='showntitle',
            name='title_shown',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.Title'),
        ),
        migrations.AddField(
            model_name='shownriddle',
            name='solver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.User'),
        ),
        migrations.AddField(
            model_name='riddle',
            name='riddler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.User'),
        ),
        migrations.AddField(
            model_name='riddle',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubbing.Title'),
        ),
    ]
