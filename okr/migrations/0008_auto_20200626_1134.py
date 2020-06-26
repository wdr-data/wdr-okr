# Generated by Django 3.0.7 on 2020-06-26 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0007_auto_20200626_0953"),
    ]

    operations = [
        migrations.CreateModel(
            name="InstaCollaborationType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
            ],
            options={
                "verbose_name": "Instagram-Collaboration Format",
                "verbose_name_plural": "Instagram-Collaboration Formate",
            },
        ),
        migrations.AddField(
            model_name="instacollaboration",
            name="collaboration_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="collaboration",
                to="okr.InstaCollaborationType",
                verbose_name="Format",
            ),
        ),
    ]
