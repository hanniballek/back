import os
import sys
import json
import random
from datetime import datetime, timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from .routes.ai_recommendations import ai_bp
from .routes.products import products_bp
from .routes.virtual_tryons import virtual_bp
from .routes.monetization import monetization_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'fashion_ai_secret_key_2024'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(virtual_bp, url_prefix='/api')
app.register_blueprint(monetization_bp, url_prefix='/api')

# Mock data storage (in production, use a real database)
users_db = {}
products_db = []
recommendations_db = {}

# Initialize mock products data
def init_mock_data():
    global products_db
    products_db = [
        {
            "id": 1,
            "title": "فستان صيفي أنيق",
            "brand": "Zara",
            "price": 89,
            "original_price": 120,
            "discount": 26,
            "category": "فستان",
            "color": "أبيض",
            "style": "صيفي",
            "image": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=600&fit=crop",
            "description": "فستان صيفي أنيق مصنوع من القطن الطبيعي 100%",
            "tags": ["صيفي", "أنيق", "مناسبات", "قطن"],
            "sizes": ["XS", "S", "M", "L", "XL"],
            "rating": 4.5,
            "reviews": 234,
            "store_url": "https://www.zara.com/example"
        },
        {
            "id": 2,
            "title": "بدلة رجالية كلاسيكية",
            "brand": "Hugo Boss",
            "price": 299,
            "original_price": 399,
            "discount": 25,
            "category": "بدلة",
            "color": "أسود",
            "style": "كلاسيكي",
            "image": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=600&fit=crop",
            "description": "بدلة رجالية كلاسيكية مثالية للعمل والمناسبات الرسمية",
            "tags": ["رسمي", "كلاسيكي", "عمل"],
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "rating": 4.7,
            "reviews": 156,
            "store_url": "https://www.hugoboss.com/example"
        },
        {
            "id": 3,
            "title": "حذاء رياضي عصري",
            "brand": "Nike",
            "price": 120,
            "original_price": 150,
            "discount": 20,
            "category": "حذاء",
            "color": "أبيض",
            "style": "رياضي",
            "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400&h=600&fit=crop",
            "description": "حذاء رياضي مريح وعصري، مثالي للأنشطة اليومية والرياضة",
            "tags": ["رياضي", "مريح", "عصري"],
            "sizes": ["38", "39", "40", "41", "42", "43", "44"],
            "rating": 4.8,
            "reviews": 892,
            "store_url": "https://www.nike.com/example"
        }
    ]

# AI Recommendation Engine
class FashionAIEngine:
    @staticmethod
    def calculate_match_score(user_profile, product):
        """Calculate how well a product matches a user's profile"""
        score = 0
        
        # Style matching (40% weight)
        if user_profile.get('style') == product.get('style'):
            score += 40
        elif user_profile.get('style') in ['casual', 'trendy'] and product.get('style') in ['casual', 'trendy']:
            score += 30
        
        # Body type and product category matching (30% weight)
        body_type = user_profile.get('body_type', '')
        category = product.get('category', '')
        if body_type and category:
            # Simple matching logic (can be enhanced with ML)
            if body_type == 'hourglass' and category in ['فستان', 'تنورة']:
                score += 30
            elif body_type == 'rectangle' and category in ['جاكيت', 'بدلة']:
                score += 30
            else:
                score += 20
        
        # Budget matching (20% weight)
        budget = user_profile.get('budget', '')
        price = product.get('price', 0)
        if budget:
            if budget == '0-100' and price <= 100:
                score += 20
            elif budget == '100-300' and 100 <= price <= 300:
                score += 20
            elif budget == '300-500' and 300 <= price <= 500:
                score += 20
            elif budget == '500-1000' and 500 <= price <= 1000:
                score += 20
            elif budget == '1000+' and price >= 1000:
                score += 20
            else:
                score += 10
        
        # Age and style appropriateness (10% weight)
        age = user_profile.get('age', 25)
        if age:
            age = int(age)
            if 18 <= age <= 25 and product.get('style') in ['trendy', 'casual']:
                score += 10
            elif 26 <= age <= 35 and product.get('style') in ['casual', 'classic']:
                score += 10
            elif age >= 36 and product.get('style') in ['classic', 'formal']:
                score += 10
            else:
                score += 5
        
        return min(score, 100)  # Cap at 100%
    
    @staticmethod
    def get_recommendations(user_profile, limit=10):
        """Get personalized recommendations for a user"""
        recommendations = []
        
        for product in products_db:
            match_score = FashionAIEngine.calculate_match_score(user_profile, product)
            
            recommendation = {
                **product,
                "ai_match": match_score,
                "recommendation_reason": FashionAIEngine.get_recommendation_reason(user_profile, product, match_score)
            }
            recommendations.append(recommendation)
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x['ai_match'], reverse=True)
        return recommendations[:limit]
    
    @staticmethod
    def get_recommendation_reason(user_profile, product, match_score):
        """Generate explanation for why this product is recommended"""
        reasons = []
        
        if user_profile.get('style') == product.get('style'):
            reasons.append(f"يتماشى مع أسلوبك المفضل ({product.get('style')})")
        
        if match_score >= 90:
            reasons.append("مطابقة ممتازة لملفك الشخصي")
        elif match_score >= 80:
            reasons.append("مطابقة جيدة جداً لتفضيلاتك")
        elif match_score >= 70:
            reasons.append("مناسب لك بشكل جيد")
        
        budget = user_profile.get('budget', '')
        price = product.get('price', 0)
        if budget and budget != '1000+' and price <= 300:
            reasons.append("ضمن ميزانيتك المحددة")
        
        if not reasons:
            reasons.append("منتج عالي الجودة ومناسب للعديد من المناسبات")
        
        return " • ".join(reasons)

# Initialize data on startup
init_mock_data()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Fashion AI Backend API", 200

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Fashion AI Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

