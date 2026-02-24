# Generated migration - adds tradition field to Catechism

from django.db import migrations, models


def set_known_traditions(apps, schema_editor):
    Catechism = apps.get_model('catechism', 'Catechism')
    Catechism.objects.filter(slug__in=['wsc', 'wlc', 'wcf']).update(
        tradition='westminster'
    )
    Catechism.objects.filter(slug__in=['heidelberg', 'belgic', 'dort']).update(
        tradition='three_forms_of_unity'
    )


class Migration(migrations.Migration):

    dependencies = [
        ("catechism", "0019_add_systematic_theology_document_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="catechism",
            name="tradition",
            field=models.CharField(
                choices=[
                    ("westminster", "Westminster Standards"),
                    ("three_forms_of_unity", "Three Forms of Unity"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=30,
            ),
        ),
        migrations.RunPython(set_known_traditions, migrations.RunPython.noop),
    ]