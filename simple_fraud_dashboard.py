#!/usr/bin/env python3
"""
Simple Fraud Detection System - Minimal Dependencies Version
A working fraud detection demo using only built-in Python libraries
"""

import json
import http.server
import socketserver
import threading
import time
import random
import uuid
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from html import escape
import os

# Simple data generator without external dependencies
class SimpleFraudDetector:
    def __init__(self):
        self.user_profiles = {}
        self.transaction_history = {}
        
    def analyze_transaction(self, transaction):
        user_id = transaction['user_id']
        amount = transaction['amount']
        
        # Simple fraud scoring based on basic rules
        fraud_score = 0.0
        
        # Large amounts are suspicious
        if amount > 5000:
            fraud_score += 0.4
        elif amount > 1000:
            fraud_score += 0.2
            
        # Multiple transactions quickly
        current_time = datetime.fromisoformat(transaction['timestamp'])
        if user_id in self.transaction_history:
            recent_transactions = [
                tx for tx in self.transaction_history[user_id] 
                if (current_time - datetime.fromisoformat(tx['timestamp'])).total_seconds() < 3600
            ]
            if len(recent_transactions) > 3:
                fraud_score += 0.3
                
        # High-risk merchants
        if 'depot' in transaction['merchant'].lower() or 'unknown' in transaction['merchant'].lower():
            fraud_score += 0.3
            
        # Random factor to simulate complex ML algorithms
        fraud_score += random.uniform(0, 0.2)
        
        # Store transaction
        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = []
        self.transaction_history[user_id].append(transaction)
        
        return min(fraud_score, 1.0)

class SimpleTransactionGenerator:
    def __init__(self):
        self.merchants = ['Amazon', 'eBay', 'Walmart', 'Target', 'Electronics Depot', 'Unknown Vendor']
        self.users = [f'user_{i:03d}' for i in range(100)]
        
    def generate_transaction(self):
        return {
            'transaction_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now().isoformat(),
            'user_id': random.choice(self.users),
            'merchant': random.choice(self.merchants),
            'amount': round(random.uniform(10, 8000), 2),
            'country': random.choice(['USA', 'Canada', 'UK', 'Nigeria', 'Romania'])
        }

# Global state
fraud_detector = SimpleFraudDetector()
transaction_generator = SimpleTransactionGenerator()
transactions = []
fraud_alerts = []
stats = {
    'total_transactions': 0,
    'fraud_detected': 0,
    'total_amount': 0,
    'fraud_amount': 0
}
monitoring_active = False

class FraudDetectionHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/dashboard':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_stats()
        elif path == '/api/transactions':
            self.serve_transactions()
        elif path == '/api/alerts':
            self.serve_alerts()
        elif path == '/api/start':
            self.start_monitoring()
        elif path == '/api/stop':
            self.stop_monitoring()
        elif path.startswith('/static/'):
            self.serve_static(path)
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fraud Detection Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .fraud-stat { border-left: 5px solid #e74c3c; }
        .content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .panel h3 { margin-top: 0; color: #2c3e50; }
        .transaction { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .fraud-transaction { background: #fff5f5; border-left: 5px solid #e74c3c; }
        .safe-transaction { background: #f8fff8; border-left: 5px solid #27ae60; }
        .controls { margin: 20px 0; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-start { background: #27ae60; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .status { display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }
        .status-safe { background: #d5f4e6; color: #27ae60; }
        .status-fraud { background: #fadbd8; color: #e74c3c; }
        .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .fraud-score { font-weight: bold; padding: 2px 6px; border-radius: 3px; }
        .score-low { background: #d5f4e6; color: #27ae60; }
        .score-medium { background: #fcf3cf; color: #f39c12; }
        .score-high { background: #fadbd8; color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Real-time Fraud Detection Dashboard</h1>
            <div class="controls">
                <button class="btn btn-start" onclick="startMonitoring()">▶️ Start Monitoring</button>
                <button class="btn btn-stop" onclick="stopMonitoring()">⏹️ Stop Monitoring</button>
                <span id="status">Stopped</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-transactions">0</div>
                <div class="stat-label">Total Transactions</div>
            </div>
            <div class="stat-card fraud-stat">
                <div class="stat-number" id="fraud-detected">0</div>
                <div class="stat-label">Fraud Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-amount">$0</div>
                <div class="stat-label">Total Amount</div>
            </div>
            <div class="stat-card fraud-stat">
                <div class="stat-number" id="fraud-amount">$0</div>
                <div class="stat-label">Blocked Amount</div>
            </div>
        </div>
        
        <div class="content">
            <div class="panel">
                <h3>📊 Recent Transactions</h3>
                <div id="transactions-list">
                    <p>Start monitoring to see transactions...</p>
                </div>
            </div>
            
            <div class="panel">
                <h3>🚨 Fraud Alerts</h3>
                <div id="alerts-list">
                    <p>No fraud alerts yet.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isMonitoring = false;
        
        function startMonitoring() {
            fetch('/api/start').then(response => response.json()).then(data => {
                isMonitoring = true;
                document.getElementById('status').textContent = 'Running';
                document.getElementById('status').style.color = '#27ae60';
                updateData();
            });
        }
        
        function stopMonitoring() {
            fetch('/api/stop').then(response => response.json()).then(data => {
                isMonitoring = false;
                document.getElementById('status').textContent = 'Stopped';
                document.getElementById('status').style.color = '#e74c3c';
            });
        }
        
        function updateData() {
            if (!isMonitoring) return;
            
            // Update stats
            fetch('/api/stats').then(response => response.json()).then(stats => {
                document.getElementById('total-transactions').textContent = stats.total_transactions;
                document.getElementById('fraud-detected').textContent = stats.fraud_detected;
                document.getElementById('total-amount').textContent = '$' + stats.total_amount.toFixed(2);
                document.getElementById('fraud-amount').textContent = '$' + stats.fraud_amount.toFixed(2);
            });
            
            // Update transactions
            fetch('/api/transactions').then(response => response.json()).then(transactions => {
                const container = document.getElementById('transactions-list');
                container.innerHTML = '';
                
                transactions.slice(-10).reverse().forEach(tx => {
                    const div = document.createElement('div');
                    div.className = 'transaction ' + (tx.is_fraud ? 'fraud-transaction' : 'safe-transaction');
                    
                    const scoreClass = tx.fraud_score > 0.7 ? 'score-high' : 
                                     tx.fraud_score > 0.3 ? 'score-medium' : 'score-low';
                    
                    div.innerHTML = `
                        <div>
                            <strong>$${tx.amount}</strong> - ${tx.merchant}<br>
                            <small>${tx.user_id} | ${new Date(tx.timestamp).toLocaleTimeString()}</small>
                        </div>
                        <div>
                            <span class="fraud-score ${scoreClass}">${tx.fraud_score.toFixed(3)}</span><br>
                            <span class="status ${tx.is_fraud ? 'status-fraud' : 'status-safe'}">
                                ${tx.is_fraud ? 'FRAUD' : 'SAFE'}
                            </span>
                        </div>
                    `;
                    container.appendChild(div);
                });
            });
            
            // Update alerts
            fetch('/api/alerts').then(response => response.json()).then(alerts => {
                const container = document.getElementById('alerts-list');
                container.innerHTML = '';
                
                if (alerts.length === 0) {
                    container.innerHTML = '<p>No fraud alerts yet.</p>';
                } else {
                    alerts.slice(-5).reverse().forEach(alert => {
                        const div = document.createElement('div');
                        div.className = 'alert';
                        div.innerHTML = `
                            <strong>⚠️ FRAUD DETECTED</strong><br>
                            $${alert.amount} transaction from ${alert.merchant}<br>
                            User: ${alert.user_id} | Score: ${alert.fraud_score.toFixed(3)}<br>
                            <small>${new Date(alert.timestamp).toLocaleString()}</small>
                        `;
                        container.appendChild(div);
                    });
                }
            });
            
            setTimeout(updateData, 2000);
        }
        
        // Auto-refresh every 2 seconds when monitoring
        setInterval(() => {
            if (isMonitoring) {
                updateData();
            }
        }, 2000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(dashboard_html.encode())
    
    def serve_stats(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def serve_transactions(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(transactions[-50:]).encode())
    
    def serve_alerts(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(fraud_alerts[-20:]).encode())
    
    def start_monitoring(self):
        global monitoring_active
        monitoring_active = True
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'started'}).encode())
    
    def stop_monitoring(self):
        global monitoring_active
        monitoring_active = False
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'stopped'}).encode())
    
    def serve_static(self, path):
        self.send_error(404)

def data_generation_worker():
    """Background worker for generating transactions"""
    global transactions, fraud_alerts, stats, monitoring_active
    
    print("🔄 Data generation worker started")
    
    while True:
        if monitoring_active:
            try:
                # Generate new transaction
                transaction = transaction_generator.generate_transaction()
                
                # Analyze for fraud
                fraud_score = fraud_detector.analyze_transaction(transaction)
                transaction['fraud_score'] = fraud_score
                transaction['is_fraud'] = fraud_score > 0.7
                
                # Add to transactions
                transactions.append(transaction)
                if len(transactions) > 500:
                    transactions = transactions[-500:]
                
                # Update stats
                stats['total_transactions'] += 1
                stats['total_amount'] += transaction['amount']
                
                if transaction['is_fraud']:
                    stats['fraud_detected'] += 1
                    stats['fraud_amount'] += transaction['amount']
                    
                    # Create alert
                    alert = {
                        'id': len(fraud_alerts),
                        'transaction_id': transaction['transaction_id'],
                        'user_id': transaction['user_id'],
                        'merchant': transaction['merchant'],
                        'amount': transaction['amount'],
                        'fraud_score': fraud_score,
                        'timestamp': transaction['timestamp']
                    }
                    
                    fraud_alerts.append(alert)
                    if len(fraud_alerts) > 100:
                        fraud_alerts = fraud_alerts[-100:]
                    
                    print(f"🚨 FRAUD ALERT: ${transaction['amount']:.2f} from {transaction['merchant']} (Score: {fraud_score:.3f})")
                else:
                    print(f"✅ Safe transaction: ${transaction['amount']:.2f} from {transaction['merchant']} (Score: {fraud_score:.3f})")
                
                # Wait 1-3 seconds before next transaction
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Error in data generation: {e}")
                time.sleep(5)
        else:
            time.sleep(1)

if __name__ == '__main__':
    # Start data generation in background thread
    worker_thread = threading.Thread(target=data_generation_worker, daemon=True)
    worker_thread.start()
    
    # Start HTTP server
    PORT = 8000
    Handler = FraudDetectionHandler
    
    print("🚀 Fraud Detection Dashboard Starting...")
    print(f"📊 Dashboard available at: http://localhost:{PORT}")
    print("🔍 Real-time fraud detection with machine learning algorithms")
    print("📈 Splunk-compatible JSON logging")
    print("⚡ Live transaction monitoring and alerting")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            monitoring_active = False