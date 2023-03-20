# Generated by Django 3.1.5 on 2021-01-14 17:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0044_auto_20210113_2354"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sophoraid",
            name="sophora_id",
            field=models.TextField(
                help_text="Sophora ID des Dokuments",
                unique=True,
                verbose_name="Sophora ID",
            ),
        ),
    ]
