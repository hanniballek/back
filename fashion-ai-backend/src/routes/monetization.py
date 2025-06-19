from flask import Blueprint, request, jsonify
import json
from datetime import datetime, timedelta
import random
import uuid

monetization_bp = Blueprint('monetization', __name__)

# Mock storage for earnings and referrals
user_earnings = {}
referral_codes = {}
affiliate_links = {}
commission_rates = {
    'referral_signup': 5.0,  # $5 for each successful referral signup
    'purchase_commission': 0.05,  # 5% commission on purchases
    'virtual_tryon_premium': 2.0,  # $2 for each premium virtual try-on
    'ai_consultation': 10.0  # $10 for each AI style consultation
}

@monetization_bp.route('/earnings/<user_id>')
def get_user_earnings(user_id):
    """Get earnings summary for a user"""
    try:
        earnings = user_earnings.get(user_id, {
            'total_earnings': 0,
            'pending_earnings': 0,
            'paid_earnings': 0,
            'referral_count': 0,
            'commission_earnings': 0,
            'bonus_earnings': 0,
            'transactions': []
        })
        
        # Generate mock recent transactions if none exist
        if not earnings.get('transactions'):
            earnings['transactions'] = generate_mock_transactions(user_id)
            earnings['total_earnings'] = sum(t['amount'] for t in earnings['transactions'])
            earnings['pending_earnings'] = sum(t['amount'] for t in earnings['transactions'] if t['status'] == 'pending')
            earnings['paid_earnings'] = sum(t['amount'] for t in earnings['transactions'] if t['status'] == 'paid')
            earnings['referral_count'] = len([t for t in earnings['transactions'] if t['type'] == 'referral'])
            earnings['commission_earnings'] = sum(t['amount'] for t in earnings['transactions'] if t['type'] == 'commission')
            earnings['bonus_earnings'] = sum(t['amount'] for t in earnings['transactions'] if t['type'] == 'bonus')
            
            user_earnings[user_id] = earnings
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "earnings": earnings,
            "commission_rates": commission_rates,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monetization_bp.route('/referral-code/<user_id>')
def get_referral_code(user_id):
    """Get or generate referral code for a user"""
    try:
        if user_id not in referral_codes:
            # Generate unique referral code
            code = f"FASHION{user_id.upper()[:3]}{random.randint(100, 999)}"
            referral_codes[user_id] = {
                'code': code,
                'created_at': datetime.now().isoformat(),
                'uses': 0,
                'successful_referrals': 0
            }
        
        referral_data = referral_codes[user_id]
        referral_link = f"https://fashion-ai.com/register?ref={referral_data['code']}"
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "referral_code": referral_data['code'],
            "referral_link": referral_link,
            "stats": {
                "total_uses": referral_data['uses'],
                "successful_referrals": referral_data['successful_referrals'],
                "earnings_per_referral": commission_rates['referral_signup']
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monetization_bp.route('/affiliate-links/<user_id>')
def get_affiliate_links(user_id):
    """Get affiliate links for products"""
    try:
        # Generate affiliate links for popular products
        products = [
            {"id": 1, "name": "فستان صيفي أنيق", "brand": "Zara", "commission": "5%"},
            {"id": 2, "name": "بدلة رجالية كلاسيكية", "brand": "Hugo Boss", "commission": "7%"},
            {"id": 3, "name": "حذاء رياضي عصري", "brand": "Nike", "commission": "4%"},
            {"id": 4, "name": "حقيبة يد أنيقة", "brand": "Michael Kors", "commission": "6%"},
            {"id": 5, "name": "ساعة ذكية", "brand": "Apple", "commission": "3%"}
        ]
        
        affiliate_links_list = []
        for product in products:
            link_id = str(uuid.uuid4())[:8]
            affiliate_link = f"https://fashion-ai.com/product/{product['id']}?aff={user_id}&link={link_id}"
            
            affiliate_links_list.append({
                "product_id": product['id'],
                "product_name": product['name'],
                "brand": product['brand'],
                "commission_rate": product['commission'],
                "affiliate_link": affiliate_link,
                "clicks": random.randint(0, 50),
                "conversions": random.randint(0, 5),
                "earnings": round(random.uniform(0, 25), 2)
            })
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "affiliate_links": affiliate_links_list,
            "total_links": len(affiliate_links_list),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monetization_bp.route('/withdraw-request', methods=['POST'])
def request_withdrawal():
    """Request earnings withdrawal"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        payment_details = data.get('payment_details', {})
        
        if not all([user_id, amount, payment_method]):
            return jsonify({
                "status": "error",
                "message": "user_id, amount, and payment_method are required"
            }), 400
        
        # Check if user has sufficient earnings
        earnings = user_earnings.get(user_id, {})
        available_balance = earnings.get('total_earnings', 0) - earnings.get('paid_earnings', 0)
        
        if amount > available_balance:
            return jsonify({
                "status": "error",
                "message": "Insufficient balance for withdrawal"
            }), 400
        
        # Create withdrawal request
        withdrawal_id = str(uuid.uuid4())
        withdrawal_request = {
            "withdrawal_id": withdrawal_id,
            "user_id": user_id,
            "amount": amount,
            "payment_method": payment_method,
            "payment_details": payment_details,
            "status": "pending",
            "requested_at": datetime.now().isoformat(),
            "processing_time": "3-5 business days"
        }
        
        # Update user earnings
        if user_id not in user_earnings:
            user_earnings[user_id] = {'transactions': []}
        
        user_earnings[user_id]['transactions'].append({
            "id": withdrawal_id,
            "type": "withdrawal",
            "amount": -amount,
            "description": f"Withdrawal request - {payment_method}",
            "status": "pending",
            "date": datetime.now().isoformat()
        })
        
        return jsonify({
            "status": "success",
            "withdrawal_request": withdrawal_request,
            "message": "Withdrawal request submitted successfully",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monetization_bp.route('/earnings-analytics/<user_id>')
def get_earnings_analytics(user_id):
    """Get detailed earnings analytics"""
    try:
        # Generate mock analytics data
        analytics = {
            "daily_earnings": generate_daily_earnings(),
            "earnings_by_source": {
                "referrals": round(random.uniform(20, 80), 2),
                "commissions": round(random.uniform(30, 120), 2),
                "bonuses": round(random.uniform(5, 25), 2),
                "premium_features": round(random.uniform(10, 40), 2)
            },
            "top_performing_links": [
                {"product": "فستان صيفي أنيق", "clicks": 45, "conversions": 8, "earnings": 23.50},
                {"product": "حذاء رياضي عصري", "clicks": 38, "conversions": 6, "earnings": 18.20},
                {"product": "حقيبة يد أنيقة", "clicks": 29, "conversions": 4, "earnings": 15.80}
            ],
            "referral_performance": {
                "total_referrals": random.randint(5, 25),
                "successful_conversions": random.randint(3, 15),
                "conversion_rate": round(random.uniform(0.6, 0.8), 2),
                "average_earnings_per_referral": commission_rates['referral_signup']
            },
            "monthly_trends": generate_monthly_trends()
        }
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@monetization_bp.route('/leaderboard')
def get_earnings_leaderboard():
    """Get top earners leaderboard"""
    try:
        # Generate mock leaderboard
        leaderboard = []
        for i in range(10):
            leaderboard.append({
                "rank": i + 1,
                "user_name": f"مستخدم {i + 1}",
                "total_earnings": round(random.uniform(100, 1000), 2),
                "referrals": random.randint(5, 50),
                "badge": get_user_badge(random.uniform(100, 1000))
            })
        
        # Sort by earnings
        leaderboard.sort(key=lambda x: x['total_earnings'], reverse=True)
        
        # Update ranks
        for i, user in enumerate(leaderboard):
            user['rank'] = i + 1
        
        return jsonify({
            "status": "success",
            "leaderboard": leaderboard,
            "total_users": len(leaderboard),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def generate_mock_transactions(user_id):
    """Generate mock transaction history"""
    transactions = []
    
    # Generate referral earnings
    for i in range(random.randint(2, 8)):
        transactions.append({
            "id": str(uuid.uuid4())[:8],
            "type": "referral",
            "amount": commission_rates['referral_signup'],
            "description": f"إحالة مستخدم جديد - مستخدم {i + 1}",
            "status": random.choice(["paid", "pending"]),
            "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    # Generate commission earnings
    for i in range(random.randint(3, 10)):
        amount = round(random.uniform(2, 25), 2)
        transactions.append({
            "id": str(uuid.uuid4())[:8],
            "type": "commission",
            "amount": amount,
            "description": f"عمولة شراء - منتج {i + 1}",
            "status": random.choice(["paid", "pending"]),
            "date": (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat()
        })
    
    # Generate bonus earnings
    for i in range(random.randint(1, 3)):
        amount = round(random.uniform(5, 15), 2)
        transactions.append({
            "id": str(uuid.uuid4())[:8],
            "type": "bonus",
            "amount": amount,
            "description": f"مكافأة إنجاز - {random.choice(['هدف شهري', 'مستخدم مميز', 'تحدي خاص'])}",
            "status": "paid",
            "date": (datetime.now() - timedelta(days=random.randint(1, 15))).isoformat()
        })
    
    return sorted(transactions, key=lambda x: x['date'], reverse=True)

def generate_daily_earnings():
    """Generate daily earnings for the last 30 days"""
    daily_earnings = []
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        earnings = round(random.uniform(0, 15), 2)
        daily_earnings.append({
            "date": date.strftime("%Y-%m-%d"),
            "earnings": earnings
        })
    return list(reversed(daily_earnings))

def generate_monthly_trends():
    """Generate monthly earnings trends"""
    months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"]
    trends = []
    for month in months:
        trends.append({
            "month": month,
            "earnings": round(random.uniform(50, 200), 2),
            "referrals": random.randint(2, 15),
            "commissions": round(random.uniform(20, 100), 2)
        })
    return trends

def get_user_badge(earnings):
    """Get user badge based on earnings"""
    if earnings >= 500:
        return "نجم ذهبي"
    elif earnings >= 200:
        return "نجم فضي"
    elif earnings >= 50:
        return "نجم برونزي"
    else:
        return "مبتدئ"

