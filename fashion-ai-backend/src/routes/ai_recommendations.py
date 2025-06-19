from flask import Blueprint, request, jsonify
import json
from datetime import datetime

ai_bp = Blueprint('ai_recommendations', __name__)

# Mock user profiles storage
user_profiles = {}

@ai_bp.route('/recommendations/<user_id>')
def get_user_recommendations(user_id):
    """Get personalized recommendations for a specific user"""
    try:
        # Get user profile
        user_profile = user_profiles.get(user_id, {})
        
        if not user_profile:
            # Return default recommendations if no profile exists
            from src.main import products_db
            recommendations = products_db[:5]
            for rec in recommendations:
                rec['ai_match'] = 85  # Default match score
                rec['recommendation_reason'] = "توصية عامة بناءً على الشعبية"
        else:
            # Get AI-powered recommendations
            from src.main import FashionAIEngine
            recommendations = FashionAIEngine.get_recommendations(user_profile, limit=10)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "total": len(recommendations),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_bp.route('/recommendations/feed')
def get_feed_recommendations():
    """Get general feed recommendations (for non-logged-in users)"""
    try:
        from src.main import products_db
        import random
        
        # Shuffle products and add mock engagement data
        feed_items = []
        for product in products_db:
            item = {
                **product,
                "likes": random.randint(500, 3000),
                "comments": random.randint(20, 200),
                "ai_match": random.randint(80, 95),
                "user": {
                    "name": random.choice(["سارة أحمد", "محمد علي", "ليلى حسن", "أحمد محمود", "فاطمة خالد"]),
                    "avatar": f"https://images.unsplash.com/photo-{random.choice(['1494790108755-2616b612b786', '1507003211169-0a1dd7228f2d', '1438761681033-6461ffad8d80'])}?w=40&h=40&fit=crop&crop=face"
                },
                "posted_at": "منذ ساعتين"
            }
            feed_items.append(item)
        
        # Shuffle for variety
        random.shuffle(feed_items)
        
        return jsonify({
            "status": "success",
            "feed": feed_items,
            "total": len(feed_items),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_bp.route('/analyze-style', methods=['POST'])
def analyze_user_style():
    """Analyze user's style preferences and update their profile"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_data = data.get('user_data', {})
        
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "user_id is required"
            }), 400
        
        # Store/update user profile
        user_profiles[user_id] = {
            **user_profiles.get(user_id, {}),
            **user_data,
            "last_updated": datetime.now().isoformat()
        }
        
        # Generate style analysis
        analysis = generate_style_analysis(user_data)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "analysis": analysis,
            "profile_updated": True,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ai_bp.route('/smart-search', methods=['POST'])
def smart_search():
    """AI-powered smart search for fashion items"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = data.get('user_id')
        filters = data.get('filters', {})
        
        from src.main import products_db, FashionAIEngine
        
        # Get user profile for personalization
        user_profile = user_profiles.get(user_id, {}) if user_id else {}
        
        # Filter products based on search criteria
        results = []
        for product in products_db:
            # Text search
            if query and query.lower() not in product.get('title', '').lower() and \
               query.lower() not in ' '.join(product.get('tags', [])).lower():
                continue
            
            # Apply filters
            if filters.get('category') and product.get('category') != filters['category']:
                continue
            if filters.get('color') and product.get('color') != filters['color']:
                continue
            if filters.get('style') and product.get('style') != filters['style']:
                continue
            if filters.get('price_range'):
                price = product.get('price', 0)
                price_range = filters['price_range']
                if price_range == '0-50' and price > 50:
                    continue
                elif price_range == '50-100' and (price < 50 or price > 100):
                    continue
                elif price_range == '100-200' and (price < 100 or price > 200):
                    continue
                elif price_range == '200-500' and (price < 200 or price > 500):
                    continue
                elif price_range == '500+' and price < 500:
                    continue
            
            # Calculate AI match score if user profile exists
            if user_profile:
                ai_match = FashionAIEngine.calculate_match_score(user_profile, product)
                product_result = {**product, "ai_match": ai_match}
            else:
                product_result = {**product, "ai_match": 85}
            
            results.append(product_result)
        
        # Sort by AI match score if user profile exists, otherwise by rating
        if user_profile:
            results.sort(key=lambda x: x.get('ai_match', 0), reverse=True)
        else:
            results.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return jsonify({
            "status": "success",
            "query": query,
            "filters": filters,
            "results": results,
            "total": len(results),
            "personalized": bool(user_profile),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def generate_style_analysis(user_data):
    """Generate AI-powered style analysis for a user"""
    analysis = {
        "style_profile": "متوازن",
        "recommendations": [],
        "color_palette": [],
        "body_type_advice": "",
        "confidence_score": 85
    }
    
    # Analyze based on user data
    age = user_data.get('age')
    if age:
        age = int(age)
        if 18 <= age <= 25:
            analysis["style_profile"] = "عصري وجريء"
            analysis["recommendations"].append("جرب الألوان الزاهية والقطع العصرية")
        elif 26 <= age <= 35:
            analysis["style_profile"] = "أنيق ومتوازن"
            analysis["recommendations"].append("امزج بين الكلاسيكي والعصري")
        else:
            analysis["style_profile"] = "كلاسيكي وأنيق"
            analysis["recommendations"].append("ركز على القطع الكلاسيكية عالية الجودة")
    
    # Body type advice
    body_type = user_data.get('body_type')
    if body_type == 'hourglass':
        analysis["body_type_advice"] = "جسمك متوازن، يمكنك ارتداء معظم الأساليب بثقة"
        analysis["recommendations"].append("الفساتين الضيقة والتنانير تبرز جمال قوامك")
    elif body_type == 'pear':
        analysis["body_type_advice"] = "ركز على إبراز الجزء العلوي من جسمك"
        analysis["recommendations"].append("اختر قمصان بألوان فاتحة وتنانير داكنة")
    elif body_type == 'apple':
        analysis["body_type_advice"] = "ركز على إطالة القوام وإبراز الساقين"
        analysis["recommendations"].append("الفساتين الإمبراطورية والقمصان الطويلة مناسبة لك")
    
    # Color recommendations based on skin tone
    skin_tone = user_data.get('skin_tone')
    if skin_tone == 'fair':
        analysis["color_palette"] = ["الأزرق", "الوردي", "البنفسجي", "الأخضر الفاتح"]
    elif skin_tone == 'medium':
        analysis["color_palette"] = ["الأحمر", "البرتقالي", "الأصفر", "الأخضر"]
    elif skin_tone == 'olive':
        analysis["color_palette"] = ["الأخضر الزيتوني", "البني", "الذهبي", "الأحمر الداكن"]
    elif skin_tone == 'dark':
        analysis["color_palette"] = ["الأبيض", "الأصفر الزاهي", "الوردي الفاقع", "الفيروزي"]
    
    return analysis

