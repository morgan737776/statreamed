from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from documents.models import Document
from core.models import Patient

class Command(BaseCommand):
    help = 'Creates default user groups and assigns permissions for the application.'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user groups...')

        # Define the groups and the permissions they should have
        # Permissions are referenced by their codename
        groups_and_permissions = {
            'Администраторы': {
                Document: ['view_document', 'add_document', 'change_document', 'delete_document', 'approve_document'],
                Patient: ['view_patient', 'add_patient', 'change_patient', 'delete_patient'],
            },
            'Врачи': {
                Document: ['view_document', 'add_document', 'change_document', 'approve_document'],
                Patient: ['view_patient', 'add_patient', 'change_patient'],
            },
            'Сотрудники регистратуры': {
                Document: ['view_document', 'add_document'],
                Patient: ['view_patient', 'add_patient', 'change_patient'],
            }
        }

        for group_name, model_permissions in groups_and_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created.'))
            
            # Clear existing permissions to ensure a clean setup
            group.permissions.clear()

            for model, permissions in model_permissions.items():
                content_type = ContentType.objects.get_for_model(model)
                for perm_codename in permissions:
                    try:
                        permission = Permission.objects.get(
                            content_type=content_type,
                            codename=perm_codename
                        )
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Warning: Permission "{perm_codename}" not found for model "{model.__name__}".'))
            
            self.stdout.write(f'Permissions assigned to group "{group_name}".')

        self.stdout.write(self.style.SUCCESS('Successfully completed setting up groups and permissions.'))
