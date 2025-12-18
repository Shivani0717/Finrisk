"""ETL Pipeline for Financial Data"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import logging
from database import get_db_connection, get_db_cursor

logger = logging.getLogger(__name__)
fake = Faker()

class FinancialDataGenerator:
    """Generate realistic financial transaction data"""
    
    PAYMENT_METHODS = ['CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'PAYPAL', 'CRYPTO', 'WALLET']
    PAYMENT_STATUSES = ['SUCCESS', 'FAILED', 'PENDING', 'REFUNDED']
    BUSINESS_TYPES = ['E-COMMERCE', 'RETAIL', 'SUBSCRIPTION', 'MARKETPLACE', 'FINANCIAL_SERVICES', 'TRAVEL']
    FAILURE_REASONS = [
        'Insufficient funds',
        'Card declined',
        'Authentication failed',
        'Network timeout',
        'Invalid card details',
        'Fraud detection triggered',
        'Daily limit exceeded'
    ]
    COUNTRIES = ['USA', 'UK', 'CANADA', 'GERMANY', 'FRANCE', 'INDIA', 'SINGAPORE', 'AUSTRALIA']
    
    def __init__(self, num_customers=500, num_merchants=50, num_transactions=5000):
        self.num_customers = num_customers
        self.num_merchants = num_merchants
        self.num_transactions = num_transactions
    
    def generate_customers(self):
        """Generate customer data"""
        customers = []
        for i in range(self.num_customers):
            credit_score = random.randint(300, 850)
            if credit_score >= 720:
                risk_category = 'LOW'
            elif credit_score >= 600:
                risk_category = 'MEDIUM'
            else:
                risk_category = 'HIGH'
            
            customers.append({
                'customer_id': f'CUST{i+1:05d}',
                'customer_name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number()[:20],
                'country': random.choice(self.COUNTRIES),
                'registration_date': fake.date_time_between(start_date='-2y', end_date='now'),
                'credit_score': credit_score,
                'risk_category': risk_category
            })
        
        return pd.DataFrame(customers)
    
    def generate_merchants(self):
        """Generate merchant data"""
        merchants = []
        for i in range(self.num_merchants):
            merchants.append({
                'merchant_id': f'MERCH{i+1:04d}',
                'merchant_name': fake.company(),
                'business_type': random.choice(self.BUSINESS_TYPES),
                'country': random.choice(self.COUNTRIES),
                'commission_rate': round(random.uniform(1.5, 5.0), 2),
                'status': random.choices(['ACTIVE', 'INACTIVE', 'SUSPENDED'], weights=[0.85, 0.10, 0.05])[0]
            })
        
        return pd.DataFrame(merchants)
    
    def generate_payments(self, customers_df, merchants_df):
        """Generate payment transaction data"""
        payments = []
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(self.num_transactions):
            customer = customers_df.sample(1).iloc[0]
            merchant = merchants_df.sample(1).iloc[0]
            
            # Status probability influenced by customer risk
            if customer['risk_category'] == 'HIGH':
                status = random.choices(self.PAYMENT_STATUSES, weights=[0.65, 0.25, 0.08, 0.02])[0]
            elif customer['risk_category'] == 'MEDIUM':
                status = random.choices(self.PAYMENT_STATUSES, weights=[0.85, 0.10, 0.04, 0.01])[0]
            else:
                status = random.choices(self.PAYMENT_STATUSES, weights=[0.95, 0.03, 0.015, 0.005])[0]
            
            # Generate amount with some outliers
            if random.random() < 0.05:  # 5% outliers
                amount = round(random.uniform(5000, 50000), 2)
            else:
                amount = round(random.uniform(10, 2000), 2)
            
            # Calculate risk score
            risk_score = random.uniform(0, 100)
            if amount > 5000:
                risk_score = min(100, risk_score + 30)
            if customer['risk_category'] == 'HIGH':
                risk_score = min(100, risk_score + 20)
            
            is_suspicious = risk_score > 75 or amount > 10000
            
            transaction_date = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            payments.append({
                'payment_id': f'PAY{i+1:06d}',
                'customer_id': customer['customer_id'],
                'merchant_id': merchant['merchant_id'],
                'amount': amount,
                'currency': 'USD',
                'payment_method': random.choice(self.PAYMENT_METHODS),
                'payment_status': status,
                'transaction_date': transaction_date,
                'processing_time_seconds': random.randint(1, 30),
                'failure_reason': random.choice(self.FAILURE_REASONS) if status == 'FAILED' else None,
                'risk_score': round(risk_score, 2),
                'is_suspicious': is_suspicious
            })
        
        return pd.DataFrame(payments)
    
    def generate_settlements(self, merchants_df, payments_df):
        """Generate settlement data"""
        settlements = []
        settlement_id = 1
        
        # Group payments by merchant and date
        successful_payments = payments_df[payments_df['payment_status'] == 'SUCCESS'].copy()
        successful_payments['settlement_date'] = pd.to_datetime(successful_payments['transaction_date']).dt.date
        
        grouped = successful_payments.groupby(['merchant_id', 'settlement_date'])
        
        for (merchant_id, settlement_date), group in grouped:
            merchant = merchants_df[merchants_df['merchant_id'] == merchant_id].iloc[0]
            
            total_amount = group['amount'].sum()
            payment_count = len(group)
            commission_rate = merchant['commission_rate'] / 100
            commission_amount = round(total_amount * commission_rate, 2)
            net_amount = round(total_amount - commission_amount, 2)
            
            # Simulate SLA breaches (settlements should happen within 2 days)
            expected_settlement_date = settlement_date + timedelta(days=2)
            actual_settlement_date = settlement_date + timedelta(days=random.randint(1, 5))
            sla_breach = actual_settlement_date > expected_settlement_date
            
            status = random.choices(['COMPLETED', 'PENDING', 'FAILED'], weights=[0.90, 0.08, 0.02])[0]
            
            settlements.append({
                'settlement_id': f'SETTLE{settlement_id:05d}',
                'merchant_id': merchant_id,
                'settlement_date': actual_settlement_date,
                'total_amount': round(total_amount, 2),
                'commission_amount': commission_amount,
                'net_amount': net_amount,
                'payment_count': payment_count,
                'status': status,
                'sla_breach': sla_breach,
                'expected_settlement_date': expected_settlement_date
            })
            settlement_id += 1
        
        return pd.DataFrame(settlements)


class ETLPipeline:
    """ETL Pipeline for data loading and transformation"""
    
    @staticmethod
    def load_customers(df):
        """Load customer data into database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO customers (customer_id, customer_name, email, phone, country, 
                                         registration_date, credit_score, risk_category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING;
                """, (
                    row['customer_id'], row['customer_name'], row['email'], row['phone'],
                    row['country'], row['registration_date'], row['credit_score'], row['risk_category']
                ))
            logger.info(f"Loaded {len(df)} customers")
    
    @staticmethod
    def load_merchants(df):
        """Load merchant data into database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO merchants (merchant_id, merchant_name, business_type, 
                                         country, commission_rate, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (merchant_id) DO NOTHING;
                """, (
                    row['merchant_id'], row['merchant_name'], row['business_type'],
                    row['country'], row['commission_rate'], row['status']
                ))
            logger.info(f"Loaded {len(df)} merchants")
    
    @staticmethod
    def load_payments(df):
        """Load payment data into database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO payments (payment_id, customer_id, merchant_id, amount, currency,
                                        payment_method, payment_status, transaction_date,
                                        processing_time_seconds, failure_reason, risk_score, is_suspicious)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (payment_id) DO NOTHING;
                """, (
                    row['payment_id'], row['customer_id'], row['merchant_id'], row['amount'],
                    row['currency'], row['payment_method'], row['payment_status'], row['transaction_date'],
                    row['processing_time_seconds'], row['failure_reason'], row['risk_score'], row['is_suspicious']
                ))
            logger.info(f"Loaded {len(df)} payments")
    
    @staticmethod
    def load_settlements(df):
        """Load settlement data into database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO settlements (settlement_id, merchant_id, settlement_date, 
                                           total_amount, commission_amount, net_amount,
                                           payment_count, status, sla_breach, expected_settlement_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (settlement_id) DO NOTHING;
                """, (
                    row['settlement_id'], row['merchant_id'], row['settlement_date'],
                    row['total_amount'], row['commission_amount'], row['net_amount'],
                    row['payment_count'], row['status'], row['sla_breach'], row['expected_settlement_date']
                ))
            logger.info(f"Loaded {len(df)} settlements")
    
    @staticmethod
    def run_etl():
        """Execute full ETL pipeline"""
        logger.info("Starting ETL pipeline...")
        
        generator = FinancialDataGenerator(
            num_customers=500,
            num_merchants=50,
            num_transactions=5000
        )
        
        # Generate data
        logger.info("Generating customer data...")
        customers_df = generator.generate_customers()
        
        logger.info("Generating merchant data...")
        merchants_df = generator.generate_merchants()
        
        logger.info("Generating payment data...")
        payments_df = generator.generate_payments(customers_df, merchants_df)
        
        logger.info("Generating settlement data...")
        settlements_df = generator.generate_settlements(merchants_df, payments_df)
        
        # Load data
        ETLPipeline.load_customers(customers_df)
        ETLPipeline.load_merchants(merchants_df)
        ETLPipeline.load_payments(payments_df)
        ETLPipeline.load_settlements(settlements_df)
        
        logger.info("ETL pipeline completed successfully")
        
        return {
            'customers': len(customers_df),
            'merchants': len(merchants_df),
            'payments': len(payments_df),
            'settlements': len(settlements_df)
        }
