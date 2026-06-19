from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_add_scripture_content_type'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SupporterSubscription',
        ),
    ]
