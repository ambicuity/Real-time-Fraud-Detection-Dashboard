#!/usr/bin/env python3
"""
Logger Configuration - Structured logging for Splunk integration
Configures JSON-formatted logging compatible with Splunk ingestion
"""

import logging
import json
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger


class SplunkJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter optimized for Splunk ingestion"""
    
    def add_fields(self, log_record, record, message_dict):
        super(SplunkJSONFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add application context
        log_record['application'] = 'fraud_detection_dashboard'
        log_record['version'] = '1.0.0'
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level']
        else:
            log_record['level'] = record.levelname
        
        # Ensure source field exists
        if not log_record.get('source'):
            log_record['source'] = record.name
        
        # Add environment information
        log_record['environment'] = 'development'  # Can be configured
        
        # Add host information
        import socket
        log_record['host'] = socket.gethostname()


def setup_logging(log_level=logging.INFO):
    """
    Setup structured logging for the fraud detection system
    Returns configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger('fraud_detection')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create JSON formatter for Splunk compatibility
    json_formatter = SplunkJSONFormatter(
        '%(timestamp)s %(level)s %(source)s %(message)s',
        rename_fields={
            'levelname': 'level',
            'name': 'source'
        }
    )
    
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for persistent logging
    try:
        file_handler = logging.FileHandler('fraud_detection.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, just continue with console logging
        logger.warning(f"Could not setup file logging: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_transaction(logger, transaction, fraud_score, is_fraud):
    """Helper function to log transaction events"""
    log_data = {
        'event_type': 'transaction_processed',
        'transaction_id': transaction['transaction_id'],
        'user_id': transaction['user_id'],
        'merchant': transaction['merchant'],
        'amount': transaction['amount'],
        'currency': 'USD',
        'country': transaction['country'],
        'payment_method': transaction['payment_method'],
        'device_type': transaction['device_type'],
        'fraud_score': round(fraud_score, 3),
        'is_fraud': is_fraud,
        'processing_time_ms': 0  # Could be measured
    }
    
    if is_fraud:
        logger.warning("Fraudulent transaction detected", extra=log_data)
    else:
        logger.info("Transaction processed successfully", extra=log_data)


def log_fraud_alert(logger, alert):
    """Helper function to log fraud alerts"""
    log_data = {
        'event_type': 'fraud_alert',
        'alert_id': alert['id'],
        'transaction_id': alert['transaction_id'],
        'user_id': alert['user_id'],
        'merchant': alert['merchant'],
        'amount': alert['amount'],
        'fraud_score': alert['fraud_score'],
        'reason': alert['reason'],
        'severity': 'high' if alert['fraud_score'] > 0.8 else 'medium'
    }
    
    logger.error("FRAUD ALERT - Suspicious activity detected", extra=log_data)


def log_system_event(logger, event_type, **kwargs):
    """Helper function to log system events"""
    log_data = {
        'event_type': event_type,
        **kwargs
    }
    
    logger.info(f"System event: {event_type}", extra=log_data)


def log_user_activity(logger, user_id, activity, **kwargs):
    """Helper function to log user activities"""
    log_data = {
        'event_type': 'user_activity',
        'user_id': user_id,
        'activity': activity,
        **kwargs
    }
    
    logger.info(f"User activity: {activity}", extra=log_data)


def log_performance_metric(logger, metric_name, value, unit='ms'):
    """Helper function to log performance metrics"""
    log_data = {
        'event_type': 'performance_metric',
        'metric_name': metric_name,
        'value': value,
        'unit': unit
    }
    
    logger.info(f"Performance metric: {metric_name}", extra=log_data)


def log_security_event(logger, event_type, severity, details):
    """Helper function to log security events"""
    log_data = {
        'event_type': 'security_event',
        'security_event_type': event_type,
        'severity': severity,
        'details': details
    }
    
    if severity == 'high':
        logger.error(f"Security event: {event_type}", extra=log_data)
    elif severity == 'medium':
        logger.warning(f"Security event: {event_type}", extra=log_data)
    else:
        logger.info(f"Security event: {event_type}", extra=log_data)


# Example Splunk queries for common fraud detection scenarios
SPLUNK_QUERIES = {
    'fraud_alerts': 'index=fraud_detection event_type=fraud_alert | stats count by merchant, reason',
    'high_value_transactions': 'index=fraud_detection event_type=transaction_processed amount>1000 | sort -amount',
    'fraud_by_country': 'index=fraud_detection event_type=fraud_alert | stats count by country | sort -count',
    'user_fraud_history': 'index=fraud_detection event_type=fraud_alert user_id=* | stats count, avg(fraud_score) by user_id',
    'merchant_risk_analysis': 'index=fraud_detection event_type=transaction_processed | stats count, avg(fraud_score) by merchant',
    'time_based_fraud': 'index=fraud_detection event_type=fraud_alert | eval hour=strftime(_time,"%H") | stats count by hour',
    'payment_method_analysis': 'index=fraud_detection event_type=transaction_processed | stats count, avg(fraud_score) by payment_method',
    'device_fraud_patterns': 'index=fraud_detection event_type=fraud_alert | stats count by device_type'
}


if __name__ == '__main__':
    # Test the logging configuration
    print("🔍 Testing Logging Configuration")
    print("=" * 50)
    
    # Setup logger
    logger = setup_logging()
    
    # Test different log levels and events
    logger.info("Application startup", extra={
        'event_type': 'application_start',
        'version': '1.0.0'
    })
    
    # Simulate transaction log
    sample_transaction = {
        'transaction_id': 'tx_123456',
        'user_id': 'user_0001',
        'merchant': 'Amazon',
        'amount': 299.99,
        'country': 'USA',
        'payment_method': 'credit_card',
        'device_type': 'mobile'
    }
    
    log_transaction(logger, sample_transaction, 0.85, True)
    
    # Simulate fraud alert
    sample_alert = {
        'id': 'alert_123',
        'transaction_id': 'tx_123456',
        'user_id': 'user_0001',
        'merchant': 'Amazon',
        'amount': 299.99,
        'fraud_score': 0.85,
        'reason': 'Unusual amount for user'
    }
    
    log_fraud_alert(logger, sample_alert)
    
    # Test system events
    log_system_event(logger, 'monitoring_started', component='data_generator')
    log_user_activity(logger, 'user_0001', 'login', ip_address='192.168.1.1')
    log_performance_metric(logger, 'fraud_detection_time', 45)
    log_security_event(logger, 'multiple_failed_transactions', 'medium', 
                      'User attempted 5 transactions in 2 minutes')
    
    print("\n📋 Sample Splunk Queries:")
    for name, query in SPLUNK_QUERIES.items():
        print(f"\n{name}:")
        print(f"  {query}")
    
    print("\n✅ Logging test completed. Check fraud_detection.log file.")