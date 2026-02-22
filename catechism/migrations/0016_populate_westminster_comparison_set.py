from django.db import migrations


def create_westminster_set(apps, schema_editor):
    ComparisonSet = apps.get_model('catechism', 'ComparisonSet')
    ComparisonTheme = apps.get_model('catechism', 'ComparisonTheme')

    westminster, _ = ComparisonSet.objects.get_or_create(
        slug='westminster',
        defaults={
            'name': 'Westminster Standards',
            'description': (
                'Compare doctrinal themes side-by-side across the Westminster '
                'Shorter Catechism, Larger Catechism, and Confession of Faith.'
            ),
            'order': 1,
        },
    )
    ComparisonTheme.objects.filter(comparison_set__isnull=True).update(
        comparison_set=westminster
    )


def reverse_westminster_set(apps, schema_editor):
    ComparisonTheme = apps.get_model('catechism', 'ComparisonTheme')
    ComparisonTheme.objects.all().update(comparison_set=None)


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0015_add_comparison_set_model'),
    ]

    operations = [
        migrations.RunPython(create_westminster_set, reverse_westminster_set),
    ]
