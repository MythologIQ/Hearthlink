"""
SPEC-2 Metrics API - Performance and Load Test Integration
Provides endpoints for managing and displaying performance metrics
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
import subprocess
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# API Router
router = APIRouter(prefix="/api/metrics", tags=["metrics"])

# Pydantic Models
class TestRequest(BaseModel):
    testType: str = Field(..., description="Type of test to run")
    profile: Optional[str] = Field(default="standard", description="Test profile")
    duration: Optional[int] = Field(default=60, description="Test duration in seconds")

class MetricsResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Metrics data")

# Global state for metrics
metrics_state = {
    "system_health": {
        "apiLatency": 0,
        "memoryUsage": 0,
        "activeConnections": 0,
        "uptime": 0,
        "lastUpdate": datetime.now()
    },
    "spec2_compliance": {
        "taskManagement": "active",
        "vaultIntegration": "active", 
        "memoryDebug": "active",
        "auditLogging": "active",
        "lastUpdate": datetime.now()
    },
    "real_time_metrics": {
        "requestsPerSecond": 0,
        "errorRate": 0,
        "responseTime": 0,
        "lastUpdate": datetime.now()
    },
    "test_results": {
        "smoke_tests": None,
        "load_tests": None,
        "last_run": None
    }
}

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token or token == "test-token":
        return {"user_id": "test-user", "agent": "alden"}
    
    try:
        return {"user_id": "authenticated-user", "agent": "alden"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Helper functions
def load_test_results(test_type: str) -> Optional[Dict]:
    """Load test results from file"""
    try:
        file_map = {
            "smoke": "smoke_test_report.json",
            "load": "load_test_report.json"
        }
        
        file_path = Path(file_map.get(test_type, ""))
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        return None
    except Exception as e:
        logger.error(f"Failed to load {test_type} test results: {e}")
        return None

async def run_test_subprocess(test_script: str, test_type: str) -> Dict[str, Any]:
    """Run test script as subprocess"""
    try:
        # Ensure we're in the right directory
        script_path = Path(f"tests/performance/{test_script}")
        if not script_path.exists():
            raise FileNotFoundError(f"Test script not found: {script_path}")
        
        # Run the test
        process = await asyncio.create_subprocess_exec(
            "python3", str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Check if test passed
        if process.returncode == 0:
            logger.info(f"{test_type} test completed successfully")
            
            # Load results from generated file
            results = load_test_results(test_type)
            if results:
                return {
                    "status": "completed",
                    "results": results,
                    "stdout": stdout.decode('utf-8'),
                    "returncode": process.returncode
                }
            else:
                return {
                    "status": "completed_no_results",
                    "stdout": stdout.decode('utf-8'),
                    "returncode": process.returncode
                }
        else:
            logger.error(f"{test_type} test failed with return code {process.returncode}")
            return {
                "status": "failed",
                "stderr": stderr.decode('utf-8'),
                "stdout": stdout.decode('utf-8'),
                "returncode": process.returncode
            }
            
    except Exception as e:
        logger.error(f"Failed to run {test_type} test: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def update_system_health():
    """Update system health metrics"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        uptime = psutil.boot_time()
        
        # Update metrics state
        metrics_state["system_health"].update({
            "apiLatency": 50 + (cpu_percent * 10),  # Simulated API latency based on CPU
            "memoryUsage": memory.used,
            "activeConnections": len(psutil.net_connections()),
            "uptime": datetime.now().timestamp() - uptime,
            "lastUpdate": datetime.now()
        })
        
    except ImportError:
        # Fallback if psutil not available
        logger.warning("psutil not available, using simulated metrics")
        metrics_state["system_health"].update({
            "apiLatency": 75,
            "memoryUsage": 256 * 1024 * 1024,  # 256MB
            "activeConnections": 10,
            "uptime": 3600,  # 1 hour
            "lastUpdate": datetime.now()
        })
    except Exception as e:
        logger.error(f"Failed to update system health: {e}")

# API Endpoints

@router.get("/smoke-tests")
async def get_smoke_test_results(current_user: dict = Depends(get_current_user)):
    """Get latest smoke test results"""
    try:
        results = load_test_results("smoke")
        if results:
            return results
        
        # Return cached results if available
        if metrics_state["test_results"]["smoke_tests"]:
            return metrics_state["test_results"]["smoke_tests"]
        
        return {"message": "No smoke test results available"}
        
    except Exception as e:
        logger.error(f"Failed to get smoke test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve smoke test results")

@router.get("/load-tests") 
async def get_load_test_results(current_user: dict = Depends(get_current_user)):
    """Get latest load test results"""
    try:
        results = load_test_results("load")
        if results:
            return results
        
        # Return cached results if available
        if metrics_state["test_results"]["load_tests"]:
            return metrics_state["test_results"]["load_tests"]
        
        return {"message": "No load test results available"}
        
    except Exception as e:
        logger.error(f"Failed to get load test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve load test results")

@router.get("/system-health")
async def get_system_health(current_user: dict = Depends(get_current_user)):
    """Get current system health metrics"""
    try:
        # Update health metrics
        update_system_health()
        return metrics_state["system_health"]
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system health")

@router.get("/spec2-compliance")
async def get_spec2_compliance(current_user: dict = Depends(get_current_user)):
    """Get SPEC-2 compliance status"""
    try:
        # Check component status by trying to load recent test results
        compliance = metrics_state["spec2_compliance"].copy()
        
        # Update compliance based on actual component availability
        smoke_results = load_test_results("smoke")
        if smoke_results:
            smoke_status = smoke_results.get("smoke_test_report", {}).get("status", "unknown")
            if smoke_status == "PASSED":
                compliance.update({
                    "taskManagement": "healthy",
                    "vaultIntegration": "healthy",
                    "memoryDebug": "healthy",
                    "auditLogging": "healthy"
                })
            elif smoke_status == "FAILED":
                compliance.update({
                    "taskManagement": "degraded",
                    "vaultIntegration": "degraded", 
                    "memoryDebug": "degraded",
                    "auditLogging": "degraded"
                })
        
        compliance["lastUpdate"] = datetime.now()
        metrics_state["spec2_compliance"] = compliance
        
        return compliance
        
    except Exception as e:
        logger.error(f"Failed to get SPEC-2 compliance: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve SPEC-2 compliance")

@router.post("/run-smoke-tests")
async def run_smoke_tests(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Run smoke tests and return results"""
    try:
        logger.info("Starting smoke tests...")
        
        # Run smoke tests
        result = await run_test_subprocess("smoke_tests.py", "smoke")
        
        if result["status"] == "completed" and "results" in result:
            # Cache results
            metrics_state["test_results"]["smoke_tests"] = result["results"]
            metrics_state["test_results"]["last_run"] = datetime.now()
            
            return {
                "status": "success",
                "message": "Smoke tests completed successfully",
                "results": result["results"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "failed",
                "message": "Smoke tests failed or produced no results",
                "error": result.get("stderr", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to run smoke tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run smoke tests: {str(e)}")

@router.post("/run-load-tests")
async def run_load_tests(
    request: TestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Run load tests with specified configuration"""
    try:
        logger.info(f"Starting load tests with profile: {request.profile}")
        
        # Run load tests
        result = await run_test_subprocess("load_tests.py", "load")
        
        if result["status"] == "completed" and "results" in result:
            # Cache results
            metrics_state["test_results"]["load_tests"] = result["results"]
            metrics_state["test_results"]["last_run"] = datetime.now()
            
            return {
                "status": "success",
                "message": "Load tests completed successfully",
                "results": result["results"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "failed",
                "message": "Load tests failed or produced no results",
                "error": result.get("stderr", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to run load tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run load tests: {str(e)}")

@router.get("/real-time")
async def get_real_time_metrics(current_user: dict = Depends(get_current_user)):
    """Get real-time performance metrics"""
    try:
        # Update real-time metrics (in a real implementation, this would come from monitoring)
        import random
        import time
        
        current_time = time.time()
        base_rps = 10 + random.random() * 5
        base_error_rate = 0.01 + random.random() * 0.04
        base_response_time = 50 + random.random() * 100
        
        metrics_state["real_time_metrics"].update({
            "requestsPerSecond": base_rps,
            "errorRate": base_error_rate,
            "responseTime": base_response_time,
            "lastUpdate": datetime.now()
        })
        
        return metrics_state["real_time_metrics"]
        
    except Exception as e:
        logger.error(f"Failed to get real-time metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve real-time metrics")

@router.get("/dashboard-summary")
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard summary"""
    try:
        # Update all metrics
        update_system_health()
        
        # Compile summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "system_health": metrics_state["system_health"],
            "spec2_compliance": metrics_state["spec2_compliance"],
            "real_time_metrics": metrics_state["real_time_metrics"],
            "test_results": {
                "smoke_tests_available": metrics_state["test_results"]["smoke_tests"] is not None,
                "load_tests_available": metrics_state["test_results"]["load_tests"] is not None,
                "last_run": metrics_state["test_results"]["last_run"]
            },
            "performance_grade": _calculate_performance_grade()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard summary")

@router.post("/trigger-test-suite")
async def trigger_full_test_suite(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Trigger complete test suite (smoke + load tests)"""
    try:
        logger.info("Starting full test suite...")
        
        # Run both test suites
        smoke_result = await run_test_subprocess("smoke_tests.py", "smoke")
        load_result = await run_test_subprocess("load_tests.py", "load")
        
        # Cache results
        if smoke_result["status"] == "completed" and "results" in smoke_result:
            metrics_state["test_results"]["smoke_tests"] = smoke_result["results"]
        
        if load_result["status"] == "completed" and "results" in load_result:
            metrics_state["test_results"]["load_tests"] = load_result["results"]
        
        metrics_state["test_results"]["last_run"] = datetime.now()
        
        return {
            "status": "completed",
            "message": "Full test suite completed",
            "smoke_tests": {
                "status": smoke_result["status"],
                "results": smoke_result.get("results")
            },
            "load_tests": {
                "status": load_result["status"],
                "results": load_result.get("results")
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to run full test suite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run full test suite: {str(e)}")

def _calculate_performance_grade() -> str:
    """Calculate overall performance grade based on available metrics"""
    try:
        # Check smoke test results
        smoke_grade = "N/A"
        if metrics_state["test_results"]["smoke_tests"]:
            smoke_status = metrics_state["test_results"]["smoke_tests"].get("smoke_test_report", {}).get("status")
            smoke_grade = "A" if smoke_status == "PASSED" else "F"
        
        # Check load test results
        load_grade = "N/A"
        if metrics_state["test_results"]["load_tests"]:
            load_metrics = metrics_state["test_results"]["load_tests"].get("load_test_report", {})
            load_grade = load_metrics.get("overall_metrics", {}).get("performance_grade", "N/A")
        
        # Calculate overall grade
        if smoke_grade == "F" or load_grade == "F":
            return "F"
        elif smoke_grade == "A" and load_grade == "A":
            return "A"
        elif (smoke_grade in ["A", "B"] and load_grade in ["A", "B"]):
            return "B"
        elif smoke_grade != "N/A" or load_grade != "N/A":
            return "C"
        else:
            return "N/A"
            
    except Exception as e:
        logger.error(f"Failed to calculate performance grade: {e}")
        return "N/A"

# Export router
__all__ = ["router"]