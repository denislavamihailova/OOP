# AI SERVER MONITORING SYSTEM - STAGE 2
## Complete OOP Implementation with Events and Callbacks

---

## 📋 PROJECT OVERVIEW

This is a complete implementation of **Stage 2** of the AI Server Monitoring System project. The system demonstrates professional Object-Oriented Programming principles with an event-driven architecture using the Observer Pattern.

### Stage 2 Focus Areas:
✅ **Object-Oriented Programming (OOP)**  
✅ **Design Patterns (Observer Pattern)**  
✅ **Event Management & Callbacks**  
✅ **Exception Handling**  
✅ **Database Integration (SQLite)**  
✅ **LINQ-Style Data Queries**  

---

## 🏗️ SYSTEM ARCHITECTURE

### Core Components

```
┌─────────────────────────────────────┐
│   MonitoringService (Controller)    │
│  - Orchestrates all components      │
│  - Manages workflow                 │
└─────────────────────────────────────┘
         ↓
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
EventDispatcher  PredictionModel  DatabaseManager  Logger
(Observer)       (AI)             (Persistence)    (Logging)
    ↓
┌──────────┴──────────┐
▼                     ▼
AlertManager         Logger
(Subscriber)        (Subscriber)
```

---

## 📦 IMPLEMENTED CLASSES

### 1. **Models**
- **Server**: Represents a monitored server with basic properties
- **ServerMetric**: Encapsulates CPU, RAM, Disk metrics with validation

### 2. **Event System**
- **EventDispatcher**: Implements Observer Pattern for event management
- Events: `on_high_cpu_predicted`, `on_memory_issue`, `on_failure_risk`

### 3. **AI/ML**
- **PredictionModel**: Classifies server status (normal/warning/critical)
  - Trained with sample data
  - Makes real-time predictions
  - Provides evaluation metrics

### 4. **Listeners/Subscribers**
- **AlertManager**: Creates alerts based on events
- **Logger**: Logs all system events and errors

### 5. **Data Management**
- **DatabaseManager**: SQLite database operations
  - Auto-initializes with 4 tables
  - CRUD operations support
  - Connection management

### 6. **Orchestration**
- **MonitoringService**: Coordinator class
  - Manages metric collection
  - Triggers predictions
  - Dispatches events
  - Implements LINQ-style queries

### 7. **Exception Handling**
- **ServerMonitoringException**: Base exception
- **ModelError**: Model-related errors
- **DatabaseError**: Database-related errors
- **MetricException**: Metric validation errors

---

## 🔄 EVENT SYSTEM (Observer Pattern)

### How Events Work:

```python
# 1. Create dispatcher
dispatcher = EventDispatcher()

# 2. Define callbacks
def my_callback(data):
    print(f"Event triggered with data: {data}")

# 3. Subscribe to event
dispatcher.subscribe('event_name', my_callback)

# 4. Dispatch event
dispatcher.dispatch('event_name', {'key': 'value'})

# Callback automatically executes!
```

### Events in the System:

| Event | Trigger | Callback | Action |
|-------|---------|----------|--------|
| `on_high_cpu_predicted` | CPU > 70% | AlertManager | Creates alert |
| `on_memory_issue` | RAM > 70% | AlertManager | Creates alert |
| `on_failure_risk` | Status = critical | AlertManager | Creates CRITICAL alert |
| All events | Always | Logger | Logs event |

---

## 🎯 CLASSIFICATION LOGIC

```
Average Load = (CPU + RAM + DISK) / 3

Classification:
  ≤ 60%  → 0 (normal)
  60-80% → 1 (warning)
  > 80%  → 2 (critical)
```

---

## 📊 DATABASE SCHEMA

### Tables Created:

**servers**
```sql
id, name, ip, status, created_at
```

**metrics**
```sql
id, server_id, cpu, ram, disk, timestamp
```

**predictions**
```sql
id, server_id, classification, status, avg_load, timestamp
```

**alerts**
```sql
id, message, level, timestamp
```

---

## 🚀 QUICK START

### Running the System:

```bash
cd C:\Users\Students\PycharmProjects\OOP
python main.py
```

### Expected Output:
- System initialization
- Server registration
- Metric processing
- Event dispatching
- Alert generation
- LINQ queries
- Model evaluation

---

## 📝 USAGE EXAMPLES

### Example 1: Create and Register a Server

```python
from main import Server, MonitoringService, EventDispatcher

# Create server
server = Server(1, "WebServer", "192.168.1.10", "online")

# Register in monitoring service
monitor.register_server(server)
```

### Example 2: Collect and Process Metrics

```python
from main import ServerMetric

# Create metric
metric = ServerMetric(1, 85, 72, 65)

# Process (complete pipeline)
monitor.process_metric(metric)
# Automatically: collects → analyzes → triggers events
```

### Example 3: Subscribe to Events

```python
# Define callback
def on_critical(data):
    print(f"CRITICAL: Server {data['server_id']} is in critical state!")

# Subscribe
dispatcher.subscribe('on_failure_risk', on_critical)

# When critical metrics arrive, callback fires automatically
```

### Example 4: LINQ-Style Queries

```python
# Get metrics for specific server
server1_metrics = monitor.get_metrics_by_server(1)

# Get high CPU metrics
high_cpu = monitor.get_high_cpu_metrics(80)

# Get sorted metrics
sorted_metrics = monitor.get_sorted_metrics('cpu', reverse=True)
```

---

## 📁 PROJECT FILES

| File | Purpose |
|------|---------|
| `main.py` | Main implementation (all classes) |
| `STAGE_2_SUMMARY.md` | Stage 2 overview and accomplishments |
| `ARCHITECTURE.md` | System architecture diagrams |
| `CLASS_REFERENCE.md` | Complete class documentation with examples |
| `README.md` | This file |
| `monitoring_system.db` | SQLite database |
| `monitoring_system.log` | System logs |
| `servers.json` | Registered servers (JSON) |
| `training_data.csv` | Training data (CSV) |

---

## ✨ KEY FEATURES

✅ **Professional OOP Structure**
- Classes with proper encapsulation
- Clear separation of concerns
- Type hints throughout

✅ **Observer Pattern**
- Event dispatcher with subscribers
- Callback functions
- Loose coupling

✅ **Comprehensive Error Handling**
- Custom exception classes
- Try-catch blocks throughout
- Graceful error reporting

✅ **Data Persistence**
- SQLite database integration
- CSV and JSON file support
- Database recovery on restart

✅ **LINQ-Style Operations**
- Pythonic list comprehensions
- Sorting and filtering
- Data transformation

✅ **AI Prediction**
- Status classification
- Prediction history tracking
- Model evaluation

✅ **Logging & Alerts**
- Event logging
- Alert management
- File persistence

---

## 🔍 RUNNING WITH DETAILS

### Step-by-Step Execution:

```
STEP 1: Subscribing to Events
  ├─ AlertManager subscribed to 3 events
  └─ Logger subscribed to 3 events

STEP 2: Training Prediction Model
  └─ Model trained with 5 sample records

STEP 3: Registering Servers
  ├─ WebServer-01 registered
  ├─ DatabaseServer registered
  └─ AppServer-01 registered

STEP 4: Processing Server Metrics
  ├─ Metric 1: cpu=35%, ram=40%, disk=50% → NORMAL
  ├─ Metric 2: cpu=78%, ram=72%, disk=65% → WARNING (alerts triggered)
  ├─ Metric 3: cpu=92%, ram=88%, disk=82% → CRITICAL (alerts triggered)
  └─ ... (more metrics)

STEP 5: LINQ-Style Queries
  ├─ Filtered metrics by server
  ├─ Filtered high CPU metrics
  └─ Sorted metrics by CPU

STEP 6: Model Evaluation
  ├─ Total Predictions: 6
  ├─ Normal: 3 (50%)
  ├─ Warning: 2 (33.33%)
  └─ Critical: 1 (16.67%)

STEP 7: Alert Summary
  └─ 7 alerts generated

STEP 8: Saving Data & Cleanup
  ├─ Logs saved to file
  └─ Database connection closed
```

---

## 🎓 LEARNING OUTCOMES

This implementation demonstrates:

1. **OOP Principles**
   - Encapsulation (private methods, state management)
   - Inheritance (exception hierarchy)
   - Abstraction (interfaces via abstract base classes)
   - Polymorphism (different implementations via callbacks)

2. **Design Patterns**
   - Observer Pattern (EventDispatcher + Subscribers)
   - Singleton-like behavior (DatabaseManager)
   - Callback/Handler Pattern (Event callbacks)

3. **Python Best Practices**
   - Type hints for code clarity
   - Docstrings for documentation
   - Exception handling with custom classes
   - Context managers (database operations)

4. **Data Structures**
   - Dictionaries for flexible data representation
   - Lists for collections
   - Sets for unique identifiers

5. **Database Programming**
   - SQLite integration
   - Schema design
   - Query operations (CRUD)

6. **Functional Programming**
   - Lambda functions (sorting)
   - List comprehensions (LINQ-style)
   - Higher-order functions (callbacks)

---

## 🔧 CUSTOMIZATION

### Adding a New Event:

```python
# 1. Dispatch the event
dispatcher.dispatch('on_new_event', event_data)

# 2. Create callback
def my_new_callback(data):
    print(f"Handling: {data}")

# 3. Subscribe
dispatcher.subscribe('on_new_event', my_new_callback)
```

### Adding a New Listener:

```python
class MyListener:
    def on_event(self, event_data):
        print(f"Custom handler: {event_data}")

listener = MyListener()
dispatcher.subscribe('event_name', listener.on_event)
```

### Modifying Classification Thresholds:

```python
# In PredictionModel class
THRESHOLDS = {
    'normal_max': 60,      # Change this
    'warning_max': 80,     # Or this
    'critical_min': 80
}
```

---

## ✅ ASSESSMENT CHECKLIST

Stage 2 Requirements:
- ✅ Classes (8 main classes implemented)
- ✅ Events (3 event types with Observer pattern)
- ✅ Callbacks (4 callback functions working)
- ✅ Primary logic (Complete pipeline implemented)
- ✅ Exception handling (Custom exceptions with try-catch)
- ✅ Database integration (SQLite with 4 tables)
- ✅ Data persistence (JSON, CSV, SQLite)
- ✅ LINQ operations (Filtering, sorting, grouping)
- ✅ Documentation (Comprehensive docstrings)
- ✅ Type hints (Throughout codebase)

---

## 🚀 READY FOR STAGE 3

All Stage 2 requirements met and implemented. Ready to proceed with Stage 3 enhancements!

**Potential Stage 3 Enhancements:**
- Real-time monitoring
- Historical trend analysis
- Predictive alerts
- REST API endpoints
- Web dashboard
- Advanced ML models
- Performance optimization
- Distributed monitoring

---

## 📞 SUPPORT

For questions or issues:
1. Check `CLASS_REFERENCE.md` for detailed examples
2. Review `ARCHITECTURE.md` for system design
3. Examine `STAGE_2_SUMMARY.md` for implementation details
4. Run `main.py` to see live demonstration

---

## 📄 LICENSE & NOTES

- Implementation: June 5, 2026
- Version: 1.0
- Status: ✅ Complete and Tested
- Python Version: 3.x

---

**🎉 Stage 2 Successfully Completed!**

All classes, events, callbacks, and primary logic implemented and tested.
Database integration working with 4 tables.
Ready for Stage 3 submission!

