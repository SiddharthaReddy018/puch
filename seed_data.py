from supabase import create_client
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def seed_data():
    """Add dummy data to database."""
    
    # Sample providers data
    providers = [
        # Electricians in Mumbai
        {'name': 'Rajesh Kumar', 'service_type': 'electrician', 'location': 'mumbai', 'phone_number': '+919876543210'},
        {'name': 'Amit Sharma', 'service_type': 'electrician', 'location': 'mumbai', 'phone_number': '+919876543211'},
        {'name': 'Suresh Yadav', 'service_type': 'electrician', 'location': 'mumbai', 'phone_number': '+919876543212'},
        
        # Plumbers in Mumbai  
        {'name': 'Kiran Singh', 'service_type': 'plumber', 'location': 'mumbai', 'phone_number': '+919876543213'},
        {'name': 'Deepak Gupta', 'service_type': 'plumber', 'location': 'mumbai', 'phone_number': '+919876543214'},
        {'name': 'Manoj Tiwari', 'service_type': 'plumber', 'location': 'mumbai', 'phone_number': '+919876543215'},
        
        # Cleaning services in Mumbai
        {'name': 'Kavita Devi', 'service_type': 'cleaning', 'location': 'mumbai', 'phone_number': '+919876543216'},
        {'name': 'Sunita Kumari', 'service_type': 'cleaning', 'location': 'mumbai', 'phone_number': '+919876543217'},
        {'name': 'Geeta Sharma', 'service_type': 'cleaning', 'location': 'mumbai', 'phone_number': '+919876543218'},
    ]
    
    # Insert providers and create reviews
    for provider_data in providers:
        print(f"Creating provider: {provider_data['name']}")
        
        # Insert provider
        result = supabase.table('providers').insert(provider_data).execute()
        provider_id = result.data[0]['id']
        
        # Create sample reviews
        create_reviews(provider_id, provider_data['service_type'])
    
    print("✅ All dummy data created successfully!")

def create_reviews(provider_id, service_type):
    """Create sample reviews for a provider."""
    
    # Sample review texts by service type
    review_templates = {
        'electrician': [
            "Very punctual and skilled electrician. Fixed all wiring issues perfectly!",
            "Great work! Professional behavior and reasonable pricing.",
            "Came on time, very polite, and excellent quality work.",
            "Skilled electrician but slightly expensive. Worth it for the quality.",
            "Amazing service! Cleaned up after work and explained everything."
        ],
        'plumber': [
            "Excellent plumber! Fixed the leak permanently and fair pricing.",
            "Very skilled and punctual. Highly recommend for any plumbing work.",
            "Good work but could improve on cleanliness after completing job.",
            "Professional service and polite behavior. Will call again.",
            "Quick and efficient work. Solved the problem in no time."
        ],
        'cleaning': [
            "Best cleaning service! Very thorough and trustworthy.",
            "Always punctual and does amazing work. House looks brand new!",
            "Good cleaning but sometimes rushes. Overall satisfied with service.",
            "Excellent work and very reasonable pricing. Highly recommended!",
            "Professional and reliable. Uses good quality cleaning supplies."
        ]
    }
    
    # Sample reviewer phone numbers
    sample_phones = [
        '+919123456789', '+919123456790', '+919123456791',
        '+919123456792', '+919123456793', '+919123456794',
        '+919123456795', '+919123456796', '+919123456797'
    ]
    
    templates = review_templates.get(service_type, review_templates['electrician'])
    
    # Create 8-12 reviews per provider
    num_reviews = random.randint(8, 12)
    
    for i in range(num_reviews):
        review_data = {
            'provider_id': provider_id,
            'reviewer_phone': random.choice(sample_phones),
            'ratings': {
                'punctuality': random.randint(3, 5),
                'skill_quality': random.randint(4, 5),
                'politeness': random.randint(3, 5),
                'pricing': random.randint(3, 5)
            },
            'review_text': random.choice(templates)
        }
        
        supabase.table('reviews').insert(review_data).execute()

if __name__ == "__main__":
    seed_data()
