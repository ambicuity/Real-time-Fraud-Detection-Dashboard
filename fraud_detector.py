#!/usr/bin/env python3
"""
Fraud Detector - Advanced fraud detection algorithms
Implements multiple fraud detection techniques and scoring mechanisms
"""

import random
import math
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json


class FraudDetector:
    """Advanced fraud detection engine with multiple algorithms"""
    
    def __init__(self):
        # Transaction history for pattern analysis
        self.transaction_history = defaultdict(lambda: deque(maxlen=100))
        self.user_profiles = defaultdict(dict)
        self.merchant_risk_scores = defaultdict(float)
        self.ip_reputation = defaultdict(float)
        
        # Fraud detection thresholds
        self.thresholds = {
            'velocity_limit': 5,        # Max transactions per hour
            'amount_multiplier': 10,     # Max amount vs. average
            'location_risk': 0.8,       # Risk score for location changes
            'time_risk': 0.6,           # Risk score for unusual times
            'device_risk': 0.4,         # Risk score for device changes
            'merchant_risk': 0.7,       # Risk score for high-risk merchants
            'new_user_risk': 0.3        # Risk score for new users
        }
        
        # Known high-risk indicators
        self.high_risk_countries = ['Nigeria', 'Romania', 'China', 'Russia']
        self.high_risk_merchants = ['Electronics Depot', 'Unknown Vendor', 'Overseas Electronics']
        self.suspicious_patterns = []
        
        # Initialize risk models
        self._initialize_risk_models()
    
    def _initialize_risk_models(self):
        """Initialize risk scoring models"""
        # Set baseline merchant risk scores
        for merchant in self.high_risk_merchants:
            self.merchant_risk_scores[merchant] = 0.8
        
        # Standard merchants have lower risk
        standard_merchants = ['Amazon', 'eBay', 'Walmart', 'Target', 'Apple Store']
        for merchant in standard_merchants:
            self.merchant_risk_scores[merchant] = 0.1
    
    def analyze_transaction(self, transaction):
        """
        Analyze a transaction and return fraud score (0.0 - 1.0)
        Higher scores indicate higher fraud probability
        """
        fraud_score = 0.0
        risk_factors = []
        
        user_id = transaction['user_id']
        current_time = datetime.fromisoformat(transaction['timestamp'])
        
        # Update user profile
        self._update_user_profile(user_id, transaction)
        
        # 1. Velocity Analysis
        velocity_score = self._analyze_velocity(user_id, current_time)
        fraud_score += velocity_score * 0.25
        if velocity_score > 0.5:
            risk_factors.append('high_velocity')
        
        # 2. Amount Analysis
        amount_score = self._analyze_amount(user_id, transaction['amount'])
        fraud_score += amount_score * 0.20
        if amount_score > 0.7:
            risk_factors.append('unusual_amount')
        
        # 3. Location Analysis
        location_score = self._analyze_location(user_id, transaction)
        fraud_score += location_score * 0.15
        if location_score > 0.6:
            risk_factors.append('location_risk')
        
        # 4. Time Pattern Analysis
        time_score = self._analyze_time_pattern(current_time)
        fraud_score += time_score * 0.10
        if time_score > 0.5:
            risk_factors.append('unusual_time')
        
        # 5. Merchant Risk Analysis
        merchant_score = self._analyze_merchant_risk(transaction['merchant'])
        fraud_score += merchant_score * 0.15
        if merchant_score > 0.6:
            risk_factors.append('high_risk_merchant')
        
        # 6. Device/IP Analysis
        device_score = self._analyze_device_pattern(user_id, transaction)
        fraud_score += device_score * 0.10
        if device_score > 0.5:
            risk_factors.append('device_anomaly')
        
        # 7. User Behavior Analysis
        behavior_score = self._analyze_user_behavior(user_id, transaction)
        fraud_score += behavior_score * 0.05
        if behavior_score > 0.7:
            risk_factors.append('behavior_anomaly')
        
        # Apply fraud indicators from data generator
        if 'fraud_indicators' in transaction:
            indicator_score = len(transaction['fraud_indicators']) * 0.15
            fraud_score += indicator_score
            risk_factors.extend(transaction['fraud_indicators'])
        
        # Normalize score to 0-1 range
        fraud_score = min(fraud_score, 1.0)
        
        # Store transaction for future analysis
        self.transaction_history[user_id].append({
            'timestamp': current_time,
            'amount': transaction['amount'],
            'merchant': transaction['merchant'],
            'country': transaction['country'],
            'fraud_score': fraud_score,
            'risk_factors': risk_factors
        })
        
        return fraud_score
    
    def _update_user_profile(self, user_id, transaction):
        """Update user profile with transaction data"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'first_seen': datetime.fromisoformat(transaction['timestamp']),
                'transaction_count': 0,
                'total_amount': 0,
                'countries': set(),
                'merchants': defaultdict(int),
                'avg_amount': 0,
                'devices': set(),
                'payment_methods': set(),
                'last_transaction': None
            }
        
        profile = self.user_profiles[user_id]
        profile['transaction_count'] += 1
        profile['total_amount'] += transaction['amount']
        profile['avg_amount'] = profile['total_amount'] / profile['transaction_count']
        profile['countries'].add(transaction['country'])
        profile['merchants'][transaction['merchant']] += 1
        profile['devices'].add(transaction['device_type'])
        profile['payment_methods'].add(transaction['payment_method'])
        profile['last_transaction'] = datetime.fromisoformat(transaction['timestamp'])
    
    def _analyze_velocity(self, user_id, current_time):
        """Analyze transaction velocity (frequency)"""
        if user_id not in self.transaction_history:
            return 0.0
        
        recent_transactions = []
        cutoff_time = current_time - timedelta(hours=1)
        
        for tx in self.transaction_history[user_id]:
            if tx['timestamp'] > cutoff_time:
                recent_transactions.append(tx)
        
        transaction_count = len(recent_transactions)
        
        if transaction_count >= self.thresholds['velocity_limit']:
            return min(transaction_count / self.thresholds['velocity_limit'], 1.0)
        
        return 0.0
    
    def _analyze_amount(self, user_id, amount):
        """Analyze transaction amount patterns"""
        if user_id not in self.user_profiles:
            # New user with large amount
            if amount > 1000:
                return 0.8
            return 0.0
        
        profile = self.user_profiles[user_id]
        avg_amount = profile['avg_amount']
        
        if avg_amount == 0:
            return 0.0
        
        # Calculate how much larger this transaction is compared to average
        ratio = amount / avg_amount
        
        if ratio > self.thresholds['amount_multiplier']:
            return min(ratio / self.thresholds['amount_multiplier'], 1.0) * 0.8
        
        # Very small amounts can also be suspicious (card testing)
        if amount < 1:
            return 0.6
        
        return 0.0
    
    def _analyze_location(self, user_id, transaction):
        """Analyze location-based risk"""
        country = transaction['country']
        
        # High-risk countries
        if country in self.high_risk_countries:
            return 0.9
        
        # Check for location changes
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if len(profile['countries']) > 0 and country not in profile['countries']:
                # New country for existing user
                return 0.7
        
        return 0.0
    
    def _analyze_time_pattern(self, transaction_time):
        """Analyze time-based risk patterns"""
        hour = transaction_time.hour
        day_of_week = transaction_time.weekday()
        
        # High risk hours (2 AM - 6 AM)
        if 2 <= hour <= 6:
            return 0.8
        
        # Moderate risk hours (late night/early morning)
        if hour >= 23 or hour <= 5:
            return 0.4
        
        # Weekend nights might be slightly more risky
        if day_of_week >= 5 and (hour >= 22 or hour <= 3):
            return 0.3
        
        return 0.0
    
    def _analyze_merchant_risk(self, merchant):
        """Analyze merchant-based risk"""
        base_risk = self.merchant_risk_scores.get(merchant, 0.0)
        
        # High-risk merchant categories
        if merchant in self.high_risk_merchants:
            return 0.8
        
        # Unknown merchants are riskier
        if 'unknown' in merchant.lower() or 'depot' in merchant.lower():
            return 0.6
        
        return base_risk
    
    def _analyze_device_pattern(self, user_id, transaction):
        """Analyze device and IP patterns"""
        if user_id not in self.user_profiles:
            return 0.0
        
        profile = self.user_profiles[user_id]
        device_type = transaction['device_type']
        ip_address = transaction['ip_address']
        
        # Check for new device
        if device_type not in profile['devices']:
            return 0.4
        
        # IP reputation check (simplified)
        ip_risk = self.ip_reputation.get(ip_address, 0.0)
        
        return ip_risk
    
    def _analyze_user_behavior(self, user_id, transaction):
        """Analyze user behavior patterns"""
        if user_id not in self.user_profiles:
            # Brand new user
            return self.thresholds['new_user_risk']
        
        profile = self.user_profiles[user_id]
        
        # Check account age
        account_age = (datetime.fromisoformat(transaction['timestamp']) - profile['first_seen']).days
        if account_age < 1:  # Less than 1 day old
            return 0.6
        elif account_age < 7:  # Less than 1 week old
            return 0.3
        
        # Check for unusual payment method
        if transaction['payment_method'] not in profile['payment_methods']:
            return 0.2
        
        return 0.0
    
    def get_fraud_reason(self, transaction, fraud_score):
        """Get human-readable explanation for fraud detection"""
        if fraud_score < 0.3:
            return "Low risk transaction"
        elif fraud_score < 0.5:
            return "Moderate risk - monitoring recommended"
        elif fraud_score < 0.7:
            return "High risk - manual review suggested"
        else:
            reasons = []
            
            if 'fraud_indicators' in transaction:
                indicators = transaction['fraud_indicators']
                if 'high_velocity' in indicators:
                    reasons.append("Multiple transactions in short time")
                if 'unusual_amount' in indicators:
                    reasons.append("Unusually high transaction amount")
                if 'location_anomaly' in indicators:
                    reasons.append("Transaction from unusual location")
                if 'unusual_time' in indicators:
                    reasons.append("Transaction at unusual time")
                if 'device_anomaly' in indicators:
                    reasons.append("New device used")
                if 'high_risk_merchant' in indicators:
                    reasons.append("High-risk merchant")
            
            if transaction['country'] in self.high_risk_countries:
                reasons.append(f"Transaction from high-risk country ({transaction['country']})")
            
            if transaction['amount'] > 5000:
                reasons.append("Very high transaction amount")
            
            if not reasons:
                reasons.append("Multiple risk factors detected")
            
            return "; ".join(reasons)
    
    def get_user_risk_profile(self, user_id):
        """Get comprehensive risk profile for a user"""
        if user_id not in self.user_profiles:
            return {'error': 'User not found'}
        
        profile = self.user_profiles[user_id]
        transaction_history = list(self.transaction_history[user_id])
        
        # Calculate risk metrics
        avg_fraud_score = 0
        if transaction_history:
            avg_fraud_score = sum(tx['fraud_score'] for tx in transaction_history) / len(transaction_history)
        
        high_risk_transactions = sum(1 for tx in transaction_history if tx['fraud_score'] > 0.7)
        
        return {
            'user_id': user_id,
            'account_age_days': (datetime.now() - profile['first_seen']).days,
            'total_transactions': profile['transaction_count'],
            'total_amount': round(profile['total_amount'], 2),
            'avg_amount': round(profile['avg_amount'], 2),
            'countries_used': len(profile['countries']),
            'merchants_used': len(profile['merchants']),
            'devices_used': len(profile['devices']),
            'payment_methods_used': len(profile['payment_methods']),
            'avg_fraud_score': round(avg_fraud_score, 3),
            'high_risk_transactions': high_risk_transactions,
            'risk_level': 'High' if avg_fraud_score > 0.5 else 'Medium' if avg_fraud_score > 0.3 else 'Low'
        }
    
    def get_system_stats(self):
        """Get fraud detection system statistics"""
        total_users = len(self.user_profiles)
        total_transactions = sum(len(history) for history in self.transaction_history.values())
        
        if total_transactions == 0:
            return {
                'total_users': 0,
                'total_transactions': 0,
                'fraud_rate': 0.0,
                'avg_fraud_score': 0.0
            }
        
        fraud_transactions = 0
        total_fraud_score = 0
        
        for history in self.transaction_history.values():
            for tx in history:
                total_fraud_score += tx['fraud_score']
                if tx['fraud_score'] > 0.7:
                    fraud_transactions += 1
        
        return {
            'total_users': total_users,
            'total_transactions': total_transactions,
            'fraud_transactions': fraud_transactions,
            'fraud_rate': round(fraud_transactions / total_transactions * 100, 2),
            'avg_fraud_score': round(total_fraud_score / total_transactions, 3)
        }


if __name__ == '__main__':
    # Test the fraud detector
    from data_generator import ECommerceDataGenerator
    
    print("🔍 Testing Fraud Detection Engine")
    print("=" * 50)
    
    detector = FraudDetector()
    generator = ECommerceDataGenerator()
    
    # Generate and analyze test transactions
    for i in range(10):
        transaction = generator.generate_transaction()
        fraud_score = detector.analyze_transaction(transaction)
        is_fraud = fraud_score > 0.7
        
        print(f"Transaction {i+1}: ${transaction['amount']:.2f} from {transaction['merchant']}")
        print(f"User: {transaction['user_id']}, Country: {transaction['country']}")
        print(f"Fraud Score: {fraud_score:.3f} ({'FRAUD' if is_fraud else 'SAFE'})")
        
        if is_fraud:
            reason = detector.get_fraud_reason(transaction, fraud_score)
            print(f"Reason: {reason}")
        
        print("-" * 30)
    
    # Print system statistics
    stats = detector.get_system_stats()
    print("📊 System Statistics:")
    print(json.dumps(stats, indent=2))