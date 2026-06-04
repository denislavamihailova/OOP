"""
AI Server Monitoring System - Stage 2
OOP + Events + Callbacks + Primary Logic
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Callable, Optional
from abc import ABC, abstractmethod
import sqlite3


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
            
            self.connection.commit()
            print("✓ Database initialized successfully")
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


# ============================================================================
# DEMO / PRIMARY LOGIC
# ============================================================================

def main():
    """Main execution demonstrating the system"""
    
    print("="*70)
    print("AI SERVER MONITORING SYSTEM - STAGE 2")
    print("OOP + Events + Callbacks + Primary Logic")
    print("="*70)
    
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
    print("\n" + "="*70)
    print("STEP 7: Alert Summary")
    print("="*70)
    
    alerts = alert_manager.get_alerts()
    print(f"\n🚨 Total Alerts Generated: {len(alerts)}")
    for alert in alerts:
        print(f"  [{alert['level']}] {alert['message']}")
    
    # -----------------------------------------------------------------------
    # STEP 8: Save logs and close database
    # -----------------------------------------------------------------------
    print("\n" + "="*70)
    print("STEP 8: Saving Data & Cleanup")
    print("="*70)
    
    logger.save_to_file()
    db.close()
    
    print("\n" + "="*70)
    print("✓ STAGE 2 COMPLETE - System demonstration finished!")
    print("="*70)
    print("\n📋 Generated files:")
    print("  - monitoring_system.log")
    print("  - monitoring_system.db")
    print("  - training_data.csv")
    print("  - servers.json")


if __name__ == '__main__':
    try:
        main()
    except ServerMonitoringException as e:
        print(f"✗ System Error: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected Error: {str(e)}")
