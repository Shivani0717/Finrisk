# SQL Query Examples
## Financial Payments Analytics System

This document provides ready-to-use SQL queries for common analytics scenarios.

---

## Table of Contents
1. [Transaction Analytics](#transaction-analytics)
2. [Risk & Fraud Detection](#risk--fraud-detection)
3. [Merchant Analytics](#merchant-analytics)
4. [Customer Analytics](#customer-analytics)
5. [Settlement Analysis](#settlement-analysis)
6. [Performance Queries](#performance-queries)

---

## Transaction Analytics

### 1. Daily Transaction Summary
```sql
SELECT * FROM get_daily_transaction_summary('2025-12-15');
```

### 2. Transaction Volume by Hour
```sql
SELECT 
    EXTRACT(HOUR FROM transaction_date) as hour_of_day,
    COUNT(*) as transaction_count,
    SUM(amount) FILTER (WHERE payment_status = 'SUCCESS') as revenue
FROM payments
WHERE DATE(transaction_date) = CURRENT_DATE
GROUP BY EXTRACT(HOUR FROM transaction_date)
ORDER BY hour_of_day;
```

### 3. Weekly Transaction Trends
```sql
SELECT 
    DATE_TRUNC('week', transaction_date) as week_start,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') as successful,
    COUNT(*) FILTER (WHERE payment_status = 'FAILED') as failed,
    SUM(amount) FILTER (WHERE payment_status = 'SUCCESS') as revenue
FROM payments
WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', transaction_date)
ORDER BY week_start DESC;
```

### 4. Transaction Distribution by Payment Method
```sql
SELECT 
    payment_method,
    COUNT(*) as total_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    ROUND(AVG(processing_time_seconds), 2) as avg_processing_time
FROM payments
GROUP BY payment_method
ORDER BY total_count DESC;
```

### 5. Success Rate by Payment Method
```sql
SELECT 
    payment_method,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') as successful,
    COUNT(*) FILTER (WHERE payment_status = 'FAILED') as failed,
    ROUND(
        COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') * 100.0 / COUNT(*), 
        2
    ) as success_rate
FROM payments
GROUP BY payment_method
ORDER BY success_rate DESC;
```

### 6. Top 10 Highest Value Transactions
```sql
SELECT 
    p.payment_id,
    p.amount,
    p.payment_status,
    c.customer_name,
    m.merchant_name,
    p.transaction_date
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
JOIN merchants m ON p.merchant_id = m.merchant_id
ORDER BY p.amount DESC
LIMIT 10;
```

---

## Risk & Fraud Detection

### 1. High-Risk Transactions (Using Stored Procedure)
```sql
SELECT * FROM detect_high_risk_transactions(75.0);
```

### 2. Suspicious Transactions by Risk Category
```sql
SELECT 
    c.risk_category,
    COUNT(*) as suspicious_count,
    SUM(p.amount) as total_amount,
    AVG(p.risk_score) as avg_risk_score
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
WHERE p.is_suspicious = TRUE
GROUP BY c.risk_category
ORDER BY suspicious_count DESC;
```

### 3. Customers with Multiple Failed Payments
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.risk_category,
    COUNT(*) FILTER (WHERE p.payment_status = 'FAILED') as failed_count,
    COUNT(*) as total_attempts,
    ROUND(
        COUNT(*) FILTER (WHERE p.payment_status = 'FAILED') * 100.0 / COUNT(*), 
        2
    ) as failure_rate
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.risk_category
HAVING COUNT(*) FILTER (WHERE p.payment_status = 'FAILED') >= 3
ORDER BY failed_count DESC;
```

### 4. Fraud Pattern Detection - Large Transactions from High-Risk Customers
```sql
SELECT 
    p.payment_id,
    c.customer_name,
    c.risk_category,
    p.amount,
    p.risk_score,
    p.payment_status,
    p.transaction_date
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
WHERE c.risk_category = 'HIGH'
  AND p.amount > 5000
  AND p.payment_status = 'SUCCESS'
ORDER BY p.amount DESC;
```

### 5. Anomalous Transaction Amounts
```sql
WITH stats AS (
    SELECT 
        AVG(amount) as mean_amount,
        STDDEV(amount) as std_amount
    FROM payments
    WHERE payment_status = 'SUCCESS'
)
SELECT 
    p.payment_id,
    p.amount,
    c.customer_name,
    m.merchant_name,
    p.transaction_date,
    ROUND((p.amount - stats.mean_amount) / stats.std_amount, 2) as z_score
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
JOIN merchants m ON p.merchant_id = m.merchant_id
CROSS JOIN stats
WHERE ABS((p.amount - stats.mean_amount) / stats.std_amount) > 3
ORDER BY ABS((p.amount - stats.mean_amount) / stats.std_amount) DESC;
```

---

## Merchant Analytics

### 1. Merchant Performance Dashboard
```sql
SELECT * FROM vw_merchant_performance
ORDER BY total_revenue DESC
LIMIT 20;
```

### 2. Merchant Revenue Ranking
```sql
WITH ranked_merchants AS (
    SELECT 
        merchant_id,
        merchant_name,
        total_revenue,
        RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
        PERCENT_RANK() OVER (ORDER BY total_revenue DESC) as percentile
    FROM vw_merchant_performance
    WHERE total_revenue IS NOT NULL
)
SELECT 
    revenue_rank,
    merchant_name,
    total_revenue,
    ROUND(percentile * 100, 2) as top_percentile
FROM ranked_merchants
WHERE revenue_rank <= 10;
```

### 3. Merchant Performance by Business Type
```sql
SELECT 
    m.business_type,
    COUNT(DISTINCT m.merchant_id) as merchant_count,
    SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as total_revenue,
    AVG(p.amount) as avg_transaction,
    COUNT(p.payment_id) as total_transactions
FROM merchants m
LEFT JOIN payments p ON m.merchant_id = p.merchant_id
GROUP BY m.business_type
ORDER BY total_revenue DESC;
```

### 4. Merchant Churn Risk - Low Activity Merchants
```sql
SELECT 
    m.merchant_id,
    m.merchant_name,
    m.business_type,
    COUNT(p.payment_id) as transactions_last_30_days,
    MAX(p.transaction_date) as last_transaction_date,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(p.transaction_date)) as days_since_last_txn
FROM merchants m
LEFT JOIN payments p ON m.merchant_id = p.merchant_id 
    AND p.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY m.merchant_id, m.merchant_name, m.business_type
HAVING COUNT(p.payment_id) < 5 OR MAX(p.transaction_date) < CURRENT_DATE - INTERVAL '14 days'
ORDER BY days_since_last_txn DESC;
```

### 5. Merchant Settlement Summary
```sql
SELECT 
    m.merchant_name,
    COUNT(s.settlement_id) as settlement_count,
    SUM(s.total_amount) as total_settled,
    SUM(s.commission_amount) as total_commission,
    SUM(s.net_amount) as total_net,
    COUNT(*) FILTER (WHERE s.sla_breach = TRUE) as sla_breaches
FROM merchants m
JOIN settlements s ON m.merchant_id = s.merchant_id
GROUP BY m.merchant_id, m.merchant_name
ORDER BY total_settled DESC;
```

---

## Customer Analytics

### 1. Customer Insights Overview
```sql
SELECT * FROM vw_customer_insights
ORDER BY total_spent DESC
LIMIT 50;
```

### 2. Customer Lifetime Value (CLV)
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.risk_category,
    COUNT(p.payment_id) as total_transactions,
    SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as lifetime_value,
    AVG(p.amount) as avg_transaction,
    MIN(p.transaction_date) as first_transaction,
    MAX(p.transaction_date) as last_transaction,
    EXTRACT(DAY FROM MAX(p.transaction_date) - MIN(p.transaction_date)) as customer_age_days
FROM customers c
LEFT JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.customer_id, c.customer_name, c.risk_category
HAVING COUNT(p.payment_id) > 0
ORDER BY lifetime_value DESC
LIMIT 50;
```

### 3. Customer Segmentation by Spending
```sql
WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as total_spent
    FROM customers c
    LEFT JOIN payments p ON c.customer_id = p.customer_id
    GROUP BY c.customer_id, c.customer_name
),
quartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_spent) as q1,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_spent) as q2,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_spent) as q3
    FROM customer_spending
)
SELECT 
    cs.customer_id,
    cs.customer_name,
    cs.total_spent,
    CASE 
        WHEN cs.total_spent >= q.q3 THEN 'High Value'
        WHEN cs.total_spent >= q.q2 THEN 'Medium Value'
        WHEN cs.total_spent >= q.q1 THEN 'Low Value'
        ELSE 'Minimal Value'
    END as customer_segment
FROM customer_spending cs
CROSS JOIN quartiles q
ORDER BY cs.total_spent DESC;
```

### 4. Customer Retention Analysis
```sql
WITH customer_activity AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', transaction_date) as month,
        COUNT(*) as transactions
    FROM payments
    WHERE payment_status = 'SUCCESS'
    GROUP BY customer_id, DATE_TRUNC('month', transaction_date)
)
SELECT 
    month,
    COUNT(DISTINCT customer_id) as active_customers,
    COUNT(DISTINCT customer_id) FILTER (
        WHERE customer_id IN (
            SELECT customer_id 
            FROM customer_activity ca2 
            WHERE ca2.month = customer_activity.month - INTERVAL '1 month'
        )
    ) as returning_customers
FROM customer_activity
GROUP BY month
ORDER BY month DESC;
```

### 5. Customer Risk Profile Distribution
```sql
SELECT 
    risk_category,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    AVG(credit_score) as avg_credit_score,
    COUNT(p.payment_id) as total_transactions,
    SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as total_revenue
FROM customers c
LEFT JOIN payments p ON c.customer_id = p.customer_id
GROUP BY risk_category
ORDER BY customer_count DESC;
```

---

## Settlement Analysis

### 1. SLA Breach Report
```sql
SELECT * FROM identify_sla_breaches()
ORDER BY days_delayed DESC;
```

### 2. Settlement Status Summary
```sql
SELECT 
    status,
    COUNT(*) as settlement_count,
    SUM(total_amount) as total_amount,
    SUM(net_amount) as total_net,
    AVG(net_amount) as avg_net,
    COUNT(*) FILTER (WHERE sla_breach = TRUE) as sla_breaches
FROM settlements
GROUP BY status
ORDER BY settlement_count DESC;
```

### 3. Daily Settlement Volume
```sql
SELECT 
    settlement_date,
    COUNT(*) as settlement_count,
    SUM(total_amount) as total_amount,
    SUM(commission_amount) as total_commission,
    SUM(net_amount) as net_to_merchants,
    SUM(payment_count) as total_payments_settled
FROM settlements
WHERE settlement_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY settlement_date
ORDER BY settlement_date DESC;
```

### 4. Commission Analysis
```sql
SELECT 
    m.merchant_name,
    m.commission_rate,
    COUNT(s.settlement_id) as settlements,
    SUM(s.total_amount) as gross_amount,
    SUM(s.commission_amount) as total_commission_earned,
    SUM(s.net_amount) as net_paid_to_merchant,
    ROUND(
        SUM(s.commission_amount) * 100.0 / SUM(s.total_amount), 
        2
    ) as effective_commission_rate
FROM merchants m
JOIN settlements s ON m.merchant_id = s.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.commission_rate
ORDER BY total_commission_earned DESC
LIMIT 20;
```

### 5. Settlement Delay Analysis
```sql
SELECT 
    EXTRACT(DAY FROM settlement_date - expected_settlement_date) as days_delay,
    COUNT(*) as settlement_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM settlements
GROUP BY EXTRACT(DAY FROM settlement_date - expected_settlement_date)
ORDER BY days_delay;
```

---

## Performance Queries

### 1. Payment Processing Time Analysis
```sql
SELECT 
    payment_method,
    payment_status,
    AVG(processing_time_seconds) as avg_processing_time,
    MIN(processing_time_seconds) as min_processing_time,
    MAX(processing_time_seconds) as max_processing_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY processing_time_seconds) as median_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_seconds) as p95_time
FROM payments
GROUP BY payment_method, payment_status
ORDER BY payment_method, payment_status;
```

### 2. Failure Reason Analysis
```sql
SELECT 
    failure_reason,
    COUNT(*) as failure_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    SUM(amount) as lost_revenue
FROM payments
WHERE payment_status = 'FAILED'
  AND failure_reason IS NOT NULL
GROUP BY failure_reason
ORDER BY failure_count DESC;
```

### 3. Geographic Transaction Analysis
```sql
SELECT 
    c.country,
    COUNT(p.payment_id) as transactions,
    COUNT(DISTINCT c.customer_id) as unique_customers,
    SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as revenue,
    AVG(p.amount) as avg_transaction,
    ROUND(
        COUNT(*) FILTER (WHERE p.payment_status = 'SUCCESS') * 100.0 / COUNT(*), 
        2
    ) as success_rate
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.country
ORDER BY revenue DESC;
```

### 4. Refund Analysis
```sql
SELECT 
    DATE(transaction_date) as refund_date,
    COUNT(*) as refund_count,
    SUM(amount) as refund_amount,
    COUNT(DISTINCT customer_id) as affected_customers,
    AVG(amount) as avg_refund_amount
FROM payments
WHERE payment_status = 'REFUNDED'
  AND transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(transaction_date)
ORDER BY refund_date DESC;
```

### 5. Currency Distribution
```sql
SELECT 
    currency,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') as successful_txns
FROM payments
GROUP BY currency
ORDER BY transaction_count DESC;
```

---

## Advanced Analytics

### 1. Cohort Analysis - Customer Acquisition by Month
```sql
WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(transaction_date)) as cohort_month
    FROM payments
    WHERE payment_status = 'SUCCESS'
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT 
        fp.customer_id,
        fp.cohort_month,
        DATE_TRUNC('month', p.transaction_date) as activity_month,
        SUM(p.amount) as revenue
    FROM first_purchase fp
    JOIN payments p ON fp.customer_id = p.customer_id
    WHERE p.payment_status = 'SUCCESS'
    GROUP BY fp.customer_id, fp.cohort_month, DATE_TRUNC('month', p.transaction_date)
)
SELECT 
    cohort_month,
    COUNT(DISTINCT customer_id) as cohort_size,
    EXTRACT(MONTH FROM AGE(activity_month, cohort_month)) as months_since_first,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(revenue) as cohort_revenue
FROM monthly_activity
GROUP BY cohort_month, months_since_first
ORDER BY cohort_month DESC, months_since_first;
```

### 2. Time-Based Success Rate Trends
```sql
SELECT 
    DATE_TRUNC('day', transaction_date) as date,
    EXTRACT(HOUR FROM transaction_date) as hour,
    COUNT(*) as transactions,
    ROUND(
        COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') * 100.0 / COUNT(*), 
        2
    ) as success_rate,
    AVG(amount) as avg_amount
FROM payments
WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE_TRUNC('day', transaction_date), EXTRACT(HOUR FROM transaction_date)
ORDER BY date DESC, hour;
```

### 3. Merchant Concentration Risk
```sql
WITH merchant_revenue AS (
    SELECT 
        merchant_id,
        SUM(amount) FILTER (WHERE payment_status = 'SUCCESS') as revenue
    FROM payments
    GROUP BY merchant_id
),
total_revenue AS (
    SELECT SUM(revenue) as total FROM merchant_revenue
)
SELECT 
    m.merchant_name,
    mr.revenue,
    ROUND(mr.revenue * 100.0 / tr.total, 2) as revenue_percentage,
    SUM(ROUND(mr.revenue * 100.0 / tr.total, 2)) OVER (ORDER BY mr.revenue DESC) as cumulative_percentage
FROM merchant_revenue mr
JOIN merchants m ON mr.merchant_id = m.merchant_id
CROSS JOIN total_revenue tr
ORDER BY mr.revenue DESC
LIMIT 20;
```

---

## Indexes for Performance

```sql
-- Already created during initialization
-- Listed here for reference

CREATE INDEX idx_payments_date ON payments(transaction_date);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_merchant ON payments(merchant_id);
CREATE INDEX idx_settlements_date ON settlements(settlement_date);
CREATE INDEX idx_settlements_merchant ON settlements(merchant_id);
```

---

## Materialized Views (Optional for Performance)

```sql
-- Create materialized view for daily aggregates
CREATE MATERIALIZED VIEW mv_daily_stats AS
SELECT 
    DATE(transaction_date) as date,
    payment_method,
    payment_status,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM payments
GROUP BY DATE(transaction_date), payment_method, payment_status;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW mv_daily_stats;
```

---

## Notes

- Replace `CURRENT_DATE` with specific dates as needed
- Adjust date ranges in WHERE clauses for your analysis period
- Add indexes on frequently filtered columns for better performance
- Use EXPLAIN ANALYZE to optimize query performance
- Consider materialized views for frequently accessed aggregations

---

**Last Updated:** December 2025  
**Version:** 1.0
