"""
PHASE 05 — PURCHASE PREDICTION MODEL
======================================
Goal: "இந்த customer அடுத்த 30 நாளில் வாங்குவாரா?"
      Predict probability of purchase (0.0 → 1.0)

Models tried:
  1. Logistic Regression (baseline)
  2. Random Forest       (main model)
  3. XGBoost             (best performer)

Output:
  models/prediction_model.pkl
  models/prediction_features.pkl
  data/model_evaluation.txt
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing   import StandardScaler
from sklearn.linear_model    import LogisticRegression
from sklearn.ensemble        import RandomForestClassifier
from sklearn.metrics         import (classification_report,
                                     confusion_matrix,
                                     roc_auc_score,
                                     roc_curve,
                                     accuracy_score)
import xgboost as xgb
import joblib, os, warnings
warnings.filterwarnings('ignore')

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

FEATURE_COLS = [
    'total_orders',
    'total_spend',
    'avg_order_value',
    'recency_days',
    'unique_products',
    'total_quantity',
    'purchase_rate',
    'total_views',
    'total_carts',
    'avg_time_spent',
    'cart_rate',
]


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'user_features.csv'))
    df = df.fillna(0)
    X  = df[FEATURE_COLS]
    y  = df['will_buy']
    return df, X, y


def train_all_models(X_train, y_train):
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest'      : RandomForestClassifier(n_estimators=200,
                                                       max_depth=8,
                                                       class_weight='balanced',
                                                       random_state=42),
        'XGBoost'            : xgb.XGBClassifier(n_estimators=200,
                                                   learning_rate=0.05,
                                                   max_depth=5,
                                                   use_label_encoder=False,
                                                   eval_metric='logloss',
                                                   random_state=42),
    }
    for name, m in models.items():
        m.fit(X_train, y_train)
        cv = cross_val_score(m, X_train, y_train, cv=5, scoring='roc_auc')
        print(f"  {name:<25} CV AUC: {cv.mean():.4f} ± {cv.std():.4f}")
    return models


def evaluate(models, X_test, y_test):
    results = {}
    for name, m in models.items():
        y_pred  = m.predict(X_test)
        y_proba = m.predict_proba(X_test)[:, 1]
        results[name] = {
            'accuracy' : accuracy_score(y_test, y_pred),
            'auc'      : roc_auc_score(y_test, y_proba),
            'report'   : classification_report(y_test, y_pred),
            'cm'       : confusion_matrix(y_test, y_pred),
            'y_proba'  : y_proba,
        }
        print(f"\n  ── {name} ──")
        print(f"  Accuracy : {results[name]['accuracy']:.4f}")
        print(f"  ROC-AUC  : {results[name]['auc']:.4f}")
    return results


def plot_results(models, results, X_test, y_test, feature_names):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor('#FAFAFA')

    # 1. ROC Curves
    ax = axes[0]
    colors = ['#185FA5', '#3B6D11', '#A32D2D']
    for (name, res), color in zip(results.items(), colors):
        fpr, tpr, _ = roc_curve(y_test, res['y_proba'])
        ax.plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.3f})", color=color)
    ax.plot([0,1],[0,1],'--', color='gray', alpha=0.5)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Confusion Matrix (best model = XGBoost)
    ax     = axes[1]
    best   = results['XGBoost']
    cm     = best['cm']
    im     = ax.imshow(cm, cmap='Blues')
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(['Not Buy','Buy']); ax.set_yticklabels(['Not Buy','Buy'])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i,j]), ha='center', va='center',
                    color='white' if cm[i,j] > cm.max()/2 else 'black',
                    fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted'); ax.set_ylabel('Actual')
    ax.set_title('Confusion Matrix (XGBoost)')
    plt.colorbar(im, ax=ax)

    # 3. Feature Importance (Random Forest)
    ax   = axes[2]
    rf   = models['Random Forest']
    imp  = pd.Series(rf.feature_importances_, index=feature_names).sort_values()
    imp.plot(kind='barh', ax=ax, color='#185FA5', alpha=0.8)
    ax.set_xlabel('Importance Score')
    ax.set_title('Feature Importance (Random Forest)')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'prediction_evaluation.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Chart saved → data/prediction_evaluation.png")


def main():
    print("Loading features ...")
    df, X, y = load_data()
    print(f"  Dataset: {X.shape[0]} users, {X.shape[1]} features")
    print(f"  Class balance → will_buy=1: {y.sum()} | will_buy=0: {(y==0).sum()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

    print("\nTraining all models ...")
    models = train_all_models(X_train, y_train)

    print("\nEvaluating models ...")
    results = evaluate(models, X_test, y_test)

    # Pick best model by AUC
    best_name = max(results, key=lambda k: results[k]['auc'])
    best_model = models[best_name]
    print(f"\n  Best model: {best_name} (AUC={results[best_name]['auc']:.4f})")

    print("\nGenerating evaluation charts ...")
    plot_results(models, results, X_test, y_test, FEATURE_COLS)

    print("\nSaving best model ...")
    joblib.dump(best_model,   os.path.join(MODEL_DIR, 'prediction_model.pkl'))
    joblib.dump(FEATURE_COLS, os.path.join(MODEL_DIR, 'prediction_features.pkl'))

    # Save full evaluation report
    with open(os.path.join(DATA_DIR, 'model_evaluation.txt'), 'w') as f:
        for name, res in results.items():
            f.write(f"\n{'='*40}\n{name}\n{'='*40}\n")
            f.write(f"Accuracy : {res['accuracy']:.4f}\n")
            f.write(f"ROC-AUC  : {res['auc']:.4f}\n")
            f.write(f"\nClassification Report:\n{res['report']}\n")

    print("\n" + "="*50)
    print("PREDICTION MODEL TRAINING COMPLETE")
    print("="*50)
    print(f"  Best Model  : {best_name}")
    print(f"  Accuracy    : {results[best_name]['accuracy']:.4f}")
    print(f"  ROC-AUC     : {results[best_name]['auc']:.4f}")
    print(f"  Saved to    : models/prediction_model.pkl")
    print("="*50)


if __name__ == '__main__':
    main()
