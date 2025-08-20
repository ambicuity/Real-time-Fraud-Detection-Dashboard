# Real-time Fraud Detection Dashboard

A comprehensive real-time fraud detection system with data visualization, streaming data ingestion, and advanced analytics capabilities. This project demonstrates the implementation of a data-driven security system that can identify potential fraud attempts in e-commerce transactions.

## 🚀 Features

### Core Fraud Detection
- **Real-time Transaction Analysis**: Advanced fraud scoring algorithms that analyze transactions as they occur
- **Multiple Detection Models**: Velocity-based, amount-based, location-based, and behavioral pattern analysis
- **Dynamic Risk Scoring**: Adaptive fraud scores based on user history and transaction patterns
- **High-Risk Pattern Detection**: Identification of suspicious merchants, countries, and transaction patterns

### Data Visualization Dashboard
- **Real-time Charts**: Live updating fraud trend analysis and transaction distribution charts
- **Interactive UI**: Modern, responsive web interface with real-time updates
- **Alert System**: Immediate notifications for high-risk transactions
- **Statistical Overview**: Comprehensive dashboard showing fraud rates, amounts, and trends

### Data Processing & Streaming
- **Mock E-commerce Data**: Realistic transaction data generator simulating various merchants and user behaviors
- **Streaming Architecture**: Real-time data ingestion and processing capabilities
- **WebSocket Integration**: Live data streaming for instant dashboard updates
- **RESTful APIs**: Complete API endpoints for data access and system control

### Logging & Monitoring (Splunk Integration)
- **Structured JSON Logging**: Splunk-compatible log format for enterprise integration
- **Performance Metrics**: System monitoring and performance tracking
- **Security Events**: Detailed logging of fraud attempts and system events
- **Sample Splunk Queries**: Pre-built queries for common fraud analysis scenarios

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Generator │───▶│  Fraud Detector  │───▶│   Dashboard     │
│                 │    │                  │    │                 │
│ • E-commerce    │    │ • ML Algorithms  │    │ • Real-time UI  │
│ • Transactions  │    │ • Risk Scoring   │    │ • Charts/Alerts │
│ • User Patterns │    │ • Pattern Match  │    │ • WebSocket     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Splunk Logging  │
                       │                 │
                       │ • JSON Format   │
                       │ • Security Log  │
                       │ • Metrics       │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Python 3.x**: Core application framework
- **Flask**: Web server and API endpoints
- **Flask-SocketIO**: Real-time WebSocket communication
- **JSON Logging**: Structured logging for Splunk integration

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Real-time data visualization
- **WebSocket API**: Live data streaming
- **Moment.js**: Time formatting and manipulation

### Data & Analytics
- **JSON Data Format**: Lightweight data exchange
- **In-memory Processing**: Fast real-time analysis
- **Statistical Analysis**: Fraud pattern recognition
- **Time-series Analysis**: Trend detection and monitoring

## 📊 Fraud Detection Algorithms

### 1. Velocity Analysis
- Monitors transaction frequency per user
- Detects rapid-fire transaction attempts
- Configurable time windows and thresholds

### 2. Amount-based Detection
- Analyzes transaction amounts vs. user history
- Identifies unusually large transactions
- Detects micro-transaction patterns (card testing)

### 3. Location Risk Analysis
- Monitors geographical transaction patterns
- High-risk country identification
- Location change anomaly detection

### 4. Behavioral Analysis
- User behavior pattern learning
- Device and payment method analysis
- Account age and history consideration

### 5. Merchant Risk Scoring
- Merchant reputation and risk assessment
- Category-based risk evaluation
- Pattern-based suspicious merchant detection

## 🚀 Quick Start

### Simple Version (No Dependencies)
```bash
# Clone the repository
git clone https://github.com/ambicuity/Real-time-Fraud-Detection-Dashboard.git
cd Real-time-Fraud-Detection-Dashboard

# Run the simple dashboard (uses only built-in Python libraries)
python simple_fraud_dashboard.py

# Open browser to http://localhost:8000
```

### Full-Featured Version (Advanced)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the advanced dashboard
python app.py

# Open browser to http://localhost:5000
```

## 📱 Dashboard Usage

### Starting Monitoring
1. Open the dashboard in your web browser
2. Click "Start Monitoring" to begin real-time fraud detection
3. Watch as transactions are processed and analyzed in real-time

### Understanding the Interface
- **Statistics Cards**: Overview of total transactions, fraud detected, and amounts
- **Fraud Trend Chart**: Real-time visualization of transaction patterns
- **Recent Transactions**: Live feed of processed transactions with risk scores
- **Fraud Alerts**: Immediate notifications of high-risk transactions

### Fraud Scoring
- **0.0 - 0.3**: Low Risk (Green) - Safe transactions
- **0.3 - 0.7**: Medium Risk (Yellow) - Suspicious, monitor closely  
- **0.7 - 1.0**: High Risk (Red) - Likely fraud, immediate action required

## 🔍 API Endpoints

### Statistics
```http
GET /api/stats
```
Returns current system statistics including transaction counts and fraud rates.

### Transactions
```http
GET /api/transactions?limit=50&fraud_only=false
```
Retrieves recent transactions with optional filtering.

### Fraud Alerts
```http
GET /api/alerts?limit=20
```
Gets recent fraud alerts with detailed information.

### System Control
```http
GET /api/start_monitoring    # Start real-time processing
GET /api/stop_monitoring     # Stop real-time processing
```

## 📈 Splunk Integration

### Log Format
All events are logged in JSON format compatible with Splunk ingestion:

```json
{
  "timestamp": "2025-08-20T22:28:35.809Z",
  "level": "WARNING",
  "event_type": "fraud_detected",
  "transaction_id": "f64d8a74",
  "user_id": "user_090",
  "amount": 5316.64,
  "fraud_score": 0.850,
  "merchant": "Unknown Vendor",
  "application": "fraud_detection_dashboard"
}
```

### Sample Splunk Queries

**Fraud Alerts by Merchant**
```splunk
index=fraud_detection event_type=fraud_alert | stats count by merchant | sort -count
```

**High-Value Transactions**
```splunk
index=fraud_detection event_type=transaction_processed amount>1000 | sort -amount
```

**Fraud Rate by Time**
```splunk
index=fraud_detection event_type=fraud_alert | timechart count by hour
```

## 🧪 Testing the System

### Fraud Pattern Testing
The system automatically generates various fraud patterns:
- High-velocity transactions (multiple transactions in short time)
- Unusual amounts (significantly higher than user average)
- High-risk merchants ("Unknown Vendor", "Electronics Depot")
- Geographic anomalies (transactions from high-risk countries)
- Time-based patterns (transactions at unusual hours)

### Demo Scenarios
1. **Normal Shopping**: Regular transactions with low fraud scores
2. **Card Testing**: Multiple small transactions in quick succession
3. **Account Takeover**: Large transactions from new devices/locations
4. **Merchant Fraud**: Suspicious patterns from high-risk merchants

## 🔒 Security Features

### Data Protection
- No sensitive financial data stored permanently
- In-memory processing for real-time analysis
- Secure API endpoints with proper error handling

### Fraud Prevention
- Real-time transaction blocking capabilities
- Immediate alert system for high-risk transactions
- Comprehensive logging for audit trails

### Monitoring & Alerting
- System health monitoring
- Performance metrics tracking
- Automated fraud alert notifications

## 📊 Performance Metrics

### System Capabilities
- **Processing Speed**: 1000+ transactions per minute
- **Detection Latency**: Sub-second fraud analysis
- **Memory Usage**: Optimized for real-time processing
- **Scalability**: Horizontal scaling support

### Fraud Detection Accuracy
- **False Positive Rate**: Configurable thresholds
- **Detection Rate**: Multi-layered analysis approach
- **Response Time**: Real-time alerting system

## 🚀 Deployment Options

### Local Development
- Simple HTTP server for testing and development
- Built-in data generation for demo purposes
- No external dependencies required for basic functionality

### Production Deployment
- Flask-based web server with production WSGI
- Docker containerization support
- Kubernetes deployment configurations
- Load balancer and scaling support

### Cloud Integration
- AWS/Azure/GCP deployment ready
- Container orchestration support
- Auto-scaling based on transaction volume
- Integration with cloud logging services

## 🤝 Contributing

This project demonstrates advanced data analysis, real-time processing, and fraud detection capabilities. The system showcases:

- **Data Engineering**: Real-time data processing and streaming
- **Machine Learning**: Fraud detection algorithms and pattern recognition
- **Web Development**: Modern dashboard with real-time updates
- **System Integration**: Splunk logging and enterprise monitoring
- **Security**: Fraud prevention and anomaly detection

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🏆 Key Achievements

✅ **Real-time Processing**: Sub-second transaction analysis and fraud detection  
✅ **Advanced Analytics**: Multi-layered fraud detection algorithms  
✅ **Data Visualization**: Interactive charts and real-time dashboards  
✅ **Enterprise Integration**: Splunk-compatible logging and monitoring  
✅ **Scalable Architecture**: Designed for high-volume transaction processing  
✅ **Security Focus**: Comprehensive fraud prevention and detection system  

---

**Built with ❤️ for real-time fraud detection and security analytics**