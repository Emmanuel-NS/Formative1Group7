# Model Training & Experimentation Notes

This note captures the small model-training slice of the project.

## Target
- Forecast next-day `N02BE` demand

## Experiments

| Experiment | Features | Test MAE | Test RMSE | Test R² |
|---|---|---:|---:|---:|
| Random Forest | Lags + Calendar | 8.86 | 12.21 | 0.4368 |
| XGBoost | Lags + MA + Cross-Category | 8.61 | 11.67 | 0.4855 |

## Training setup
- Chronological split was used to avoid leakage.
- TimeSeriesSplit was used during tuning so each fold respected time order.

## Tuning highlights
- Random Forest search focused on `n_estimators`, `max_depth`, and `min_samples_leaf`.
- XGBoost search focused on `learning_rate`, `max_depth`, `n_estimators`, and `subsample`.

## Quick takeaway
- XGBoost performed slightly better and became the selected model.
- Lagged demand, moving averages, and related category signals were the most useful features.

## Result interpretation
- The test metrics show a modest but consistent gain for XGBoost over Random Forest.
- The final model choice matches the forecast script used later in the project.
