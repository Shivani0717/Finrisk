# Financial Payments Analytics & Risk Monitoring System

## 🚀 Project Overview

A comprehensive financial analytics platform that ingests transaction data, processes it using ETL pipelines, performs risk checks, and presents insights via REST APIs and database views for BI tool integration.

**Key Features:**
- Advanced SQL stored procedures for complex analytics
- Real-time payment transaction monitoring
- Risk detection and fraud identification
- SLA breach monitoring for settlements
- ETL pipeline with automated data generation
- REST API for external integrations
- BI tool ready (Power BI, Tableau) with database views

---

## 📊 Architecture

```
Data Generation → ETL Pipeline → PostgreSQL → REST API → BI Tools
                                      ↓
                             Stored Procedures
                                  & Views
```

---

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 14+
- **ETL:** Python (Pandas, NumPy, Faker)
- **API Docs:** OpenAPI/Swagger
- **Libraries:** psycopg2, SQLAlchemy

---

## 🗂️ Database Schema

### Tables
1. **customers** - Customer information with risk profiles
2. **merchants** - Merchant details and commission rates
3. **payments** - Transaction records with risk scores
4. **settlements** - Merchant settlement tracking with SLA data

### Stored Procedures
1. `get_daily_transaction_summary(date)` - Daily transaction analytics
2. `detect_failed_payments(start_date, end_date)` - Failed payment identification
3. `identify_sla_breaches()` - SLA breach detection
4. `detect_high_risk_transactions(threshold)` - High-risk transaction flagging

### Views (BI Integration)
1. `vw_payment_analytics` - Aggregated payment metrics
2. `vw_merchant_performance` - Merchant KPIs
3. `vw_customer_insights` - Customer behavior analysis

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip package manager

### Installation

```bash
# Install dependencies
cd /app/backend
pip install -r requirements.txt

# Configure PostgreSQL connection
# Edit /app/backend/.env with your PostgreSQL credentials:
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=financial_analytics
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=postgres
```

### Initialize System

```bash
# Start the backend server (automatic via supervisor)
# The server runs on http://localhost:8001

# Initialize database schema and stored procedures
curl -X POST http://localhost:8001/api/etl/initialize

# Run ETL pipeline to generate and load sample data
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
    "settlements": 450
  }
}
```

---

## 📡 API Endpoints

### System Management
- `POST /api/etl/initialize` - Initialize database
- `POST /api/etl/run` - Execute ETL pipeline
- `GET /api/health` - Health check

### Reports
- `GET /api/reports/daily-summary?report_date=2025-01-15` - Daily summary
- `GET /api/reports/failed-payments?start_date=2025-01-01&end_date=2025-01-31` - Failed payments
- `GET /api/reports/sla-breaches` - SLA breaches
- `GET /api/reports/high-risk-transactions?risk_threshold=70.0` - High-risk transactions

### Analytics
- `GET /api/analytics/payment-analytics?limit=100` - Payment analytics
- `GET /api/analytics/merchant-performance` - Merchant performance
- `GET /api/analytics/customer-insights?limit=100` - Customer insights

### API Documentation
Access interactive API docs: `http://localhost:8001/docs`

---

## 🎯 Usage Examples

### Get Daily Transaction Summary
```bash
curl "http://localhost:8001/api/reports/daily-summary?report_date=2025-01-15"
```

**Response:**
```json
{
  "transaction_date": "2025-01-15",
  "total_transactions": 150,
  "successful_transactions": 142,
  "failed_transactions": 6,
  "success_rate": 94.67,
  "total_revenue": 118333.47
}
```

### Detect High-Risk Transactions
```bash
curl "http://localhost:8001/api/reports/high-risk-transactions?risk_threshold=75.0"
```

### Get Merchant Performance
```bash
curl http://localhost:8001/api/analytics/merchant-performance
```

---

## 📊 BI Tool Integration

### Power BI
1. Open Power BI Desktop
2. Get Data → PostgreSQL database
3. Server: `localhost:5432`
4. Database: `financial_analytics`
5. Import views:
   - `vw_payment_analytics`
   - `vw_merchant_performance`
   - `vw_customer_insights`
6. Create visualizations

### Tableau
1. Connect → PostgreSQL
2. Server: `localhost`, Port: `5432`
3. Database: `financial_analytics`
4. Select tables/views
5. Build dashboards

### Recommended Visualizations
- **Payment Trends:** Daily transaction volume, success rates
- **Risk Heatmap:** Amount vs Risk Score scatter plot
- **Merchant Performance:** Revenue comparison, success rates
- **SLA Monitoring:** Breach tracking, days delayed

---

## 🎓 Project Management Aspects

### Documentation
- **BRD:** `/app/docs/BRD_Business_Requirements.md`
- **FSD:** `/app/docs/FSD_Functional_Specification.md`

### Key Deliverables
✅ Business Requirement Document  
✅ Functional Specification Document  
✅ Database schema with relationships  
✅ Stored procedures for complex analytics  
✅ ETL pipeline with data validation  
✅ REST API with comprehensive endpoints  
✅ BI-ready database views  
✅ Sample data generation (5000+ transactions)  

### Business-Technical Mapping
| Business Need | Technical Solution |
|---------------|-------------------|
| Monitor payments | Real-time transaction tracking |
| Identify risks | Risk scoring algorithm + stored procedures |
| Reduce manual reporting | Automated ETL + scheduled reports |
| Financial insights | Advanced SQL analytics + BI views |
| SLA compliance | Automated breach detection |

---

## 🔧 Development

### Project Structure
```
/app/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── database.py            # Database connection management
│   ├── stored_procedures.py   # SQL stored procedures
│   ├── etl_pipeline.py        # ETL logic and data generation
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment configuration
├── docs/
│   ├── BRD_Business_Requirements.md
│   └── FSD_Functional_Specification.md
└── README.md
```

### Key Files
- `database.py` - PostgreSQL connection and schema initialization
- `stored_procedures.py` - Advanced SQL procedures and views
- `etl_pipeline.py` - Data generation and ETL logic
- `server.py` - REST API endpoints

---

## 📈 Data Generation

The ETL pipeline generates realistic financial data:

**Customers (500):**
- Names, emails, phone numbers
- Credit scores (300-850)
- Risk categories (LOW/MEDIUM/HIGH)

**Merchants (50):**
- Company names
- Business types (E-commerce, Retail, etc.)
- Commission rates (1.5-5.0%)

**Payments (5000):**
- Transaction amounts ($10-$50,000)
- Multiple payment methods
- Status distributions (Success/Failed/Pending/Refunded)
- Risk scores and fraud flags
- 90 days of historical data

**Settlements (~450):**
- Commission calculations
- SLA breach simulations
- Settlement status tracking

---

## 🎯 How This Matches Your JD Requirements

### Project Management
- ✅ Business requirement documentation
- ✅ Functional specifications
- ✅ Risk register and mitigation strategies
- ✅ Project timeline with phases

### Technical Skills
- ✅ Complex SQL stored procedures
- ✅ Database views and functions
- ✅ ETL pipeline implementation
- ✅ Data warehouse design
- ✅ Payment & finance domain knowledge

### Automation
- ✅ Automated ETL process
- ✅ Scheduled data generation
- ✅ API-driven report generation

### Analytics & BI
- ✅ Dashboard-ready views
- ✅ KPI calculations
- ✅ BI tool integration

### Business Translation
- ✅ Business rules → SQL logic
- ✅ Stakeholder requirements → Technical specs
- ✅ Financial metrics implementation

---

## 🚨 Production Issue Simulation

### Common Scenarios
1. **Missing Data:** Handle NULL values in ETL
2. **Incorrect Settlements:** Validate commission calculations
3. **Failed ETL Job:** Error logging and retry logic
4. **Performance Issues:** Query optimization with indexes

### Troubleshooting
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Test database connection
psql -h localhost -U postgres -d financial_analytics -c "SELECT 1;"

# Verify data loaded
curl http://localhost:8001/api/analytics/merchant-performance
```

---

## 📚 Next Steps (Phase 2)

- [ ] Automated email report generation
- [ ] Real-time alerts for high-risk transactions
- [ ] AI/ML anomaly detection (Isolation Forest)
- [ ] Advanced fraud detection models
- [ ] Scheduled report automation (Airflow)
- [ ] Production deployment with monitoring

---

## 📞 Support

For questions or issues, check:
- API Documentation: `http://localhost:8001/docs`
- Business Requirements: `/app/docs/BRD_Business_Requirements.md`
- Technical Specs: `/app/docs/FSD_Functional_Specification.md`

---

## 📝 License

This is a portfolio/demonstration project for technical and project management skills.

---

**Built with ❤️ to demonstrate:**
- Advanced SQL & Database Design
- ETL & Data Warehousing
- API Development
- Project Management
- Business-Technical Translation
- BI & Analytics Integration
