from django.db import migrations


def clear_comparison_themes_hash(apps, schema_editor):
    """Force reload of comparison themes so locus values get populated.

    Migration 0013 was deployed before the RunPython step was added,
    so Django recorded it as applied without clearing the hash.
    This standalone migration ensures the hash is cleared on the next build.
    """
    DataVersion = apps.get_model('catechism', 'DataVersion')
    DataVersion.objects.filter(name='comparison-themes').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0013_add_locus_to_comparisontheme'),
    ]

    operations = [
        migrations.RunPython(clear_comparison_themes_hash, migrations.RunPython.noop),
    ]
