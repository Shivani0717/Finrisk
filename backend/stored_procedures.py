"""SQL Stored Procedures and Functions"""
import logging
from database import get_db_connection

logger = logging.getLogger(__name__)

def create_stored_procedures():
    """Create all stored procedures and views"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Stored Procedure: Daily Transaction Summary
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_daily_transaction_summary(
                p_date DATE
            )
            RETURNS TABLE (
                transaction_date DATE,
                total_transactions BIGINT,
                successful_transactions BIGINT,
                failed_transactions BIGINT,
                pending_transactions BIGINT,
                refunded_transactions BIGINT,
                total_amount DECIMAL(15,2),
                success_rate DECIMAL(5,2),
                avg_transaction_amount DECIMAL(15,2),
                total_revenue DECIMAL(15,2)
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    p_date AS transaction_date,
                    COUNT(*)::BIGINT AS total_transactions,
                    COUNT(*) FILTER (WHERE payment_status = 'SUCCESS')::BIGINT AS successful_transactions,
                    COUNT(*) FILTER (WHERE payment_status = 'FAILED')::BIGINT AS failed_transactions,
                    COUNT(*) FILTER (WHERE payment_status = 'PENDING')::BIGINT AS pending_transactions,
                    COUNT(*) FILTER (WHERE payment_status = 'REFUNDED')::BIGINT AS refunded_transactions,
                    COALESCE(SUM(amount), 0)::DECIMAL(15,2) AS total_amount,
                    CASE 
                        WHEN COUNT(*) > 0 THEN 
                            ROUND((COUNT(*) FILTER (WHERE payment_status = 'SUCCESS')::DECIMAL / COUNT(*)::DECIMAL * 100), 2)
                        ELSE 0 
                    END AS success_rate,
                    COALESCE(AVG(amount), 0)::DECIMAL(15,2) AS avg_transaction_amount,
                    COALESCE(SUM(amount) FILTER (WHERE payment_status = 'SUCCESS'), 0)::DECIMAL(15,2) AS total_revenue
                FROM payments
                WHERE DATE(transaction_date) = p_date;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Stored Procedure: Failed Payment Detection
        cursor.execute("""
            CREATE OR REPLACE FUNCTION detect_failed_payments(
                p_start_date DATE,
                p_end_date DATE
            )
            RETURNS TABLE (
                payment_id VARCHAR(50),
                customer_id VARCHAR(50),
                customer_name VARCHAR(255),
                merchant_name VARCHAR(255),
                amount DECIMAL(15,2),
                payment_method VARCHAR(50),
                transaction_date TIMESTAMP,
                failure_reason TEXT
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    p.payment_id,
                    p.customer_id,
                    c.customer_name,
                    m.merchant_name,
                    p.amount,
                    p.payment_method,
                    p.transaction_date,
                    p.failure_reason
                FROM payments p
                JOIN customers c ON p.customer_id = c.customer_id
                JOIN merchants m ON p.merchant_id = m.merchant_id
                WHERE p.payment_status = 'FAILED'
                  AND DATE(p.transaction_date) BETWEEN p_start_date AND p_end_date
                ORDER BY p.transaction_date DESC;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Stored Procedure: SLA Breach Identification
        cursor.execute("""
            CREATE OR REPLACE FUNCTION identify_sla_breaches()
            RETURNS TABLE (
                settlement_id VARCHAR(50),
                merchant_id VARCHAR(50),
                merchant_name VARCHAR(255),
                settlement_date DATE,
                expected_settlement_date DATE,
                days_delayed INTEGER,
                total_amount DECIMAL(15,2),
                net_amount DECIMAL(15,2)
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    s.settlement_id,
                    s.merchant_id,
                    m.merchant_name,
                    s.settlement_date,
                    s.expected_settlement_date,
                    (s.settlement_date - s.expected_settlement_date)::INTEGER AS days_delayed,
                    s.total_amount,
                    s.net_amount
                FROM settlements s
                JOIN merchants m ON s.merchant_id = m.merchant_id
                WHERE s.sla_breach = TRUE
                ORDER BY days_delayed DESC;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Stored Procedure: Risk Detection
        cursor.execute("""
            CREATE OR REPLACE FUNCTION detect_high_risk_transactions(
                p_risk_threshold DECIMAL DEFAULT 70.0
            )
            RETURNS TABLE (
                payment_id VARCHAR(50),
                customer_id VARCHAR(50),
                customer_name VARCHAR(255),
                amount DECIMAL(15,2),
                risk_score DECIMAL(5,2),
                transaction_date TIMESTAMP,
                payment_status VARCHAR(20)
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    p.payment_id,
                    p.customer_id,
                    c.customer_name,
                    p.amount,
                    p.risk_score,
                    p.transaction_date,
                    p.payment_status
                FROM payments p
                JOIN customers c ON p.customer_id = c.customer_id
                WHERE (p.risk_score >= p_risk_threshold OR p.is_suspicious = TRUE)
                  AND p.payment_status != 'REFUNDED'
                ORDER BY p.risk_score DESC, p.transaction_date DESC;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Create analytical views for BI tools
        cursor.execute("""
            CREATE OR REPLACE VIEW vw_payment_analytics AS
            SELECT 
                DATE(p.transaction_date) as payment_date,
                p.payment_status,
                p.payment_method,
                p.currency,
                m.merchant_name,
                m.business_type,
                c.country as customer_country,
                COUNT(*) as transaction_count,
                SUM(p.amount) as total_amount,
                AVG(p.amount) as avg_amount,
                AVG(p.processing_time_seconds) as avg_processing_time,
                COUNT(*) FILTER (WHERE p.is_suspicious = TRUE) as suspicious_count
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            JOIN merchants m ON p.merchant_id = m.merchant_id
            GROUP BY DATE(p.transaction_date), p.payment_status, p.payment_method, 
                     p.currency, m.merchant_name, m.business_type, c.country;
        """)
        
        cursor.execute("""
            CREATE OR REPLACE VIEW vw_merchant_performance AS
            SELECT 
                m.merchant_id,
                m.merchant_name,
                m.business_type,
                m.status,
                COUNT(p.payment_id) as total_transactions,
                COUNT(*) FILTER (WHERE p.payment_status = 'SUCCESS') as successful_transactions,
                COUNT(*) FILTER (WHERE p.payment_status = 'FAILED') as failed_transactions,
                SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as total_revenue,
                AVG(p.amount) as avg_transaction_amount,
                CASE 
                    WHEN COUNT(p.payment_id) > 0 THEN
                        ROUND((COUNT(*) FILTER (WHERE p.payment_status = 'SUCCESS')::DECIMAL / COUNT(*)::DECIMAL * 100), 2)
                    ELSE 0
                END as success_rate
            FROM merchants m
            LEFT JOIN payments p ON m.merchant_id = p.merchant_id
            GROUP BY m.merchant_id, m.merchant_name, m.business_type, m.status;
        """)
        
        cursor.execute("""
            CREATE OR REPLACE VIEW vw_customer_insights AS
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                c.country,
                c.credit_score,
                c.risk_category,
                COUNT(p.payment_id) as total_transactions,
                SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as total_spent,
                AVG(p.amount) as avg_transaction_amount,
                COUNT(*) FILTER (WHERE p.payment_status = 'FAILED') as failed_transaction_count,
                MAX(p.transaction_date) as last_transaction_date
            FROM customers c
            LEFT JOIN payments p ON c.customer_id = p.customer_id
            GROUP BY c.customer_id, c.customer_name, c.email, c.country, 
                     c.credit_score, c.risk_category;
        """)
        
        logger.info("Stored procedures and views created successfully")
