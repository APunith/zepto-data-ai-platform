import os
import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
)
from imblearn.over_sampling import SMOTE

VIS_DIR = os.path.join(os.path.dirname(__file__), "visualizations")
os.makedirs(VIS_DIR, exist_ok=True)

df_raw = sns.load_dataset("titanic")
csv_path = os.path.join(os.path.dirname(__file__), "titanic.csv")
df_raw.to_csv(csv_path, index=False)

df = df_raw.copy()

missing_pct = (df.isnull().sum() / len(df)) * 100
print("Missing Values Percentage per Column:")
print(missing_pct[missing_pct > 0])

df["age"] = df["age"].fillna(df["age"].median())

if "deck" in df.columns:
    df = df.drop(columns=["deck"])

df = df.dropna(subset=["embarked", "embark_town"])


for col in ["age", "fare"]:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
    print(f"IQR Outliers in {col}: {len(outliers)}")

fare_mean = df["fare"].mean()
fare_median = df["fare"].median()
fare_mode = df["fare"].mode()[0]
print(f"Fare Mean: {fare_mean:.2f}, Median: {fare_median:.2f}, Mode: {fare_mode:.2f}")
print("Conclusion: Fare distribution is heavily right-skewed (Mean > Median > Mode).")

numeric_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
corr_matrix = df[numeric_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("6x6 Correlation Matrix")
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "correlation_heatmap.png"))
plt.close()

feature_cols = ["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
X = df[feature_cols]
y = df["survived"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
numeric_features = ["pclass", "age", "sibsp", "parch", "fare"]
categorical_features = ["sex", "embarked"]

num_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

cat_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", num_transformer, numeric_features),
        ("cat", cat_transformer, categorical_features)
    ]
)

classifiers = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=4),
    "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100)
}

results = []
for name, clf in classifiers.items():
    model_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])
    
    model_pipeline.fit(X_train, y_train)
    y_pred = model_pipeline.predict(X_test)
    y_proba = model_pipeline.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    results.append({
        "Model": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1 Score": round(f1, 4),
        "AUC": round(auc, 4)
    })

print("\n--- Classifier Performance Metrics ---")
print(pd.DataFrame(results))

X_train_prep = preprocessor.fit_transform(X_train)
X_test_prep = preprocessor.transform(X_test)

smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train_prep, y_train)

rf_smote = RandomForestClassifier(random_state=42)
rf_smote.fit(X_train_sm, y_train_sm)
y_pred_sm = rf_smote.predict(X_test_prep)
print(f"\nRandom Forest + SMOTE F1 Score: {f1_score(y_test, y_pred_sm):.4f}")

rf_oob = RandomForestClassifier(oob_score=True, random_state=42)
param_grid = {
    "classifier__n_estimators": [50, 100],
    "classifier__max_depth": [3, 5, 10],
    "classifier__max_features": ["sqrt", "log2"]
}

rf_search_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", rf_oob)
])

grid_search = GridSearchCV(rf_search_pipeline, param_grid, cv=5, scoring="f1")
grid_search.fit(X_train, y_train)

best_rf = grid_search.best_estimator_
best_oob = best_rf.named_steps["classifier"].oob_score_
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Out-of-Bag (OOB) Score: {best_oob:.4f}")

X_reg = df[["pclass", "sex", "age", "sibsp", "parch", "embarked"]]
y_reg = df["fare"]

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

preprocessor_reg = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), ["pclass", "age", "sibsp", "parch"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["sex", "embarked"])
    ]
)

reg_pipeline = Pipeline([
    ("preprocessor", preprocessor_reg),
    ("regressor", LinearRegression())
])

reg_pipeline.fit(X_train_r, y_train_r)
y_pred_r = reg_pipeline.predict(X_test_r)

mae = mean_absolute_error(y_test_r, y_pred_r)
rmse = np.sqrt(mean_squared_error(y_test_r, y_pred_r))
r2 = r2_score(y_test_r, y_pred_r)
n = len(y_test_r)
p = X_train_r.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

print("\n--- Regression Task Metrics (Fare Prediction) ---")
print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}, Adjusted R2: {adj_r2:.4f}")

model_path = os.path.join(os.path.dirname(__file__), "models", "best_pipeline.joblib")
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(best_rf, model_path)
print(f"\nSaved complete pipeline artifact to {model_path}")

reloaded_model = joblib.load(model_path)
test_sample = X_test.iloc[:1]
sample_pred = reloaded_model.predict(test_sample)
print(f"Reload Sanity Check Prediction on raw sample: {sample_pred[0]}")