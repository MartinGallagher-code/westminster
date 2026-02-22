"""Remove stale 'locus' column from comparisontheme table.

This column was added by a migration that was later reverted from code
but had already been applied to the production database.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0011_dataversion'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE catechism_comparisontheme DROP COLUMN IF EXISTS locus;",
            reverse_sql="ALTER TABLE catechism_comparisontheme ADD COLUMN locus varchar(100) NOT NULL DEFAULT '';",
        ),
    ]
