from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='occupational_health_service',
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text='Service de médecine du travail (nom, organisme, etc.)',
            ),
        ),
    ]
