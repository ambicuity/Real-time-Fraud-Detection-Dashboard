#!/usr/bin/env python3
"""
Real-time Fraud Detection Dashboard - Main Application
A comprehensive fraud detection system with real-time monitoring capabilities.
"""

import logging
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import uuid
import random

from fraud_detector import FraudDetector
from data_generator import ECommerceDataGenerator
from logger_config import setup_logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fraud_detection_secret_key'

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize components
fraud_detector = FraudDetector()
data_generator = ECommerceDataGenerator()

# Setup logging for Splunk integration
logger = setup_logging()

# Global variables for data storage
transactions = []
fraud_alerts = []
dashboard_stats = {
    'total_transactions': 0,
    'fraud_detected': 0,
    'total_amount': 0,
    'fraud_amount': 0,
    'last_updated': None
}

# Data generation control
data_generation_active = False
data_thread = None


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/stats')
def get_stats():
    """Get current dashboard statistics"""
    return jsonify(dashboard_stats)


@app.route('/api/transactions')
def get_transactions():
    """Get recent transactions with optional filtering"""
    limit = request.args.get('limit', 100, type=int)
    fraud_only = request.args.get('fraud_only', 'false').lower() == 'true'
    
    filtered_transactions = transactions
    if fraud_only:
        filtered_transactions = [t for t in transactions if t.get('is_fraud', False)]
    
    return jsonify(filtered_transactions[-limit:])


@app.route('/api/alerts')
def get_alerts():
    """Get recent fraud alerts"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(fraud_alerts[-limit:])


@app.route('/api/start_monitoring')
def start_monitoring():
    """Start real-time data generation and monitoring"""
    global data_generation_active, data_thread
    
    if not data_generation_active:
        data_generation_active = True
        data_thread = threading.Thread(target=data_generation_worker, daemon=True)
        data_thread.start()
        logger.info("Real-time monitoring started", extra={
            'action': 'monitoring_started',
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'status': 'started', 'message': 'Real-time monitoring activated'})
    
    return jsonify({'status': 'already_running', 'message': 'Monitoring is already active'})


@app.route('/api/stop_monitoring')
def stop_monitoring():
    """Stop real-time data generation and monitoring"""
    global data_generation_active
    
    data_generation_active = False
    logger.info("Real-time monitoring stopped", extra={
        'action': 'monitoring_stopped',
        'timestamp': datetime.now().isoformat()
    })
    return jsonify({'status': 'stopped', 'message': 'Real-time monitoring deactivated'})


def data_generation_worker():
    """Background worker for generating and processing e-commerce transactions"""
    global transactions, fraud_alerts, dashboard_stats
    
    logger.info("Data generation worker started", extra={
        'action': 'worker_started',
        'timestamp': datetime.now().isoformat()
    })
    
    while data_generation_active:
        try:
            # Generate new transaction
            transaction = data_generator.generate_transaction()
            
            # Perform fraud detection
            fraud_score = fraud_detector.analyze_transaction(transaction)
            transaction['fraud_score'] = fraud_score
            transaction['is_fraud'] = fraud_score > 0.7  # Threshold for fraud detection
            
            # Add to transactions list
            transactions.append(transaction)
            
            # Keep only last 1000 transactions in memory
            if len(transactions) > 1000:
                transactions = transactions[-1000:]
            
            # Update dashboard statistics
            dashboard_stats['total_transactions'] += 1
            dashboard_stats['total_amount'] += transaction['amount']
            dashboard_stats['last_updated'] = datetime.now().isoformat()
            
            # Handle fraud detection
            if transaction['is_fraud']:
                dashboard_stats['fraud_detected'] += 1
                dashboard_stats['fraud_amount'] += transaction['amount']
                
                # Create fraud alert
                alert = {
                    'id': str(uuid.uuid4()),
                    'transaction_id': transaction['transaction_id'],
                    'timestamp': transaction['timestamp'],
                    'fraud_score': fraud_score,
                    'amount': transaction['amount'],
                    'user_id': transaction['user_id'],
                    'merchant': transaction['merchant'],
                    'reason': fraud_detector.get_fraud_reason(transaction, fraud_score)
                }
                
                fraud_alerts.append(alert)
                
                # Keep only last 500 alerts
                if len(fraud_alerts) > 500:
                    fraud_alerts = fraud_alerts[-500:]
                
                # Log fraud detection for Splunk
                logger.warning("Fraud detected", extra={
                    'action': 'fraud_detected',
                    'transaction_id': transaction['transaction_id'],
                    'fraud_score': fraud_score,
                    'amount': transaction['amount'],
                    'user_id': transaction['user_id'],
                    'merchant': transaction['merchant'],
                    'timestamp': transaction['timestamp']
                })
                
                # Emit real-time fraud alert
                socketio.emit('fraud_alert', alert)
            
            # Log transaction for Splunk
            logger.info("Transaction processed", extra={
                'action': 'transaction_processed',
                'transaction_id': transaction['transaction_id'],
                'amount': transaction['amount'],
                'is_fraud': transaction['is_fraud'],
                'fraud_score': fraud_score,
                'timestamp': transaction['timestamp']
            })
            
            # Emit real-time transaction update
            socketio.emit('new_transaction', transaction)
            
            # Emit updated statistics
            socketio.emit('stats_update', dashboard_stats)
            
            # Wait before generating next transaction (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Error in data generation worker: {str(e)}", extra={
                'action': 'worker_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(5)  # Wait longer on error


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected", extra={
        'action': 'client_connected',
        'timestamp': datetime.now().isoformat()
    })
    
    # Send current statistics to new client
    emit('stats_update', dashboard_stats)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected", extra={
        'action': 'client_disconnected',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    logger.info("Starting Fraud Detection Dashboard", extra={
        'action': 'application_start',
        'timestamp': datetime.now().isoformat()
    })
    
    print("🚀 Real-time Fraud Detection Dashboard Starting...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔍 Monitor logs for Splunk integration")
    print("⚡ Real-time updates via WebSocket")
    
    # Start the Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)