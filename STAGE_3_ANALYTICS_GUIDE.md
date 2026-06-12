# 🔬 STAGE 3 ANALYTICS & ML GUIDE
## Advanced Features Walkthrough

---

## 📋 TABLE OF CONTENTS

1. [Advanced ML Model](#advanced-ml-model)
2. [Trend Analysis](#trend-analysis)
3. [Anomaly Detection](#anomaly-detection)
4. [Data Analytics](#data-analytics)
5. [Risk Scoring](#risk-scoring)
6. [Report Generation](#report-generation)
7. [LINQ Operations](#linq-operations)
8. [Examples](#examples)

---

## 🤖 ADVANCED ML MODEL

### Overview
The `MLModel` class uses scikit-learn's RandomForest classifier for advanced predictions with:
- Train/test split validation
- Feature scaling
- Confidence scoring
- Multi-class probability estimates
- Performance metrics

### Creating & Training

```python
from main import MLModel
import numpy as np

# Initialize model
model = MLModel()

# Prepare training data
training_data = [
    {'cpu': 20, 'ram': 25, 'disk': 30, 'label': 'normal'},
    {'cpu': 75, 'ram': 80, 'disk': 70, 'label': 'warning'},
    {'cpu': 95, 'ram': 92, 'disk': 88, 'label': 'critical'},
    # ... more samples
]

# Train with validation split
results = model.train_with_validation(training_data, test_size=0.3)

# Access performance metrics
print(f"Accuracy: {results['accuracy']}")
print(f"F1-Score: {results['f1_score']}")
```

### Making Predictions

```python
# Create a metric
metric = ServerMetric(1, 85, 78, 72)

# Get prediction with confidence
prediction = model.predict_advanced(metric)

# Results include
{
    'server_id': 1,
    'classification': 1,           # 0=normal, 1=warning, 2=critical
    'status': 'warning',
    'confidence': 0.85,            # Confidence (0-1)
    'probabilities': {
        'normal': 0.10,
        'warning': 0.85,
        'critical': 0.05
    },
    'timestamp': '2026-06-12T...'
}
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `test_size` | float | 0.2 | Proportion for testing (0-1) |
| `n_estimators` | int | 100 | Number of trees in forest |
| `max_depth` | int | 10 | Maximum tree depth |
| `random_state` | int | 42 | For reproducibility |

### Performance Evaluation

```python
# After training, access metrics
results = model.training_results

{
    'status': 'trained',
    'train_size': 6,
    'test_size': 3,
    'accuracy': 1.0,
    'precision': 1.0,
    'recall': 1.0,
    'f1_score': 1.0,
    'confusion_matrix': [
        [3, 0, 0],  # True negatives, false positives
        [0, 3, 0],
        [0, 0, 3]
    ]
}
```

---

## 📈 TREND ANALYSIS

### Overview
The `TrendAnalyzer` class detects trends in metrics over time:
- Identifies increasing/decreasing/stable trends
- Calculates trend strength
- Provides forecasting
- Detects anomalies

### Detecting Trends

```python
from main import TrendAnalyzer

analyzer = TrendAnalyzer()

# Get trend for a server's metrics
trend = analyzer.calculate_trend(server_metrics)

print(f"Trend: {trend['trend']}")              # UP, DOWN, STABLE
print(f"Strength: {trend['trend_strength']}%") # How strong
print(f"Velocity: {trend['velocity']}")        # Rate of change
```

### Trend Output

```python
{
    'trend': 'INCREASING',        # or DECREASING, STABLE
    'trend_strength': 15.5,       # Percentage change
    'avg_first_half': 55.2,       # Average of first half
    'avg_second_half': 63.8,      # Average of second half
    'velocity': 8.6               # Points per period
}
```

### Forecasting

```python
# Predict next 3 periods
forecast = analyzer.forecast_next_period(metrics, periods=3)

if forecast['status'] == 'success':
    print(f"Current: {forecast['current_value']}%")
    print(f"Forecast: {forecast['forecast']}")
    # Output: [52.3, 54.1, 55.2]
```

### Interpretation Guide

| Trend | Strength | Meaning | Action |
|-------|----------|---------|--------|
| INCREASING | <5% | Slowly rising | Monitor |
| INCREASING | 5-15% | Steadily rising | Plan capacity |
| INCREASING | >15% | Rapidly rising | Immediate action |
| DECREASING | Any | Improving | Continue monitoring |
| STABLE | Any | Stable | Normal operation |

---

## 🔍 ANOMALY DETECTION

### Overview
Detects unusual data points using statistical Z-score method:
- Configurable sensitivity
- Multiple metrics
- Severity classification

### Detecting Anomalies

```python
from main import TrendAnalyzer

analyzer = TrendAnalyzer()

# Default: 2 sigma (95% of data)
anomalies = analyzer.detect_anomalies(metrics, threshold_sigma=2.0)

for anomaly in anomalies:
    print(f"Server {anomaly['server_id']}")
    print(f"  Metric: {anomaly['metric_type']}")
    print(f"  Value: {anomaly['value']}%")
    print(f"  Z-Score: {anomaly['z_score']}")
    print(f"  Severity: {anomaly['severity']}")
```

### Anomaly Output

```python
{
    'server_id': 1,
    'metric_type': 'cpu_usage',
    'value': 95.0,
    'average': 50.2,
    'z_score': 2.45,              # How many std deviations
    'severity': 'MEDIUM',         # or HIGH
    'timestamp': '2026-06-12T...'
}
```

### Sensitivity Thresholds

```python
# Different sensitivities
analyzer.detect_anomalies(metrics, threshold_sigma=1.5)  # Very sensitive
analyzer.detect_anomalies(metrics, threshold_sigma=2.0)  # Normal (default)
analyzer.detect_anomalies(metrics, threshold_sigma=3.0)  # Only extreme
```

| Sigma | Coverage | Sensitivity |
|-------|----------|-------------|
| 1.5σ | ~93% | Very High |
| 2.0σ | ~95% | High |
| 2.5σ | ~98% | Medium |
| 3.0σ | ~99.7% | Low |

---

## 📊 DATA ANALYTICS

### Overview
The `DataAnalytics` class provides:
- Aggregate statistics
- Grouping operations
- Risk scoring
- Server ranking

### Aggregate Statistics

```python
from main import DataAnalytics

# Get CPU statistics
cpu_stats = DataAnalytics.aggregate_metrics(metrics, 'cpu_usage')

print(f"Count: {cpu_stats['count']}")
print(f"Mean: {cpu_stats['mean']}%")
print(f"Min: {cpu_stats['min']}%")
print(f"Max: {cpu_stats['max']}%")
print(f"Std Dev: {cpu_stats['std']}%")
```

### Grouping Operations

```python
# Group by server
grouped = DataAnalytics.group_by_server(metrics)

for server_id, metrics_list in grouped.items():
    print(f"Server {server_id}: {len(metrics_list)} metrics")
    
# Output:
# Server 1: 3 metrics
# Server 2: 2 metrics
# Server 3: 1 metric
```

### Statistics Output

```python
{
    'metric_type': 'cpu_usage',
    'count': 6,
    'mean': 61.67,
    'min': 30,
    'max': 92,
    'std': 26.76,
    'sum': 370
}
```

---

## 💯 RISK SCORING

### Overview
Calculate risk scores using weighted formula:
- Formula: `risk = cpu_weight × cpu% + ram_weight × ram% + disk_weight × disk%`
- Default weights: CPU=0.4, RAM=0.4, Disk=0.2
- Range: 0-100%

### Calculate Risk

```python
from main import DataAnalytics

metric = ServerMetric(1, 85, 78, 72)

# Get risk score
risk = DataAnalytics.calculate_risk_score(metric)
print(f"Risk Score: {risk}%")

# With custom weights
risk = DataAnalytics.calculate_risk_score(
    metric,
    weight_cpu=0.5,    # Higher weight
    weight_ram=0.3,
    weight_disk=0.2
)
```

### Risk Classification

```python
# Get critical servers (above threshold)
critical = DataAnalytics.get_critical_servers(metrics, threshold=0.7)

for server in critical:
    print(f"Server {server['server_id']}: {server['risk_score']}%")
    print(f"  Status: {server['status']}")  # CRITICAL or HIGH
```

### Risk Levels

| Score | Status | Action |
|-------|--------|--------|
| 0-40% | LOW | Normal operation |
| 40-70% | MEDIUM | Monitor |
| 70-85% | HIGH | Planning needed |
| >85% | CRITICAL | Immediate action |

---

## 📋 REPORT GENERATION

### Overview
The `ReportGenerator` class creates reports in multiple formats:
- JSON (programmatic)
- HTML (visual)
- CSV (spreadsheets)

### Generate Reports

```python
from main import ReportGenerator

generator = ReportGenerator()

# Generate summary
report = generator.generate_summary_report(
    monitoring_service,
    ml_model=ml_model,
    trend_analyzer=analyzer
)

# Access summary
print(f"Servers: {report['servers_monitored']}")
print(f"Metrics: {report['total_metrics_collected']}")
print(f"Anomalies: {report['anomalies_detected']}")
```

### Export Formats

```python
# Export to JSON
generator.export_to_json(report, 'report.json')

# Export to CSV
generator.export_to_csv(report, 'report.csv')

# Generate HTML report
generator.generate_html_report(report, 'report.html')
```

### Report Content

```python
{
    'generated_at': '2026-06-12T22:35:15',
    'period': 'Real-time Monitoring',
    'servers_monitored': 3,
    'total_metrics_collected': 6,
    'classification_breakdown': {
        'normal': 3,
        'warning': 2,
        'critical': 1
    },
    'anomalies_detected': 0,
    'trends': 0
}
```

---

## 🔗 LINQ OPERATIONS

### Grouping Operations

```python
# Group metrics by server
grouped = monitor.group_metrics_by_server()
# Returns: Dict[int, List[ServerMetric]]

# Group by classification
normal = monitor.get_metrics_by_classification(0)
warning = monitor.get_metrics_by_classification(1)
critical = monitor.get_metrics_by_classification(2)
```

### Aggregation Operations

```python
# Get statistics
stats = monitor.get_aggregate_statistics('cpu_usage')
# Returns: mean, min, max, std, count, sum

# Average load per server
loads = monitor.get_average_load_by_server()
# Returns: Dict[int, float]
```

### Filtering Operations

```python
# Get critical servers
critical = monitor.get_critical_servers(threshold=0.7)

# Get top N risk servers
top_5 = monitor.get_top_servers_by_risk(top_n=5)

# Get metrics in time range
recent = monitor.get_metrics_by_time_range(start_iso, end_iso)
```

---

## 💡 EXAMPLES

### Example 1: Complete ML Workflow

```python
from main import *

# Initialize
ml_model = MLModel()
monitoring_service = MonitoringService(...)

# Train
training_data = [...]
results = ml_model.train_with_validation(training_data)
print(f"Accuracy: {results['accuracy']}")

# Predict
metric = ServerMetric(1, 85, 78, 72)
prediction = ml_model.predict_advanced(metric)
print(f"Status: {prediction['status']}")
print(f"Confidence: {prediction['confidence']}")
```

### Example 2: Trend Analysis Workflow

```python
analyzer = TrendAnalyzer()

# Analyze trends
trend = analyzer.calculate_trend(metrics)
print(f"Trend: {trend['trend']} ({trend['trend_strength']}%)")

# Detect anomalies
anomalies = analyzer.detect_anomalies(metrics, threshold_sigma=2.0)
print(f"Found {len(anomalies)} anomalies")

# Forecast
forecast = analyzer.forecast_next_period(metrics, periods=5)
if forecast['status'] == 'success':
    print(f"Next periods: {forecast['forecast']}")
```

### Example 3: Analytics & Risk Workflow

```python
# Get statistics
cpu_stats = DataAnalytics.aggregate_metrics(metrics, 'cpu_usage')
print(f"CPU Mean: {cpu_stats['mean']}%")

# Find critical servers
critical = DataAnalytics.get_critical_servers(metrics, 0.7)
for server in critical:
    print(f"Server {server['server_id']}: {server['status']}")

# Group analysis
grouped = DataAnalytics.group_by_server(metrics)
for server_id, server_metrics in grouped.items():
    risk = DataAnalytics.calculate_risk_score(server_metrics[0])
    print(f"Server {server_id} risk: {risk}%")
```

### Example 4: Report Generation Workflow

```python
generator = ReportGenerator()

# Generate report
report = generator.generate_summary_report(
    monitoring_service,
    ml_model,
    trend_analyzer
)

# Export in multiple formats
generator.export_to_json(report, 'report.json')
generator.export_to_csv(report, 'report.csv')
generator.generate_html_report(report, 'report.html')

print("Reports generated successfully!")
```

---

## 🎯 BEST PRACTICES

### 1. Model Training
```python
# ✅ Good: Balanced data, proper split
training_data = [
    {'cpu': 20, 'ram': 25, 'disk': 30, 'label': 'normal'},
    # ... equal distribution
]
results = ml_model.train_with_validation(training_data, test_size=0.3)

# ❌ Bad: Unbalanced, no validation split
```

### 2. Anomaly Detection
```python
# ✅ Good: Understand your data distribution first
stats = DataAnalytics.aggregate_metrics(metrics, 'cpu_usage')
# Then use appropriate sigma

# ❌ Bad: Use default without understanding data
anomalies = analyzer.detect_anomalies(metrics)  # May miss/flag too much
```

### 3. Risk Scoring
```python
# ✅ Good: Customize weights for your use case
risk = DataAnalytics.calculate_risk_score(metric, 0.5, 0.3, 0.2)

# ❌ Bad: Always use defaults
```

### 4. Report Generation
```python
# ✅ Good: Include all relevant context
report = generator.generate_summary_report(
    monitoring_service,
    ml_model,
    trend_analyzer
)

# ❌ Bad: Empty report with no data
```

---

## 🔧 TROUBLESHOOTING

### Issue: ML Model Not Available
```
⚠️ scikit-learn not installed
✅ Solution: pip install scikit-learn numpy
```

### Issue: Anomalies Not Detected
```
⚠️ All values within normal range
✅ Solution: Try lower threshold_sigma (2.0 → 1.5)
```

### Issue: Forecast Inaccurate
```
⚠️ Not enough historical data
✅ Solution: Collect more metrics before forecasting
```

### Issue: Risk Score Always Same
```
⚠️ Check your weight sum (should equal 1.0)
✅ Solution: Verify weight_cpu + weight_ram + weight_disk = 1.0
```

---

## 📚 REFERENCE

### MLModel Methods
- `__init__()` - Initialize model
- `train_with_validation(data, test_size)` - Train with validation
- `predict_advanced(metric)` - Make prediction

### TrendAnalyzer Methods
- `detect_anomalies(metrics, threshold_sigma)` - Find anomalies
- `calculate_trend(metrics)` - Analyze trend
- `forecast_next_period(metrics, periods)` - Forecast future

### DataAnalytics Methods (Static)
- `aggregate_metrics(metrics, metric_type)` - Get statistics
- `group_by_server(metrics)` - Group by server ID
- `calculate_risk_score(metric, ...)` - Calculate risk
- `get_critical_servers(metrics, threshold)` - Find critical

### ReportGenerator Methods
- `generate_summary_report(service, ml_model, analyzer)` - Create report
- `export_to_json(report, filename)` - JSON export
- `export_to_csv(report, filename)` - CSV export
- `generate_html_report(report, filename)` - HTML export

---

**Last Updated:** June 12, 2026  
**Version:** 3.0  
**Status:** Complete
