# ARCHITECTURE DOCUMENTATION - STAGE 2

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│         AI SERVER MONITORING SYSTEM - STAGE 2                  │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │  MonitoringService   │
                    │   (Controller)       │
                    └──────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌─────────────┐  ┌──────────────┐
    │  Servers   │  │  Metrics    │  │ Prediction   │
    │            │  │             │  │ Model (AI)   │
    └────────────┘  └─────────────┘  └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                ┌───────────┴────────────┐
                ▼                        ▼
        ┌──────────────────┐    ┌─────────────────┐
        │ EventDispatcher  │    │ DatabaseManager │
        │ (Observer        │    │ (Persistence)   │
        │  Pattern)        │    └─────────────────┘
        └──────────────────┘           │
                │                      ▼
        ┌───────┴───────┐      ┌──────────────────┐
        ▼               ▼      │   SQLite DB      │
    ┌────────────┐ ┌──────────┐├──────────────────┤
    │AlertManager│ │Logger    ││ • servers        │
    │(Listener)  │ │(Listener)││ • metrics        │
    └────────────┘ └──────────┘│ • predictions    │
        │               │       │ • alerts         │
        └───────┬───────┘       └──────────────────┘
                ▼
        ┌──────────────────┐
        │   Alerts + Logs  │
        │   Output Files   │
        └──────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING PIPELINE                 │
└──────────────────────────────────────────────────────────────┘

1. METRIC COLLECTION
   ┌─────────────────┐
   │ Raw Metrics     │ ← (CPU%, RAM%, DISK%)
   │ (ServerMetric)  │
   └────────┬────────┘
            ▼
2. VALIDATION
   ┌──────────────────────┐
   │ Validate ranges      │ ← (0-100%)
   │ Throw exceptions     │
   └────────┬─────────────┘
            ▼
3. PREDICTION
   ┌────────────────────────────┐
   │ Calculate average load     │ ← ((CPU+RAM+DISK)/3)
   │ Classify status            │
   │ Store in history           │
   └────────┬───────────────────┘
            ▼
4. EVENT DISPATCH
   ┌────────────────────────────┐
   │ Check thresholds:          │
   │ • CPU > 70% ?              │
   │ • RAM > 70% ?              │
   │ • Status = critical ?      │
   └────────┬───────────────────┘
            ▼
5. CALLBACK EXECUTION
   ┌─────────────────┬──────────────────┐
   ▼                 ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌─────────┐
│ AlertManager │ │   Logger     │ │Database │
│              │ │              │ │Manager  │
│create_alert()│ │write_log()   │ │insert() │
└──────────────┘ └──────────────┘ └─────────┘
```

---

## 📦 Class Hierarchy

```
ServerMonitoringException (Base)
    ├── ModelError
    ├── DatabaseError
    └── MetricException

Models:
    ├── Server
    │   ├─ Attributes: id, name, ip, status
    │   ├─ Methods: to_dict()
    │   └─ Representation: __repr__()
    │
    └── ServerMetric
        ├─ Attributes: server_id, cpu_usage, ram_usage, disk_usage, timestamp
        ├─ Methods: get_average_load(), to_dict()
        └─ Validation: Ranges 0-100%

System Components:
    ├── EventDispatcher
    │   ├─ _subscribers: Dict[str, List[Callable]]
    │   ├─ subscribe()
    │   ├─ dispatch()
    │   └─ unsubscribe()
    │
    ├── PredictionModel
    │   ├─ THRESHOLDS: Configuration
    │   ├─ train(data)
    │   ├─ predict(metric)
    │   └─ evaluate()
    │
    ├── AlertManager (Observer)
    │   ├─ alerts: List[Dict]
    │   ├─ create_alert()
    │   ├─ on_high_cpu_predicted() [Callback]
    │   ├─ on_memory_issue() [Callback]
    │   └─ on_failure_risk() [Callback]
    │
    ├── Logger (Observer)
    │   ├─ logs: List[Dict]
    │   ├─ write_log()
    │   ├─ save_to_file()
    │   └─ on_event() [Callback]
    │
    ├── DatabaseManager
    │   ├─ connect()
    │   ├─ initialize_database()
    │   ├─ insert()
    │   ├─ update()
    │   ├─ get_data()
    │   └─ close()
    │
    └── MonitoringService (Coordinator)
        ├─ dispatcher, model, db, logger
        ├─ register_server()
        ├─ collect_metrics()
        ├─ analyze()
        ├─ trigger_events()
        ├─ process_metric()
        ├─ get_metrics_by_server() [LINQ]
        ├─ get_sorted_metrics() [LINQ]
        └─ get_high_cpu_metrics() [LINQ]
```

---

## 🎯 Observer Pattern Implementation

```
┌─────────────────────────────────────────────┐
│           OBSERVER PATTERN                  │
└─────────────────────────────────────────────┘

Subject: EventDispatcher
┌─────────────────────────────┐
│ _subscribers = {            │
│   'on_high_cpu_predicted': │
│     [callback1, callback2],  │
│   'on_memory_issue': [...], │
│   'on_failure_risk': [...]  │
│ }                           │
└─────────────────────────────┘

Observers:
┌─────────────────┐       ┌──────────────┐
│ AlertManager    │       │  Logger      │
│ (Listener)      │       │ (Listener)   │
│                 │       │              │
│ Methods:        │       │ Methods:     │
│ • on_high_cpu   │       │ • on_event() │
│ • on_memory     │       │              │
│ • on_failure    │       │              │
└─────────────────┘       └──────────────┘

Event Flow:
EventDispatcher.dispatch('on_high_cpu_predicted', data)
        │
        ├─→ AlertManager.on_high_cpu_predicted(data)
        │              ↓
        │         create_alert()
        │
        └─→ Logger.on_event(data)
                   ↓
                write_log()
```

---

## 📊 Database Schema

```sql
CREATE TABLE servers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    status TEXT DEFAULT 'online',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    cpu REAL NOT NULL,
    ram REAL NOT NULL,
    disk REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);

CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    classification INTEGER NOT NULL,  -- 0,1,2
    status TEXT NOT NULL,              -- normal,warning,critical
    avg_load REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    level TEXT NOT NULL,               -- INFO,WARNING,CRITICAL
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 Event Triggering Logic

```python
# Classification Rules
if avg_load <= 60%:
    classification = 0  # NORMAL
    status = "normal"
elif avg_load <= 80%:
    classification = 1  # WARNING
    status = "warning"
else:
    classification = 2  # CRITICAL
    status = "critical"

# Event Triggering
if status in ["warning", "critical"]:
    if cpu > 70%:
        dispatch('on_high_cpu_predicted')  # Alert + Log
    if ram > 70%:
        dispatch('on_memory_issue')        # Alert + Log

if status == "critical":
    dispatch('on_failure_risk')             # Alert + Log (CRITICAL)
```

---

## 📝 Type Annotations Used

```python
# Function signatures with type hints:

def subscribe(self, event_name: str, callback: Callable) -> None:
    """Subscribe to an event"""
    
def dispatch(self, event_name: str, data: Dict) -> None:
    """Dispatch an event"""
    
def train(self, data: List[Dict]) -> None:
    """Train the model"""
    
def predict(self, metric: ServerMetric) -> Dict:
    """Predict status"""
    
def get_data(self, table: str, condition: Optional[str] = None) -> List[Dict]:
    """Get data from database"""
```

---

## 🎯 LINQ-Style Operations

```python
# Filtering
high_cpu = [m for m in metrics if m.cpu_usage > 80]

# Sorting
sorted_metrics = sorted(metrics, key=lambda m: m.cpu_usage, reverse=True)

# Grouping (via comprehension)
by_server = {sid: [m for m in metrics if m.server_id == sid] 
             for sid in set(m.server_id for m in metrics)}
```

---

## ✅ Status Chart

```
Average Load        Classification     Alert Level
─────────────────────────────────────────────────
0-60%              0 (normal)          None
61-80%             1 (warning)         ⚠️  WARNING
81-100%            2 (critical)        🚨 CRITICAL

Alert Thresholds:
─────────────────────────────────────────────────
CPU > 70%          → on_high_cpu_predicted
RAM > 70%          → on_memory_issue
Status = critical  → on_failure_risk
```

---

## 📂 File Structure

```
OOP/
├── main.py                      (Main implementation)
├── STAGE_2_SUMMARY.md          (This summary)
├── ARCHITECTURE.md             (This file)
├── monitoring_system.db        (SQLite database)
├── monitoring_system.log       (Log file)
├── servers.json                (Server configuration)
└── training_data.csv           (Training data)
```

---

## 🚀 Execution Flow

```
main()
  │
  ├─ Initialize components
  │   ├─ EventDispatcher()
  │   ├─ PredictionModel()
  │   ├─ DatabaseManager()
  │   ├─ Logger()
  │   ├─ AlertManager()
  │   └─ MonitoringService()
  │
  ├─ Subscribe to events
  │   ├─ AlertManager callbacks × 3
  │   └─ Logger callback × 3
  │
  ├─ Train model with sample data
  │
  ├─ Register 3 servers
  │
  ├─ Process 6 test metrics
  │   └─ For each: collect → analyze → trigger_events
  │
  ├─ LINQ queries
  │   ├─ Filter by server
  │   ├─ Filter high CPU
  │   └─ Sort by CPU
  │
  ├─ Model evaluation
  │
  ├─ Show alerts
  │
  └─ Cleanup
      └─ Save logs, close database
```

---

Generated: June 5, 2026 | Version: 1.0 | Status: ✅ Complete

