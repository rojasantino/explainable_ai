"""
PHASE 07 — EXPLAINABLE AI WITH SHAP
======================================
AI முடிவை மனிதர் புரியுமாறு விளக்கல்:
  "இந்த product ஏன் recommend செய்யப்பட்டது?"
  "இந்த customer ஏன் வாங்குவார் என்று predict செய்தோம்?"

Output:
  models/shap_explainer.pkl
  data/shap_chart.png
  data/user_explanations.csv
"""

import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, warnings
warnings.filterwarnings('ignore')

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


# Human-readable feature name mapping (Tamil context labels)
FEATURE_LABELS = {
    'total_orders'    : 'Purchase Frequency',
    'total_spend'     : 'Total Money Spent',
    'avg_order_value' : 'Average Basket Size',
    'recency_days'    : 'Days Since Last Purchase',
    'unique_products' : 'Product Variety',
    'total_quantity'  : 'Total Items Bought',
    'purchase_rate'   : 'Purchase Rate (per day)',
    'total_views'     : 'Product Views',
    'total_carts'     : 'Cart Additions',
    'avg_time_spent'  : 'Avg Time on Site (sec)',
    'cart_rate'       : 'Cart-to-View Ratio',
}

REASON_TEMPLATES = {
    'total_orders':     ('You shop frequently with us',
                         'Your purchase frequency is low'),
    'total_spend':      ('Your high spending pattern',
                         'Your spending is currently low'),
    'avg_order_value':  ('Your large average basket size',
                         'Your basket size is small'),
    'recency_days':     ('Your recent activity on our platform',
                         'You have not shopped recently'),
    'unique_products':  ('Your interest in diverse products',
                         'You tend to buy from fewer categories'),
    'total_quantity':   ('You buy in larger quantities',
                         'You buy fewer items per visit'),
    'purchase_rate':    ('Your consistent purchase habits',
                         'Your purchase rate has slowed'),
    'total_views':      ('You actively browse our products',
                         'Limited product browsing detected'),
    'total_carts':      ('You frequently add items to cart',
                         'Low cart activity observed'),
    'avg_time_spent':   ('You spend quality time browsing',
                         'Short browsing sessions detected'),
    'cart_rate':        ('High cart-to-view conversion',
                         'Low cart conversion rate'),
}


class SHAPExplainer:
    def __init__(self, model, feature_names: list):
        self.model         = model
        self.feature_names = feature_names
        self.explainer     = shap.TreeExplainer(model)

    def get_shap_values(self, X: pd.DataFrame) -> np.ndarray:
        shap_vals = self.explainer.shap_values(X)
        # For binary classification: could be list [class0, class1] or 3D array
        if isinstance(shap_vals, list):
            return shap_vals[1]          # list format → class 1
        if shap_vals.ndim == 3:
            return shap_vals[:, :, 1]    # 3D array → class 1 slice
        return shap_vals

    def explain_user(self, user_row: pd.DataFrame, top_n: int = 3) -> dict:
        """
        Returns plain-English explanation for one user's prediction.
        """
        shap_vals = self.get_shap_values(user_row)[0]
        prob      = self.model.predict_proba(user_row)[0][1]

        # Sort features by absolute SHAP value
        impact = sorted(
            zip(self.feature_names, shap_vals),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        reasons = []
        for feat, val in impact[:top_n]:
            positive = val > 0
            template  = REASON_TEMPLATES.get(feat, (feat, feat))
            reason    = template[0] if positive else template[1]
            reasons.append({
                'feature'      : feat,
                'display_name' : FEATURE_LABELS.get(feat, feat),
                'shap_value'   : round(float(val), 4),
                'direction'    : 'positive' if positive else 'negative',
                'reason_text'  : reason
            })

        return {
            'buy_probability' : round(float(prob), 3),
            'prediction'      : 'Will Buy' if prob >= 0.5 else 'May Not Buy',
            'confidence'      : 'High' if abs(prob - 0.5) > 0.3 else 'Medium',
            'top_reasons'     : reasons,
            'plain_english'   : self._build_sentence(reasons, prob)
        }

    def _build_sentence(self, reasons: list, prob: float) -> str:
        if not reasons:
            return "Insufficient data to explain."
        parts = [r['reason_text'] for r in reasons[:3]]
        verdict = "likely to purchase" if prob >= 0.5 else "may not purchase soon"
        return f"This customer is {verdict}. Key factors: {'; '.join(parts)}."

    def plot_summary(self, X: pd.DataFrame, out_path: str):
        shap_vals = self.get_shap_values(X)
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor('#FAFAFA')

        # Bar plot — mean |SHAP| per feature
        ax = axes[0]
        mean_abs = np.abs(shap_vals).mean(axis=0)
        feat_imp = pd.Series(mean_abs, index=self.feature_names).sort_values()
        display  = feat_imp.rename(index=FEATURE_LABELS)
        display.plot(kind='barh', ax=ax, color='#185FA5', alpha=0.8)
        ax.set_xlabel('Mean |SHAP Value|')
        ax.set_title('Feature Importance (SHAP)', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Beeswarm-style scatter
        ax = axes[1]
        for i, feat in enumerate(feat_imp.index):
            col_idx = self.feature_names.index(feat)
            vals    = shap_vals[:, col_idx]
            feat_v  = X.iloc[:, col_idx].values
            scatter = ax.scatter(
                vals, np.full_like(vals, i, dtype=float) + np.random.uniform(-0.3, 0.3, len(vals)),
                c=feat_v, cmap='RdYlBu_r', alpha=0.4, s=10
            )
        ax.set_yticks(range(len(feat_imp)))
        ax.set_yticklabels([FEATURE_LABELS.get(f, f) for f in feat_imp.index], fontsize=9)
        ax.axvline(0, color='gray', linewidth=0.8, linestyle='--')
        ax.set_xlabel('SHAP Value (impact on prediction)')
        ax.set_title('SHAP Beeswarm Plot', fontweight='bold')
        ax.grid(True, alpha=0.2, axis='x')

        plt.tight_layout()
        plt.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  SHAP chart saved → {out_path}")


def main():
    print("Loading model and data ...")
    model        = joblib.load(os.path.join(MODEL_DIR, 'prediction_model.pkl'))
    feature_cols = joblib.load(os.path.join(MODEL_DIR, 'prediction_features.pkl'))
    df           = pd.read_csv(os.path.join(DATA_DIR, 'user_features.csv')).fillna(0)

    X = df[feature_cols]

    print("Building SHAP explainer ...")
    explainer = SHAPExplainer(model, feature_cols)

    print("Generating SHAP summary chart ...")
    explainer.plot_summary(X, os.path.join(DATA_DIR, 'shap_chart.png'))

    print("Saving explainer ...")
    joblib.dump(explainer, os.path.join(MODEL_DIR, 'shap_explainer.pkl'))

    print("\nGenerating explanations for all users ...")
    explanation_rows = []
    for _, row in df.iterrows():
        user_row = pd.DataFrame([row[feature_cols]])
        result   = explainer.explain_user(user_row)
        explanation_rows.append({
            'user_id'        : int(row['user_id']),
            'buy_probability': result['buy_probability'],
            'prediction'     : result['prediction'],
            'confidence'     : result['confidence'],
            'reason_1'       : result['top_reasons'][0]['reason_text'] if len(result['top_reasons']) > 0 else '',
            'reason_2'       : result['top_reasons'][1]['reason_text'] if len(result['top_reasons']) > 1 else '',
            'reason_3'       : result['top_reasons'][2]['reason_text'] if len(result['top_reasons']) > 2 else '',
            'plain_english'  : result['plain_english']
        })

    exp_df = pd.DataFrame(explanation_rows)
    exp_df.to_csv(os.path.join(DATA_DIR, 'user_explanations.csv'), index=False)

    print("\n" + "="*50)
    print("EXPLAINABLE AI COMPLETE")
    print("="*50)
    print(f"  Users explained: {len(exp_df)}")
    print(f"\n  Sample explanation for user {exp_df.iloc[0]['user_id']}:")
    print(f"  Prediction     : {exp_df.iloc[0]['prediction']}")
    print(f"  Probability    : {exp_df.iloc[0]['buy_probability']}")
    print(f"  Reason 1       : {exp_df.iloc[0]['reason_1']}")
    print(f"  Plain English  : {exp_df.iloc[0]['plain_english']}")
    print("="*50)


if __name__ == '__main__':
    main()
