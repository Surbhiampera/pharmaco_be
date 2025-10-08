# Route Separation Plan for app_v2.py

## Current Route Analysis

The `app_v2.py` file contains **34 API endpoints** that can be logically separated into the following manageable modules:

## 1. **Data Upload & Management Routes** (1 endpoint)

**File: `routes/data_routes.py`**

- `POST /upload` - Upload and process dataset

## 2. **Basic Statistics Routes** (8 endpoints)

**File: `routes/stats_routes.py`**

- `GET /total-reports` - Get total number of reports
- `GET /detected-signals` - Get count of detected signals
- `GET /critical-signals` - Get count of critical signals
- `GET /high-risk` - Get high-risk pairs count
- `GET /signal-rate` - Get signal rate
- `GET /total-signal-pairs` - Get total signal pairs
- `GET /average-severity` - Get average severity
- `GET /system-status` - Get system status

## 3. **Signal Analysis Routes** (4 endpoints)

**File: `routes/signal_routes.py`**

- `GET /top-drugs-signals` - Get top drugs with signals
- `GET /top-adverse-events` - Get top adverse events
- `GET /drug-event-signal-pairs` - Get drug-event signal pairs
- `GET /statistical-measures` - Get statistical measures

## 4. **AI Model Routes** (8 endpoints)

**File: `routes/ai_routes.py`**

- `GET /ai-signals` - Get AI-detected signals
- `GET /ai-signal-count` - Get AI signal count
- `GET /ai-high-confidence-signals` - Get high-confidence AI signals
- `GET /ai-model-status` - Get AI model status
- `GET /hybrid-signals` - Get hybrid signals (AI + statistical)
- `GET /ai-prediction-distribution` - Get AI prediction distribution
- `POST /predict-single` - Predict single drug-event pair
- `GET /predicted-dataset` - Get dataset with AI predictions

## 5. **Visualization & Analytics Routes** (8 endpoints)

**File: `routes/analytics_routes.py`**

- `GET /distribution-analysis` - Get distribution analysis
- `GET /temporal-trends` - Get temporal trends
- `GET /risk-heatmaps` - Get risk heatmaps
- `GET /top-drugs-detected` - Get top detected drugs
- `GET /most-frequent-adverse-events` - Get most frequent events
- `GET /signal-trends` - Get signal trends
- `GET /drug-event-severity-heatmap` - Get severity heatmap
- `GET /temporal-patterns` - Get temporal patterns

## 6. **Risk Assessment Routes** (3 endpoints)

**File: `routes/risk_routes.py`**

- `GET /risk-assessment` - Get risk assessment
- `GET /quick-actions` - Get quick action suggestions
- `GET /key-insights` - Get key insights

## 7. **Signal Distribution Routes** (2 endpoints)

**File: `routes/distribution_routes.py`**

- `GET /signal-distribution` - Get signal distribution
- `GET /signal-criteria` - Get signal criteria

## Implementation Strategy

### Phase 1: Create Route Modules

1. Create each route file with proper imports
2. Move utility functions to shared modules
3. Update imports in main app

### Phase 2: Shared Utilities

1. Create `routes/shared/` folder for common utilities
2. Move data processing functions
3. Create shared models and schemas

### Phase 3: Update Main App

1. Remove route definitions from `app_v2.py`
2. Add route imports and includes
3. Keep only core app configuration

## Benefits of Separation

1. **Maintainability**: Each module focuses on specific functionality
2. **Scalability**: Easy to add new features to specific modules
3. **Testing**: Individual modules can be tested separately
4. **Code Organization**: Clear separation of concerns
5. **Team Development**: Different developers can work on different modules

## File Structure After Separation

```
routes/
├── __init__.py
├── shared/
│   ├── __init__.py
│   ├── data_processing.py
│   ├── cache_utils.py
│   └── response_utils.py
├── data_routes.py
├── stats_routes.py
├── signal_routes.py
├── ai_routes.py
├── analytics_routes.py
├── risk_routes.py
├── distribution_routes.py
├── demo_routes.py (existing)
├── drug_routes.py (existing)
├── indi_routes.py (existing)
├── outc_routes.py (existing)
├── reac_routes.py (existing)
├── rpsr_routes.py (existing)
└── ther_routes.py (existing)
```

## Next Steps

1. Create shared utilities module
2. Create each route module
3. Move utility functions to shared modules
4. Update main app to import all routes
5. Test all endpoints work correctly
6. Update documentation

This separation will make the codebase much more manageable and maintainable.
