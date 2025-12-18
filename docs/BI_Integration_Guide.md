# BI Tool Integration Guide
## Financial Payments Analytics System

This guide provides step-by-step instructions for connecting Power BI and Tableau to the Financial Analytics database.

---

## Quick Start

### Database Connection Details

- **Host:** `localhost` (or your server IP)
- **Port:** `5432`
- **Database:** `financial_analytics`
- **Username:** `postgres`
- **Password:** `postgres`

---

## Power BI Integration

### Step 1: Install PostgreSQL Connector
1. Power BI Desktop includes PostgreSQL connector by default
2. No additional drivers needed

### Step 2: Connect to Database
1. Open Power BI Desktop
2. Click **Home** \u2192 **Get Data** \u2192 **More**
3. Search for **PostgreSQL database**
4. Click **Connect**

### Step 3: Enter Connection Details
1. **Server:** `localhost:5432`
2. **Database:** `financial_analytics`
3. **Data Connectivity mode:** Import (recommended) or DirectQuery
4. Click **OK**

### Step 4: Authentication
1. Select **Database** authentication
2. **User name:** `postgres`
3. **Password:** `postgres`
4. Click **Connect**

### Step 5: Select Data Sources
Select the following views and tables:
- \u2611\ufe0f `vw_payment_analytics`
- \u2611\ufe0f `vw_merchant_performance`
- \u2611\ufe0f `vw_customer_insights`
- \u2611\ufe0f `payments` (optional for detailed analysis)
- \u2611\ufe0f `settlements` (optional for settlement tracking)

Click **Load**

### Step 6: Create Relationships (if loading multiple tables)
1. Go to **Model** view
2. Power BI auto-detects relationships
3. Verify:
   - `payments.customer_id` \u2192 `customers.customer_id`
   - `payments.merchant_id` \u2192 `merchants.merchant_id`

### Recommended Power BI Visualizations

#### 1. Payment Trends Dashboard
```
Visualizations:
- Line Chart: Daily transaction volume (payment_date vs transaction_count)
- Clustered Column Chart: Success vs Failed payments by date
- Pie Chart: Payment method distribution
- Card: Total revenue (sum of total_amount where status = SUCCESS)
- Card: Success rate percentage
```

#### 2. Risk & Fraud Monitoring
```
Visualizations:
- Scatter Plot: Amount (X-axis) vs Risk Score (Y-axis)
  - Color by: payment_status
  - Size by: amount
- Table: High-risk transactions (filter risk_score >= 70)
- Gauge: Suspicious transaction percentage
```

#### 3. Merchant Performance
```
Visualizations:
- Bar Chart: Top 10 merchants by revenue
- Table: Merchant performance metrics
  - Columns: merchant_name, total_transactions, success_rate, total_revenue
- Treemap: Revenue by business_type
```

#### 4. Customer Insights
```
Visualizations:
- Stacked Bar Chart: Customers by risk_category
- Scatter Plot: Total spent vs Failed transactions
- Table: Top customers by total_spent
```

#### 5. SLA Monitoring
```
Data Source: Use stored procedure via custom query:
SELECT * FROM identify_sla_breaches();

Visualizations:
- Table: SLA breaches with days_delayed
- Card: Total SLA breaches count
- Bar Chart: Days delayed distribution
```

### Using Stored Procedures in Power BI

To call stored procedures:
1. **Get Data** \u2192 **PostgreSQL database**
2. Click **Advanced options**
3. In **SQL statement** field, enter:
   ```sql
   SELECT * FROM get_daily_transaction_summary(CURRENT_DATE);
   ```
4. Click **OK**

---

## Tableau Integration

### Step 1: Install PostgreSQL Driver
1. Download PostgreSQL ODBC driver from [https://www.postgresql.org/ftp/odbc/versions/](https://www.postgresql.org/ftp/odbc/versions/)
2. Install the driver
3. Restart Tableau

### Step 2: Connect to PostgreSQL
1. Open Tableau Desktop
2. Under **To a Server**, click **PostgreSQL**
3. Enter connection details:
   - **Server:** `localhost`
   - **Port:** `5432`
   - **Database:** `financial_analytics`
   - **Authentication:** Username and Password
   - **Username:** `postgres`
   - **Password:** `postgres`
4. Click **Sign In**

### Step 3: Select Data Sources
1. Under **Schema**, select **public**
2. Drag tables/views to the canvas:
   - `vw_payment_analytics`
   - `vw_merchant_performance`
   - `vw_customer_insights`

### Step 4: Create Relationships
Tableau automatically detects relationships based on naming conventions.

Verify in **Data Source** tab:
- Click on relationship lines to verify joins

### Recommended Tableau Dashboards

#### Dashboard 1: Executive Summary
```
Layout: 2x2 grid

Top Left: KPI Cards
- Total Revenue (SUM of total_amount where status = SUCCESS)
- Total Transactions
- Average Success Rate
- Active Merchants

Top Right: Line Chart
- X-axis: payment_date
- Y-axis: transaction_count
- Color: payment_status

Bottom Left: Bar Chart
- X-axis: merchant_name (Top 10)
- Y-axis: total_revenue
- Sort: Descending

Bottom Right: Pie Chart
- Dimension: payment_method
- Measure: transaction_count
```

#### Dashboard 2: Risk Heat Map
```
Main Visualization: Scatter Plot
- Rows: risk_score
- Columns: amount
- Color: payment_status
- Size: amount
- Tooltip: payment_id, customer_name, merchant_name

Filter Panel:
- Date range
- Risk score threshold
- Payment status
```

#### Dashboard 3: Settlement & SLA Tracking
```
Custom SQL Connection:
SELECT * FROM identify_sla_breaches();

Visualizations:
- Table: Settlement details
- Highlight Table: Days delayed by merchant
- Bar Chart: SLA breach count by merchant
```

### Using Stored Procedures in Tableau

Method 1: Initial SQL
1. Connect to PostgreSQL
2. In connection dialog, click **Initial SQL**
3. Enter: `SELECT * FROM get_daily_transaction_summary(CURRENT_DATE);`

Method 2: Custom SQL Query
1. After connecting, click **New Custom SQL**
2. Enter your query:
   ```sql
   SELECT * FROM detect_high_risk_transactions(75.0);
   ```
3. Click **OK**

---

## API-Based Integration (Alternative)

If direct database connection is not available, use the REST API:

### Endpoints for BI Tools

```
# Daily Summary
GET /api/reports/daily-summary?report_date=2025-12-15

# Failed Payments
GET /api/reports/failed-payments?start_date=2025-12-01&end_date=2025-12-31

# High Risk Transactions
GET /api/reports/high-risk-transactions?risk_threshold=70.0

# SLA Breaches
GET /api/reports/sla-breaches

# Payment Analytics
GET /api/analytics/payment-analytics?limit=1000

# Merchant Performance
GET /api/analytics/merchant-performance

# Customer Insights
GET /api/analytics/customer-insights?limit=500
```

### Connecting via API in Power BI

1. **Get Data** \u2192 **Web**
2. Enter API URL: `http://localhost:8001/api/analytics/payment-analytics`
3. Click **OK**
4. Power BI auto-parses JSON response
5. Click **Into Table** \u2192 **Expand** columns

### Connecting via API in Tableau

1. **Connect** \u2192 **Web Data Connector**
2. Enter API URL
3. Use Web Data Connector to parse JSON
4. Alternatively, use Tableau's **JSON file** connector:
   - Download API response as JSON file
   - **Connect** \u2192 **JSON file**

---

## Sample Queries for Custom Analysis

### Query 1: Daily Revenue Trend (Last 30 Days)
```sql
SELECT 
    DATE(transaction_date) as date,
    SUM(amount) FILTER (WHERE payment_status = 'SUCCESS') as revenue,
    COUNT(*) as transactions
FROM payments
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(transaction_date)
ORDER BY date;
```

### Query 2: Merchant Performance Comparison
```sql
SELECT 
    m.merchant_name,
    m.business_type,
    COUNT(p.payment_id) as total_txns,
    SUM(p.amount) FILTER (WHERE p.payment_status = 'SUCCESS') as revenue,
    ROUND(AVG(CASE WHEN p.payment_status = 'SUCCESS' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
FROM merchants m
LEFT JOIN payments p ON m.merchant_id = p.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.business_type
HAVING COUNT(p.payment_id) > 0
ORDER BY revenue DESC;
```

### Query 3: Risk Distribution by Country
```sql
SELECT 
    c.country,
    c.risk_category,
    COUNT(p.payment_id) as transactions,
    SUM(p.amount) as total_amount,
    AVG(p.risk_score) as avg_risk_score
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.country, c.risk_category
ORDER BY c.country, c.risk_category;
```

### Query 4: Payment Method Performance
```sql
SELECT 
    payment_method,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE payment_status = 'SUCCESS') as successful,
    COUNT(*) FILTER (WHERE payment_status = 'FAILED') as failed,
    ROUND(AVG(processing_time_seconds), 2) as avg_processing_time
FROM payments
GROUP BY payment_method
ORDER BY total DESC;
```

---

## Data Refresh Strategy

### Power BI
**Scheduled Refresh:**
1. Publish report to Power BI Service
2. Configure dataset settings
3. Set refresh schedule (e.g., daily at 6 AM)

**Manual Refresh:**
- Click **Refresh** in Power BI Desktop

### Tableau
**Live Connection:** 
- Data refreshes on dashboard load
- Best for real-time monitoring

**Extract:**
- Create extract for better performance
- Schedule extract refresh via Tableau Server

---

## Performance Optimization Tips

### 1. Use Views Instead of Base Tables
- Views are pre-aggregated
- Faster query performance
- Cleaner data model

### 2. Apply Filters Early
- Filter dates at connection level
- Reduce data volume
- Faster dashboard load times

### 3. Use Aggregated Data
- For trend analysis, use daily/weekly aggregates
- Avoid loading transaction-level data unnecessarily

### 4. Optimize Relationships
- Use proper join types
- Verify cardinality (1:many, many:1)

### 5. Limit Historical Data
```sql
-- In custom SQL, filter recent data
SELECT * FROM vw_payment_analytics
WHERE payment_date >= CURRENT_DATE - INTERVAL '90 days';
```

---

## Troubleshooting

### Connection Issues
**Problem:** Cannot connect to database
**Solutions:**
1. Verify PostgreSQL is running: `sudo service postgresql status`
2. Check firewall settings
3. Verify credentials
4. Test connection: `psql -h localhost -U postgres -d financial_analytics`

### Slow Performance
**Problem:** Dashboard loads slowly
**Solutions:**
1. Use database views instead of raw tables
2. Create indexes on frequently filtered columns
3. Use data extracts instead of live connections
4. Limit date range in queries

### Data Not Showing
**Problem:** No data in visualizations
**Solutions:**
1. Verify ETL pipeline ran: `curl -X POST http://localhost:8001/api/etl/run`
2. Check date filters
3. Verify data exists: `curl http://localhost:8001/api/analytics/payment-analytics`

---

## Security Best Practices

1. **Use Read-Only Credentials** for BI tools
   ```sql
   CREATE USER bi_reader WITH PASSWORD 'secure_password';
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_reader;
   GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO bi_reader;
   ```

2. **Restrict Network Access**
   - Configure `pg_hba.conf` to limit connections
   - Use SSL/TLS for connections

3. **Row-Level Security** (Optional)
   ```sql
   CREATE POLICY merchant_policy ON payments
   FOR SELECT USING (merchant_id = current_setting('app.current_merchant')::VARCHAR);
   ```

---

## Support & Resources

- **API Documentation:** `http://localhost:8001/docs`
- **Database Schema:** `/app/docs/FSD_Functional_Specification.md`
- **Business Requirements:** `/app/docs/BRD_Business_Requirements.md`

---

**Last Updated:** December 2025  
**Version:** 1.0
