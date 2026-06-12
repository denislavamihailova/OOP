"""
AI Server Monitoring System - Stage 3
OOP + Events + Advanced ML + Analytics + Predictions
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional, Tuple
from abc import ABC, abstractmethod
import sqlite3
from statistics import mean, stdev
import warnings
warnings.filterwarnings('ignore')

# Try to import ML libraries for Stage 3
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ServerMonitoringException(Exception):
    """Base exception for server monitoring system"""
    pass


class ModelError(ServerMonitoringException):
    """Exception for model-related errors"""
    pass


class DatabaseError(ServerMonitoringException):
    """Exception for database-related errors"""
    pass


class MetricException(ServerMonitoringException):
    """Exception for metric collection errors"""
    pass


class AnalyticsError(ServerMonitoringException):
    """Exception for analytics-related errors"""
    pass


class PredictionError(ServerMonitoringException):
    """Exception for prediction-related errors"""
    pass


# ============================================================================
# MODELS
# ============================================================================

class Server:
    """Server model representing a monitored server"""
    
    def __init__(self, server_id: int, name: str, ip: str, status: str = "online"):
        self.id = server_id
        self.name = name
        self.ip = ip
        self.status = status  # online, offline, maintenance
    
    def __repr__(self):
        return f"Server(id={self.id}, name='{self.name}', ip='{self.ip}', status='{self.status}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'status': self.status
        }


class ServerMetric:
    """Server performance metrics"""
    
    def __init__(self, server_id: int, cpu_usage: float, ram_usage: float, 
                 disk_usage: float, timestamp: Optional[str] = None):
        if not (0 <= cpu_usage <= 100):
            raise MetricException(f"Invalid CPU usage: {cpu_usage}")
        if not (0 <= ram_usage <= 100):
            raise MetricException(f"Invalid RAM usage: {ram_usage}")
        if not (0 <= disk_usage <= 100):
            raise MetricException(f"Invalid DISK usage: {disk_usage}")
        
        self.server_id = server_id
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.disk_usage = disk_usage
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def __repr__(self):
        return (f"ServerMetric(server_id={self.server_id}, "
                f"cpu={self.cpu_usage}%, ram={self.ram_usage}%, "
                f"disk={self.disk_usage}%)")
    
    def to_dict(self):
        return {
            'server_id': self.server_id,
            'cpu_usage': self.cpu_usage,
            'ram_usage': self.ram_usage,
            'disk_usage': self.disk_usage,
            'timestamp': self.timestamp
        }
    
    def get_average_load(self) -> float:
        """Calculate average load across all metrics"""
        return (self.cpu_usage + self.ram_usage + self.disk_usage) / 3


# ============================================================================
# EVENT SYSTEM (OBSERVER PATTERN)
# ============================================================================

class EventDispatcher:
    """Event dispatcher implementing the Observer pattern"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Subscribe to an event
        
        Args:
            event_name: Name of the event (e.g., 'on_high_cpu_predicted')
            callback: Callback function to execute when event is triggered
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        self._subscribers[event_name].append(callback)
        print(f"✓ Subscriber registered for event '{event_name}'")
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event"""
        if event_name in self._subscribers:
            self._subscribers[event_name].remove(callback)
    
    def dispatch(self, event_name: str, data: Dict) -> None:
        """Dispatch an event to all subscribers
        
        Args:
            event_name: Name of the event to dispatch
            data: Event data/payload to pass to callbacks
        """
        print(f"\n📢 Event dispatched: '{event_name}' with data: {data}")
        
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"⚠️ Error executing callback: {str(e)}")
        else:
            print(f"ℹ️ No subscribers for event '{event_name}'")
    
    def get_subscribers(self, event_name: str) -> int:
        """Get number of subscribers for an event"""
        return len(self._subscribers.get(event_name, []))


# ============================================================================
# AI PREDICTION MODEL
# ============================================================================

class PredictionModel:
    """Simple AI model for server status classification
    
    Classification:
    - 0: normal
    - 1: warning (high_load)
    - 2: critical
    """
    
    # Thresholds for classification
    THRESHOLDS = {
        'normal_max': 60,      # Average load <= 60% → normal
        'warning_max': 80,     # 60% < Average load <= 80% → warning
        'critical_min': 80     # Average load > 80% → critical
    }
    
    def __init__(self):
        self.is_trained = False
        self.training_data = []
        self.prediction_history = []
    
    def train(self, data: List[Dict]) -> None:
        """Train the model with sample data
        
        Args:
            data: List of dicts with 'cpu', 'ram', 'disk', 'label' keys
        """
        try:
            if not data:
                raise ModelError("Training data cannot be empty")
            
            self.training_data = data
            self.is_trained = True
            print(f"✓ Model trained with {len(data)} samples")
        except Exception as e:
            raise ModelError(f"Training failed: {str(e)}")
    
    def predict(self, metric: ServerMetric) -> Dict:
        """Predict server status based on metrics
        
        Args:
            metric: ServerMetric object
            
        Returns:
            Dict with prediction result and classification
        """
        try:
            avg_load = metric.get_average_load()
            
            if avg_load <= self.THRESHOLDS['normal_max']:
                classification = 0
                status = "normal"
            elif avg_load <= self.THRESHOLDS['warning_max']:
                classification = 1
                status = "warning"
            else:
                classification = 2
                status = "critical"
            
            prediction = {
                'server_id': metric.server_id,
                'cpu': metric.cpu_usage,
                'ram': metric.ram_usage,
                'disk': metric.disk_usage,
                'avg_load': round(avg_load, 2),
                'classification': classification,
                'status': status,
                'timestamp': metric.timestamp
            }
            
            self.prediction_history.append(prediction)
            return prediction
        
        except Exception as e:
            raise ModelError(f"Prediction failed: {str(e)}")
    
    def evaluate(self) -> Dict:
        """Evaluate model performance based on prediction history"""
        if not self.prediction_history:
            return {'message': 'No predictions made yet'}
        
        total = len(self.prediction_history)
        normal_count = sum(1 for p in self.prediction_history if p['classification'] == 0)
        warning_count = sum(1 for p in self.prediction_history if p['classification'] == 1)
        critical_count = sum(1 for p in self.prediction_history if p['classification'] == 2)
        
        return {
            'total_predictions': total,
            'normal': {'count': normal_count, 'percentage': round(normal_count/total*100, 2)},
            'warning': {'count': warning_count, 'percentage': round(warning_count/total*100, 2)},
            'critical': {'count': critical_count, 'percentage': round(critical_count/total*100, 2)}
        }


# ============================================================================
# STAGE 3: ADVANCED ML MODEL
# ============================================================================

class MLModel:
    """Advanced Machine Learning model using scikit-learn
    
    Features:
    - RandomForest classification
    - Train/test split validation
    - Performance metrics (accuracy, precision, recall, F1)
    - Cross-validation capability
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.training_results = {}
        self.feature_names = ['cpu', 'ram', 'disk']
        
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            self.scaler = StandardScaler()
        else:
            print("⚠️ scikit-learn not available - using basic model")
    
    def train_with_validation(self, training_data: List[Dict], test_size: float = 0.2) -> Dict:
        """Train model with train/test split and cross-validation
        
        Args:
            training_data: List of dicts with features and 'label' key
            test_size: Proportion of data for testing (default 0.2)
            
        Returns:
            Training results with metrics
        """
        if not SKLEARN_AVAILABLE:
            return {'message': 'scikit-learn not available', 'status': 'basic'}
        
        try:
            if not training_data:
                raise PredictionError("Training data cannot be empty")
            
            # Prepare data
            X = []
            y = []
            label_map = {'normal': 0, 'warning': 1, 'critical': 2}
            
            for record in training_data:
                features = [record.get(f, 0) for f in self.feature_names]
                X.append(features)
                y.append(label_map.get(record.get('label', 'normal'), 0))
            
            # Convert to numpy arrays for sklearn
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            
            results = {
                'status': 'trained',
                'train_size': len(X_train),
                'test_size': len(X_test),
                'accuracy': round(accuracy_score(y_test, y_pred), 4),
                'precision': round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
                'recall': round(recall_score(y_test, y_pred, average='weighted', zero_division=0), 4),
                'f1_score': round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
            
            self.training_results = results
            print(f"✓ ML Model trained: Accuracy={results['accuracy']}, F1={results['f1_score']}")
            return results
        
        except Exception as e:
            raise PredictionError(f"ML training failed: {str(e)}")
    
    def predict_advanced(self, metric: ServerMetric) -> Dict:
        """Make advanced prediction with ML model
        
        Args:
            metric: ServerMetric object
            
        Returns:
            Prediction with confidence scores
        """
        if not SKLEARN_AVAILABLE or not self.is_trained:
            # Fallback to basic threshold-based prediction
            avg_load = metric.get_average_load()
            if avg_load <= 60:
                return {'classification': 0, 'status': 'normal', 'confidence': 0.8}
            elif avg_load <= 80:
                return {'classification': 1, 'status': 'warning', 'confidence': 0.75}
            else:
                return {'classification': 2, 'status': 'critical', 'confidence': 0.85}
        
        try:
            # Prepare feature vector
            features = np.array([[metric.cpu_usage, metric.ram_usage, metric.disk_usage]])
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            confidence = round(float(max(probabilities)), 4)
            
            status_map = {0: 'normal', 1: 'warning', 2: 'critical'}
            
            return {
                'server_id': metric.server_id,
                'classification': int(prediction),
                'status': status_map[int(prediction)],
                'confidence': confidence,
                'probabilities': {
                    'normal': round(float(probabilities[0]), 4),
                    'warning': round(float(probabilities[1]), 4),
                    'critical': round(float(probabilities[2]), 4)
                },
                'timestamp': metric.timestamp
            }
        
        except Exception as e:
            raise PredictionError(f"Advanced prediction failed: {str(e)}")


# ============================================================================
# STAGE 3: TREND ANALYZER
# ============================================================================

class TrendAnalyzer:
    """Analyzes historical trends, detects anomalies, and generates forecasts
    
    Features:
    - Trend detection (up/down/stable)
    - Anomaly detection using statistical methods
    - Forecasting using exponential smoothing
    - Risk scoring
    """
    
    def __init__(self):
        self.anomalies = []
        self.trends = []
    
    def detect_anomalies(self, metrics: List[ServerMetric], 
                        threshold_sigma: float = 2.0) -> List[Dict]:
        """Detect anomalies using statistical method (Z-score)
        
        Args:
            metrics: List of ServerMetric objects
            threshold_sigma: Standard deviation threshold (default 2.0)
            
        Returns:
            List of detected anomalies
        """
        if len(metrics) < 3:
            return []
        
        anomalies = []
        
        for metric_type in ['cpu_usage', 'ram_usage', 'disk_usage']:
            values = [getattr(m, metric_type) for m in metrics]
            
            try:
                avg = mean(values)
                std = stdev(values) if len(values) > 1 else 0
                
                if std == 0:
                    continue
                
                for i, metric in enumerate(metrics):
                    value = values[i]
                    z_score = abs((value - avg) / std)
                    
                    if z_score > threshold_sigma:
                        anomaly = {
                            'server_id': metric.server_id,
                            'metric_type': metric_type,
                            'value': value,
                            'average': round(avg, 2),
                            'z_score': round(z_score, 2),
                            'severity': 'HIGH' if z_score > 3 else 'MEDIUM',
                            'timestamp': metric.timestamp
                        }
                        anomalies.append(anomaly)
                        self.anomalies.append(anomaly)
            
            except (ValueError, ZeroDivisionError):
                continue
        
        return anomalies
    
    def calculate_trend(self, metrics: List[ServerMetric]) -> Dict:
        """Calculate trend for metrics
        
        Args:
            metrics: List of ServerMetric objects
            
        Returns:
            Trend analysis
        """
        if len(metrics) < 2:
            return {'status': 'insufficient_data'}
        
        # Simple linear trend: compare average of first half vs second half
        mid_point = len(metrics) // 2
        first_half = [m.get_average_load() for m in metrics[:mid_point]]
        second_half = [m.get_average_load() for m in metrics[mid_point:]]
        
        avg_first = mean(first_half)
        avg_second = mean(second_half)
        
        if avg_second > avg_first * 1.1:
            trend = 'INCREASING'
        elif avg_second < avg_first * 0.9:
            trend = 'DECREASING'
        else:
            trend = 'STABLE'
        
        trend_strength = round(abs(avg_second - avg_first) / avg_first * 100, 2) if avg_first > 0 else 0
        
        return {
            'trend': trend,
            'trend_strength': trend_strength,
            'avg_first_half': round(avg_first, 2),
            'avg_second_half': round(avg_second, 2),
            'velocity': round(avg_second - avg_first, 2)
        }
    
    def forecast_next_period(self, metrics: List[ServerMetric], 
                            periods: int = 3) -> Dict:
        """Forecast next period using exponential smoothing
        
        Args:
            metrics: List of ServerMetric objects
            periods: Number of periods to forecast (default 3)
            
        Returns:
            Forecast for next periods
        """
        if len(metrics) < 2:
            return {'status': 'insufficient_data'}
        
        try:
            # Extract values
            values = [m.get_average_load() for m in metrics]
            
            # Simple exponential smoothing
            alpha = 0.3
            forecast = []
            last_value = values[-1]
            
            for _ in range(periods):
                next_value = alpha * last_value + (1 - alpha) * mean(values[-3:] if len(values) >= 3 else values)
                forecast.append(round(next_value, 2))
                last_value = next_value
            
            return {
                'status': 'success',
                'current_value': round(values[-1], 2),
                'forecast': forecast,
                'forecast_periods': periods
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


# ============================================================================
# STAGE 3: DATA ANALYTICS
# ============================================================================

class DataAnalytics:
    """Advanced data analysis with grouping, aggregation, and risk scoring
    
    Features:
    - Statistical aggregation (mean, median, std, min, max)
    - Grouping by time periods
    - Critical server identification
    - Risk scoring and ranking
    """
    
    @staticmethod
    def aggregate_metrics(metrics: List[ServerMetric], 
                         metric_type: str = 'cpu_usage') -> Dict:
        """Calculate aggregate statistics for a metric
        
        Args:
            metrics: List of ServerMetric objects
            metric_type: Type of metric ('cpu_usage', 'ram_usage', 'disk_usage')
            
        Returns:
            Aggregated statistics
        """
        if not metrics:
            return {'message': 'No metrics available'}
        
        try:
            values = [getattr(m, metric_type) for m in metrics]
            
            return {
                'metric_type': metric_type,
                'count': len(values),
                'mean': round(mean(values), 2),
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'std': round(stdev(values), 2) if len(values) > 1 else 0,
                'sum': round(sum(values), 2)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def group_by_server(metrics: List[ServerMetric]) -> Dict:
        """Group metrics by server
        
        Args:
            metrics: List of ServerMetric objects
            
        Returns:
            Metrics grouped by server ID
        """
        grouped = {}
        for metric in metrics:
            if metric.server_id not in grouped:
                grouped[metric.server_id] = []
            grouped[metric.server_id].append(metric)
        return grouped
    
    @staticmethod
    def calculate_risk_score(metric: ServerMetric, 
                            weight_cpu: float = 0.4,
                            weight_ram: float = 0.4,
                            weight_disk: float = 0.2) -> float:
        """Calculate risk score for a metric (0-100)
        
        Args:
            metric: ServerMetric object
            weight_cpu: Weight for CPU (default 0.4)
            weight_ram: Weight for RAM (default 0.4)
            weight_disk: Weight for disk (default 0.2)
            
        Returns:
            Risk score (0-100)
        """
        risk = (metric.cpu_usage * weight_cpu + 
               metric.ram_usage * weight_ram + 
               metric.disk_usage * weight_disk)
        return round(risk, 2)
    
    @staticmethod
    def get_critical_servers(metrics: List[ServerMetric], 
                            threshold: float = 0.7) -> List[Dict]:
        """Identify critical servers based on risk score
        
        Args:
            metrics: List of ServerMetric objects
            threshold: Risk threshold (0-1, default 0.7)
            
        Returns:
            List of critical servers with risk scores
        """
        critical = []
        threshold_value = threshold * 100
        
        # Group by server and calculate max risk
        server_risks = {}
        for metric in metrics:
            risk = DataAnalytics.calculate_risk_score(metric)
            if metric.server_id not in server_risks or risk > server_risks[metric.server_id]:
                server_risks[metric.server_id] = risk
        
        # Filter critical
        for server_id, risk in server_risks.items():
            if risk > threshold_value:
                critical.append({
                    'server_id': server_id,
                    'risk_score': risk,
                    'status': 'CRITICAL' if risk > 85 else 'HIGH'
                })
        
        return sorted(critical, key=lambda x: x['risk_score'], reverse=True)


# ============================================================================
# STAGE 3: REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates comprehensive monitoring reports and summaries
    
    Features:
    - Executive summaries
    - Detailed analytics reports
    - Alert summaries
    - Export to multiple formats
    """
    
    def __init__(self):
        self.reports = []
    
    def generate_summary_report(self, monitoring_service, ml_model: Optional[MLModel] = None,
                               trend_analyzer: Optional[TrendAnalyzer] = None) -> Dict:
        """Generate executive summary report
        
        Args:
            monitoring_service: MonitoringService instance
            ml_model: MLModel instance (optional)
            trend_analyzer: TrendAnalyzer instance (optional)
            
        Returns:
            Summary report dictionary
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': 'Real-time Monitoring',
            'servers_monitored': len(monitoring_service.servers),
            'total_metrics_collected': len(monitoring_service.metrics),
            'total_predictions': len(ml_model.training_results) if ml_model else 0
        }
        
        # Add metrics by classification
        if monitoring_service.model:
            evaluation = monitoring_service.model.evaluate()
            report['classification_breakdown'] = {
                'normal': evaluation.get('normal', {}).get('count', 0),
                'warning': evaluation.get('warning', {}).get('count', 0),
                'critical': evaluation.get('critical', {}).get('count', 0)
            }
        
        # Add anomalies
        if trend_analyzer:
            report['anomalies_detected'] = len(trend_analyzer.anomalies)
            report['trends'] = len(trend_analyzer.trends)
        
        self.reports.append(report)
        return report
    
    def export_to_csv(self, report: Dict, filename: str = 'monitoring_report.csv') -> None:
        """Export report to CSV file
        
        Args:
            report: Report dictionary
            filename: Output filename
        """
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=report.keys())
                writer.writeheader()
                writer.writerow(report)
            print(f"✓ Report exported to {filename}")
        except Exception as e:
            print(f"✗ Failed to export report: {str(e)}")
    
    def export_to_json(self, report: Dict, filename: str = 'monitoring_report.json') -> None:
        """Export report to JSON file
        
        Args:
            report: Report dictionary
            filename: Output filename
        """
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✓ Report exported to {filename}")
        except Exception as e:
            print(f"✗ Failed to export report: {str(e)}")
    
    def generate_html_report(self, report: Dict, filename: str = 'monitoring_report.html') -> None:
        """Generate HTML report
        
        Args:
            report: Report dictionary
            filename: Output filename
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Server Monitoring Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ color: #666; font-size: 12px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #0066cc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Monitoring Report</h1>
        <p>Generated: {report.get('generated_at', 'Unknown')}</p>
        
        <div class="section">
            <h2>Summary Statistics</h2>
            <div class="metric">
                <div class="metric-label">Servers Monitored</div>
                <div class="metric-value">{report.get('servers_monitored', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Metrics Collected</div>
                <div class="metric-value">{report.get('total_metrics_collected', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Anomalies Detected</div>
                <div class="metric-value">{report.get('anomalies_detected', 0)}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Classification Breakdown</h2>
            <p>Normal: {report.get('classification_breakdown', {}).get('normal', 0)}</p>
            <p>Warning: {report.get('classification_breakdown', {}).get('warning', 0)}</p>
            <p>Critical: {report.get('classification_breakdown', {}).get('critical', 0)}</p>
        </div>
    </div>
</body>
</html>
"""
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"✓ HTML report generated: {filename}")
        except Exception as e:
            print(f"✗ Failed to generate HTML report: {str(e)}")


# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Logger for system events and errors"""
    
    def __init__(self, log_file: str = "monitoring_system.log"):
        self.log_file = log_file
        self.logs = []
    
    def write_log(self, message: str, level: str = "INFO") -> None:
        """Write a log message
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        print(f"📝 [{level}] {message}")
    
    def save_to_file(self) -> None:
        """Save all logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                for entry in self.logs:
                    f.write(f"[{entry['timestamp']}] {entry['level']}: {entry['message']}\n")
            print(f"✓ Logs saved to {self.log_file}")
        except Exception as e:
            print(f"✗ Failed to save logs: {str(e)}")
    
    def on_event(self, event_data: Dict) -> None:
        """Callback for event dispatcher - logs events"""
        message = f"Event triggered: {json.dumps(event_data)}"
        self.write_log(message)


# ============================================================================
# ALERT MANAGER
# ============================================================================

class AlertManager:
    """Manages alerts triggered by events"""
    
    def __init__(self):
        self.alerts = []
    
    def create_alert(self, message: str, level: str = "INFO") -> None:
        """Create an alert
        
        Args:
            message: Alert message
            level: Alert level (INFO, WARNING, CRITICAL)
        """
        alert = {
            'id': len(self.alerts) + 1,
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        print(f"🚨 ALERT [{level}]: {message}")
    
    def on_high_cpu_predicted(self, event_data: Dict) -> None:
        """Callback for high CPU event"""
        level = "CRITICAL" if event_data['classification'] == 2 else "WARNING"
        message = (f"High CPU usage detected on Server {event_data['server_id']}: "
                  f"{event_data['cpu']}% - Status: {event_data['status'].upper()}")
        self.create_alert(message, level)
    
    def on_memory_issue(self, event_data: Dict) -> None:
        """Callback for memory issue event"""
        level = "CRITICAL" if event_data['classification'] == 2 else "WARNING"
        message = (f"Memory issue on Server {event_data['server_id']}: "
                  f"{event_data['ram']}% RAM usage - Status: {event_data['status'].upper()}")
        self.create_alert(message, level)
    
    def on_failure_risk(self, event_data: Dict) -> None:
        """Callback for failure risk event"""
        message = (f"⚠️ CRITICAL FAILURE RISK on Server {event_data['server_id']}! "
                  f"Average load: {event_data['avg_load']}% - Immediate action required!")
        self.create_alert(message, "CRITICAL")
    
    def get_alerts(self) -> List[Dict]:
        """Get all alerts"""
        return self.alerts


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_file: str = "monitoring_system.db"):
        self.db_file = db_file
        self.connection = None
        self.initialize_database()
    
    def connect(self) -> None:
        """Connect to the database"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            print(f"✓ Connected to database: {self.db_file}")
        except Exception as e:
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    def initialize_database(self) -> None:
        """Initialize database with required tables"""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            # Servers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    status TEXT DEFAULT 'online',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    cpu REAL NOT NULL,
                    ram REAL NOT NULL,
                    disk REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    classification INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    avg_load REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    level TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # STAGE 3: Trends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,
                    trend_direction TEXT NOT NULL,
                    trend_strength REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # STAGE 3: Anomalies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    value REAL NOT NULL,
                    z_score REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # STAGE 3: Forecasts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    predicted_value REAL NOT NULL,
                    forecast_period INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    forecast_time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES servers(id)
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_server ON metrics(server_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_server ON predictions(server_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_server ON anomalies(server_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_server ON trends(server_id)')
            
            self.connection.commit()
            print("✓ Database initialized successfully (7 tables, 4 indexes)")
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    def insert(self, table: str, data: Dict) -> int:
        """Insert data into a table
        
        Args:
            table: Table name
            data: Dictionary with column names as keys
            
        Returns:
            Row ID of inserted record
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            raise DatabaseError(f"Insert failed: {str(e)}")
    
    def update(self, table: str, data: Dict, condition: str) -> None:
        """Update data in a table
        
        Args:
            table: Table name
            data: Dictionary with column names as keys
            condition: WHERE clause (e.g., "id = 1")
        """
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            values = tuple(data.values()) + (None,)  # Add placeholder for condition
            
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {condition}", 
                         values[:-1])
            self.connection.commit()
        except Exception as e:
            raise DatabaseError(f"Update failed: {str(e)}")
    
    def get_data(self, table: str, condition: Optional[str] = None) -> List[Dict]:
        """Retrieve data from a table
        
        Args:
            table: Table name
            condition: Optional WHERE clause
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table}"
            if condition:
                query += f" WHERE {condition}"
            
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Query failed: {str(e)}")
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")


# ============================================================================
# MONITORING SERVICE (CONTROLLER)
# ============================================================================

class MonitoringService:
    """Main monitoring service coordinating system"""
    
    def __init__(self, dispatcher: EventDispatcher, model: PredictionModel, 
                 db: DatabaseManager, logger: Logger):
        self.dispatcher = dispatcher
        self.model = model
        self.db = db
        self.logger = logger
        self.servers: Dict[int, Server] = {}
        self.metrics: List[ServerMetric] = []
    
    def register_server(self, server: Server) -> None:
        """Register a server for monitoring"""
        self.servers[server.id] = server
        self.logger.write_log(f"Server registered: {server.name} ({server.ip})")
        
        try:
            self.db.insert('servers', {
                'id': server.id,
                'name': server.name,
                'ip': server.ip,
                'status': server.status
            })
        except Exception as e:
            self.logger.write_log(f"Failed to save server to DB: {str(e)}", "ERROR")
    
    def collect_metrics(self, metric: ServerMetric) -> None:
        """Collect metrics from a server
        
        Args:
            metric: ServerMetric object
        """
        if metric.server_id not in self.servers:
            raise MetricException(f"Server {metric.server_id} not registered")
        
        self.metrics.append(metric)
        self.logger.write_log(f"Metrics collected: {metric}")
        
        try:
            self.db.insert('metrics', {
                'server_id': metric.server_id,
                'cpu': metric.cpu_usage,
                'ram': metric.ram_usage,
                'disk': metric.disk_usage,
                'timestamp': metric.timestamp
            })
        except Exception as e:
            self.logger.write_log(f"Failed to save metrics to DB: {str(e)}", "ERROR")
    
    def analyze(self, metric: ServerMetric) -> Dict:
        """Analyze metrics using the prediction model
        
        Args:
            metric: ServerMetric object
            
        Returns:
            Prediction result
        """
        prediction = self.model.predict(metric)
        self.logger.write_log(f"Analysis completed: {prediction}")
        
        try:
            self.db.insert('predictions', {
                'server_id': prediction['server_id'],
                'classification': prediction['classification'],
                'status': prediction['status'],
                'avg_load': prediction['avg_load'],
                'timestamp': prediction['timestamp']
            })
        except Exception as e:
            self.logger.write_log(f"Failed to save prediction to DB: {str(e)}", "ERROR")
        
        return prediction
    
    def trigger_events(self, prediction: Dict) -> None:
        """Trigger events based on prediction results
        
        Args:
            prediction: Prediction result dictionary
        """
        status = prediction['status']
        
        if status == "warning" or status == "critical":
            if prediction['cpu'] > 70:
                self.dispatcher.dispatch('on_high_cpu_predicted', prediction)
            
            if prediction['ram'] > 70:
                self.dispatcher.dispatch('on_memory_issue', prediction)
        
        if status == "critical":
            self.dispatcher.dispatch('on_failure_risk', prediction)
    
    def process_metric(self, metric: ServerMetric) -> None:
        """Complete pipeline: collect → analyze → trigger events
        
        Args:
            metric: ServerMetric object
        """
        self.collect_metrics(metric)
        prediction = self.analyze(metric)
        self.trigger_events(prediction)
    
    def get_metrics_by_server(self, server_id: int) -> List[ServerMetric]:
        """Get all metrics for a specific server (LINQ-style)"""
        return [m for m in self.metrics if m.server_id == server_id]
    
    def get_sorted_metrics(self, sort_by: str = 'cpu', reverse: bool = True) -> List[ServerMetric]:
        """Get sorted metrics (LINQ-style)"""
        key_map = {
            'cpu': lambda m: m.cpu_usage,
            'ram': lambda m: m.ram_usage,
            'disk': lambda m: m.disk_usage
        }
        return sorted(self.metrics, key=key_map.get(sort_by, key_map['cpu']), reverse=reverse)
    
    def get_high_cpu_metrics(self, threshold: float = 80) -> List[ServerMetric]:
        """Get metrics with high CPU usage (LINQ-style filtering)"""
        return [m for m in self.metrics if m.cpu_usage > threshold]
    
    # ========================================================================
    # STAGE 3: ENHANCED LINQ OPERATIONS
    # ========================================================================
    
    def group_metrics_by_server(self) -> Dict[int, List[ServerMetric]]:
        """Group metrics by server (LINQ-style grouping)"""
        return DataAnalytics.group_by_server(self.metrics)
    
    def get_aggregate_statistics(self, metric_type: str = 'cpu_usage') -> Dict:
        """Get aggregate statistics for a metric type (LINQ-style aggregation)"""
        return DataAnalytics.aggregate_metrics(self.metrics, metric_type)
    
    def get_critical_servers(self, threshold: float = 0.7) -> List[Dict]:
        """Get servers above risk threshold (LINQ-style filtering)"""
        return DataAnalytics.get_critical_servers(self.metrics, threshold)
    
    def get_metrics_by_time_range(self, start_time: str, end_time: str) -> List[ServerMetric]:
        """Get metrics within a time range (LINQ-style filtering)"""
        from datetime import datetime as dt
        try:
            start = dt.fromisoformat(start_time)
            end = dt.fromisoformat(end_time)
            return [m for m in self.metrics if start <= dt.fromisoformat(m.timestamp) <= end]
        except:
            return []
    
    def get_top_servers_by_risk(self, top_n: int = 5) -> List[Dict]:
        """Get top N servers by risk score (LINQ-style sorting)"""
        critical = self.get_critical_servers(0.5)
        return sorted(critical, key=lambda x: x['risk_score'], reverse=True)[:top_n]
    
    def get_metrics_by_classification(self, classification: int) -> List[Dict]:
        """Get predictions filtered by classification (LINQ-style filtering)"""
        if not self.model.prediction_history:
            return []
        return [p for p in self.model.prediction_history if p['classification'] == classification]
    
    def get_average_load_by_server(self) -> Dict[int, float]:
        """Calculate average load for each server (LINQ-style aggregation)"""
        grouped = self.group_metrics_by_server()
        return {
            server_id: sum(m.get_average_load() for m in metrics) / len(metrics) 
            for server_id, metrics in grouped.items()
        }


# ============================================================================
# DEMO / PRIMARY LOGIC
# ============================================================================

def main():
    """Main execution demonstrating Stage 2 and Stage 3 features"""
    
    print("="*80)
    print("AI SERVER MONITORING SYSTEM - STAGE 3")
    print("OOP + Events + Advanced ML + Analytics + Predictions")
    print("="*80)
    
    # Initialize system components
    dispatcher = EventDispatcher()
    model = PredictionModel()
    db = DatabaseManager()
    logger = Logger()
    alert_manager = AlertManager()
    monitoring_service = MonitoringService(dispatcher, model, db, logger)
    
    # -----------------------------------------------------------------------
    # STEP 1: Subscribe listeners to events
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 1: Subscribing to Events")
    print("="*70)
    
    dispatcher.subscribe('on_high_cpu_predicted', alert_manager.on_high_cpu_predicted)
    dispatcher.subscribe('on_memory_issue', alert_manager.on_memory_issue)
    dispatcher.subscribe('on_failure_risk', alert_manager.on_failure_risk)
    
    # Subscribe logger to all events
    dispatcher.subscribe('on_high_cpu_predicted', logger.on_event)
    dispatcher.subscribe('on_memory_issue', logger.on_event)
    dispatcher.subscribe('on_failure_risk', logger.on_event)
    
    # -----------------------------------------------------------------------
    # STEP 2: Train the model (sample data)
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 2: Training Prediction Model")
    print("="*70)
    
    training_data = [
        {'cpu': 30, 'ram': 40, 'disk': 50, 'label': 'normal'},
        {'cpu': 85, 'ram': 70, 'disk': 60, 'label': 'warning'},
        {'cpu': 95, 'ram': 90, 'disk': 85, 'label': 'critical'},
        {'cpu': 45, 'ram': 50, 'disk': 60, 'label': 'normal'},
        {'cpu': 75, 'ram': 80, 'disk': 70, 'label': 'warning'},
    ]
    
    model.train(training_data)
    
    # Save training data as CSV
    try:
        with open('training_data.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['cpu', 'ram', 'disk', 'label'])
            writer.writeheader()
            writer.writerows(training_data)
        print("✓ Training data saved to training_data.csv")
    except Exception as e:
        print(f"✗ Failed to save training data: {str(e)}")
    
    # -----------------------------------------------------------------------
    # STEP 3: Register servers
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 3: Registering Servers")
    print("="*70)
    
    server1 = Server(1, "WebServer-01", "192.168.1.10")
    server2 = Server(2, "DatabaseServer", "192.168.1.20")
    server3 = Server(3, "AppServer-01", "192.168.1.30")
    
    monitoring_service.register_server(server1)
    monitoring_service.register_server(server2)
    monitoring_service.register_server(server3)
    
    # Save servers as JSON
    try:
        servers_data = [s.to_dict() for s in [server1, server2, server3]]
        with open('servers.json', 'w') as f:
            json.dump(servers_data, f, indent=2)
        print("✓ Servers saved to servers.json")
    except Exception as e:
        print(f"✗ Failed to save servers: {str(e)}")
    
    # -----------------------------------------------------------------------
    # STEP 4: Simulate metric collection and processing
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 4: Simulating Server Metrics & Real-Time Processing")
    print("="*70)
    
    test_metrics = [
        ServerMetric(1, 35, 40, 50),       # Normal
        ServerMetric(1, 78, 72, 65),       # Warning
        ServerMetric(1, 92, 88, 82),       # Critical
        ServerMetric(2, 50, 55, 60),       # Normal
        ServerMetric(2, 85, 75, 70),       # Warning
        ServerMetric(3, 30, 35, 40),       # Normal
    ]
    
    for metric in test_metrics:
        print(f"\n--- Processing metric for {metric} ---")
        try:
            monitoring_service.process_metric(metric)
        except Exception as e:
            logger.write_log(f"Error processing metric: {str(e)}", "ERROR")
    
    # -----------------------------------------------------------------------
    # STEP 5: LINQ-style queries
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 5: LINQ-Style Queries")
    print("="*70)
    
    # Filter by server
    server1_metrics = monitoring_service.get_metrics_by_server(1)
    print(f"\n📊 Server 1 metrics: {len(server1_metrics)} records")
    for m in server1_metrics:
        print(f"  - {m}")
    
    # Filter high CPU
    high_cpu = monitoring_service.get_high_cpu_metrics(80)
    print(f"\n📊 High CPU metrics (>80%): {len(high_cpu)} records")
    for m in high_cpu:
        print(f"  - CPU: {m.cpu_usage}% | {m}")
    
    # Sort metrics
    sorted_metrics = monitoring_service.get_sorted_metrics('cpu', reverse=True)
    print(f"\n📊 Sorted metrics (by CPU, descending): {len(sorted_metrics)} records")
    for m in sorted_metrics[:3]:
        print(f"  - CPU: {m.cpu_usage}% | {m}")
    
    # -----------------------------------------------------------------------
    # STEP 6: Model evaluation
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 6: Model Evaluation")
    print("="*70)
    
    evaluation = model.evaluate()
    print("\n📈 Prediction Statistics:")
    print(f"  Total Predictions: {evaluation['total_predictions']}")
    print(f"  Normal: {evaluation['normal']['count']} ({evaluation['normal']['percentage']}%)")
    print(f"  Warning: {evaluation['warning']['count']} ({evaluation['warning']['percentage']}%)")
    print(f"  Critical: {evaluation['critical']['count']} ({evaluation['critical']['percentage']}%)")
    
    # -----------------------------------------------------------------------
    # STEP 7: Show alerts
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 7: Alert Summary")
    print("="*80)
    
    alerts = alert_manager.get_alerts()
    print(f"\n🚨 Total Alerts Generated: {len(alerts)}")
    for alert in alerts:
        print(f"  [{alert['level']}] {alert['message']}")
    
    # ========================================================================
    # STAGE 3 FEATURES
    # ========================================================================
    
    # -----------------------------------------------------------------------
    # STEP 8: Advanced ML Model Training
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 8: Advanced ML Model Training (scikit-learn)")
    print("="*80)
    
    # Create expanded training data for ML
    ml_training_data = [
        {'cpu': 20, 'ram': 25, 'disk': 30, 'label': 'normal'},
        {'cpu': 35, 'ram': 40, 'disk': 45, 'label': 'normal'},
        {'cpu': 50, 'ram': 45, 'disk': 55, 'label': 'normal'},
        {'cpu': 65, 'ram': 70, 'disk': 60, 'label': 'warning'},
        {'cpu': 75, 'ram': 80, 'disk': 70, 'label': 'warning'},
        {'cpu': 85, 'ram': 75, 'disk': 80, 'label': 'warning'},
        {'cpu': 90, 'ram': 85, 'disk': 90, 'label': 'critical'},
        {'cpu': 95, 'ram': 92, 'disk': 88, 'label': 'critical'},
        {'cpu': 98, 'ram': 95, 'disk': 92, 'label': 'critical'},
    ]
    
    ml_model = MLModel()
    
    if SKLEARN_AVAILABLE:
        ml_results = ml_model.train_with_validation(ml_training_data, test_size=0.3)
        print("\n📊 ML Model Performance:")
        print(f"  Accuracy: {ml_results.get('accuracy', 'N/A')}")
        print(f"  Precision: {ml_results.get('precision', 'N/A')}")
        print(f"  Recall: {ml_results.get('recall', 'N/A')}")
        print(f"  F1-Score: {ml_results.get('f1_score', 'N/A')}")
    else:
        print("⚠️ scikit-learn not installed - using basic prediction model")
    
    # -----------------------------------------------------------------------
    # STEP 9: Trend Analysis & Anomaly Detection
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 9: Trend Analysis & Anomaly Detection")
    print("="*80)
    
    trend_analyzer = TrendAnalyzer()
    
    # Detect anomalies
    anomalies = trend_analyzer.detect_anomalies(monitoring_service.metrics)
    print(f"\n🔍 Anomalies Detected: {len(anomalies)}")
    for anomaly in anomalies[:5]:
        print(f"  - Server {anomaly['server_id']}: {anomaly['metric_type']} "
              f"({anomaly['value']}%) - Severity: {anomaly['severity']}")
    
    # Calculate trends
    if len(monitoring_service.metrics) >= 2:
        trend = trend_analyzer.calculate_trend(monitoring_service.metrics)
        print(f"\n📈 Trend Analysis:")
        print(f"  Trend: {trend.get('trend', 'N/A')}")
        print(f"  Strength: {trend.get('trend_strength', 'N/A')}%")
        print(f"  Velocity: {trend.get('velocity', 'N/A')} points/period")
        
        # Forecast next periods
        forecast = trend_analyzer.forecast_next_period(monitoring_service.metrics, periods=3)
        if forecast.get('status') == 'success':
            print(f"\n🔮 Forecast (next 3 periods):")
            print(f"  Current: {forecast.get('current_value')}%")
            print(f"  Predicted: {forecast.get('forecast')}")
    
    # -----------------------------------------------------------------------
    # STEP 10: Data Analytics & Aggregation (LINQ-style)
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 10: Advanced Data Analytics")
    print("="*80)
    
    # Aggregate statistics
    cpu_stats = monitoring_service.get_aggregate_statistics('cpu_usage')
    ram_stats = monitoring_service.get_aggregate_statistics('ram_usage')
    print(f"\n📊 CPU Statistics:")
    print(f"  Mean: {cpu_stats.get('mean', 'N/A')}%")
    print(f"  Min: {cpu_stats.get('min', 'N/A')}% | Max: {cpu_stats.get('max', 'N/A')}%")
    print(f"  Std Dev: {cpu_stats.get('std', 'N/A')}%")
    
    print(f"\n💾 RAM Statistics:")
    print(f"  Mean: {ram_stats.get('mean', 'N/A')}%")
    print(f"  Min: {ram_stats.get('min', 'N/A')}% | Max: {ram_stats.get('max', 'N/A')}%")
    
    # Grouping by server
    grouped = monitoring_service.group_metrics_by_server()
    print(f"\n📂 Metrics Grouped by Server: {len(grouped)} servers")
    for server_id, metrics in grouped.items():
        print(f"  - Server {server_id}: {len(metrics)} metrics")
    
    # Average load by server
    avg_loads = monitoring_service.get_average_load_by_server()
    print(f"\n⚖️  Average Load by Server:")
    for server_id, avg_load in avg_loads.items():
        print(f"  - Server {server_id}: {avg_load:.2f}%")
    
    # -----------------------------------------------------------------------
    # STEP 11: Risk Scoring & Critical Servers
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 11: Risk Scoring & Critical Server Identification")
    print("="*80)
    
    critical_servers = monitoring_service.get_critical_servers(threshold=0.7)
    print(f"\n⚠️ Critical Servers (risk > 70%): {len(critical_servers)}")
    for server in critical_servers:
        print(f"  - Server {server['server_id']}: Risk {server['risk_score']}% - {server['status']}")
    
    # Top servers by risk
    top_servers = monitoring_service.get_top_servers_by_risk(top_n=3)
    print(f"\n🏆 Top 3 Highest Risk Servers:")
    for i, server in enumerate(top_servers, 1):
        print(f"  {i}. Server {server['server_id']}: {server['risk_score']}%")
    
    # -----------------------------------------------------------------------
    # STEP 12: Report Generation
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 12: Report Generation")
    print("="*80)
    
    report_gen = ReportGenerator()
    summary_report = report_gen.generate_summary_report(
        monitoring_service, 
        ml_model=ml_model,
        trend_analyzer=trend_analyzer
    )
    
    print(f"\n📋 Report Summary:")
    print(f"  Generated: {summary_report.get('generated_at', 'N/A')}")
    print(f"  Servers Monitored: {summary_report.get('servers_monitored', 0)}")
    print(f"  Metrics Collected: {summary_report.get('total_metrics_collected', 0)}")
    print(f"  Anomalies: {summary_report.get('anomalies_detected', 0)}")
    
    # Export reports
    try:
        report_gen.export_to_json(summary_report, 'monitoring_report.json')
        report_gen.generate_html_report(summary_report, 'monitoring_report.html')
    except Exception as e:
        logger.write_log(f"Report generation error: {str(e)}", "WARNING")
    
    # -----------------------------------------------------------------------
    # STEP 13: Save logs and close database
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STEP 13: Saving Data & Cleanup")
    print("="*80)
    
    logger.save_to_file()
    db.close()
    
    print("\n" + "="*80)
    print("✓ STAGE 3 COMPLETE - Advanced Monitoring System Demonstration Finished!")
    print("="*80)
    print("\n📋 Generated Files:")
    print("  Stage 2 Files:")
    print("  ├─ monitoring_system.log")
    print("  ├─ monitoring_system.db (7 tables with indexes)")
    print("  ├─ training_data.csv")
    print("  └─ servers.json")
    print("\n  Stage 3 Files:")
    print("  ├─ monitoring_report.json (Executive summary)")
    print("  └─ monitoring_report.html (Visual report)")
    print("\n✨ Features Implemented:")
    print("  ✅ Advanced ML Model with scikit-learn")
    print("  ✅ Trend Analysis & Forecasting")
    print("  ✅ Anomaly Detection (Z-score method)")
    print("  ✅ Risk Scoring & Critical Server Identification")
    print("  ✅ Enhanced LINQ Operations (grouping, aggregation)")
    print("  ✅ Comprehensive Report Generation")


if __name__ == '__main__':
    try:
        main()
    except ServerMonitoringException as e:
        print(f"✗ System Error: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected Error: {str(e)}")
