# Generated by Django 2.1.15 on 2020-12-02 12:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shorten_urls', '0004_shorturl_hashed_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlPreviewData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=500)),
                ('url', models.URLField(max_length=256)),
                ('image_url', models.URLField(max_length=256)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('from_url', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preview_data', to='shorten_urls.ShortUrl')),
            ],
        ),
    ]
