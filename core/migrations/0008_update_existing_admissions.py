from django.db import migrations


def update_existing_admissions(apps, schema_editor):
    """
    Update existing PatientAdmission records to use the default ward.
    Also ensure each admission has a bed and ward properly set.
    """
    PatientAdmission = apps.get_model('core', 'PatientAdmission')
    Ward = apps.get_model('core', 'Ward')
    Bed = apps.get_model('core', 'Bed')
    
    # Get or create a default ward if it doesn't exist
    default_ward, created = Ward.objects.get_or_create(
        name='Общая палата',
        defaults={
            'department': 'Общее отделение',
            'floor': 1,
            'capacity': 10,
            'description': 'Общая палата по умолчанию',
            'is_active': True
        }
    )
    
    # Update all admissions without a ward to use the default ward
    admissions_without_ward = PatientAdmission.objects.filter(ward__isnull=True)
    for admission in admissions_without_ward:
        # If admission has a bed but no ward, use the bed's ward
        if admission.bed and admission.bed.ward:
            admission.ward = admission.bed.ward
        else:
            admission.ward = default_ward
        
        # If admission has no bed, create one in the default ward
        if not admission.bed:
            # Create a new bed in the default ward
            bed = Bed.objects.create(
                ward=default_ward,
                number=f"B{admission.id:03d}",
                bed_type='standard',
                is_available=False
            )
            admission.bed = bed
        
        # Set default admission type and active status
        admission.admission_type = 'planned'
        admission.is_active = not bool(admission.discharge_date)
        admission.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_alter_patientdocument_options_and_more'),
    ]

    operations = [
        migrations.RunPython(update_existing_admissions, reverse_code=migrations.RunPython.noop),
    ]
