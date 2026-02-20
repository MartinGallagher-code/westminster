"""Add nullable catechism FK to Question and Topic, then populate with WSC."""
import django.db.models.deletion
from django.db import migrations, models


def set_catechism_wsc(apps, schema_editor):
    Catechism = apps.get_model('catechism', 'Catechism')
    Question = apps.get_model('catechism', 'Question')
    Topic = apps.get_model('catechism', 'Topic')
    wsc = Catechism.objects.get(slug='wsc')
    Question.objects.filter(catechism__isnull=True).update(catechism=wsc)
    Topic.objects.filter(catechism__isnull=True).update(catechism=wsc)


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0004_catechism_model'),
    ]

    operations = [
        # Add nullable FK to Question
        migrations.AddField(
            model_name='question',
            name='catechism',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='questions',
                to='catechism.catechism',
            ),
        ),
        # Add nullable FK to Topic
        migrations.AddField(
            model_name='topic',
            name='catechism',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='topics',
                to='catechism.catechism',
            ),
        ),
        # Populate existing rows with WSC
        migrations.RunPython(set_catechism_wsc, migrations.RunPython.noop),
        # Make FK non-nullable
        migrations.AlterField(
            model_name='question',
            name='catechism',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='questions',
                to='catechism.catechism',
            ),
        ),
        migrations.AlterField(
            model_name='topic',
            name='catechism',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='topics',
                to='catechism.catechism',
            ),
        ),
    ]
