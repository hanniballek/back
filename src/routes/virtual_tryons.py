from flask import Blueprint, request, jsonify
import json
import base64
import io
from datetime import datetime
import random

virtual_bp = Blueprint('virtual_tryons', __name__)

# Mock storage for virtual try-on sessions
virtual_sessions = {}

@virtual_bp.route('/virtual-tryon/create', methods=['POST'])
def create_virtual_tryon():
    """Create a new virtual try-on session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        user_image = data.get('user_image')  # Base64 encoded image
        
        if not all([user_id, product_id, user_image]):
            return jsonify({
                "status": "error",
                "message": "user_id, product_id, and user_image are required"
            }), 400
        
        # Generate session ID
        session_id = f"vto_{user_id}_{product_id}_{int(datetime.now().timestamp())}"
        
        # Store session data
        virtual_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "product_id": product_id,
            "user_image": user_image,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "message": "Virtual try-on session created successfully",
            "estimated_time": "30-60 seconds",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@virtual_bp.route('/virtual-tryon/status/<session_id>')
def get_tryon_status(session_id):
    """Get the status of a virtual try-on session"""
    try:
        session = virtual_sessions.get(session_id)
        
        if not session:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Simulate processing progress
        if session['status'] == 'processing':
            # Simulate progress based on time elapsed
            created_time = datetime.fromisoformat(session['created_at'])
            elapsed_seconds = (datetime.now() - created_time).total_seconds()
            
            if elapsed_seconds < 10:
                session['progress'] = min(30, elapsed_seconds * 3)
                session['current_step'] = "تحليل الصورة الشخصية..."
            elif elapsed_seconds < 20:
                session['progress'] = min(60, 30 + (elapsed_seconds - 10) * 3)
                session['current_step'] = "تحليل المنتج وخصائصه..."
            elif elapsed_seconds < 30:
                session['progress'] = min(90, 60 + (elapsed_seconds - 20) * 3)
                session['current_step'] = "تطبيق المنتج على الصورة..."
            else:
                session['progress'] = 100
                session['status'] = 'completed'
                session['current_step'] = "تم الانتهاء!"
                
                # Generate mock result
                session['result'] = {
                    "result_image": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=600&fit=crop",
                    "confidence_score": random.randint(85, 98),
                    "ai_feedback": generate_ai_feedback(session['product_id']),
                    "fit_analysis": {
                        "overall_fit": "ممتاز",
                        "color_match": "مناسب جداً",
                        "style_compatibility": "متوافق مع أسلوبك",
                        "size_recommendation": "المقاس M مناسب لك"
                    }
                }
        
        return jsonify({
            "status": "success",
            "session": session,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@virtual_bp.route('/virtual-tryon/result/<session_id>')
def get_tryon_result(session_id):
    """Get the final result of a virtual try-on session"""
    try:
        session = virtual_sessions.get(session_id)
        
        if not session:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        if session['status'] != 'completed':
            return jsonify({
                "status": "error",
                "message": "Session not completed yet"
            }), 400
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "result": session.get('result'),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@virtual_bp.route('/virtual-tryon/feedback', methods=['POST'])
def submit_tryon_feedback():
    """Submit feedback for a virtual try-on result"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        rating = data.get('rating')  # 1-5 stars
        feedback_text = data.get('feedback_text', '')
        
        if not session_id or not rating:
            return jsonify({
                "status": "error",
                "message": "session_id and rating are required"
            }), 400
        
        session = virtual_sessions.get(session_id)
        if not session:
            return jsonify({
                "status": "error",
                "message": "Session not found"
            }), 404
        
        # Store feedback
        session['feedback'] = {
            "rating": rating,
            "feedback_text": feedback_text,
            "submitted_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": "Feedback submitted successfully",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@virtual_bp.route('/virtual-tryon/history/<user_id>')
def get_user_tryon_history(user_id):
    """Get virtual try-on history for a user"""
    try:
        user_sessions = []
        
        for session_id, session in virtual_sessions.items():
            if session.get('user_id') == user_id:
                # Include basic session info without large image data
                session_summary = {
                    "session_id": session_id,
                    "product_id": session.get('product_id'),
                    "status": session.get('status'),
                    "created_at": session.get('created_at'),
                    "has_result": 'result' in session
                }
                
                if 'result' in session:
                    session_summary['confidence_score'] = session['result'].get('confidence_score')
                    session_summary['overall_fit'] = session['result']['fit_analysis'].get('overall_fit')
                
                user_sessions.append(session_summary)
        
        # Sort by creation date (newest first)
        user_sessions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "sessions": user_sessions,
            "total": len(user_sessions),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def generate_ai_feedback(product_id):
    """Generate AI feedback for virtual try-on result"""
    feedback_options = [
        {
            "overall": "هذا المنتج يبدو رائعاً عليك! اللون يتماشى بشكل مثالي مع لون بشرتك.",
            "pros": ["اللون مناسب جداً", "القصة تبرز نقاط القوة في جسمك", "الأسلوب يتماشى مع شخصيتك"],
            "suggestions": ["يمكنك إضافة إكسسوارات ذهبية لإطلالة أكثر أناقة", "حذاء بكعب متوسط سيكمل الإطلالة"]
        },
        {
            "overall": "خيار جيد! هذا المنتج مناسب لك ولكن يمكن تحسين الإطلالة ببعض التعديلات.",
            "pros": ["المقاس مناسب", "الجودة تبدو عالية", "مناسب للمناسبات المختلفة"],
            "suggestions": ["جرب لون أفتح للحصول على إطلالة أكثر إشراقاً", "أضف حزام لإبراز الخصر"]
        },
        {
            "overall": "إطلالة مميزة! هذا المنتج يناسب أسلوبك الشخصي بشكل كبير.",
            "pros": ["يبرز شخصيتك المميزة", "مريح وعملي", "يناسب عدة مناسبات"],
            "suggestions": ["اختر إكسسوارات بسيطة لتوازن الإطلالة", "يمكن تنسيقه مع قطع أخرى بسهولة"]
        }
    ]
    
    return random.choice(feedback_options)

