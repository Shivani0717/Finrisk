from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

# Import database modules
from database import get_db_connection, get_db_cursor, init_database
from stored_procedures import create_stored_procedures
from etl_pipeline import ETLPipeline

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Financial Payments Analytics API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class DailyTransactionSummary(BaseModel):
    transaction_date: date
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    refunded_transactions: int
    total_amount: float
    success_rate: float
    avg_transaction_amount: float
    total_revenue: float

class FailedPayment(BaseModel):
    payment_id: str
    customer_id: str
    customer_name: str
    merchant_name: str
    amount: float
    payment_method: str
    transaction_date: datetime
    failure_reason: Optional[str]

class SLABreach(BaseModel):
    settlement_id: str
    merchant_id: str
    merchant_name: str
    settlement_date: date
    expected_settlement_date: date
    days_delayed: int
    total_amount: float
    net_amount: float

class HighRiskTransaction(BaseModel):
    payment_id: str
    customer_id: str
    customer_name: str
    amount: float
    risk_score: float
    transaction_date: datetime
    payment_status: str

class PaymentAnalytics(BaseModel):
    payment_date: date
    payment_status: str
    payment_method: str
    currency: str
    merchant_name: str
    business_type: str
    customer_country: str
    transaction_count: int
    total_amount: float
    avg_amount: float
    avg_processing_time: Optional[float]
    suspicious_count: int

class MerchantPerformance(BaseModel):
    merchant_id: str
    merchant_name: str
    business_type: str
    status: str
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    total_revenue: Optional[float]
    avg_transaction_amount: Optional[float]
    success_rate: float

class CustomerInsight(BaseModel):
    customer_id: str
    customer_name: str
    email: str
    country: str
    credit_score: int
    risk_category: str
    total_transactions: int
    total_spent: Optional[float]
    avg_transaction_amount: Optional[float]
    failed_transaction_count: int
    last_transaction_date: Optional[datetime]

class ETLStatus(BaseModel):
    status: str
    message: str
    records_loaded: Optional[dict] = None

# API Routes
@api_router.get("/")
async def root():
    return {
        "message": "Financial Payments Analytics & Risk Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "analytics": "/api/analytics/*",
            "reports": "/api/reports/*",
            "etl": "/api/etl/*"
        }
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@api_router.post("/etl/initialize", response_model=ETLStatus)
async def initialize_database():
    """Initialize database schema and stored procedures"""
    try:
        init_database()
        create_stored_procedures()
        return ETLStatus(
            status="success",
            message="Database initialized successfully"
        )
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/etl/run", response_model=ETLStatus)
async def run_etl_pipeline():
    """Execute ETL pipeline to generate and load data"""
    try:
        records = ETLPipeline.run_etl()
        return ETLStatus(
            status="success",
            message="ETL pipeline completed successfully",
            records_loaded=records
        )
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/daily-summary", response_model=DailyTransactionSummary)
async def get_daily_summary(report_date: date = Query(..., description="Date for the report (YYYY-MM-DD)")):
    """Get daily transaction summary using stored procedure"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT * FROM get_daily_transaction_summary(%s)", (report_date,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="No data found for the specified date")
            
            return DailyTransactionSummary(**dict(result))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/failed-payments", response_model=List[FailedPayment])
async def get_failed_payments(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get failed payments report using stored procedure"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute(
                "SELECT * FROM detect_failed_payments(%s, %s)",
                (start_date, end_date)
            )
            results = cursor.fetchall()
            return [FailedPayment(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get failed payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/sla-breaches", response_model=List[SLABreach])
async def get_sla_breaches():
    """Get SLA breach report using stored procedure"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT * FROM identify_sla_breaches()")
            results = cursor.fetchall()
            return [SLABreach(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get SLA breaches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/high-risk-transactions", response_model=List[HighRiskTransaction])
async def get_high_risk_transactions(risk_threshold: float = Query(70.0, description="Risk score threshold")):
    """Get high-risk transactions using stored procedure"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute(
                "SELECT * FROM detect_high_risk_transactions(%s)",
                (risk_threshold,)
            )
            results = cursor.fetchall()
            return [HighRiskTransaction(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get high-risk transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/payment-analytics", response_model=List[PaymentAnalytics])
async def get_payment_analytics(limit: int = Query(100, le=1000)):
    """Get payment analytics from database view"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute(f"SELECT * FROM vw_payment_analytics ORDER BY payment_date DESC LIMIT {limit}")
            results = cursor.fetchall()
            return [PaymentAnalytics(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get payment analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/merchant-performance", response_model=List[MerchantPerformance])
async def get_merchant_performance():
    """Get merchant performance from database view"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT * FROM vw_merchant_performance ORDER BY total_revenue DESC")
            results = cursor.fetchall()
            return [MerchantPerformance(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get merchant performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/customer-insights", response_model=List[CustomerInsight])
async def get_customer_insights(limit: int = Query(100, le=1000)):
    """Get customer insights from database view"""
    try:
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute(f"SELECT * FROM vw_customer_insights ORDER BY total_spent DESC LIMIT {limit}")
            results = cursor.fetchall()
            return [CustomerInsight(**dict(row)) for row in results]
    except Exception as e:
        logger.error(f"Failed to get customer insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Financial Analytics API started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Financial Analytics API shutdown")
