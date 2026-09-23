import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, mean_squared_error, r2_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# 1. Setup Directories
os.makedirs("analytics/visualizations", exist_ok=True)
os.makedirs("analytics/models", exist_ok=True)

# 2. Data Ingestion from Module 1 Database
db_path = os.path.join("data_pipeline", "zepto_catalog.db")
if not os.path.exists(db_path):
    db_path = "zepto_catalog.db"

conn = sqlite3.connect(db_path)
query = """
SELECT b.title, b.price_gbp, b.price_inr, b.rating, b.in_stock, c.category_name
FROM books b
JOIN categories c ON b.category_id = c.category_id
"""
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Dataset successfully loaded with {len(df)} records.")

# 3. Handle Null Values & Cleaning Safeguards
if df.isnull().sum().sum() > 0:
    df['price_gbp'] = df['price_gbp'].fillna(df['price_gbp'].median())
    df['price_inr'] = df['price_inr'].fillna(df['price_inr'].median())
    df['rating'] = df['rating'].fillna(df['rating'].median())

# 4. Exploratory Data Analysis Plots
plt.figure(figsize=(8, 5))
sns.histplot(df['price_inr'], kde=True, color='teal')
plt.title('Distribution of Price (INR)')
plt.savefig('analytics/visualizations/price_distribution.png')
plt.close()

plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='rating', palette='viridis')
plt.title('Book Rating Counts')
plt.savefig('analytics/visualizations/rating_distribution.png')
plt.close()

print("Saved EDA plots to analytics/visualizations/")

# 5. ML Pipeline 1: Classification (Predict High-Value Books)
# Target: 1 if price_inr > median, else 0
median_price = df['price_inr'].median()
df['is_high_value'] = (df['price_inr'] > median_price).astype(int)

X_cls = df[['rating', 'in_stock', 'category_name']]
y_cls = df['is_high_value']

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_cls, y_cls, test_size=0.2, random_state=42, stratify=y_cls
)

preprocessor_cls = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['category_name']),
        ('num', StandardScaler(), ['rating', 'in_stock'])
    ]
)

cls_pipeline = Pipeline([
    ('preprocessor', preprocessor_cls),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Hyperparameter Tuning using GridSearchCV
param_grid = {
    'classifier__n_estimators': [50, 100],
    'classifier__max_depth': [None, 5, 10]
}

grid_search = GridSearchCV(cls_pipeline, param_grid, cv=3, scoring='f1')
grid_search.fit(X_train_c, y_train_c)

best_cls_model = grid_search.best_estimator_
y_pred_c = best_cls_model.predict(X_test_c)

print("\n--- Classification Performance ---")
print(classification_report(y_test_c, y_pred_c))

# Save Best Classification Model
joblib.dump(best_cls_model, "analytics/models/best_classifier.joblib")
print("Saved classifier model to analytics/models/best_classifier.joblib")

# 6. ML Pipeline 2: Regression (Predict Price INR)
X_reg = df[['rating', 'in_stock', 'category_name']]
y_reg = df['price_inr']

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

reg_pipeline = Pipeline([
    ('preprocessor', preprocessor_cls),
    ('regressor', LinearRegression())
])

reg_pipeline.fit(X_train_r, y_train_r)
y_pred_r = reg_pipeline.predict(X_test_r)

r2 = r2_score(y_test_r, y_pred_r)
rmse = np.sqrt(mean_squared_error(y_test_r, y_pred_r))

print("\n--- Regression Performance ---")
print(f"R2 Score: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")

# Save Regression Model
joblib.dump(reg_pipeline, "analytics/models/price_regressor.joblib")
print("Saved regressor model to analytics/models/price_regressor.joblib")
