from django.db import migrations, models


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
    ]
