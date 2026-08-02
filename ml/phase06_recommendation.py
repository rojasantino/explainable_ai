"""
PHASE 06 — RECOMMENDATION SYSTEM
===================================
Two approaches:
  1. Collaborative Filtering  → "Similar users bought X"
  2. Content-Based Filtering  → "Similar to products you viewed"

Output:
  models/recommender.pkl
  data/sample_recommendations.csv
"""

import pandas as pd
import numpy as np
import sys, os

# Add project ROOT to path so models_classes can be found whether
# this script is run from ml/ folder or from project root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ml.models_classes import CollaborativeFilter, ContentBasedFilter
from sklearn.metrics.pairwise import cosine_similarity
import joblib, warnings
warnings.filterwarnings('ignore')

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


# ─────────────────────────────────────────────────────────────────────────────
# 1. COLLABORATIVE FILTERING
# ─────────────────────────────────────────────────────────────────────────────

class CollaborativeFilter:
    """
    User-based collaborative filtering.
    "Users who bought what you bought, also bought X"
    """

    def __init__(self, n_similar_users: int = 10):
        self.n_similar = n_similar_users
        self.matrix    = None
        self.sim_df    = None
        self.orders    = None

    def fit(self, orders: pd.DataFrame):
        self.orders = orders
        # Create user × product purchase matrix
        self.matrix = orders.pivot_table(
            index   = 'user_id',
            columns = 'product_id',
            values  = 'quantity',
            aggfunc = 'sum',
            fill_value = 0
        )
        # Cosine similarity between all user pairs
        sim_matrix = cosine_similarity(self.matrix)
        self.sim_df = pd.DataFrame(
            sim_matrix,
            index   = self.matrix.index,
            columns = self.matrix.index
        )
        print(f"  Matrix shape: {self.matrix.shape}")
        print(f"  Similarity matrix: {self.sim_df.shape}")
        return self

    def recommend(self, user_id, top_n: int = 5) -> list:
        if user_id not in self.sim_df.index:
            # Cold start → return most popular products
            return self._popular_products(top_n)

        # Find top similar users (exclude self)
        similar_users = (
            self.sim_df[user_id]
            .drop(user_id, errors='ignore')
            .sort_values(ascending=False)
            .head(self.n_similar)
            .index.tolist()
        )

        # Products bought by similar users
        sim_orders = self.orders[self.orders['user_id'].isin(similar_users)]

        # Products already bought by this user
        already_bought = (
            self.orders[self.orders['user_id'] == user_id]['product_id']
            .unique().tolist()
        )

        # Recommend products NOT yet bought
        candidates = (
            sim_orders[~sim_orders['product_id'].isin(already_bought)]
            ['product_id']
            .value_counts()
            .head(top_n)
            .index.tolist()
        )

        # Fallback if not enough recommendations
        if len(candidates) < top_n:
            popular = self._popular_products(top_n)
            for p in popular:
                if p not in candidates and p not in already_bought:
                    candidates.append(p)
                    if len(candidates) >= top_n:
                        break

        return candidates[:top_n]

    def _popular_products(self, n: int) -> list:
        return (
            self.orders['product_id']
            .value_counts()
            .head(n)
            .index.tolist()
        )

    def similarity_score(self, user_id) -> float:
        """Return average similarity to top-10 neighbors"""
        if user_id not in self.sim_df.index:
            return 0.0
        scores = (
            self.sim_df[user_id]
            .drop(user_id, errors='ignore')
            .sort_values(ascending=False)
            .head(10)
            .values
        )
        return float(np.mean(scores))


# ─────────────────────────────────────────────────────────────────────────────
# 2. CONTENT-BASED FILTERING
# ─────────────────────────────────────────────────────────────────────────────

class ContentBasedFilter:
    """
    Product content similarity using category & price.
    "Products similar to what you viewed"
    """

    def __init__(self):
        self.products = None
        self.sim_df   = None

    def fit(self, products: pd.DataFrame):
        self.products = products.copy()
        # One-hot encode category
        cat_dummies = pd.get_dummies(products['category'], prefix='cat')
        # Normalize price to 0-1
        price_norm = (products['price'] - products['price'].min()) / (
            products['price'].max() - products['price'].min() + 1e-9
        )
        # Feature matrix
        feat = pd.concat([cat_dummies, price_norm.rename('price_norm')], axis=1)
        sim  = cosine_similarity(feat)
        self.sim_df = pd.DataFrame(
            sim,
            index   = products['product_id'].values,
            columns = products['product_id'].values
        )
        return self

    def recommend_similar(self, product_id: str, top_n: int = 5) -> list:
        if product_id not in self.sim_df.index:
            return []
        similar = (
            self.sim_df[product_id]
            .drop(product_id, errors='ignore')
            .sort_values(ascending=False)
            .head(top_n)
            .index.tolist()
        )
        return similar


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("Loading data ...")
    orders   = pd.read_csv(os.path.join(DATA_DIR, 'orders_clean.csv'))
    products = pd.read_csv(os.path.join(DATA_DIR, 'products_clean.csv'))

    print("\nTraining Collaborative Filter ...")
    cf = CollaborativeFilter(n_similar_users=10)
    cf.fit(orders)

    print("\nTraining Content-Based Filter ...")
    cb = ContentBasedFilter()
    cb.fit(products)

    print("\nSaving models ...")
    joblib.dump({'cf': cf, 'cb': cb}, os.path.join(MODEL_DIR, 'recommender.pkl'))

    # ── Sample recommendations for all users ──────────────────────────────
    print("\nGenerating sample recommendations ...")
    sample_users = orders['user_id'].unique()[:20]
    rows = []
    for uid in sample_users:
        recs = cf.recommend(uid, top_n=5)
        score = cf.similarity_score(uid)
        rows.append({
            'user_id'        : uid,
            'recommendations': ', '.join(str(r) for r in recs),
            'n_recs'         : len(recs),
            'similarity_score': round(score, 4)
        })

    rec_df = pd.DataFrame(rows)
    rec_df.to_csv(os.path.join(DATA_DIR, 'sample_recommendations.csv'), index=False)

    print("\n" + "="*50)
    print("RECOMMENDATION SYSTEM COMPLETE")
    print("="*50)
    print(f"  Total users in matrix : {cf.matrix.shape[0]}")
    print(f"  Total products tracked: {cf.matrix.shape[1]}")
    print("\n  Sample Recommendations (first 5 users):")
    print(rec_df.head(5).to_string(index=False))
    print("="*50)

    # Test content-based
    test_product = products['product_id'].iloc[0]
    similar_prods = cb.recommend_similar(test_product, top_n=3)
    print(f"\n  Content-based: Products similar to {test_product}: {similar_prods}")


if __name__ == '__main__':
    main()
