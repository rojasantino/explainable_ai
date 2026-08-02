"""
PHASE 03 — FEATURE ENGINEERING
================================
RFM Analysis + Behavior Features:
  R → Recency   (எத்தனை நாள் முன்பு வாங்கினார்?)
  F → Frequency (எத்தனை முறை வாங்கினார்?)
  M → Monetary  (மொத்தம் எவ்வளவு செலவழித்தார்?)

Output: data/user_features.csv
"""

import pandas as pd
import numpy as np
import os

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')


def build_rfm_features(orders: pd.DataFrame) -> pd.DataFrame:
    snapshot = orders['date'].max() + pd.Timedelta(days=1)

    rfm = orders.groupby('user_id').agg(
        total_orders    = ('order_id',   'count'),
        total_spend     = ('amount',     'sum'),
        avg_order_value = ('amount',     'mean'),
        last_purchase   = ('date',       'max'),
        first_purchase  = ('date',       'min'),
        unique_products = ('product_id', 'nunique'),
        total_quantity  = ('quantity',   'sum'),
    ).reset_index()

    rfm['recency_days'] = (snapshot - rfm['last_purchase']).dt.days
    rfm['customer_age_days'] = (snapshot - rfm['first_purchase']).dt.days
    rfm['purchase_rate'] = (
        rfm['total_orders'] / rfm['customer_age_days'].replace(0, 1)
    )

    return rfm


def build_activity_features(activity: pd.DataFrame) -> pd.DataFrame:
    af = activity.groupby('user_id').agg(
        total_views      = ('viewed',          'sum'),
        total_carts      = ('carted',          'sum'),
        avg_time_spent   = ('time_spent_sec',  'mean'),
        unique_viewed    = ('product_id',       'nunique'),
    ).reset_index()

    af['cart_rate'] = af['total_carts'] / af['total_views'].replace(0, 1)
    return af


def build_category_features(orders: pd.DataFrame,
                             products: pd.DataFrame) -> pd.DataFrame:
    merged = orders.merge(products[['product_id','category']], on='product_id')
    top_cat = (
        merged.groupby(['user_id','category'])['order_id']
        .count()
        .reset_index()
        .sort_values('order_id', ascending=False)
        .drop_duplicates('user_id')
        .rename(columns={'category':'fav_category','order_id':'fav_cat_orders'})
    )
    return top_cat[['user_id','fav_category','fav_cat_orders']]


def create_target_label(rfm: pd.DataFrame, threshold_days: int = 30) -> pd.DataFrame:
    """
    will_buy = 1  →  customer purchased in last 30 days (Active buyer)
    will_buy = 0  →  customer has NOT purchased in 30+ days (Inactive)
    """
    rfm['will_buy'] = (rfm['recency_days'] <= threshold_days).astype(int)
    return rfm


def main():
    print("Loading cleaned data ...")
    orders   = pd.read_csv(os.path.join(DATA_DIR, 'orders_clean.csv'),   parse_dates=['date'])
    products = pd.read_csv(os.path.join(DATA_DIR, 'products_clean.csv'))
    activity = pd.read_csv(os.path.join(DATA_DIR, 'activity_clean.csv'), parse_dates=['date'])

    print("Building RFM features ...")
    rfm = build_rfm_features(orders)

    print("Building activity features ...")
    af  = build_activity_features(activity)

    print("Building category features ...")
    cat = build_category_features(orders, products)

    print("Merging all features ...")
    features = rfm.merge(af,  on='user_id', how='left')
    features = features.merge(cat, on='user_id', how='left')

    # Fill missing activity data with 0
    fill_cols = ['total_views','total_carts','avg_time_spent',
                 'unique_viewed','cart_rate']
    features[fill_cols] = features[fill_cols].fillna(0)

    # Create label
    features = create_target_label(features)

    # Drop non-numeric cols for ML (keep for reference)
    features.to_csv(os.path.join(DATA_DIR, 'user_features.csv'), index=False)

    print("\n" + "="*50)
    print("FEATURE ENGINEERING COMPLETE")
    print("="*50)
    print(f"  Total users with features : {len(features)}")
    print(f"  Active buyers (will_buy=1): {features['will_buy'].sum()}")
    print(f"  Inactive (will_buy=0)     : {(features['will_buy']==0).sum()}")
    print(f"  Features created          : {len(features.columns)} columns")
    print("\n  Column list:")
    for col in features.columns:
        print(f"    - {col}")
    print("="*50)
    print(f"\nSaved → data/user_features.csv")


if __name__ == '__main__':
    main()
