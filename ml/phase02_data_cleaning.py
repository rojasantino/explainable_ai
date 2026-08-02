"""
PHASE 02 — DATA CLEANING
=========================
படிகள்:
  1. Load all 4 CSV files
  2. Check missing values
  3. Remove duplicates & invalid rows
  4. Fix data types
  5. Save cleaned files
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_and_clean_users():
    df = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'))
    print(f"\n[USERS] Raw shape: {df.shape}")
    print(df.isnull().sum())

    df.dropna(subset=['user_id'], inplace=True)
    df.drop_duplicates(subset=['user_id'], inplace=True)
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['age'] = df['age'].clip(18, 100)     # Remove unrealistic ages

    print(f"[USERS] Clean shape: {df.shape}")
    df.to_csv(os.path.join(DATA_DIR, 'users_clean.csv'), index=False)
    return df


def load_and_clean_products():
    df = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
    print(f"\n[PRODUCTS] Raw shape: {df.shape}")

    df.dropna(subset=['product_id', 'price'], inplace=True)
    df.drop_duplicates(subset=['product_id'], inplace=True)
    df = df[df['price'] > 0]                # Remove zero/negative price
    df['price'] = df['price'].round(2)

    print(f"[PRODUCTS] Clean shape: {df.shape}")
    df.to_csv(os.path.join(DATA_DIR, 'products_clean.csv'), index=False)
    return df


def load_and_clean_orders():
    df = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
    print(f"\n[ORDERS] Raw shape: {df.shape}")

    df.dropna(subset=['user_id', 'product_id', 'amount'], inplace=True)
    df.drop_duplicates(subset=['order_id'], inplace=True)
    df = df[df['quantity'] > 0]             # Remove negative qty
    df = df[df['amount'] > 0]               # Remove negative amount
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['status'] != 'returned']     # Keep only delivered orders

    print(f"[ORDERS] Clean shape: {df.shape}")
    df.to_csv(os.path.join(DATA_DIR, 'orders_clean.csv'), index=False)
    return df


def load_and_clean_activity():
    df = pd.read_csv(os.path.join(DATA_DIR, 'user_activity.csv'))
    print(f"\n[ACTIVITY] Raw shape: {df.shape}")

    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df['time_spent_sec'] = df['time_spent_sec'].clip(0, 3600)

    print(f"[ACTIVITY] Clean shape: {df.shape}")
    df.to_csv(os.path.join(DATA_DIR, 'activity_clean.csv'), index=False)
    return df


def print_summary(users, products, orders, activity):
    print("\n" + "="*50)
    print("CLEANING SUMMARY")
    print("="*50)
    print(f"  Users    : {len(users):>6} rows")
    print(f"  Products : {len(products):>6} rows")
    print(f"  Orders   : {len(orders):>6} rows")
    print(f"  Activity : {len(activity):>6} rows")
    print(f"\n  Date range: {orders['date'].min().date()} → {orders['date'].max().date()}")
    print(f"  Avg order value: ₹{orders['amount'].mean():,.0f}")
    print(f"  Unique customers: {orders['user_id'].nunique()}")
    print(f"  Unique products sold: {orders['product_id'].nunique()}")
    print("="*50)


if __name__ == '__main__':
    users    = load_and_clean_users()
    products = load_and_clean_products()
    orders   = load_and_clean_orders()
    activity = load_and_clean_activity()
    print_summary(users, products, orders, activity)
    print("\nCleaned files saved to /data/ folder.")
