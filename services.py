from supabase import Client
from typing import List, Dict, Any
import uuid
from datetime import datetime

class ServiceManager:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def search_providers(self, service_type: str, location: str) -> List[Dict]:
        """Search for providers by service type and location."""
        result = self.supabase.table('providers').select('*').eq(
            'service_type', service_type.lower()
        ).eq('location', location.lower()).order('avg_rating', desc=True).execute()
        
        return result.data
    
    async def get_provider_summary(self, provider_id: str, user_contacts: List[str]) -> Dict:
        """Get provider summary with AI insights and contact highlights."""
        # Get provider info
        provider = self.supabase.table('providers').select('*').eq('id', provider_id).execute()
        if not provider.data:
            raise Exception("Provider not found")
        
        provider = provider.data[0]
        
        # Get reviews
        reviews = self.supabase.table('reviews').select('*').eq('provider_id', provider_id).execute()
        
        # Get AI insights
        insights = self.supabase.table('ai_insights').select('*').eq('provider_id', provider_id).execute()
        
        # Find reviews from user contacts
        contact_reviews = []
        if user_contacts and reviews.data:
            for review in reviews.data:
                if review['reviewer_phone'] in user_contacts:
                    contact_reviews.append({
                        'reviewer_name': self._get_contact_name(review['reviewer_phone'], user_contacts),
                        'text': review['review_text'],
                        'ratings': review['ratings']
                    })
        
        # Compile summary
        summary = {
            'id': provider['id'],
            'name': provider['name'],
            'service_type': provider['service_type'],
            'location': provider['location'],
            'rating': provider['avg_rating'],
            'total_reviews': provider['total_reviews'],
            'contact_reviews': contact_reviews,
            'top_praise': insights.data[0]['top_praise'] if insights.data else {},
            'concerns': insights.data[0]['top_concerns'] if insights.data else {},
            'emerging_mentions': insights.data[0]['emerging_mentions'] if insights.data else {}
        }
        
        return summary
    
    async def add_review(self, provider_id: str, reviewer_phone: str, ratings: Dict, review_text: str) -> str:
        """Add a new review and update provider stats."""
        review_data = {
            'provider_id': provider_id,
            'reviewer_phone': reviewer_phone,
            'ratings': ratings,
            'review_text': review_text
        }
        
        # Insert review
        result = self.supabase.table('reviews').insert(review_data).execute()
        
        # Update provider stats
        await self._update_provider_stats(provider_id)
        
        return result.data[0]['id']
    
    async def _update_provider_stats(self, provider_id: str):
        """Update provider's average rating and review count."""
        reviews = self.supabase.table('reviews').select('ratings').eq('provider_id', provider_id).execute()
        
        if reviews.data:
            total_ratings = []
            for review in reviews.data:
                avg_rating = sum(review['ratings'].values()) / len(review['ratings'])
                total_ratings.append(avg_rating)
            
            new_avg = sum(total_ratings) / len(total_ratings)
            
            self.supabase.table('providers').update({
                'avg_rating': round(new_avg, 1),
                'total_reviews': len(reviews.data)
            }).eq('id', provider_id).execute()
    
    def _get_contact_name(self, phone: str, contacts: List[str]) -> str:
        """Get contact name from phone number (placeholder - would integrate with WhatsApp)."""
        return f"Contact {phone[-4:]}"  # Show last 4 digits for privacy
