
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_management_project.settings')
django.setup()

from django.apps import apps
import uuid

def check_and_fix_all_models():
    app_config = apps.get_app_config('tour_management')
    for model in app_config.get_models():
        if hasattr(model, 'uuid'):
            print(f"Checking {model.__name__}...")
            all_objs = model.objects.all()
            uuids = [str(o.uuid) for o in all_objs]
            unique_uuids = set(uuids)
            if len(uuids) != len(unique_uuids):
                print(f"FAIL: {model.__name__} has duplicate UUIDs! Total: {len(uuids)}, Unique: {len(unique_uuids)}")
                count = 0 
                for obj in all_objs:
                    obj.uuid = uuid.uuid4()
                    obj.save()
                    count += 1
                print(f"Fixed {count} records.")
            else:
                print(f"PASS: {model.__name__} UUIDs are unique.")

check_and_fix_all_models()
