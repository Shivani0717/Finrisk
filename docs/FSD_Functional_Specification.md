# Functional Specification Document (FSD)
## Automated Financial Payments Analytics & Risk Monitoring System

**Document Version:** 1.0  
**Date:** December 2025  
**Technical Lead:** Project Manager

---

## 1. System Overview

### 1.1 Architecture
```
┌─────────────────┐
│  Data Sources   │
│  (Generated)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ETL Pipeline   │
│  (Python/Pandas)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  Data Warehouse │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   REST APIs     │
└────────┬────────┘
         │
         ├─────────────► BI Tools (Power BI/Tableau)
         │
         └─────────────► External Applications
```

### 1.2 Technology Stack
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 14+
- **ETL:** Python (Pandas, NumPy, Faker)
- **API Documentation:** OpenAPI/Swagger
- **Deployment:** Docker/Kubernetes

---

## 2. Database Schema

### 2.1 Tables

#### CUSTOMERS
```sql
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    country VARCHAR(100),
    registration_date TIMESTAMP,
    credit_score INTEGER (300-850),
    risk_category VARCHAR(20), -- LOW/MEDIUM/HIGH
    created_at TIMESTAMP
);
```

#### MERCHANTS
```sql
CREATE TABLE merchants (
    merchant_id VARCHAR(50) PRIMARY KEY,
    merchant_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    country VARCHAR(100),
    commission_rate DECIMAL(5,2),
    status VARCHAR(20), -- ACTIVE/INACTIVE/SUSPENDED
    created_at TIMESTAMP
);
```

#### PAYMENTS
```sql
CREATE TABLE payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers,
    merchant_id VARCHAR(50) REFERENCES merchants,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    payment_status VARCHAR(20), -- SUCCESS/FAILED/PENDING/REFUNDED
    transaction_date TIMESTAMP NOT NULL,
    processing_time_seconds INTEGER,
    failure_reason TEXT,
    risk_score DECIMAL(5,2),
    is_suspicious BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### SETTLEMENTS
```sql
CREATE TABLE settlements (
    settlement_id VARCHAR(50) PRIMARY KEY,
    merchant_id VARCHAR(50) REFERENCES merchants,
    settlement_date DATE NOT NULL,
    total_amount DECIMAL(15,2),
    commission_amount DECIMAL(15,2),
    net_amount DECIMAL(15,2),
    payment_count INTEGER,
    status VARCHAR(20), -- PENDING/COMPLETED/FAILED
    sla_breach BOOLEAN,
    expected_settlement_date DATE,
    created_at TIMESTAMP
);
```

### 2.2 Indexes
```sql
CREATE INDEX idx_payments_date ON payments(transaction_date);
CREATE INDEX idx_payments_status ON payments(payment_status);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_merchant ON payments(merchant_id);
CREATE INDEX idx_settlements_date ON settlements(settlement_date);
CREATE INDEX idx_settlements_merchant ON settlements(merchant_id);
```

---

## 3. Stored Procedures

### 3.1 get_daily_transaction_summary
**Purpose:** Generate daily transaction summary  
**Parameters:**
- `p_date` (DATE): Report date

**Returns:**
- transaction_date
- total_transactions
- successful_transactions
- failed_transactions
- pending_transactions
- refunded_transactions
- total_amount
- success_rate
- avg_transaction_amount
- total_revenue

**Usage:**
```sql
SELECT * FROM get_daily_transaction_summary('2025-01-15');
```

### 3.2 detect_failed_payments
**Purpose:** Identify failed payments in date range  
**Parameters:**
- `p_start_date` (DATE): Start date
- `p_end_date` (DATE): End date

**Returns:**
- payment_id
- customer_id
- customer_name
- merchant_name
- amount
- payment_method
- transaction_date
- failure_reason

**Usage:**
```sql
SELECT * FROM detect_failed_payments('2025-01-01', '2025-01-31');
```

### 3.3 identify_sla_breaches
**Purpose:** Identify settlement SLA breaches  
**Parameters:** None

**Returns:**
- settlement_id
- merchant_id
- merchant_name
- settlement_date
- expected_settlement_date
- days_delayed
- total_amount
- net_amount

**Usage:**
```sql
SELECT * FROM identify_sla_breaches();
```

### 3.4 detect_high_risk_transactions
**Purpose:** Detect high-risk transactions  
**Parameters:**
- `p_risk_threshold` (DECIMAL): Risk score threshold (default: 70.0)

**Returns:**
- payment_id
- customer_id
- customer_name
- amount
- risk_score
- transaction_date
- payment_status

**Usage:**
```sql
SELECT * FROM detect_high_risk_transactions(75.0);
```

---

## 4. Database Views (BI Integration)

### 4.1 vw_payment_analytics
Aggregated payment analytics by date, status, method, merchant, and country

### 4.2 vw_merchant_performance
Merchant-level KPIs including transactions, revenue, and success rates

### 4.3 vw_customer_insights
Customer behavior analysis including spending patterns and risk profiles

---

## 5. REST API Endpoints

### 5.1 System Management

#### POST /api/etl/initialize
Initialize database schema and stored procedures

**Response:**
```json
{
  "status": "success",
  "message": "Database initialized successfully"
}
```

#### POST /api/etl/run
Execute ETL pipeline to generate and load data

**Response:**
```json
{
  "status": "success",
  "message": "ETL pipeline completed successfully",
  "records_loaded": {
    "customers": 500,
    "merchants": 50,
    "payments": 5000,
    "settlements": 450
  }
}
```

#### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 5.2 Reports

#### GET /api/reports/daily-summary
Get daily transaction summary

**Parameters:**
- `report_date` (query): Date in YYYY-MM-DD format

**Response:**
```json
{
  "transaction_date": "2025-01-15",
  "total_transactions": 150,
  "successful_transactions": 142,
  "failed_transactions": 6,
  "pending_transactions": 2,
  "refunded_transactions": 0,
  "total_amount": 125000.50,
  "success_rate": 94.67,
  "avg_transaction_amount": 833.34,
  "total_revenue": 118333.47
}
```

#### GET /api/reports/failed-payments
Get failed payments in date range

**Parameters:**
- `start_date` (query): Start date YYYY-MM-DD
- `end_date` (query): End date YYYY-MM-DD

**Response:**
```json
[
  {
    "payment_id": "PAY001234",
    "customer_id": "CUST00123",
    "customer_name": "John Doe",
    "merchant_name": "Tech Store Inc",
    "amount": 299.99,
    "payment_method": "CREDIT_CARD",
    "transaction_date": "2025-01-15T14:30:00",
    "failure_reason": "Insufficient funds"
  }
]
```

#### GET /api/reports/sla-breaches
Get settlement SLA breaches

**Response:**
```json
[
  {
    "settlement_id": "SETTLE00123",
    "merchant_id": "MERCH0012",
    "merchant_name": "Fashion Store",
    "settlement_date": "2025-01-20",
    "expected_settlement_date": "2025-01-17",
    "days_delayed": 3,
    "total_amount": 15000.00,
    "net_amount": 14625.00
  }
]
```

#### GET /api/reports/high-risk-transactions
Get high-risk transactions

**Parameters:**
- `risk_threshold` (query, optional): Risk score threshold (default: 70.0)

**Response:**
```json
[
  {
    "payment_id": "PAY005678",
    "customer_id": "CUST00456",
    "customer_name": "Jane Smith",
    "amount": 15000.00,
    "risk_score": 85.5,
    "transaction_date": "2025-01-15T16:45:00",
    "payment_status": "SUCCESS"
  }
]
```

### 5.3 Analytics

#### GET /api/analytics/payment-analytics
Get payment analytics from view

**Parameters:**
- `limit` (query, optional): Max records (default: 100, max: 1000)

#### GET /api/analytics/merchant-performance
Get merchant performance metrics

#### GET /api/analytics/customer-insights
Get customer insights

**Parameters:**
- `limit` (query, optional): Max records (default: 100, max: 1000)

---

## 6. ETL Pipeline

### 6.1 Data Generation

**FinancialDataGenerator Class:**
- Generates realistic customer data (500 records)
- Generates merchant data (50 records)
- Generates payment transactions (5000 records)
- Generates settlement data

**Features:**
- Realistic names, emails, phone numbers using Faker
- Risk-based payment success rates
- Outlier transaction amounts (5% high-value)
- Time-distributed transactions (90 days)
- Calculated risk scores
- Simulated SLA breaches

### 6.2 Data Loading

**ETLPipeline Class:**
- Loads data into PostgreSQL tables
- Handles conflicts with ON CONFLICT DO NOTHING
- Maintains referential integrity
- Logs progress and errors

### 6.3 Data Quality Rules

1. **Customers:**
   - Unique email addresses
   - Valid credit scores (300-850)
   - Risk category matches credit score

2. **Payments:**
   - Valid foreign keys (customer_id, merchant_id)
   - Positive amounts
   - Valid payment statuses
   - Failure reasons only for failed payments

3. **Settlements:**
   - Valid merchant references
   - Net amount = Total amount - Commission
   - SLA breach correctly calculated

---

## 7. Integration with BI Tools

### 7.1 Power BI Integration

**Connection Method:** PostgreSQL Direct Connect

**Steps:**
1. Open Power BI Desktop
2. Get Data → PostgreSQL database
3. Server: `localhost:5432`
4. Database: `financial_analytics`
5. Select views: `vw_payment_analytics`, `vw_merchant_performance`, `vw_customer_insights`
6. Load data and create visualizations

### 7.2 Tableau Integration

**Connection Method:** PostgreSQL Connector

**Steps:**
1. Open Tableau
2. Connect → To a Server → PostgreSQL
3. Server: `localhost`, Port: `5432`
4. Database: `financial_analytics`
5. Select tables/views
6. Create dashboards

### 7.3 Recommended Visualizations

1. **Payment Trends Dashboard:**
   - Line chart: Daily transaction volume
   - Bar chart: Success vs Failed payments
   - Pie chart: Payment method distribution

2. **Risk Heatmap:**
   - Scatter plot: Amount vs Risk Score
   - Color-coded by payment status

3. **Merchant Performance:**
   - Bar chart: Top merchants by revenue
   - Success rate comparison

4. **SLA Monitoring:**
   - Table: SLA breaches with days delayed
   - Gauge: Overall SLA compliance percentage

---

## 8. Error Handling

### 8.1 API Error Responses

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- 200: Success
- 404: Not Found
- 500: Internal Server Error
- 503: Service Unavailable

### 8.2 Database Error Handling

- Connection failures: Retry with exponential backoff
- Transaction rollback on errors
- Comprehensive error logging

---

## 9. Performance Optimization

### 9.1 Database Indexes
- Created on frequently queried columns
- Composite indexes for multi-column queries

### 9.2 Query Optimization
- Use of stored procedures for complex queries
- Materialized views for heavy computations (future)
- Query result caching (future)

### 9.3 API Performance
- Pagination for large result sets
- Connection pooling
- Async operations where applicable

---

## 10. Security Considerations

### 10.1 Database Security
- Parameterized queries (SQL injection prevention)
- Principle of least privilege for database users
- Encrypted connections (SSL/TLS)

### 10.2 API Security
- CORS configuration
- Rate limiting (future)
- Authentication & Authorization (future)
- Input validation

---

## 11. Testing Strategy

### 11.1 Unit Testing
- Test individual functions
- Mock database connections
- Test data generators

### 11.2 Integration Testing
- Test API endpoints
- Test stored procedures
- Test ETL pipeline

### 11.3 Performance Testing
- Load testing with 1000+ concurrent requests
- Database query performance
- ETL throughput testing

---

## 12. Deployment Guide

### 12.1 Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip/yarn package managers

### 12.2 Installation Steps

```bash
# Install Python dependencies
cd /app/backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with PostgreSQL credentials

# Initialize database
curl -X POST http://localhost:8001/api/etl/initialize

# Run ETL pipeline
curl -X POST http://localhost:8001/api/etl/run
```

### 12.3 Verification

```bash
# Health check
curl http://localhost:8001/api/health

# Test report endpoint
curl "http://localhost:8001/api/reports/daily-summary?report_date=2025-01-15"
```

---

## 13. Maintenance & Support

### 13.1 Monitoring
- API endpoint health checks
- Database connection monitoring
- Error log review

### 13.2 Backup & Recovery
- Daily database backups
- Transaction log backups
- Disaster recovery procedures

### 13.3 Upgrade Path
- Schema migrations using Alembic
- Zero-downtime deployments
- Rollback procedures

---

## 14. Future Enhancements

### Phase 2 Features:
- Automated email reports
- Real-time alerts via webhooks
- AI/ML anomaly detection
- Advanced fraud detection models
- Multi-currency support
- Custom report builder

---

## 15. Appendix

### 15.1 Sample Queries

**Get top 10 merchants by revenue:**
```sql
SELECT * FROM vw_merchant_performance 
ORDER BY total_revenue DESC 
LIMIT 10;
```

**Get high-risk customers:**
```sql
SELECT * FROM vw_customer_insights 
WHERE risk_category = 'HIGH' 
ORDER BY total_spent DESC;
```

### 15.2 Glossary

- **ETL:** Extract, Transform, Load
- **SLA:** Service Level Agreement
- **BI:** Business Intelligence
- **API:** Application Programming Interface
- **CRUD:** Create, Read, Update, Delete

---

**Document Control:**

| Version | Date | Author | Changes |
|---------|------|--------|----------|
| 1.0 | Dec 2025 | Technical Lead | Initial version |
