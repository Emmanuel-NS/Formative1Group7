# Model Training & Experimentation Notes

This note captures the small model-training slice of the project.

## Target
- Forecast next-day `N02BE` demand

## Experiments

| Experiment | Features | Test MAE | Test RMSE | Test R² |
|---|---|---:|---:|---:|
| Random Forest | Lags + Calendar | 8.86 | 12.21 | 0.4368 |
| XGBoost | Lags + MA + Cross-Category | 8.61 | 11.67 | 0.4855 |

## Quick takeaway
- XGBoost performed slightly better and became the selected model.
- Lagged demand, moving averages, and related category signals were the most useful features.
