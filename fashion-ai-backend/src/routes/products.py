from flask import Blueprint, request, jsonify
import json
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def get_all_products():
    """Get all products with optional filtering"""
    try:
        from src.main import products_db
        
        # Get query parameters
        category = request.args.get('category')
        brand = request.args.get('brand')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        style = request.args.get('style')
        color = request.args.get('color')
        
        # Filter products
        filtered_products = products_db.copy()
        
        if category:
            filtered_products = [p for p in filtered_products if p.get('category') == category]
        if brand:
            filtered_products = [p for p in filtered_products if p.get('brand') == brand]
        if min_price:
            filtered_products = [p for p in filtered_products if p.get('price', 0) >= min_price]
        if max_price:
            filtered_products = [p for p in filtered_products if p.get('price', 0) <= max_price]
        if style:
            filtered_products = [p for p in filtered_products if p.get('style') == style]
        if color:
            filtered_products = [p for p in filtered_products if p.get('color') == color]
        
        return jsonify({
            "status": "success",
            "products": filtered_products,
            "total": len(filtered_products),
            "filters_applied": {
                "category": category,
                "brand": brand,
                "min_price": min_price,
                "max_price": max_price,
                "style": style,
                "color": color
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@products_bp.route('/products/<int:product_id>')
def get_product_details(product_id):
    """Get detailed information about a specific product"""
    try:
        from src.main import products_db
        
        # Find product by ID
        product = next((p for p in products_db if p['id'] == product_id), None)
        
        if not product:
            return jsonify({
                "status": "error",
                "message": "Product not found"
            }), 404
        
        # Add additional details for product page
        detailed_product = {
            **product,
            "features": [
                "مصنوع من مواد عالية الجودة",
                "قابل للغسل في الغسالة",
                "متوفر بعدة ألوان ومقاسات",
                "تصميم مقاوم للتجعد",
                "مناسب لجميع المواسم"
            ],
            "care_instructions": [
                "اغسل بالماء البارد",
                "لا تستخدم المبيض",
                "اتركه ليجف في الهواء",
                "كوي على درجة حرارة منخفضة"
            ],
            "shipping_info": {
                "free_shipping": True,
                "delivery_time": "2-5 أيام عمل",
                "return_policy": "إرجاع مجاني خلال 30 يوم"
            },
            "seller_info": {
                "name": f"{product['brand']} Official Store",
                "rating": 4.8,
                "total_reviews": 15420,
                "verified": True
            }
        }
        
        return jsonify({
            "status": "success",
            "product": detailed_product,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@products_bp.route('/products/similar/<int:product_id>')
def get_similar_products(product_id):
    """Get products similar to the specified product"""
    try:
        from src.main import products_db
        
        # Find the reference product
        reference_product = next((p for p in products_db if p['id'] == product_id), None)
        
        if not reference_product:
            return jsonify({
                "status": "error",
                "message": "Reference product not found"
            }), 404
        
        # Find similar products based on category, style, or brand
        similar_products = []
        for product in products_db:
            if product['id'] == product_id:
                continue
            
            similarity_score = 0
            
            # Same category
            if product.get('category') == reference_product.get('category'):
                similarity_score += 40
            
            # Same style
            if product.get('style') == reference_product.get('style'):
                similarity_score += 30
            
            # Same brand
            if product.get('brand') == reference_product.get('brand'):
                similarity_score += 20
            
            # Similar price range (within 50% difference)
            ref_price = reference_product.get('price', 0)
            prod_price = product.get('price', 0)
            if ref_price > 0 and abs(prod_price - ref_price) / ref_price <= 0.5:
                similarity_score += 10
            
            if similarity_score >= 30:  # Minimum threshold for similarity
                similar_products.append({
                    **product,
                    "similarity_score": similarity_score
                })
        
        # Sort by similarity score
        similar_products.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({
            "status": "success",
            "reference_product_id": product_id,
            "similar_products": similar_products[:6],  # Return top 6 similar products
            "total": len(similar_products),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@products_bp.route('/products/trending')
def get_trending_products():
    """Get trending/popular products"""
    try:
        from src.main import products_db
        import random
        
        # Add trending metrics to products
        trending_products = []
        for product in products_db:
            trending_product = {
                **product,
                "trending_score": random.randint(70, 100),
                "views_today": random.randint(500, 2000),
                "purchases_today": random.randint(10, 50),
                "trending_reason": random.choice([
                    "الأكثر مبيعاً اليوم",
                    "ترند جديد في الموضة",
                    "مفضل المشاهير",
                    "عرض محدود الوقت"
                ])
            }
            trending_products.append(trending_product)
        
        # Sort by trending score
        trending_products.sort(key=lambda x: x['trending_score'], reverse=True)
        
        return jsonify({
            "status": "success",
            "trending_products": trending_products,
            "total": len(trending_products),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@products_bp.route('/products/categories')
def get_product_categories():
    """Get all available product categories"""
    try:
        categories = [
            {"id": "dress", "name": "فساتين", "count": 150},
            {"id": "suit", "name": "بدل", "count": 89},
            {"id": "shoes", "name": "أحذية", "count": 234},
            {"id": "bags", "name": "حقائب", "count": 67},
            {"id": "accessories", "name": "إكسسوارات", "count": 123},
            {"id": "casual", "name": "ملابس كاجوال", "count": 198},
            {"id": "formal", "name": "ملابس رسمية", "count": 76},
            {"id": "sportswear", "name": "ملابس رياضية", "count": 145}
        ]
        
        return jsonify({
            "status": "success",
            "categories": categories,
            "total": len(categories),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@products_bp.route('/products/brands')
def get_product_brands():
    """Get all available brands"""
    try:
        brands = [
            {"id": "zara", "name": "Zara", "count": 45},
            {"id": "hm", "name": "H&M", "count": 38},
            {"id": "nike", "name": "Nike", "count": 67},
            {"id": "adidas", "name": "Adidas", "count": 52},
            {"id": "hugo-boss", "name": "Hugo Boss", "count": 23},
            {"id": "gucci", "name": "Gucci", "count": 15},
            {"id": "prada", "name": "Prada", "count": 12},
            {"id": "versace", "name": "Versace", "count": 8}
        ]
        
        return jsonify({
            "status": "success",
            "brands": brands,
            "total": len(brands),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

