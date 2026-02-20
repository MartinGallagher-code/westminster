"""Create Catechism model and WSC record."""
from django.db import migrations, models


def create_wsc(apps, schema_editor):
    Catechism = apps.get_model('catechism', 'Catechism')
    Catechism.objects.create(
        name='Westminster Shorter Catechism',
        abbreviation='WSC',
        slug='wsc',
        description='The Westminster Shorter Catechism, composed in 1647, contains 107 questions and answers summarizing the essential doctrines of the Christian faith.',
        year=1647,
        total_questions=107,
    )


def remove_wsc(apps, schema_editor):
    Catechism = apps.get_model('catechism', 'Catechism')
    Catechism.objects.filter(slug='wsc').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0003_scripturepassage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Catechism',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('abbreviation', models.CharField(max_length=10, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('year', models.PositiveIntegerField(blank=True, null=True)),
                ('total_questions', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['abbreviation'],
            },
        ),
        migrations.RunPython(create_wsc, remove_wsc),
    ]
