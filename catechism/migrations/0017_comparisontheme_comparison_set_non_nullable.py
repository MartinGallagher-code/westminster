from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0016_populate_westminster_comparison_set'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparisontheme',
            name='comparison_set',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='themes',
                to='catechism.comparisonset',
            ),
        ),
    ]
