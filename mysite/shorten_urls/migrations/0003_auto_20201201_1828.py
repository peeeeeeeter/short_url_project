# Generated by Django 2.1.15 on 2020-12-01 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shorten_urls', '0002_shorturl_random_offset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shorturl',
            name='original_url',
            field=models.TextField(unique=True),
        ),
    ]
