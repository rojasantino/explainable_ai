"""
PHASE 08 — FLASK REST API
===========================
Endpoints:
  GET  /api/health                    → server health check
  GET  /api/predict/<user_id>         → buy probability
  GET  /api/recommend/<user_id>       → top-N product recommendations
  GET  /api/explain/<user_id>         → SHAP explanation (plain English)
  GET  /api/segment/<user_id>         → customer segment (High Value / Loyal / etc.)
  GET  /api/customer/<user_id>        → full customer profile (all above combined)
  GET  /api/products                  → product catalogue
  GET  /api/dashboard/stats           → summary stats for dashboard

Run:
  python api/app.py
  → http://localhost:5000
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from ml.models_classes import CollaborativeFilter, ContentBasedFilter, SHAPExplainer
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os, traceback, time

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, '..', 'data')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)   # Allow Angular frontend (localhost:4200) to call

# ── Load models & data at startup ────────────────────────────────────────────
print("Loading models ...")

try:
    prediction_model   = joblib.load(f'{MODEL_DIR}/prediction_model.pkl')
    feature_cols       = joblib.load(f'{MODEL_DIR}/prediction_features.pkl')
    segmentation_model = joblib.load(f'{MODEL_DIR}/segmentation.pkl')
    seg_scaler         = joblib.load(f'{MODEL_DIR}/seg_scaler.pkl')
    seg_label_map      = joblib.load(f'{MODEL_DIR}/seg_label_map.pkl')
    recommender_data   = joblib.load(f'{MODEL_DIR}/recommender.pkl')
    shap_explainer     = joblib.load(f'{MODEL_DIR}/shap_explainer.pkl')
    print("All models loaded successfully.")
except Exception as e:
    print(f"WARNING: Could not load some models: {e}")
    prediction_model = segmentation_model = seg_scaler = None
    seg_label_map = recommender_data = shap_explainer = None
    feature_cols = []

try:
    df_features  = pd.read_csv(f'{DATA_DIR}/user_features.csv').fillna(0)
    df_segments  = pd.read_csv(f'{DATA_DIR}/user_segments.csv')
    df_orders    = pd.read_csv(f'{DATA_DIR}/orders_clean.csv')
    df_products  = pd.read_csv(f'{DATA_DIR}/products_clean.csv')
    df_users     = pd.read_csv(f'{DATA_DIR}/users_clean.csv')
    df_explain   = pd.read_csv(f'{DATA_DIR}/user_explanations.csv')
    print("All data files loaded.")
except Exception as e:
    print(f"WARNING: Could not load some data files: {e}")
    df_features = df_segments = df_orders = df_products = df_users = df_explain = pd.DataFrame()


# ── Helper: JSON-safe conversion ─────────────────────────────────────────────
def safe(val):
    if isinstance(val, (np.integer,)):   return int(val)
    if isinstance(val, (np.floating,)):  return float(val)
    if isinstance(val, (np.ndarray,)):   return val.tolist()
    if pd.isna(val):                     return None
    return val


def error_response(msg: str, code: int = 400):
    return jsonify({'success': False, 'error': msg}), code


# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return jsonify({
        'name'     : 'Explainable AI Customer Personalization API',
        'version'  : '1.0.0',
        'endpoints': [
            '/api/health',
            '/api/predict/<user_id>',
            '/api/recommend/<user_id>',
            '/api/explain/<user_id>',
            '/api/segment/<user_id>',
            '/api/customer/<user_id>',
            '/api/products',
            '/api/dashboard/stats',
        ]
    })


@app.route('/api/health')
def health():
    return jsonify({
        'status'      : 'ok',
        'timestamp'   : time.time(),
        'models_loaded': prediction_model is not None,
        'data_loaded'  : not df_features.empty,
    })


# ── 1. PREDICT ───────────────────────────────────────────────────────────────
@app.route('/api/predict/<int:user_id>')
def predict(user_id):
    try:
        row = df_features[df_features['user_id'] == user_id]
        if row.empty:
            return error_response(f'User {user_id} not found', 404)

        X    = row[feature_cols]
        prob = float(prediction_model.predict_proba(X)[0][1])

        return jsonify({
            'success'        : True,
            'user_id'        : user_id,
            'buy_probability': round(prob, 3),
            'prediction'     : 'Will Buy' if prob >= 0.5 else 'May Not Buy',
            'confidence'     : 'High' if abs(prob - 0.5) > 0.3 else 'Medium',
            'probability_pct': f"{prob * 100:.1f}%"
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 2. RECOMMEND ─────────────────────────────────────────────────────────────
@app.route('/api/recommend/<int:user_id>')
def recommend(user_id):
    try:
        top_n = int(request.args.get('n', 5))
        cf    = recommender_data['cf']
        recs  = cf.recommend(user_id, top_n=top_n)

        # Enrich with product details
        products_info = []
        for pid in recs:
            prod_row = df_products[df_products['product_id'] == pid]
            if not prod_row.empty:
                p = prod_row.iloc[0]
                products_info.append({
                    'product_id': pid,
                    'name'      : safe(p.get('name', pid)),
                    'category'  : safe(p.get('category', '')),
                    'price'     : safe(p.get('price', 0)),
                    'brand'     : safe(p.get('brand', '')),
                })
            else:
                products_info.append({'product_id': pid, 'name': pid})

        return jsonify({
            'success'        : True,
            'user_id'        : user_id,
            'recommendations': products_info,
            'count'          : len(products_info),
            'method'         : 'collaborative_filtering'
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 3. EXPLAIN ───────────────────────────────────────────────────────────────
@app.route('/api/explain/<int:user_id>')
def explain(user_id):
    try:
        exp_row = df_explain[df_explain['user_id'] == user_id]
        if not exp_row.empty:
            r = exp_row.iloc[0]
            reasons = [r['reason_1'], r['reason_2'], r['reason_3']]
            reasons = [x for x in reasons if pd.notna(x) and x != '']
            return jsonify({
                'success'        : True,
                'user_id'        : user_id,
                'buy_probability': safe(r['buy_probability']),
                'prediction'     : safe(r['prediction']),
                'confidence'     : safe(r['confidence']),
                'reasons'        : reasons,
                'plain_english'  : safe(r['plain_english']),
            })

        # Fallback: compute live
        row = df_features[df_features['user_id'] == user_id]
        if row.empty:
            return error_response(f'User {user_id} not found', 404)

        X      = row[feature_cols]
        result = shap_explainer.explain_user(X)
        return jsonify({
            'success'        : True,
            'user_id'        : user_id,
            **result
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 4. SEGMENT ───────────────────────────────────────────────────────────────
@app.route('/api/segment/<int:user_id>')
def segment(user_id):
    try:
        seg_row = df_segments[df_segments['user_id'] == user_id]
        if seg_row.empty:
            return error_response(f'User {user_id} not found', 404)

        s = seg_row.iloc[0]

        # Segment-specific marketing message
        messages = {
            'High Value'   : 'Exclusive VIP offers just for you!',
            'Loyal'        : 'Thank you for being a loyal customer!',
            'At Risk'      : 'We miss you! Come back for special deals.',
            'New Customer' : 'Welcome! Here are our top picks for you.',
        }
        seg_name = safe(s.get('segment_name', 'Unknown'))

        return jsonify({
            'success'        : True,
            'user_id'        : user_id,
            'segment_id'     : safe(s.get('segment_id', -1)),
            'segment_name'   : seg_name,
            'marketing_msg'  : messages.get(seg_name, ''),
            'total_spend'    : safe(s.get('total_spend', 0)),
            'total_orders'   : safe(s.get('total_orders', 0)),
            'recency_days'   : safe(s.get('recency_days', 0)),
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 5. FULL CUSTOMER PROFILE ─────────────────────────────────────────────────
@app.route('/api/customer/<int:user_id>')
def customer_profile(user_id):
    try:
        # Base user info
        user_row = df_users[df_users['user_id'] == user_id]
        if user_row.empty:
            return error_response(f'User {user_id} not found', 404)

        u = user_row.iloc[0]

        # Purchase history
        user_orders = df_orders[df_orders['user_id'] == user_id]
        order_count = len(user_orders)
        total_spend = float(user_orders['amount'].sum()) if order_count else 0

        # Prediction
        pred_row = df_features[df_features['user_id'] == user_id]
        buy_prob = 0.0
        if not pred_row.empty:
            buy_prob = float(prediction_model.predict_proba(
                pred_row[feature_cols])[0][1])

        # Segment
        seg_row  = df_segments[df_segments['user_id'] == user_id]
        seg_name = safe(seg_row.iloc[0]['segment_name']) if not seg_row.empty else 'Unknown'

        # Recommendations
        cf   = recommender_data['cf']
        recs = cf.recommend(user_id, top_n=5)

        # Explanation
        exp_row = df_explain[df_explain['user_id'] == user_id]
        reasons = []
        if not exp_row.empty:
            r = exp_row.iloc[0]
            reasons = [r['reason_1'], r['reason_2'], r['reason_3']]
            reasons = [x for x in reasons if pd.notna(x) and x != '']

        return jsonify({
            'success': True,
            'profile': {
                'user_id'        : user_id,
                'age'            : safe(u.get('age')),
                'gender'         : safe(u.get('gender')),
                'location'       : safe(u.get('location')),
                'total_orders'   : order_count,
                'total_spend'    : round(total_spend, 2),
                'segment'        : seg_name,
                'buy_probability': round(buy_prob, 3),
                'recommendations': recs,
                'reasons'        : reasons,
            }
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 6. PRODUCTS ──────────────────────────────────────────────────────────────
@app.route('/api/products')
def products():
    try:
        category = request.args.get('category')
        limit    = int(request.args.get('limit', 20))
        df       = df_products.copy()
        if category:
            df = df[df['category'].str.lower() == category.lower()]
        df = df.head(limit)
        return jsonify({
            'success'  : True,
            'products' : df.to_dict(orient='records'),
            'count'    : len(df)
        })
    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── 7. DASHBOARD STATS ───────────────────────────────────────────────────────
@app.route('/api/dashboard/stats')
def dashboard_stats():
    try:
        seg_counts = df_segments['segment_name'].value_counts().to_dict() \
                     if not df_segments.empty else {}

        # Monthly revenue
        if not df_orders.empty:
            df_orders['date'] = pd.to_datetime(df_orders['date'])
            monthly = (
                df_orders.groupby(df_orders['date'].dt.to_period('M'))['amount']
                .sum()
                .tail(6)
            )
            monthly_revenue = [
                {'month': str(k), 'revenue': round(float(v), 2)}
                for k, v in monthly.items()
            ]
        else:
            monthly_revenue = []

        # Top products
        if not df_orders.empty:
            top_prods = (
                df_orders.groupby('product_id')['quantity']
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            top_products = [
                {'product_id': pid, 'total_sold': int(qty)}
                for pid, qty in top_prods.items()
            ]
        else:
            top_products = []

        return jsonify({
            'success': True,
            'stats': {
                'total_customers'  : int(df_users['user_id'].nunique()) if not df_users.empty else 0,
                'total_orders'     : int(len(df_orders)),
                'total_revenue'    : round(float(df_orders['amount'].sum()), 2) if not df_orders.empty else 0,
                'avg_order_value'  : round(float(df_orders['amount'].mean()), 2) if not df_orders.empty else 0,
                'active_customers' : int(df_features['will_buy'].sum()) if not df_features.empty else 0,
                'segments'         : seg_counts,
                'monthly_revenue'  : monthly_revenue,
                'top_products'     : top_products,
            }
        })

    except Exception:
        return error_response(traceback.format_exc(), 500)


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\nStarting Flask API ...")
    print("URL: http://localhost:5000")
    print("Test: http://localhost:5000/api/health\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
