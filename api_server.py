import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from database_manager import DatabaseManager
from report_generator import ReportGenerator
from config import settings
from logging_config import configure_logging
from typing import Optional

# Configure logging
configure_logging()

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize database manager
database_manager = DatabaseManager()

# Initialize report generator
report_generator = ReportGenerator()

# Define request and response models
class SoHStatusRequest(BaseModel):
    battery_id: str

class SoHStatusResponse(BaseModel):
    battery_id: str
    soh_status: float

class TriggerMeasurementRequest(BaseModel):
    battery_id: str

class TriggerMeasurementResponse(BaseModel):
    measurement_id: str

class DownloadReportsRequest(BaseModel):
    battery_id: str

class DownloadReportsResponse(BaseModel):
    reports: List[str]

class QueryDegradationModesRequest(BaseModel):
    battery_id: str

class QueryDegradationModesResponse(BaseModel):
    degradation_modes: List[str]

# Define exception classes
class SoHStatusException(Exception):
    pass

class TriggerMeasurementException(Exception):
    pass

class DownloadReportsException(Exception):
    pass

class QueryDegradationModesException(Exception):
    pass

# Define helper functions
def get_soh_status(battery_id: str) -> float:
    try:
        soh_status = database_manager.get_soh_status(battery_id)
        return soh_status
    except Exception as e:
        logger.error(f"Error getting SoH status: {e}")
        raise SoHStatusException("Error getting SoH status")

def trigger_measurement(battery_id: str) -> str:
    try:
        measurement_id = database_manager.trigger_measurement(battery_id)
        return measurement_id
    except Exception as e:
        logger.error(f"Error triggering measurement: {e}")
        raise TriggerMeasurementException("Error triggering measurement")

def download_reports(battery_id: str) -> List[str]:
    try:
        reports = report_generator.generate_reports(battery_id)
        return reports
    except Exception as e:
        logger.error(f"Error downloading reports: {e}")
        raise DownloadReportsException("Error downloading reports")

def query_degradation_modes(battery_id: str) -> List[str]:
    try:
        degradation_modes = database_manager.query_degradation_modes(battery_id)
        return degradation_modes
    except Exception as e:
        logger.error(f"Error querying degradation modes: {e}")
        raise QueryDegradationModesException("Error querying degradation modes")

# Define API endpoints
@app.get("/soh_status", response_model=SoHStatusResponse)
async def get_soh_status_endpoint(request: SoHStatusRequest):
    try:
        soh_status = get_soh_status(request.battery_id)
        return SoHStatusResponse(battery_id=request.battery_id, soh_status=soh_status)
    except SoHStatusException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger_measurement", response_model=TriggerMeasurementResponse)
async def trigger_measurement_endpoint(request: TriggerMeasurementRequest):
    try:
        measurement_id = trigger_measurement(request.battery_id)
        return TriggerMeasurementResponse(measurement_id=measurement_id)
    except TriggerMeasurementException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download_reports", response_model=DownloadReportsResponse)
async def download_reports_endpoint(request: DownloadReportsRequest):
    try:
        reports = download_reports(request.battery_id)
        return DownloadReportsResponse(reports=reports)
    except DownloadReportsException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_degradation_modes", response_model=QueryDegradationModesResponse)
async def query_degradation_modes_endpoint(request: QueryDegradationModesRequest):
    try:
        degradation_modes = query_degradation_modes(request.battery_id)
        return QueryDegradationModesResponse(degradation_modes=degradation_modes)
    except QueryDegradationModesException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)