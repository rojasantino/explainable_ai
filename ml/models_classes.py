"""
SHARED CLASS DEFINITIONS
=========================
Flask API needs to import these classes before loading .pkl files.
joblib pickle requires the class definition to be importable.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import shap


class CollaborativeFilter:
    def __init__(self, n_similar_users=10):
        self.n_similar = n_similar_users
        self.matrix = None
        self.sim_df = None
        self.orders = None

    def fit(self, orders):
        self.orders = orders
        self.matrix = orders.pivot_table(
            index='user_id', columns='product_id',
            values='quantity', aggfunc='sum', fill_value=0
        )
        sim = cosine_similarity(self.matrix)
        self.sim_df = pd.DataFrame(sim, index=self.matrix.index,
                                   columns=self.matrix.index)
        return self

    def recommend(self, user_id, top_n=5):
        if user_id not in self.sim_df.index:
            return self._popular_products(top_n)
        similar_users = (
            self.sim_df[user_id].drop(user_id, errors='ignore')
            .sort_values(ascending=False).head(self.n_similar).index.tolist()
        )
        sim_orders     = self.orders[self.orders['user_id'].isin(similar_users)]
        already_bought = self.orders[self.orders['user_id'] == user_id]['product_id'].unique()
        candidates     = (
            sim_orders[~sim_orders['product_id'].isin(already_bought)]
            ['product_id'].value_counts().head(top_n).index.tolist()
        )
        if len(candidates) < top_n:
            for p in self._popular_products(top_n):
                if p not in candidates and p not in already_bought:
                    candidates.append(p)
                if len(candidates) >= top_n:
                    break
        return candidates[:top_n]

    def _popular_products(self, n):
        return self.orders['product_id'].value_counts().head(n).index.tolist()

    def similarity_score(self, user_id):
        if user_id not in self.sim_df.index:
            return 0.0
        return float(
            self.sim_df[user_id].drop(user_id, errors='ignore')
            .sort_values(ascending=False).head(10).values.mean()
        )


class ContentBasedFilter:
    def __init__(self):
        self.products = None
        self.sim_df   = None

    def fit(self, products):
        self.products = products.copy()
        cat   = pd.get_dummies(products['category'], prefix='cat')
        price = (products['price'] - products['price'].min()) / (
            products['price'].max() - products['price'].min() + 1e-9)
        feat  = pd.concat([cat, price.rename('price_norm')], axis=1)
        sim   = cosine_similarity(feat)
        self.sim_df = pd.DataFrame(sim, index=products['product_id'].values,
                                   columns=products['product_id'].values)
        return self

    def recommend_similar(self, product_id, top_n=5):
        if product_id not in self.sim_df.index:
            return []
        return (
            self.sim_df[product_id].drop(product_id, errors='ignore')
            .sort_values(ascending=False).head(top_n).index.tolist()
        )


FEATURE_LABELS = {
    'total_orders'    : 'Purchase Frequency',
    'total_spend'     : 'Total Money Spent',
    'avg_order_value' : 'Average Basket Size',
    'recency_days'    : 'Days Since Last Purchase',
    'unique_products' : 'Product Variety',
    'total_quantity'  : 'Total Items Bought',
    'purchase_rate'   : 'Purchase Rate',
    'total_views'     : 'Product Views',
    'total_carts'     : 'Cart Additions',
    'avg_time_spent'  : 'Avg Time on Site',
    'cart_rate'       : 'Cart-to-View Ratio',
}

REASON_TEMPLATES = {
    'total_orders'   : ('You shop frequently with us',        'Your purchase frequency is low'),
    'total_spend'    : ('Your high spending pattern',         'Your spending is currently low'),
    'avg_order_value': ('Your large average basket size',     'Your basket size is small'),
    'recency_days'   : ('Your recent activity on our platform','You have not shopped recently'),
    'unique_products': ('Your interest in diverse products',   'You tend to buy from fewer categories'),
    'total_quantity' : ('You buy in larger quantities',        'You buy fewer items per visit'),
    'purchase_rate'  : ('Your consistent purchase habits',     'Your purchase rate has slowed'),
    'total_views'    : ('You actively browse our products',    'Limited product browsing detected'),
    'total_carts'    : ('You frequently add items to cart',    'Low cart activity observed'),
    'avg_time_spent' : ('You spend quality time browsing',     'Short browsing sessions detected'),
    'cart_rate'      : ('High cart-to-view conversion',        'Low cart conversion rate'),
}


class SHAPExplainer:
    def __init__(self, model, feature_names):
        self.model         = model
        self.feature_names = feature_names
        self.explainer     = shap.TreeExplainer(model)

    def get_shap_values(self, X):
        vals = self.explainer.shap_values(X)
        if isinstance(vals, list):
            return vals[1]
        if vals.ndim == 3:
            return vals[:, :, 1]
        return vals

    def explain_user(self, user_row, top_n=3):
        shap_vals = self.get_shap_values(user_row)[0]
        prob      = self.model.predict_proba(user_row)[0][1]
        impact    = sorted(zip(self.feature_names, shap_vals),
                           key=lambda x: abs(x[1]), reverse=True)
        reasons   = []
        for feat, val in impact[:top_n]:
            tpl = REASON_TEMPLATES.get(feat, (feat, feat))
            reasons.append({
                'feature'     : feat,
                'display_name': FEATURE_LABELS.get(feat, feat),
                'shap_value'  : round(float(val), 4),
                'direction'   : 'positive' if val > 0 else 'negative',
                'reason_text' : tpl[0] if val > 0 else tpl[1]
            })
        verdict = "likely to purchase" if prob >= 0.5 else "may not purchase soon"
        parts   = [r['reason_text'] for r in reasons[:3]]
        return {
            'buy_probability': round(float(prob), 3),
            'prediction'     : 'Will Buy' if prob >= 0.5 else 'May Not Buy',
            'confidence'     : 'High' if abs(prob - 0.5) > 0.3 else 'Medium',
            'top_reasons'    : reasons,
            'plain_english'  : f"This customer is {verdict}. Key factors: {'; '.join(parts)}."
        }
