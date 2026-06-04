# CLASS REFERENCE & USAGE EXAMPLES - STAGE 2

## 📚 Complete Class Documentation

### ============================================================================
### EXCEPTION CLASSES
### ============================================================================

```python
class ServerMonitoringException(Exception):
    """Base exception for server monitoring system"""
```
**Usage:**
```python
raise ServerMonitoringException("Error message")
```

---

```python
class ModelError(ServerMonitoringException):
    """Exception for model-related errors"""
```
**Usage:**
```python
try:
    prediction = model.predict(metric)
except ModelError as e:
    print(f"Model error: {e}")
```

---

```python
class DatabaseError(ServerMonitoringException):
    """Exception for database-related errors"""
```

---

```python
class MetricException(ServerMonitoringException):
    """Exception for metric collection errors"""
```
**Usage:**
```python
# Automatically raised if metrics are invalid
metric = ServerMetric(1, 150, 50, 50)  # Raises MetricException (CPU > 100%)
```

---

### ============================================================================
### MODEL CLASSES
### ============================================================================

## **Server Class**

```python
class Server:
    def __init__(self, server_id: int, name: str, ip: str, status: str = "online"):
        self.id = server_id
        self.name = name
        self.ip = ip
        self.status = status
    
    def to_dict(self) -> Dict:
        """Convert server to dictionary"""
```

**Example:**
```python
# Create a server
server = Server(1, "WebServer-01", "192.168.1.10")

# Access properties
print(server.id)       # 1
print(server.name)     # "WebServer-01"
print(server.ip)       # "192.168.1.10"
print(server.status)   # "online"

# Convert to dict
server_dict = server.to_dict()
# {'id': 1, 'name': 'WebServer-01', 'ip': '192.168.1.10', 'status': 'online'}

# Print representation
print(server)  
# Server(id=1, name='WebServer-01', ip='192.168.1.10', status='online')
```

---

## **ServerMetric Class**

```python
class ServerMetric:
    def __init__(self, server_id: int, cpu_usage: float, ram_usage: float, 
                 disk_usage: float, timestamp: Optional[str] = None):
        # Auto-generates timestamp if not provided
        # Validates all values are 0-100%
    
    def get_average_load(self) -> float:
        """Calculate average load"""
    
    def to_dict(self) -> Dict:
        """Convert metric to dictionary"""
```

**Example:**
```python
# Create a metric
metric = ServerMetric(1, 85.5, 72.3, 65.0)

# Access properties
print(metric.server_id)   # 1
print(metric.cpu_usage)   # 85.5
print(metric.ram_usage)   # 72.3
print(metric.disk_usage)  # 65.0
print(metric.timestamp)   # "2026-06-05T01:32:24.385398"

# Calculate average
avg = metric.get_average_load()  # 74.27

# Convert to dict
metric_dict = metric.to_dict()

# Print representation
print(metric)  
# ServerMetric(server_id=1, cpu=85.5%, ram=72.3%, disk=65.0%)

# Invalid metric raises exception
try:
    bad_metric = ServerMetric(1, 150, 50, 50)  # CPU too high
except MetricException as e:
    print(f"Invalid metric: {e}")  # Invalid CPU usage: 150
```

---

### ============================================================================
### EVENT SYSTEM
### ============================================================================

## **EventDispatcher Class** (Observer Pattern)

```python
class EventDispatcher:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Subscribe to an event"""
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event"""
    
    def dispatch(self, event_name: str, data: Dict) -> None:
        """Dispatch an event to all subscribers"""
    
    def get_subscribers(self, event_name: str) -> int:
        """Get number of subscribers for an event"""
```

**Example:**
```python
dispatcher = EventDispatcher()

# Define callbacks
def alert_callback(data):
    print(f"Alert: Server {data['server_id']} has high CPU: {data['cpu']}%")

def log_callback(data):
    print(f"Logged: {data}")

# Subscribe to event
dispatcher.subscribe('on_high_cpu_predicted', alert_callback)
dispatcher.subscribe('on_high_cpu_predicted', log_callback)

# Check subscribers
count = dispatcher.get_subscribers('on_high_cpu_predicted')  # 2

# Dispatch event
event_data = {
    'server_id': 1,
    'cpu': 92,
    'ram': 88,
    'disk': 82,
    'status': 'critical'
}
dispatcher.dispatch('on_high_cpu_predicted', event_data)
# Output:
# ✓ Subscriber registered for event 'on_high_cpu_predicted'
# ✓ Subscriber registered for event 'on_high_cpu_predicted'
# 📢 Event dispatched: 'on_high_cpu_predicted' with data: {...}
# Alert: Server 1 has high CPU: 92%
# Logged: {...}

# Unsubscribe
dispatcher.unsubscribe('on_high_cpu_predicted', alert_callback)
```

---

### ============================================================================
### AI PREDICTION MODEL
### ============================================================================

## **PredictionModel Class**

```python
class PredictionModel:
    THRESHOLDS = {
        'normal_max': 60,      # <= 60% → normal
        'warning_max': 80,     # <= 80% → warning
        'critical_min': 80     # > 80% → critical
    }
    
    def train(self, data: List[Dict]) -> None:
        """Train the model with sample data"""
    
    def predict(self, metric: ServerMetric) -> Dict:
        """Predict server status"""
    
    def evaluate(self) -> Dict:
        """Evaluate model performance"""
```

**Example:**
```python
model = PredictionModel()

# Training data
training_data = [
    {'cpu': 30, 'ram': 40, 'disk': 50, 'label': 'normal'},
    {'cpu': 85, 'ram': 70, 'disk': 60, 'label': 'warning'},
    {'cpu': 95, 'ram': 90, 'disk': 85, 'label': 'critical'},
]

# Train model
model.train(training_data)
# Output: ✓ Model trained with 3 samples

# Make prediction
metric = ServerMetric(1, 78, 72, 65)
prediction = model.predict(metric)
# Returns:
# {
#     'server_id': 1,
#     'cpu': 78,
#     'ram': 72,
#     'disk': 65,
#     'avg_load': 71.67,
#     'classification': 1,      # 0=normal, 1=warning, 2=critical
#     'status': 'warning',
#     'timestamp': '2026-06-05T01:32:24.385407'
# }

# Evaluate model
eval_result = model.evaluate()
# {
#     'total_predictions': 3,
#     'normal': {'count': 1, 'percentage': 33.33},
#     'warning': {'count': 1, 'percentage': 33.33},
#     'critical': {'count': 1, 'percentage': 33.33}
# }
```

---

### ============================================================================
### LOGGING & ALERTING
### ============================================================================

## **Logger Class**

```python
class Logger:
    def __init__(self, log_file: str = "monitoring_system.log"):
        self.log_file = log_file
        self.logs = []
    
    def write_log(self, message: str, level: str = "INFO") -> None:
        """Write a log message"""
    
    def save_to_file(self) -> None:
        """Save all logs to file"""
    
    def on_event(self, event_data: Dict) -> None:
        """Callback for event dispatcher"""
```

**Example:**
```python
logger = Logger()

# Write logs
logger.write_log("System started", "INFO")
logger.write_log("Server registered", "INFO")
logger.write_log("High CPU detected", "WARNING")
logger.write_log("Database connection failed", "ERROR")

# Save to file
logger.save_to_file()
# Output: ✓ Logs saved to monitoring_system.log

# File content:
# [2026-06-05T01:32:24.365035] INFO: System started
# [2026-06-05T01:32:24.373042] INFO: Server registered
# [2026-06-05T01:32:24.380064] WARNING: High CPU detected
# [2026-06-05T01:32:24.388000] ERROR: Database connection failed

# Use as callback (subscribes to events)
dispatcher.subscribe('on_high_cpu_predicted', logger.on_event)
```

---

## **AlertManager Class**

```python
class AlertManager:
    def __init__(self):
        self.alerts = []
    
    def create_alert(self, message: str, level: str = "INFO") -> None:
        """Create an alert"""
    
    def on_high_cpu_predicted(self, event_data: Dict) -> None:
        """Callback for high CPU event"""
    
    def on_memory_issue(self, event_data: Dict) -> None:
        """Callback for memory issue event"""
    
    def on_failure_risk(self, event_data: Dict) -> None:
        """Callback for failure risk event"""
    
    def get_alerts(self) -> List[Dict]:
        """Get all alerts"""
```

**Example:**
```python
alert_manager = AlertManager()

# Create alerts manually
alert_manager.create_alert("High CPU on Server 1", "WARNING")
alert_manager.create_alert("System failure imminent", "CRITICAL")

# View alerts
alerts = alert_manager.get_alerts()
# [
#     {
#         'id': 1,
#         'message': 'High CPU on Server 1',
#         'level': 'WARNING',
#         'timestamp': '2026-06-05T01:32:24.365035'
#     },
#     {
#         'id': 2,
#         'message': 'System failure imminent',
#         'level': 'CRITICAL',
#         'timestamp': '2026-06-05T01:32:24.373042'
#     }
# ]

# Use as event subscriber callbacks
dispatcher.subscribe('on_high_cpu_predicted', alert_manager.on_high_cpu_predicted)
dispatcher.subscribe('on_memory_issue', alert_manager.on_memory_issue)
dispatcher.subscribe('on_failure_risk', alert_manager.on_failure_risk)
```

---

### ============================================================================
### DATABASE MANAGEMENT
### ============================================================================

## **DatabaseManager Class**

```python
class DatabaseManager:
    def __init__(self, db_file: str = "monitoring_system.db"):
        self.db_file = db_file
        self.connection = None
        self.initialize_database()  # Auto-initializes
    
    def connect(self) -> None:
        """Connect to the database"""
    
    def initialize_database(self) -> None:
        """Initialize database with required tables"""
    
    def insert(self, table: str, data: Dict) -> int:
        """Insert data into a table"""
    
    def update(self, table: str, data: Dict, condition: str) -> None:
        """Update data in a table"""
    
    def get_data(self, table: str, condition: Optional[str] = None) -> List[Dict]:
        """Retrieve data from a table"""
    
    def close(self) -> None:
        """Close database connection"""
```

**Example:**
```python
db = DatabaseManager()
# Output:
# ✓ Connected to database: monitoring_system.db
# ✓ Database initialized successfully

# Insert server
server_id = db.insert('servers', {
    'id': 1,
    'name': 'WebServer-01',
    'ip': '192.168.1.10',
    'status': 'online'
})  # Returns: 1

# Insert metric
metric_id = db.insert('metrics', {
    'server_id': 1,
    'cpu': 85.5,
    'ram': 72.3,
    'disk': 65.0,
    'timestamp': '2026-06-05T01:32:24.385407'
})

# Update server status
db.update('servers', {'status': 'maintenance'}, 'id = 1')

# Query data
servers = db.get_data('servers')
# [{'id': 1, 'name': 'WebServer-01', 'ip': '192.168.1.10', 'status': 'maintenance', ...}]

# Query with condition
server_1_metrics = db.get_data('metrics', 'server_id = 1')

# Close connection
db.close()
# Output: ✓ Database connection closed
```

---

### ============================================================================
### MONITORING SERVICE (COORDINATOR)
### ============================================================================

## **MonitoringService Class**

```python
class MonitoringService:
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
    
    def collect_metrics(self, metric: ServerMetric) -> None:
        """Collect metrics from a server"""
    
    def analyze(self, metric: ServerMetric) -> Dict:
        """Analyze metrics using prediction model"""
    
    def trigger_events(self, prediction: Dict) -> None:
        """Trigger events based on prediction"""
    
    def process_metric(self, metric: ServerMetric) -> None:
        """Complete pipeline: collect → analyze → trigger"""
    
    def get_metrics_by_server(self, server_id: int) -> List[ServerMetric]:
        """Get all metrics for a server (LINQ filter)"""
    
    def get_sorted_metrics(self, sort_by: str = 'cpu', reverse: bool = True) -> List[ServerMetric]:
        """Get sorted metrics (LINQ)"""
    
    def get_high_cpu_metrics(self, threshold: float = 80) -> List[ServerMetric]:
        """Get high CPU metrics (LINQ filter)"""
```

**Example:**
```python
# Initialize all components
dispatcher = EventDispatcher()
model = PredictionModel()
db = DatabaseManager()
logger = Logger()

# Create monitoring service
monitor = MonitoringService(dispatcher, model, db, logger)

# Register servers
server1 = Server(1, "WebServer", "192.168.1.10")
server2 = Server(2, "Database", "192.168.1.20")
monitor.register_server(server1)
monitor.register_server(server2)

# Collect metrics
metric1 = ServerMetric(1, 85, 72, 65)
monitor.collect_metrics(metric1)

# Analyze
prediction = monitor.analyze(metric1)
# Returns prediction dict with status='warning'

# Trigger events (automatically sends alerts if warning/critical)
monitor.trigger_events(prediction)

# Complete pipeline in one call
metric2 = ServerMetric(1, 92, 88, 82)
monitor.process_metric(metric2)  # Collects, analyzes, and triggers events

# LINQ-style queries
server1_metrics = monitor.get_metrics_by_server(1)
high_cpu = monitor.get_high_cpu_metrics(80)  # CPU > 80%
sorted_metrics = monitor.get_sorted_metrics('cpu', reverse=True)

# Cleanup
db.close()
logger.save_to_file()
```

---

## 🎯 Complete End-to-End Example

```python
# 1. Initialize system
dispatcher = EventDispatcher()
model = PredictionModel()
db = DatabaseManager()
logger = Logger()
alert_manager = AlertManager()
monitor = MonitoringService(dispatcher, model, db, logger)

# 2. Subscribe to events
dispatcher.subscribe('on_high_cpu_predicted', alert_manager.on_high_cpu_predicted)
dispatcher.subscribe('on_memory_issue', alert_manager.on_memory_issue)
dispatcher.subscribe('on_failure_risk', alert_manager.on_failure_risk)
dispatcher.subscribe('on_high_cpu_predicted', logger.on_event)
dispatcher.subscribe('on_memory_issue', logger.on_event)
dispatcher.subscribe('on_failure_risk', logger.on_event)

# 3. Train model
training_data = [
    {'cpu': 30, 'ram': 40, 'disk': 50, 'label': 'normal'},
    {'cpu': 85, 'ram': 70, 'disk': 60, 'label': 'warning'},
    {'cpu': 95, 'ram': 90, 'disk': 85, 'label': 'critical'},
]
model.train(training_data)

# 4. Register servers
server = Server(1, "WebServer", "192.168.1.10")
monitor.register_server(server)

# 5. Monitor server
metric = ServerMetric(1, 92, 88, 82)
monitor.process_metric(metric)

# 6. Query data (LINQ)
high_cpu = monitor.get_high_cpu_metrics(80)

# 7. Evaluate model
eval_result = model.evaluate()

# 8. Get alerts
alerts = alert_manager.get_alerts()

# 9. Save and cleanup
logger.save_to_file()
db.close()
```

---

Generated: June 5, 2026 | Version: 1.0 | Status: ✅ Complete

