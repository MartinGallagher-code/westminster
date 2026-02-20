"""Replace old unique constraints with catechism-scoped ones."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0005_add_catechism_fk'),
    ]

    operations = [
        # Remove old unique on Question.number
        migrations.AlterField(
            model_name='question',
            name='number',
            field=models.PositiveIntegerField(db_index=True),
        ),
        # Remove old unique on Topic.slug and Topic.order
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name='topic',
            name='order',
            field=models.PositiveIntegerField(),
        ),
        # Add new composite unique constraints
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('catechism', 'number')},
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together={('catechism', 'slug'), ('catechism', 'order')},
        ),
    ]
