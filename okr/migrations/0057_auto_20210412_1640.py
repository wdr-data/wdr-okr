# Generated by Django 3.1.7 on 2021-04-12 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0056_auto_20210331_1749"),
    ]

    operations = [
        migrations.AlterField(
            model_name="insta",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts",
                max_length=200,
                unique=True,
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts",
                max_length=200,
                unique=True,
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts",
                max_length=200,
                unique=True,
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="tiktok",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts",
                max_length=200,
                unique=True,
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="youtube",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts",
                max_length=200,
                unique=True,
                verbose_name="Name",
            ),
        ),
    ]
