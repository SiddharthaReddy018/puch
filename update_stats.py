from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def update_all_provider_stats():
    """Update stats for all providers based on their reviews."""
    
    # Get all providers
    providers = supabase.table('providers').select('id').execute()
    
    for provider in providers.data:
        provider_id = provider['id']
        
        # Get reviews for this provider
        reviews = supabase.table('reviews').select('ratings').eq('provider_id', provider_id).execute()
        
        if reviews.data:
            # Calculate average rating
            total_ratings = []
            for review in reviews.data:
                avg_rating = sum(review['ratings'].values()) / len(review['ratings'])
                total_ratings.append(avg_rating)
            
            new_avg = sum(total_ratings) / len(total_ratings)
            
            # Update provider
            supabase.table('providers').update({
                'avg_rating': round(new_avg, 1),
                'total_reviews': len(reviews.data)
            }).eq('id', provider_id).execute()
            
            print(f"Updated provider {provider_id}: {round(new_avg, 1)}/5 ({len(reviews.data)} reviews)")

if __name__ == "__main__":
    update_all_provider_stats()
    print("✅ All provider stats updated!")
