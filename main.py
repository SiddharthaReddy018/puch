import os
from fastapi import FastAPI
from supabase import create_client
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Gaali Guide AI", version="1.0.0")

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pydantic Models
class SearchRequest(BaseModel):
    service_type: str
    location: str
    user_contacts: Optional[List[str]] = []

class ReviewRequest(BaseModel):
    provider_id: str
    reviewer_phone: str
    punctuality: int
    skill_quality: int
    politeness: int
    pricing: int
    review_text: str

@app.get("/")
async def root():
    return {"message": "Gaali Guide AI is running!", "status": "healthy"}

@app.post("/search_services")
async def search_local_services(request: SearchRequest):
    """Search for local service providers."""
    try:
        # Search providers in database
        result = supabase.table('providers').select('*').eq(
            'service_type', request.service_type.lower()
        ).eq('location', request.location.lower()).order('avg_rating', desc=True).execute()
        
        if not result.data:
            return {"message": f"No {request.service_type} found in {request.location}"}
        
        # Format response
        providers = []
        for provider in result.data[:3]:  # Top 3 results
            
            # Get reviews for this provider
            reviews = supabase.table('reviews').select('*').eq(
                'provider_id', provider['id']
            ).execute()
            
            # Check for contact reviews
            contact_reviews = []
            if request.user_contacts:
                for review in reviews.data:
                    if review['reviewer_phone'] in request.user_contacts:
                        contact_reviews.append({
                            'reviewer_phone': review['reviewer_phone'],
                            'text': review['review_text'],
                            'ratings': review['ratings']
                        })
            
            # Calculate rating breakdown
            rating_breakdown = {'punctuality': [], 'skill_quality': [], 'politeness': [], 'pricing': []}
            for review in reviews.data:
                for key, value in review['ratings'].items():
                    if key in rating_breakdown:
                        rating_breakdown[key].append(value)
            
            # Calculate percentages
            strengths = {}
            for key, values in rating_breakdown.items():
                if values:
                    avg = sum(values) / len(values)
                    strengths[key] = round((avg / 5) * 100, 1)
            
            provider_info = {
                'id': provider['id'],
                'name': provider['name'],
                'service_type': provider['service_type'],
                'rating': provider['avg_rating'],
                'total_reviews': provider['total_reviews'],
                'location': provider['location'],
                'phone': provider['phone_number'],
                'has_contact_reviews': len(contact_reviews) > 0,
                'contact_reviews': contact_reviews[:2],  # Show max 2
                'strengths': strengths,
                'top_strength': max(strengths.items(), key=lambda x: x[1]) if strengths else None
            }
            providers.append(provider_info)
        
        return {
            'service_type': request.service_type,
            'location': request.location,
            'total_found': len(result.data),
            'providers': providers
        }
        
    except Exception as e:
        return {"error": str(e), "details": "Database connection or query failed"}

@app.post("/submit_review")
async def submit_review(request: ReviewRequest):
    """Submit a review for a provider."""
    try:
        ratings = {
            'punctuality': request.punctuality,
            'skill_quality': request.skill_quality,
            'politeness': request.politeness,
            'pricing': request.pricing
        }
        
        # Validate ratings (1-5 scale)
        for key, value in ratings.items():
            if not (1 <= value <= 5):
                return {"error": f"{key} rating must be between 1 and 5"}
        
        # Insert review
        review_data = {
            'provider_id': request.provider_id,
            'reviewer_phone': request.reviewer_phone,
            'ratings': ratings,
            'review_text': request.review_text
        }
        
        result = supabase.table('reviews').insert(review_data).execute()
        
        if not result.data:
            return {"error": "Failed to submit review"}
        
        # Update provider stats
        await update_provider_stats(request.provider_id)
        
        return {
            "message": "Review submitted successfully!",
            "review_id": result.data[0]['id'],
            "provider_id": request.provider_id
        }
        
    except Exception as e:
        return {"error": str(e), "details": "Failed to submit review"}

@app.get("/provider/{provider_id}")
async def get_provider_details(provider_id: str, contacts: str = ""):
    """Get detailed provider information."""
    try:
        user_contacts = contacts.split(",") if contacts else []
        
        # Get provider
        provider_result = supabase.table('providers').select('*').eq('id', provider_id).execute()
        if not provider_result.data:
            return {"error": "Provider not found"}
        
        provider = provider_result.data[0]
        
        # Get reviews
        reviews_result = supabase.table('reviews').select('*').eq('provider_id', provider_id).execute()
        reviews = reviews_result.data
        
        # Analyze reviews
        contact_reviews = []
        all_ratings = {'punctuality': [], 'skill_quality': [], 'politeness': [], 'pricing': []}
        recent_reviews = []
        
        for review in reviews:
            # Contact reviews
            if review['reviewer_phone'] in user_contacts:
                contact_reviews.append({
                    'text': review['review_text'],
                    'ratings': review['ratings'],
                    'phone': review['reviewer_phone'][-4:]  # Last 4 digits for privacy
                })
            
            # All ratings for analysis
            for key, value in review['ratings'].items():
                if key in all_ratings:
                    all_ratings[key].append(value)
            
            # Recent reviews
            recent_reviews.append({
                'text': review['review_text'],
                'ratings': review['ratings'],
                'timestamp': review['timestamp']
            })
        
        # Calculate strengths and concerns
        strengths = {}
        concerns = {}
        for key, values in all_ratings.items():
            if values:
                avg = sum(values) / len(values)
                percentage = round((avg / 5) * 100, 1)
                if percentage >= 80:
                    strengths[key.replace('_', ' ').title()] = percentage
                elif percentage <= 60:
                    concerns[key.replace('_', ' ').title()] = percentage
        
        return {
            'provider': {
                'id': provider['id'],
                'name': provider['name'],
                'service_type': provider['service_type'],
                'location': provider['location'],
                'phone': provider['phone_number'],
                'rating': provider['avg_rating'],
                'total_reviews': provider['total_reviews']
            },
            'contact_reviews': contact_reviews,
            'strengths': strengths,
            'concerns': concerns,
            'recent_reviews': recent_reviews[-3:],  # Last 3 reviews
            'summary': {
                'total_reviews': len(reviews),
                'has_contact_reviews': len(contact_reviews) > 0,
                'top_strength': max(strengths.items(), key=lambda x: x[1]) if strengths else None,
                'main_concern': max(concerns.items(), key=lambda x: x[1]) if concerns else None
            }
        }
        
    except Exception as e:
        return {"error": str(e), "details": "Failed to get provider details"}

@app.get("/services")
async def get_available_services():
    """Get list of available service types and locations."""
    try:
        # Get unique service types
        services_result = supabase.table('providers').select('service_type').execute()
        service_types = list(set([p['service_type'] for p in services_result.data]))
        
        # Get unique locations
        locations_result = supabase.table('providers').select('location').execute()
        locations = list(set([p['location'] for p in locations_result.data]))
        
        return {
            'service_types': service_types,
            'locations': locations,
            'total_providers': len(services_result.data)
        }
        
    except Exception as e:
        return {"error": str(e)}

async def update_provider_stats(provider_id: str):
    """Update provider's average rating and review count."""
    try:
        reviews = supabase.table('reviews').select('ratings').eq('provider_id', provider_id).execute()
        
        if reviews.data:
            total_ratings = []
            for review in reviews.data:
                avg_rating = sum(review['ratings'].values()) / len(review['ratings'])
                total_ratings.append(avg_rating)
            
            new_avg = sum(total_ratings) / len(total_ratings)
            
            supabase.table('providers').update({
                'avg_rating': round(new_avg, 1),
                'total_reviews': len(reviews.data)
            }).eq('id', provider_id).execute()
            
    except Exception as e:
        print(f"Error updating provider stats: {e}")

# WhatsApp-style formatted responses
@app.post("/whatsapp_search")
async def whatsapp_search_format(request: SearchRequest):
    """Search with WhatsApp-friendly response format."""
    try:
        search_result = await search_local_services(request)
        
        if 'error' in search_result:
            return {"whatsapp_message": f"❌ {search_result['error']}"}
        
        if 'message' in search_result:  # No providers found
            return {"whatsapp_message": f"🔍 {search_result['message']}\n\nWould you like to add a new {request.service_type}?"}
        
        # Format for WhatsApp
        message = f"🔍 **{request.service_type.title()} in {request.location.title()}**\n\n"
        
        for i, provider in enumerate(search_result['providers'], 1):
            message += f"**{i}. {provider['name']}** ⭐ {provider['rating']}/5\n"
            message += f"📍 {provider['location']} | 📞 {provider['phone']}\n"
            
            if provider['has_contact_reviews']:
                message += f"👥 **From your contacts:** {len(provider['contact_reviews'])} review(s)\n"
                message += f"💭 *\"{provider['contact_reviews'][0]['text'][:50]}...\"*\n"
            
            if provider['top_strength']:
                strength_name, strength_pct = provider['top_strength']
                message += f"✅ **Strong in:** {strength_name.replace('_', ' ').title()} ({strength_pct}%)\n"
            
            message += f"📱 **View Details:** /provider_{provider['id']}\n\n"
        
        return {"whatsapp_message": message}
        
    except Exception as e:
        return {"whatsapp_message": f"❌ Sorry, search failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Railway uses PORT env var
    uvicorn.run(app, host="0.0.0.0", port=port)
