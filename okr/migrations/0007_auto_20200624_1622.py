# Generated by Django 3.0.7 on 2020-06-24 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0006_instastory_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="instastory",
            name="caption",
            field=models.TextField(verbose_name="Text"),
        ),
    ]