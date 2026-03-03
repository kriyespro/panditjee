import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, PanditProfile, ClientProfile
from apps.core.models import City

def create_test_users():
    print("Creating test users...")
    
    city, _ = City.objects.get_or_create(name='Surat', slug='surat', state='Gujarat', is_active=True)
    
    # 1. Admin User
    try:
        if not User.objects.filter(email='admin@sd.com').exists():
            User.objects.create_superuser('admin@sd.com', 'admin@sd.com', 'AdminPassword123!', first_name='Super', last_name='Admin')
            print("Created Admin user")
    except Exception as e:
        print(f"Error creating Admin: {e}")

    # 2A. Approved Pandit
    try:
        if not User.objects.filter(email='pandit.ram@sd.com').exists():
            u = User.objects.create_user('pandit.ram@sd.com', 'pandit.ram@sd.com', 'PanditPassword123!', first_name='Ram', last_name='Shastri', role='PANDIT', phone='9876500001')
            PanditProfile.objects.create(user=u, city=city, experience_years=15, base_price=2100.00, status='APPROVED')
            print("Created Approved Pandit")
    except Exception as e:
        print(f"Error creating Pandit Ram: {e}")

    # 2B. Pending Pandit
    try:
        if not User.objects.filter(email='pandit.shyam@sd.com').exists():
            u = User.objects.create_user('pandit.shyam@sd.com', 'pandit.shyam@sd.com', 'PanditPassword123!', first_name='Shyam', last_name='Joshi', role='PANDIT', phone='9876500002')
            PanditProfile.objects.create(user=u, city=city, experience_years=5, base_price=1100.00, status='PENDING')
            print("Created Pending Pandit")
    except Exception as e:
        print(f"Error creating Pandit Shyam: {e}")

    # 3. Client Account
    try:
        if not User.objects.filter(email='client.rahul@sd.com').exists():
            u = User.objects.create_user('client.rahul@sd.com', 'client.rahul@sd.com', 'ClientPassword123!', first_name='Rahul', last_name='Mehta', role='CLIENT', phone='9876500003')
            ClientProfile.objects.create(user=u)
            print("Created Client")
    except Exception as e:
        print(f"Error creating Client: {e}")

    print("Test users creation complete.")

if __name__ == '__main__':
    create_test_users()
