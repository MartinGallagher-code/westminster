from django.db import migrations, models


def clear_comparison_themes_hash(apps, schema_editor):
    """Force reload of comparison themes so locus values get populated."""
    DataVersion = apps.get_model('catechism', 'DataVersion')
    DataVersion.objects.filter(name='comparison-themes').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0012_remove_stale_locus_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparisontheme',
            name='locus',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RunPython(clear_comparison_themes_hash, migrations.RunPython.noop),
    ]
