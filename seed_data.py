import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, PanditProfile, ClientProfile
from apps.core.models import City, PujaCategory
from apps.bookings.models import Booking

def seed_db():
    print("Starting database seeding...")

    # Data lists for randomness
    first_names_pandit = ['Ram', 'Shyam', 'Govind', 'Hari', 'Murlidhar', 'Krishna', 'Gopal', 'Radha', 'Ramesh', 'Suresh', 'Dinesh', 'Mahesh', 'Srinivas', 'Narayan', 'Vishnu', 'Shiva', 'Keshava', 'Madhav', 'Mukund', 'Murari']
    last_names_pandit = ['Sharma', 'Shastri', 'Joshi', 'Trivedi', 'Chaturvedi', 'Vyas', 'Pandey', 'Mishra', 'Tiwari', 'Bhardwaj', 'Acharya', 'Upadhyay']
    
    first_names_client = ['Rahul', 'Amit', 'Vikram', 'Anil', 'Sunil', 'Karan', 'Arjun', 'Rajat', 'Sandeep', 'Vikas', 'Priya', 'Neha', 'Pooja', 'Anjali', 'Sneha']
    last_names_client = ['Mehta', 'Shah', 'Patel', 'Desai', 'Verma', 'Sharma', 'Singh', 'Kumar', 'Jain', 'Gupta', 'Reddy', 'Rao']

    cities_data = [
        ('Surat', 'surat', 'Gujarat'),
        ('Ahmedabad', 'ahmedabad', 'Gujarat'),
        ('Vadodara', 'vadodara', 'Gujarat'),
        ('Rajkot', 'rajkot', 'Gujarat'),
        ('Gandhinagar', 'gandhinagar', 'Gujarat')
    ]

    pujas_data = [
        ('Satyanarayana Puja', 'satyanarayana-puja', 'General'),
        ('Griha Pravesh', 'griha-pravesh', 'House'),
        ('Maha Mrityunjaya Jaap', 'maha-mrityunjaya', 'Health'),
        ('Navagraha Shanti', 'navagraha-shanti', 'Astrology'),
        (' विवाह (Marriage Ceremony)', 'marriage-ceremony', 'Wedding'),
        ('Namakaran', 'namakaran', 'Ceremony'),
        ('Rudrabhishek', 'rudrabhishek', 'Lord Shiva'),
        ('Vastu Shanti', 'vastu-shanti', 'House')
    ]

    addresses = [
        "102, Shanti Nagar, Ring Road",
        "Block C, Omkar Apartments",
        "Villa 45, Green Meadows",
        "Near Hanuman Temple, Main Branch street",
        "5th Floor, Silver Heights"
    ]

    # 1. Ensure Cities
    cities = []
    for name, slug, state in cities_data:
        c, _ = City.objects.get_or_create(name=name, slug=slug, defaults={'state': state, 'is_active': True})
        cities.append(c)
    print("Cities ensured.")

    # 2. Ensure Puja Categories
    pujas = []
    for name, slug, desc in pujas_data:
        p, _ = PujaCategory.objects.get_or_create(name=name, slug=slug, defaults={'description': desc, 'is_active': True})
        pujas.append(p)
    print("Puja Categories ensured.")

    # 3. Create 20 Clients (so they can make bookings)
    clients = list(User.objects.filter(role='CLIENT'))
    if len(clients) < 20:
        for i in range(20 - len(clients)):
            fn = random.choice(first_names_client)
            ln = random.choice(last_names_client)
            email = f"client{i}_{fn.lower()}{random.randint(100,999)}@test.com"
            try:
                user = User.objects.create_user(email=email, password='Password123!', first_name=fn, last_name=ln, role='CLIENT', phone=f"900{random.randint(1000000, 9999999)}")
                ClientProfile.objects.create(user=user)
                clients.append(user)
            except Exception:
                pass
    print(f"Clients ready ({len(clients)}).")

    # 4. Create 50 Pandits
    pandits = list(User.objects.filter(role='PANDIT'))
    pandits_profiles = list(PanditProfile.objects.all())
    
    needed_pandits = 50 - len(pandits)
    if needed_pandits > 0:
        for i in range(needed_pandits):
            fn = random.choice(first_names_pandit)
            ln = random.choice(last_names_pandit)
            email = f"pandit{i}_{fn.lower()}{ln.lower()}{random.randint(100,999)}@sd.com"
            phone = f"800{random.randint(1000000, 9999999)}"
            try:
                user = User.objects.create_user(email=email, password='Password123!', first_name=fn, last_name=ln, role='PANDIT', phone=phone)
                
                # Randomize pandit details
                city = random.choice(cities)
                exp = random.randint(2, 35)
                base_price = round(random.uniform(1100.0, 15000.0) / 100) * 100 # Nearest 100
                status = random.choices(['APPROVED', 'PENDING', 'REJECTED', 'SUSPENDED'], weights=[80, 10, 5, 5])[0]
                rating = round(random.uniform(3.5, 5.0), 1)
                total_b = random.randint(0, 100)
                
                profile = PanditProfile.objects.create(
                    user=user, city=city, experience_years=exp, base_price=base_price, 
                    status=status, average_rating=rating, total_bookings=total_b
                )
                
                # Add 2 to 5 random specializations
                spec_count = random.randint(2, len(pujas))
                profile.specializations.set(random.sample(pujas, spec_count))
                
                pandits_profiles.append(profile)
            except Exception as e:
                print(e)
    print(f"Pandits ready ({len(pandits_profiles)}).")

    # 5. Create 50 Bookings
    bookings = list(Booking.objects.all())
    needed_bookings = 50 - len(bookings)
    if needed_bookings > 0:
        # Only use approved pandits for bookings to be realistic
        approved_pandits = [p for p in pandits_profiles if p.status == 'APPROVED']
        
        for i in range(needed_bookings):
            client = random.choice(clients)
            pandit = random.choice(approved_pandits)
            
            # Select a random puja category from the pandit's specializations if possible
            pandit_specs = list(pandit.specializations.all())
            cat = random.choice(pandit_specs) if pandit_specs else random.choice(pujas)
            
            # Date between 30 days ago and 30 days in future
            days_offset = random.randint(-30, 30)
            target_date = datetime.now().date() + timedelta(days=days_offset)
            
            # Time between 6am and 6pm
            hour = random.randint(6, 18)
            time = datetime.strptime(f"{hour}:00", "%H:%M").time()
            
            addr = f"{random.choice(addresses)}, {pandit.city.name if pandit.city else 'Surat'}"
            notes = random.choice(["", "Please bring specific items for homam", "Need 2 assistants", ""])
            
            base_price = float(pandit.base_price)
            amount = base_price + random.choice([0, 500, 1100, -200]) # Some variations
            commission_pct = pandit.commission_percent if pandit.commission_percent else 20.0
            commission = round((amount * float(commission_pct)) / 100, 2)
            pandit_amount = amount - commission
            
            # Determine logic for status based on date
            # If past date, likely completed or cancelled. If future, pending/confirmed.
            if days_offset < 0:
                status = random.choices(['COMPLETED', 'CANCELLED'], weights=[85, 15])[0]
            else:
                status = random.choices(['PENDING', 'CONFIRMED', 'CANCELLED'], weights=[40, 50, 10])[0]
                
            payment = random.choice(['ONLINE', 'COD'])

            b = Booking.objects.create(
                client=client,
                pandit=pandit,
                puja_category=cat,
                puja_date=target_date,
                puja_time=time,
                address=addr,
                special_notes=notes,
                amount=amount,
                commission_amount=commission,
                pandit_amount=pandit_amount,
                status=status,
                payment_mode=payment
            )
            # Override created_at to be earlier than puja_date for realistic data
            b.created_at = datetime.now() - timedelta(days=abs(days_offset) + random.randint(1, 10))
            b.save()
            
    print(f"Bookings ready (Total: {Booking.objects.count()}).")

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_db()
