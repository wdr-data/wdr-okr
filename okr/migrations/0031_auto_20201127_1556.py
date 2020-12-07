# Generated by Django 3.1.3 on 2020-11-27 14:56

from django.db import migrations, models
import django.db.models.deletion


def remove_pages(apps, schema_editor):
    Page = apps.get_model("okr", "Page")
    Page.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0030_auto_20201126_1641"),
    ]

    operations = [
        migrations.CreateModel(
            name="SophoraDocument",
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
                (
                    "export_uuid",
                    models.CharField(
                        help_text="Die ID, die dem Dokument vom Export-System zugewiesen wurde",
                        max_length=64,
                        unique=True,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
                        verbose_name="Zeitpunkt der Erstellung",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sophora-Dokument",
                "verbose_name_plural": "Sophora-Dokumente",
                "db_table": "sophora_document",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="SophoraDocumentMeta",
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
                (
                    "editorial_update",
                    models.DateTimeField(
                        help_text="Von Redaktion gesetzes Standdatum",
                        verbose_name="Redaktioneller Stand",
                        null=True,
                    ),
                ),
                (
                    "node",
                    models.CharField(
                        help_text="Der Sophora-Strukturknoten, unter dem das Dokument momentan abgelegt ist",
                        max_length=128,
                        verbose_name="Strukturknoten",
                    ),
                ),
                (
                    "sophora_id",
                    models.CharField(
                        help_text="Momentane Sophora ID des Dokuments",
                        max_length=128,
                        verbose_name="Sophora ID",
                    ),
                ),
                (
                    "headline",
                    models.TextField(
                        help_text="Schlagzeile des Sophora-Dokuments",
                        verbose_name="Titel",
                    ),
                ),
                (
                    "teaser",
                    models.TextField(
                        help_text="Teasertext des Sophora-Dokuments",
                        verbose_name="Teaser",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        help_text="Der Typ des Sophora-Beitrags",
                        max_length=64,
                        verbose_name="Beitragstyp",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Der Zeitpunkt, an dem diese Metadaten abgerufen wurden",
                        verbose_name="Zeitpunkt der Erstellung",
                    ),
                ),
                (
                    "sophora_document",
                    models.ForeignKey(
                        help_text="Das Sophora-Dokument, zu dem diese Daten gehören",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metas",
                        related_query_name="meta",
                        to="okr.sophoradocument",
                        verbose_name="Sophora-Dokument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sophora-Dokument-Meta",
                "verbose_name_plural": "Sophora-Dokument-Metas",
                "db_table": "sophora_document_meta",
                "ordering": ["-created"],
                "unique_together": {
                    ("sophora_document", "headline", "teaser", "document_type")
                },
            },
        ),
        migrations.CreateModel(
            name="SophoraID",
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
                (
                    "sophora_id",
                    models.CharField(
                        help_text="Sophora ID des Dokuments",
                        max_length=128,
                        unique=True,
                        verbose_name="Sophora ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
                        verbose_name="Zeitpunkt der Erstellung",
                    ),
                ),
                (
                    "sophora_document",
                    models.ForeignKey(
                        help_text="Das Sophora-Dokument, zu dem diese ID gehört (hat)",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sophora_ids",
                        related_query_name="sophora_id",
                        to="okr.sophoradocument",
                        verbose_name="Sophora-Dokument",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SophoraNode",
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
                (
                    "node",
                    models.CharField(
                        max_length=128, unique=True, verbose_name="Sophora Knoten"
                    ),
                ),
                (
                    "use_exact_search",
                    models.BooleanField(
                        help_text="Wenn dieser Haken gesetzt ist, werden Unterknoten ignoriert",
                        verbose_name="Ignoriere Unterknoten",
                    ),
                ),
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Jüngste Aktualisierung des Datenpunktes",
                        verbose_name="Zuletzt upgedated",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sophora-Knoten",
                "verbose_name_plural": "Sophora-Knoten",
                "db_table": "sophora_node",
                "ordering": ["node"],
            },
        ),
        migrations.RemoveField(
            model_name="page",
            name="sophora_id",
        ),
        migrations.AlterField(
            model_name="page",
            name="property",
            field=models.ForeignKey(
                help_text="Die GSC-Property, unter der diese Seite gefunden wurde",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pages",
                related_query_name="page",
                to="okr.property",
                verbose_name="Property",
            ),
        ),
        migrations.DeleteModel(
            name="PageMeta",
        ),
        migrations.AddField(
            model_name="sophoradocument",
            name="sophora_node",
            field=models.ForeignKey(
                help_text="Der Sophora-Knoten, unter dem dieses Dokument gefunden wurde",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                related_query_name="document",
                to="okr.sophoranode",
                verbose_name="Sophora-Knoten",
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="sophora_document",
            field=models.ForeignKey(
                help_text="Das Sophora-Dokument, auf das diese Seite zeigt",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pages",
                related_query_name="page",
                to="okr.sophoradocument",
                verbose_name="Sophora-Dokument",
            ),
        ),
        migrations.RunPython(remove_pages),
    ]
