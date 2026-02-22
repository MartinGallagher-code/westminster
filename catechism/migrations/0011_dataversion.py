from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catechism', '0010_alter_scriptureindex_reference'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('data_hash', models.CharField(max_length=64)),
                ('loaded_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]