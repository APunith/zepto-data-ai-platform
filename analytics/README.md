# Module 2 — Analytics & Machine Learning Pipeline (`/analytics`)

## 1. Overview
This module performs Exploratory Data Analysis (EDA) on the scraped books dataset, executes data profiling, trains a classification pipeline to identify high-value products, trains a multivariate regression model to predict prices in INR, and serializes trained models for production use.

---

## 2. Setup & Execution

### Prerequisites & Dependencies
```bash
pip install -r analytics/requirements.txt
```
### Run the ML Pipeline
python analytics/analytics_pipeline.py

## 3. Exploratory Data Analysis & Visualizations

* Price Distribution (price_distribution.png): Evaluated pricing skewness across catalog items.

* Rating Frequencies (rating_distribution.png): Charted customer review star ratings across categories.

* Artifacts: High-resolution charts saved automatically inside analytics/visualizations/.

## 4. Machine Learning Benchmarks
### Classification Pipeline (High-Value Item Target)
* Target Definition: is_high_value (1 if price > median price, else 0).
* Model & Tuning: RandomForestClassifier tuned via GridSearchCV (3-fold cross-validation).
* Preprocessing: OneHotEncoder for categories, StandardScaler for numeric features.

### Regression Pipeline (INR Price Prediction)
* Model: LinearRegression with standard feature preprocessing.
* Metrics: Evaluated using $R^2$ Score and Root Mean Squared Error (RMSE).

## 5. Serialized Artifacts

* analytics/models/best_classifier.joblib: Serialized tuned classification pipeline.

* analytics/models/price_regressor.joblib: Serialized regression pipeline.