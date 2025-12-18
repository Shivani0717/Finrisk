# Quick Start Guide
## Financial Payments Analytics System

**5-Minute Setup Guide** 🚀

---

## Prerequisites ✅

- PostgreSQL installed and running
- Python 3.11+ with pip
- Backend server running on port 8001

---

## Step 1: Initialize System

```bash
# Initialize database schema and stored procedures
curl -X POST http://localhost:8001/api/etl/initialize
```

**Expected Output:**
```json
{
  "status": "success",
  "message": "Database initialized successfully"
}
```

---

## Step 2: Load Sample Data

```bash
# Run ETL pipeline to generate 5000+ transactions
curl -X POST http://localhost:8001/api/etl/run
```

**Expected Output:**
```json
{
  "status": "success",
  "message": "ETL pipeline completed successfully",
  "records_loaded": {
    "customers": 500,
    "merchants": 50,
    "payments": 5000,
    "settlements": 2636
  }
}
```

---

## Step 3: Test APIs

### Health Check
```bash
curl http://localhost:8001/api/health
```

### Daily Summary
```bash
curl "http://localhost:8001/api/reports/daily-summary?report_date=2025-12-15"
```

### High-Risk Transactions
```bash
curl "http://localhost:8001/api/reports/high-risk-transactions?risk_threshold=85"
```

### Merchant Performance
```bash
curl http://localhost:8001/api/analytics/merchant-performance
```

---

## Step 4: Connect BI Tool

### Power BI
1. Get Data → PostgreSQL database
2. Server: `localhost:5432`
3. Database: `financial_analytics`
4. Username: `postgres` | Password: `postgres`
5. Load views: `vw_payment_analytics`, `vw_merchant_performance`, `vw_customer_insights`

### Tableau
1. Connect → PostgreSQL
2. Same credentials as above
3. Drag views to canvas

---

## Key Endpoints 📡

| Endpoint | Purpose |
|----------|---------|
| `POST /api/etl/initialize` | Setup database |
| `POST /api/etl/run` | Load data |
| `GET /api/health` | Check status |
| `GET /api/reports/daily-summary` | Daily KPIs |
| `GET /api/reports/failed-payments` | Failed txns |
| `GET /api/reports/sla-breaches` | SLA violations |
| `GET /api/reports/high-risk-transactions` | Risk detection |
| `GET /api/analytics/payment-analytics` | Payment data |
| `GET /api/analytics/merchant-performance` | Merchant KPIs |
| `GET /api/analytics/customer-insights` | Customer data |

---

## Database Connection 🗄️

**Direct SQL Access:**
```bash
psql -h localhost -U postgres -d financial_analytics
```

**Sample Queries:**
```sql
-- Daily summary
SELECT * FROM get_daily_transaction_summary('2025-12-15');

-- Failed payments
SELECT * FROM detect_failed_payments('2025-12-01', '2025-12-31');

-- SLA breaches
SELECT * FROM identify_sla_breaches();

-- High-risk transactions
SELECT * FROM detect_high_risk_transactions(75.0);

-- Payment analytics view
SELECT * FROM vw_payment_analytics LIMIT 100;

-- Merchant performance view
SELECT * FROM vw_merchant_performance ORDER BY total_revenue DESC;

-- Customer insights view
SELECT * FROM vw_customer_insights ORDER BY total_spent DESC LIMIT 50;
```

---

## API Documentation 📚

Interactive API docs available at:
```
http://localhost:8001/docs
```

---

## Troubleshooting 🔧

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Test connection
psql -h localhost -U postgres -c "SELECT 1;"
```

### Backend Issues
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

### No Data Returned
```bash
# Re-run ETL pipeline
curl -X POST http://localhost:8001/api/etl/run

# Verify data loaded
psql -h localhost -U postgres -d financial_analytics -c "SELECT COUNT(*) FROM payments;"
```

---

## Next Steps 🎯

1. ✅ **Explore API** → Try all endpoints
2. ✅ **Connect BI Tool** → Create visualizations
3. ✅ **Run Custom Queries** → Use SQL examples
4. ✅ **Review Documentation** → BRD, FSD, BI Guide

---

## Documentation Files 📖

- **README.md** - Project overview
- **docs/BRD_Business_Requirements.md** - Business requirements
- **docs/FSD_Functional_Specification.md** - Technical specs
- **docs/BI_Integration_Guide.md** - BI tool setup
- **docs/SQL_Query_Examples.md** - Sample queries
- **docs/PROJECT_SUMMARY.md** - Project summary

---

## Support 💬

- API Docs: `http://localhost:8001/docs`
- Database: `financial_analytics` on `localhost:5432`
- Backend: Running on port `8001`

---

**System Status:** ✅ READY

**Time to Value:** < 5 minutes

**Total Records:** 5000+ transactions across 90 days
