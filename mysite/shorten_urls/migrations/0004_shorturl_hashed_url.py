# Generated by Django 2.1.15 on 2020-12-01 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shorten_urls', '0003_auto_20201201_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='shorturl',
            name='hashed_url',
            field=models.CharField(db_index=True, default='', max_length=32),
            preserve_default=False,
        ),
    ]