# Module 2 — Analytics Pipeline (/analytics)

## 1. Overview
This module profiles and analyzes the Titanic dataset, handles missing data according to explicit threshold rules, explores distributions and correlations, trains and evaluates three classification models, compares class imbalance strategies, tunes a Random Forest model with Out-of-Bag (OOB) evaluation, performs a linear regression side-task on `fare`, and exports the complete fitted pipeline artifact (`best_pipeline.joblib`).

---

## 2. Key Decisions & Missing Value Strategy
* **Offline Fallback**: Saved raw dataset as `analytics/titanic.csv` immediately after initial load.
* **Deck (77.22% missing)**: Exceeds the 30% threshold rule — dropped column due to high unreliability.
* **Age (19.87% missing)**: Falls in the 5%–30% threshold range — imputed using median value.
* **Embarked / Embark Town (0.22% missing)**: Under 5% threshold — removed missing rows.

---

## 3. Exploratory Data Analysis & Outliers
* **IQR Outliers**: Identified 65 outliers in `age` and 114 outliers in `fare`.
* **Fare Skewness**: Right-skewed distribution confirmed by the ordering: Mean (32.10) > Median (14.45) > Mode (8.05).
* **Correlation Matrix**: Generated a 6x6 correlation matrix across numeric features (`survived`, `pclass`, `age`, `sibsp`, `parch`, `fare`).

---

## 4. Model Comparison & Metrics

### Classifier Performance (Stratified Split)
| Model | Accuracy | Precision | Recall | F1 Score | AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| **Decision Tree** | 0.8090 | 0.8148 | 0.6471 | 0.7213 | 0.8560 |
| **Random Forest** | **0.8202** | 0.7812 | **0.7353** | **0.7576** | 0.8179 |

### Imbalance & Tuning Analysis
* **SMOTE Evaluation**: Random Forest with SMOTE oversampling applied strictly on training fold achieved an F1 Score of **0.7176**.
* **GridSearchCV Best Parameters**: `{'max_depth': 5, 'max_features': 'sqrt', 'n_estimators': 50}`
* **Out-of-Bag (OOB) Score**: **0.8172**

### Regression Task (Fare Prediction)
* **MAE**: 21.14
* **RMSE**: 41.75
* **R²**: 0.3468
* **Adjusted R²**: 0.3239

---

## 5. Artifact Export & Verification
The best-performing complete `Pipeline` (preprocessing steps + Random Forest classifier) was saved to disk using `joblib`:
* **Path**: `analytics/models/best_pipeline.joblib`
* **Reload Verification**: Reloaded successfully via `joblib.load()` and confirmed valid predictions on raw sample input.