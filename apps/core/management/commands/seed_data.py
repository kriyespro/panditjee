"""
apps/core/management/commands/seed_data.py
Seed initial cities, puja categories, and test users.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.management.base import BaseCommand
from apps.core.models import City, PujaCategory
from apps.users.models import User, PanditProfile, ClientProfile


CITIES = [
    {'name': 'Surat',      'state': 'Gujarat'},
    {'name': 'Ahmedabad',  'state': 'Gujarat'},
    {'name': 'Vadodara',   'state': 'Gujarat'},
]

PUJA_CATEGORIES = [
    {'name': 'Satyanarayan Puja',    'icon': '🙏', 'sort_order': 1},
    {'name': 'Havan & Yagya',        'icon': '🔥', 'sort_order': 2},
    {'name': 'Wedding Puja',         'icon': '💍', 'sort_order': 3},
    {'name': 'Griha Pravesh',        'icon': '🏠', 'sort_order': 4},
    {'name': 'Naming Ceremony',      'icon': '👶', 'sort_order': 5},
    {'name': 'Ganesh Puja',          'icon': '🐘', 'sort_order': 6},
    {'name': 'Diwali Puja',          'icon': '🪔', 'sort_order': 7},
    {'name': 'Antim Sanskar',        'icon': '⚰️', 'sort_order': 8},
    {'name': 'Navratri Puja',        'icon': '🌸', 'sort_order': 9},
    {'name': 'Katha & Pravachan',    'icon': '📿', 'sort_order': 10},
]


class Command(BaseCommand):
    help = 'Seed initial data: cities, puja categories, test users, test pandits'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding data...')

        # Cities
        for c in CITIES:
            obj, created = City.objects.get_or_create(name=c['name'], defaults={'state': c['state']})
            self.stdout.write(f"  {'✅ Created' if created else '⏭️  Exists'}: City — {obj.name}")

        # Puja categories
        for p in PUJA_CATEGORIES:
            obj, created = PujaCategory.objects.get_or_create(name=p['name'], defaults=p)
            self.stdout.write(f"  {'✅ Created' if created else '⏭️  Exists'}: Puja — {obj.name}")

        # Admin user
        if not User.objects.filter(email='admin@panditjee.com').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@panditjee.com',
                password='Admin@1234',
                first_name='Super',
                last_name='Admin',
                role=User.Role.ADMIN,
            )
            self.stdout.write('  ✅ Created: Admin — admin@panditjee.com / Admin@1234')
        else:
            self.stdout.write('  ⏭️  Exists: Admin user')

        # Test pandits
        surat = City.objects.get(name='Surat')
        ahmedabad = City.objects.get(name='Ahmedabad')
        vadodara = City.objects.get(name='Vadodara')
        satya = PujaCategory.objects.get(name='Satyanarayan Puja')
        wedding = PujaCategory.objects.get(name='Wedding Puja')
        havan = PujaCategory.objects.get(name='Havan & Yagya')

        pandits_data = [
            {'email': 'ramesh.sharma@panditjee.com', 'first': 'Ramesh', 'last': 'Sharma',
             'phone': '9876543210', 'city': surat, 'exp': 15, 'price': 1500, 'cats': [satya, wedding], 'status': 'APPROVED',
             'languages': 'Hindi, Gujarati, Sanskrit'},
            {'email': 'suresh.joshi@panditjee.com', 'first': 'Suresh', 'last': 'Joshi',
             'phone': '9876543211', 'city': ahmedabad, 'exp': 8, 'price': 1200, 'cats': [havan, satya], 'status': 'PENDING',
             'languages': 'Hindi, Gujarati'},
            {'email': 'dinesh.tiwari@panditjee.com', 'first': 'Dinesh', 'last': 'Tiwari',
             'phone': '9876543212', 'city': vadodara, 'exp': 20, 'price': 2000, 'cats': [wedding, havan], 'status': 'APPROVED',
             'languages': 'Hindi, Sanskrit, Marathi'},
        ]

        for pd in pandits_data:
            if not User.objects.filter(email=pd['email']).exists():
                u = User.objects.create_user(
                    username=pd['email'].split('@')[0],
                    email=pd['email'], password='Pandit@1234',
                    first_name=pd['first'], last_name=pd['last'],
                    phone=pd['phone'], role=User.Role.PANDIT
                )
                profile = PanditProfile.objects.create(
                    user=u, city=pd['city'],
                    experience_years=pd['exp'], base_price=pd['price'],
                    languages=pd['languages'],
                    status=pd['status'],
                    bio=f"Experienced pandit with {pd['exp']} years of vedic practice. Available for all ceremonies.",
                )
                profile.specializations.set(pd['cats'])
                self.stdout.write(f"  ✅ Created: Pandit — {pd['first']} {pd['last']} ({pd['status']})")
            else:
                self.stdout.write(f"  ⏭️  Exists: Pandit — {pd['email']}")

        # Test clients
        clients_data = [
            {'email': 'rahul.mehta@gmail.com', 'first': 'Rahul', 'last': 'Mehta', 'phone': '9123456780'},
            {'email': 'priya.shah@gmail.com',  'first': 'Priya', 'last': 'Shah',  'phone': '9123456781'},
        ]
        for cd in clients_data:
            if not User.objects.filter(email=cd['email']).exists():
                u = User.objects.create_user(
                    username=cd['email'].split('@')[0],
                    email=cd['email'], password='Client@1234',
                    first_name=cd['first'], last_name=cd['last'],
                    phone=cd['phone'], role=User.Role.CLIENT
                )
                ClientProfile.objects.create(user=u)
                self.stdout.write(f"  ✅ Created: Client — {cd['first']} {cd['last']}")
            else:
                self.stdout.write(f"  ⏭️  Exists: Client — {cd['email']}")

        self.stdout.write(self.style.SUCCESS('\n🚀 Seed complete! Check test_user.txt for credentials.'))
