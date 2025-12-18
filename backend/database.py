import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# PostgreSQL connection configuration
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', '5432'),
    'database': os.environ.get('POSTGRES_DB', 'financial_analytics'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'postgres')
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_cursor(conn):
    """Get a cursor with RealDictCursor for dict-like results"""
    return conn.cursor(cursor_factory=RealDictCursor)

def init_database():
    """Initialize database schema and stored procedures"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            -- Customers table
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                country VARCHAR(100),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                credit_score INTEGER CHECK (credit_score >= 300 AND credit_score <= 850),
                risk_category VARCHAR(20) CHECK (risk_category IN ('LOW', 'MEDIUM', 'HIGH')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            -- Merchants table
            CREATE TABLE IF NOT EXISTS merchants (
                merchant_id VARCHAR(50) PRIMARY KEY,
                merchant_name VARCHAR(255) NOT NULL,
                business_type VARCHAR(100),
                country VARCHAR(100),
                commission_rate DECIMAL(5,2) DEFAULT 2.5,
                status VARCHAR(20) CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            -- Payments table
            CREATE TABLE IF NOT EXISTS payments (
                payment_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) REFERENCES customers(customer_id),
                merchant_id VARCHAR(50) REFERENCES merchants(merchant_id),
                amount DECIMAL(15,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                payment_method VARCHAR(50),
                payment_status VARCHAR(20) CHECK (payment_status IN ('SUCCESS', 'FAILED', 'PENDING', 'REFUNDED')),
                transaction_date TIMESTAMP NOT NULL,
                processing_time_seconds INTEGER,
                failure_reason TEXT,
                risk_score DECIMAL(5,2),
                is_suspicious BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            -- Settlements table
            CREATE TABLE IF NOT EXISTS settlements (
                settlement_id VARCHAR(50) PRIMARY KEY,
                merchant_id VARCHAR(50) REFERENCES merchants(merchant_id),
                settlement_date DATE NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                commission_amount DECIMAL(15,2) NOT NULL,
                net_amount DECIMAL(15,2) NOT NULL,
                payment_count INTEGER NOT NULL,
                status VARCHAR(20) CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED')),
                sla_breach BOOLEAN DEFAULT FALSE,
                expected_settlement_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(transaction_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_merchant ON payments(merchant_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settlements_date ON settlements(settlement_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settlements_merchant ON settlements(merchant_id);")
        
        logger.info("Database schema initialized successfully")
