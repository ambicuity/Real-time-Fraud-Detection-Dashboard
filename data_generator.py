#!/usr/bin/env python3
"""
E-commerce Data Generator - Simulates realistic transaction data
Generates mock e-commerce transactions with realistic patterns and fraud scenarios
"""

import random
import uuid
from datetime import datetime, timedelta
import json


class ECommerceDataGenerator:
    """Generates realistic e-commerce transaction data"""
    
    def __init__(self):
        # Sample data for realistic transaction generation
        self.merchants = [
            'Amazon', 'eBay', 'Walmart', 'Target', 'Best Buy', 'Home Depot',
            'Macy\'s', 'Costco', 'Apple Store', 'Nike', 'Starbucks', 'McDonald\'s',
            'Shell Gas', 'BP Gas', 'Grocery Store', 'Electronics Depot'
        ]
        
        self.product_categories = [
            'Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden',
            'Sports & Outdoors', 'Books', 'Automotive', 'Health & Beauty',
            'Toys & Games', 'Travel', 'Gas & Fuel', 'Groceries'
        ]
        
        self.countries = [
            'USA', 'Canada', 'UK', 'Germany', 'France', 'Australia',
            'Japan', 'Brazil', 'India', 'China', 'Mexico', 'Spain'
        ]
        
        self.cities = {
            'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
            'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
            'UK': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Edinburgh'],
            'Germany': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
            'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide']
        }
        
        # User pool for realistic repeat customers
        self.user_pool = []
        self._initialize_user_pool()
        
        # Transaction patterns for fraud detection
        self.fraud_patterns = {
            'velocity_fraud': 0.02,  # Multiple transactions in short time
            'amount_fraud': 0.03,    # Unusually high amounts
            'location_fraud': 0.02,  # Transactions from unusual locations
            'time_fraud': 0.01       # Transactions at unusual times
        }
    
    def _initialize_user_pool(self):
        """Initialize a pool of realistic users"""
        for i in range(500):  # 500 unique users
            user = {
                'user_id': f'user_{i:04d}',
                'email': f'user{i}@example.com',
                'country': random.choice(self.countries),
                'registration_date': datetime.now() - timedelta(days=random.randint(1, 730)),
                'total_transactions': 0,
                'total_spent': 0,
                'last_transaction': None,
                'preferred_merchants': random.sample(self.merchants, random.randint(2, 5)),
                'risk_score': random.uniform(0, 0.3)  # Most users have low risk
            }
            
            # Set city based on country
            if user['country'] in self.cities:
                user['city'] = random.choice(self.cities[user['country']])
            else:
                user['city'] = 'Unknown City'
            
            self.user_pool.append(user)
    
    def generate_transaction(self):
        """Generate a single realistic e-commerce transaction"""
        # Select user (80% existing users, 20% new users)
        if random.random() < 0.8 and self.user_pool:
            user = random.choice(self.user_pool)
        else:
            user = self._create_new_user()
        
        # Generate basic transaction details
        transaction = {
            'transaction_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_id': user['user_id'],
            'email': user['email'],
            'merchant': self._select_merchant(user),
            'amount': self._generate_amount(),
            'category': random.choice(self.product_categories),
            'country': user['country'],
            'city': user['city'],
            'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'apple_pay']),
            'device_type': random.choice(['mobile', 'desktop', 'tablet']),
            'ip_address': self._generate_ip_address(),
            'session_duration': random.randint(30, 3600),  # 30 seconds to 1 hour
        }
        
        # Add potential fraud indicators
        transaction = self._add_fraud_indicators(transaction, user)
        
        # Update user statistics
        user['total_transactions'] += 1
        user['total_spent'] += transaction['amount']
        user['last_transaction'] = transaction['timestamp']
        
        return transaction
    
    def _create_new_user(self):
        """Create a new user and add to user pool"""
        user_id = f'user_{len(self.user_pool):04d}'
        country = random.choice(self.countries)
        
        user = {
            'user_id': user_id,
            'email': f'{user_id}@example.com',
            'country': country,
            'city': self.cities.get(country, ['Unknown City'])[0] if country in self.cities else 'Unknown City',
            'registration_date': datetime.now(),
            'total_transactions': 0,
            'total_spent': 0,
            'last_transaction': None,
            'preferred_merchants': random.sample(self.merchants, random.randint(1, 3)),
            'risk_score': random.uniform(0, 0.5)
        }
        
        self.user_pool.append(user)
        return user
    
    def _select_merchant(self, user):
        """Select merchant based on user preferences"""
        # 70% chance of using preferred merchant
        if random.random() < 0.7 and user['preferred_merchants']:
            return random.choice(user['preferred_merchants'])
        return random.choice(self.merchants)
    
    def _generate_amount(self):
        """Generate realistic transaction amounts"""
        # Distribution of transaction amounts
        distribution = random.random()
        
        if distribution < 0.6:  # 60% small purchases ($5-$100)
            return round(random.uniform(5, 100), 2)
        elif distribution < 0.85:  # 25% medium purchases ($100-$500)
            return round(random.uniform(100, 500), 2)
        elif distribution < 0.95:  # 10% large purchases ($500-$2000)
            return round(random.uniform(500, 2000), 2)
        else:  # 5% very large purchases ($2000-$10000)
            return round(random.uniform(2000, 10000), 2)
    
    def _generate_ip_address(self):
        """Generate realistic IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _add_fraud_indicators(self, transaction, user):
        """Add potential fraud indicators to make detection more realistic"""
        fraud_indicators = []
        
        # Velocity fraud: Multiple transactions in short time
        if user['last_transaction']:
            last_time = datetime.fromisoformat(user['last_transaction'])
            current_time = datetime.fromisoformat(transaction['timestamp'])
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff < 60:  # Less than 1 minute
                fraud_indicators.append('high_velocity')
                transaction['time_since_last'] = time_diff
        
        # Amount fraud: Unusually high amount for user
        avg_amount = user['total_spent'] / max(user['total_transactions'], 1)
        if transaction['amount'] > avg_amount * 5 and transaction['amount'] > 1000:
            fraud_indicators.append('unusual_amount')
        
        # Location fraud: Transaction from different country
        if random.random() < 0.05:  # 5% chance of location anomaly
            transaction['country'] = random.choice(self.countries)
            transaction['city'] = 'Unknown City'
            fraud_indicators.append('location_anomaly')
        
        # Time fraud: Transaction at unusual hours (2 AM - 6 AM)
        hour = datetime.fromisoformat(transaction['timestamp']).hour
        if 2 <= hour <= 6 and random.random() < 0.3:
            fraud_indicators.append('unusual_time')
        
        # Device fraud: Different device type than usual
        if random.random() < 0.1:  # 10% chance
            fraud_indicators.append('device_anomaly')
        
        # Payment method fraud: Using unusual payment method
        if random.random() < 0.05:  # 5% chance
            fraud_indicators.append('payment_anomaly')
        
        # High-risk merchant
        high_risk_merchants = ['Electronics Depot', 'Unknown Vendor']
        if transaction['merchant'] in high_risk_merchants:
            fraud_indicators.append('high_risk_merchant')
        
        transaction['fraud_indicators'] = fraud_indicators
        return transaction
    
    def generate_batch_transactions(self, count=100):
        """Generate a batch of transactions for testing"""
        transactions = []
        for _ in range(count):
            transactions.append(self.generate_transaction())
        return transactions
    
    def get_user_statistics(self):
        """Get statistics about the user pool"""
        total_users = len(self.user_pool)
        total_transactions = sum(user['total_transactions'] for user in self.user_pool)
        total_spent = sum(user['total_spent'] for user in self.user_pool)
        
        return {
            'total_users': total_users,
            'total_transactions': total_transactions,
            'total_amount': round(total_spent, 2),
            'avg_transactions_per_user': round(total_transactions / max(total_users, 1), 2),
            'avg_amount_per_transaction': round(total_spent / max(total_transactions, 1), 2)
        }


if __name__ == '__main__':
    # Test the data generator
    generator = ECommerceDataGenerator()
    
    print("🎲 Testing E-commerce Data Generator")
    print("=" * 50)
    
    # Generate sample transactions
    for i in range(5):
        transaction = generator.generate_transaction()
        print(f"Transaction {i+1}:")
        print(json.dumps(transaction, indent=2))
        print("-" * 30)
    
    # Print statistics
    stats = generator.get_user_statistics()
    print("📊 User Pool Statistics:")
    print(json.dumps(stats, indent=2))