"""
DATA GENERATION SCRIPT
======================
If you have Kaggle dataset -> skip this file and use that CSV directly.
This script creates realistic synthetic e-commerce data for testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

random.seed(42)
np.random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
N_USERS    = 500
N_PRODUCTS = 100
N_ORDERS   = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2025, 6, 30)

# ── 1. USERS ────────────────────────────────────────────────────────────────
cities = ['Chennai','Bangalore','Mumbai','Delhi','Hyderabad',
          'Pune','Kolkata','Coimbatore','Madurai','Salem']

users = pd.DataFrame({
    'user_id'    : range(101, 101 + N_USERS),
    'age'        : np.random.randint(18, 65, N_USERS),
    'gender'     : np.random.choice(['M','F'], N_USERS),
    'location'   : np.random.choice(cities, N_USERS),
    'signup_date': [START_DATE + timedelta(days=int(d))
                    for d in np.random.randint(0, 180, N_USERS)]
})
users.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)
print(f"users.csv          → {len(users)} rows")

# ── 2. PRODUCTS ─────────────────────────────────────────────────────────────
categories = ['Electronics','Fashion','Home','Books',
              'Sports','Beauty','Grocery','Toys']
brands     = ['Samsung','Nike','Apple','Puma','LG',
              'Boat','Prestige','Levi\'s','HP','Sony']

products = pd.DataFrame({
    'product_id' : [f'P{i:03d}' for i in range(1, N_PRODUCTS + 1)],
    'name'       : [f'Product {i}' for i in range(1, N_PRODUCTS + 1)],
    'category'   : np.random.choice(categories, N_PRODUCTS),
    'price'      : np.round(np.random.uniform(100, 80000, N_PRODUCTS), 2),
    'brand'      : np.random.choice(brands, N_PRODUCTS),
    'stock'      : np.random.randint(0, 500, N_PRODUCTS)
})
products.to_csv(os.path.join(DATA_DIR, 'products.csv'), index=False)
print(f"products.csv       → {len(products)} rows")

# ── 3. ORDERS ────────────────────────────────────────────────────────────────
user_ids    = users['user_id'].tolist()
product_ids = products['product_id'].tolist()
date_range  = (END_DATE - START_DATE).days

orders_list = []
for i in range(N_ORDERS):
    uid  = random.choice(user_ids)
    pid  = random.choice(product_ids)
    qty  = random.randint(1, 5)
    price= float(products[products['product_id']==pid]['price'].values[0])
    date = START_DATE + timedelta(days=random.randint(0, date_range))
    orders_list.append({
        'order_id'  : 5000 + i,
        'user_id'   : uid,
        'product_id': pid,
        'quantity'  : qty,
        'amount'    : round(price * qty, 2),
        'date'      : date.strftime('%Y-%m-%d'),
        'status'    : random.choice(['delivered','delivered','delivered','returned'])
    })

orders = pd.DataFrame(orders_list)
orders.to_csv(os.path.join(DATA_DIR, 'orders.csv'), index=False)
print(f"orders.csv         → {len(orders)} rows")

# ── 4. USER ACTIVITY ─────────────────────────────────────────────────────────
activity_list = []
for _ in range(N_ORDERS * 3):
    uid = random.choice(user_ids)
    pid = random.choice(product_ids)
    viewed  = 1
    carted  = random.choice([0,0,1])
    time_s  = random.randint(10, 600)
    date    = START_DATE + timedelta(days=random.randint(0, date_range))
    activity_list.append({
        'user_id'       : uid,
        'product_id'    : pid,
        'viewed'        : viewed,
        'carted'        : carted,
        'time_spent_sec': time_s,
        'date'          : date.strftime('%Y-%m-%d')
    })

activity = pd.DataFrame(activity_list)
activity.to_csv(os.path.join(DATA_DIR, 'user_activity.csv'), index=False)
print(f"user_activity.csv  → {len(activity)} rows")
print("\nAll datasets generated successfully!")
