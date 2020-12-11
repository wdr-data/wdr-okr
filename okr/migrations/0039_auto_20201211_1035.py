# Generated by Django 3.1.4 on 2020-12-11 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0038_auto_20201210_1505"),
    ]

    operations = [
        migrations.AlterField(
            model_name="insta",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts", max_length=200, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts", max_length=200, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts", max_length=200, verbose_name="Name"
            ),
        ),
        migrations.AlterField(
            model_name="youtube",
            name="name",
            field=models.CharField(
                help_text="Name des Objekts", max_length=200, verbose_name="Name"
            ),
        ),
    ]