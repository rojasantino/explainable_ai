"""
PHASE 04 — CUSTOMER SEGMENTATION (KMeans)
==========================================
Customer-களை 4 groups-ஆக பிரிக்கிறோம்:
  0 → High Value   (அதிக spend, அடிக்கடி வாங்குவார்)
  1 → Loyal        (நடுத்தர spend, regular)
  2 → At Risk      (முன்பு வாங்கினார், இப்போது இல்லை)
  3 → New          (சமீபத்தில் join, குறைந்த purchase)

Output:
  models/segmentation.pkl
  models/seg_scaler.pkl
  data/user_segments.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib, os

DATA_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR  = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

SEGMENT_NAMES = {
    0: 'High Value',
    1: 'Loyal',
    2: 'At Risk',
    3: 'New Customer'
}

SEGMENT_COLORS = {
    'High Value'   : '#185FA5',
    'Loyal'        : '#3B6D11',
    'At Risk'      : '#A32D2D',
    'New Customer' : '#854F0B'
}


def find_optimal_k(X_scaled, k_range=range(2, 9)):
    """Elbow method to find best K"""
    inertias   = []
    sil_scores = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X_scaled, km.labels_))
    return list(k_range), inertias, sil_scores


def auto_label_segments(df: pd.DataFrame, cluster_col='cluster') -> dict:
    """
    Automatically name clusters based on their RFM values.
    High spend + low recency  → High Value
    Low recency + medium spend → Loyal
    High recency (hasn't bought recently) → At Risk
    Low spend + low orders    → New Customer
    """
    summary = df.groupby(cluster_col).agg(
        avg_recency = ('recency_days',  'mean'),
        avg_orders  = ('total_orders',  'mean'),
        avg_spend   = ('total_spend',   'mean'),
    )
    # Rank: low recency = recently bought (good)
    summary['recency_rank'] = summary['avg_recency'].rank()     # lower is better
    summary['order_rank']   = summary['avg_orders'].rank(ascending=False)
    summary['spend_rank']   = summary['avg_spend'].rank(ascending=False)
    summary['score']        = (summary['recency_rank'] +
                               summary['order_rank'] +
                               summary['spend_rank'])

    sorted_clusters = summary['score'].sort_values().index.tolist()
    mapping = {}
    labels  = ['High Value', 'Loyal', 'New Customer', 'At Risk']
    for cluster_id, label in zip(sorted_clusters, labels):
        mapping[cluster_id] = label
    return mapping


def plot_segments(df: pd.DataFrame, out_path: str):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#FAFAFA')

    pairs = [
        ('total_spend',  'total_orders',  'Total Spend (₹)', 'Total Orders'),
        ('recency_days', 'total_spend',   'Recency (days)',   'Total Spend (₹)'),
        ('total_orders', 'avg_time_spent','Total Orders',     'Avg Time Spent (s)'),
    ]

    for ax, (x_col, y_col, xlabel, ylabel) in zip(axes, pairs):
        for seg_name, color in SEGMENT_COLORS.items():
            mask = df['segment_name'] == seg_name
            ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col],
                       c=color, label=seg_name, alpha=0.6, s=20)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.legend(fontsize=8, markerscale=1.5)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Customer Segmentation — RFM Clusters', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Chart saved → {out_path}")


def main():
    print("Loading user features ...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'user_features.csv'))

    SEG_FEATURES = ['recency_days', 'total_orders', 'total_spend',
                    'avg_order_value', 'unique_products']
    X = df[SEG_FEATURES].fillna(0)

    print("Scaling features ...")
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Finding optimal K (elbow method) ...")
    k_range, inertias, sil_scores = find_optimal_k(X_scaled)
    best_k = k_range[sil_scores.index(max(sil_scores))]
    print(f"  Best K by silhouette score: {best_k}")

    print(f"Training KMeans with K=4 (fixed for business logic) ...")
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    print("Auto-labeling segments ...")
    label_map          = auto_label_segments(df)
    df['segment_name'] = df['cluster'].map(label_map)
    df['segment_id']   = df['cluster']

    print("Saving models ...")
    joblib.dump(kmeans,  os.path.join(MODEL_DIR, 'segmentation.pkl'))
    joblib.dump(scaler,  os.path.join(MODEL_DIR, 'seg_scaler.pkl'))
    joblib.dump(label_map, os.path.join(MODEL_DIR, 'seg_label_map.pkl'))

    df.to_csv(os.path.join(DATA_DIR, 'user_segments.csv'), index=False)

    print("Generating segment chart ...")
    plot_segments(df, os.path.join(DATA_DIR, 'segmentation_chart.png'))

    print("\n" + "="*50)
    print("SEGMENTATION RESULTS")
    print("="*50)
    seg_counts = df['segment_name'].value_counts()
    for seg, count in seg_counts.items():
        pct = count / len(df) * 100
        print(f"  {seg:<15}: {count:>4} customers ({pct:.1f}%)")

    print("\n  Segment Profiles:")
    profile = df.groupby('segment_name').agg(
        avg_spend   = ('total_spend',   'mean'),
        avg_orders  = ('total_orders',  'mean'),
        avg_recency = ('recency_days',  'mean'),
    ).round(1)
    print(profile.to_string())
    print("="*50)


if __name__ == '__main__':
    main()
