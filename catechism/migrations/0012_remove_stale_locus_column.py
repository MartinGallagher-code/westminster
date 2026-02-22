"""Remove stale 'locus' column from comparisontheme table if it exists.

This column was added by a migration that was later reverted from code
but had already been applied to the production database.
"""

from django.db import migrations


def drop_locus_if_exists(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    columns = [
        col.name for col in
        connection.introspection.get_table_description(cursor, 'catechism_comparisontheme')
    ]
    if 'locus' in columns:
        cursor.execute("ALTER TABLE catechism_comparisontheme DROP COLUMN locus;")


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0011_dataversion'),
    ]

    operations = [
        migrations.RunPython(drop_locus_if_exists, migrations.RunPython.noop),
    ]
