# Generated by Django 3.1.7 on 2021-03-10 22:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0048_auto_20210309_1154"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="itunes_category",
            field=models.TextField(
                help_text="Die für den Podcast vergebenen iTunes Category",
                null=True,
                verbose_name="iTunes Category",
            ),
        ),
        migrations.AddField(
            model_name="podcast",
            name="itunes_subcategory",
            field=models.TextField(
                help_text="Die für den Podcast vergebenen iTunes Subcategory",
                null=True,
                verbose_name="iTunes Subcategory",
            ),
        ),
    ]
