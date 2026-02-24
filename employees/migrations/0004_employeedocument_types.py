from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_medicalvisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeedocument',
            name='document_type',
            field=models.CharField(choices=[('contract', 'Contrat de travail'), ('amendment', 'Avenant'), ('id_card', "Pi\u00e8ce d'identit\u00e9"), ('diploma', 'Dipl\u00f4me'), ('certificate', 'Certificat m\u00e9dical'), ('payslip', 'Bulletin de salaire'), ('attestation', 'Attestation'), ('cpam_attestation', 'Attestation CPAM'), ('rib', "Relev\u00e9 d'identit\u00e9 bancaire"), ('driving_license', 'Permis de conduire'), ('dpae', 'DPAE'), ('insurance', 'Assurance'), ('other', 'Autre')], max_length=50, verbose_name='Type de document'),
        ),
    ]
