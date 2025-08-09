"""
SPEC-2 License Validation API - Proprietary Template Protection
Handles license validation for protected templates like Steve August's Focus Formula
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import logging
import hashlib
import hmac
from pathlib import Path

from src.vault.vault import VaultManager
from src.database.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# API Router
router = APIRouter(prefix="/api/templates", tags=["license-validation"])

# Initialize services
vault_manager = VaultManager()
db_manager = DatabaseManager()

# Pydantic Models
class LicenseValidationRequest(BaseModel):
    templateId: str = Field(..., description="Template ID requiring validation")
    licenseKey: str = Field(..., description="License key to validate")
    userId: str = Field(..., description="User ID for license tracking")

class LicenseValidationResponse(BaseModel):
    valid: bool = Field(..., description="License validity status")
    templateId: str = Field(..., description="Template ID")
    licenseType: str = Field(..., description="Type of license")
    expiresAt: Optional[datetime] = Field(default=None, description="License expiration")
    usageLimit: Optional[int] = Field(default=None, description="Usage limit")
    currentUsage: int = Field(default=0, description="Current usage count")
    features: List[str] = Field(default_factory=list, description="Enabled features")
    message: str = Field(default="", description="Validation message")

class LicenseUsageRequest(BaseModel):
    templateId: str = Field(..., description="Template ID")
    licenseKey: str = Field(..., description="License key")
    userId: str = Field(..., description="User ID")
    action: str = Field(..., description="Action being performed")

class TrialRequest(BaseModel):
    templateId: str = Field(..., description="Template ID for trial")
    userId: str = Field(..., description="User ID")
    email: str = Field(..., description="User email for trial tracking")

# License validation logic
PROTECTED_TEMPLATES = {
    "steve-august-focus-formula": {
        "name": "August Weekly Focus Formula",
        "licenseType": "individual",
        "trialDays": 7,
        "maxTrialUses": 3,
        "features": ["full-template", "habit-tracking", "decision-support", "vault-integration"],
        "purchaseUrl": "https://steve-august.com/focus-formula",
        "validationSecret": "steve_august_secret_key_2025"  # In production, use environment variable
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

def generate_license_hash(template_id: str, license_key: str, secret: str) -> str:
    """Generate secure hash for license validation"""
    message = f"{template_id}:{license_key}:{datetime.now().strftime('%Y-%m')}"
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

def validate_license_format(license_key: str) -> bool:
    """Validate license key format"""
    # Steve August license format: SA-YYYY-XXXX-XXXX-XXXX
    import re
    pattern = r'^SA-\d{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, license_key))

async def get_license_usage(template_id: str, user_id: str) -> Dict[str, Any]:
    """Get license usage data from Vault"""
    try:
        usage_path = f"licenses/usage/{template_id}/{user_id}"
        usage_data = await vault_manager.retrieve_memory(
            path=usage_path,
            decrypt=True
        )
        
        if not usage_data:
            return {
                "totalUses": 0,
                "trialStarted": None,
                "lastUsed": None,
                "trialUsesRemaining": PROTECTED_TEMPLATES.get(template_id, {}).get("maxTrialUses", 0)
            }
        
        return usage_data
        
    except Exception as e:
        logger.error(f"Failed to get license usage: {e}")
        return {"totalUses": 0, "trialUsesRemaining": 0}

async def update_license_usage(template_id: str, user_id: str, usage_data: Dict[str, Any]):
    """Update license usage data in Vault"""
    try:
        usage_path = f"licenses/usage/{template_id}/{user_id}"
        
        await vault_manager.store_memory(
            content=usage_data,
            path=usage_path,
            encrypt=True,
            metadata={
                "type": "license_usage",
                "template_id": template_id,
                "user_id": user_id,
                "last_updated": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to update license usage: {e}")

def validate_steve_august_license(license_key: str) -> Dict[str, Any]:
    """Validate Steve August Focus Formula license"""
    if not validate_license_format(license_key):
        return {"valid": False, "reason": "Invalid license key format"}
    
    # Extract year and check validity
    try:
        year = int(license_key.split('-')[1])
        current_year = datetime.now().year
        
        # License valid for current year and next year
        if year < current_year or year > current_year + 1:
            return {"valid": False, "reason": "License key expired or not yet valid"}
        
        # In a real implementation, this would validate against Steve August's licensing system
        # For now, we'll accept properly formatted keys for the current/next year
        return {
            "valid": True,
            "licenseType": "individual",
            "expiresAt": datetime(year + 1, 12, 31, 23, 59, 59),
            "features": ["full-template", "habit-tracking", "decision-support", "vault-integration"]
        }
        
    except (ValueError, IndexError):
        return {"valid": False, "reason": "Invalid license key format"}

# API Endpoints

@router.post("/validate-license", response_model=LicenseValidationResponse)
async def validate_template_license(
    request: LicenseValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate license for protected template"""
    try:
        template_id = request.templateId
        
        # Check if template requires license
        if template_id not in PROTECTED_TEMPLATES:
            return LicenseValidationResponse(
                valid=True,
                templateId=template_id,
                licenseType="free",
                message="Template does not require license"
            )
        
        template_config = PROTECTED_TEMPLATES[template_id]
        
        # Get current usage
        usage_data = await get_license_usage(template_id, request.userId)
        
        # Validate license key
        if template_id == "steve-august-focus-formula":
            validation_result = validate_steve_august_license(request.licenseKey)
        else:
            validation_result = {"valid": False, "reason": "Unknown template"}
        
        if validation_result["valid"]:
            # Valid license
            response = LicenseValidationResponse(
                valid=True,
                templateId=template_id,
                licenseType=validation_result["licenseType"],
                expiresAt=validation_result.get("expiresAt"),
                features=validation_result.get("features", []),
                currentUsage=usage_data["totalUses"],
                message="License validated successfully"
            )
        else:
            # Invalid license - check trial eligibility
            trial_uses_remaining = usage_data.get("trialUsesRemaining", template_config["maxTrialUses"])
            
            if trial_uses_remaining > 0:
                response = LicenseValidationResponse(
                    valid=True,
                    templateId=template_id,
                    licenseType="trial",
                    usageLimit=template_config["maxTrialUses"],
                    currentUsage=template_config["maxTrialUses"] - trial_uses_remaining,
                    features=["limited-template"],
                    message=f"Trial access: {trial_uses_remaining} uses remaining"
                )
            else:
                response = LicenseValidationResponse(
                    valid=False,
                    templateId=template_id,
                    licenseType="none",
                    currentUsage=usage_data["totalUses"],
                    message=f"License required. {validation_result.get('reason', 'Invalid license key')}"
                )
        
        logger.info(f"License validation for {template_id}: {response.valid}")
        return response
        
    except Exception as e:
        logger.error(f"License validation failed: {e}")
        raise HTTPException(status_code=500, detail="License validation failed")

@router.post("/record-usage")
async def record_template_usage(
    request: LicenseUsageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Record template usage for license tracking"""
    try:
        template_id = request.templateId
        user_id = request.userId
        
        # Get current usage
        usage_data = await get_license_usage(template_id, user_id)
        
        # Update usage
        usage_data["totalUses"] = usage_data.get("totalUses", 0) + 1
        usage_data["lastUsed"] = datetime.now().isoformat()
        usage_data["lastAction"] = request.action
        
        # Handle trial usage
        if not request.licenseKey or not validate_license_format(request.licenseKey):
            if usage_data.get("trialUsesRemaining", 0) > 0:
                usage_data["trialUsesRemaining"] -= 1
                
                if not usage_data.get("trialStarted"):
                    usage_data["trialStarted"] = datetime.now().isoformat()
        
        # Update usage data
        await update_license_usage(template_id, user_id, usage_data)
        
        logger.info(f"Recorded usage for {template_id} by user {user_id}")
        return {"message": "Usage recorded successfully", "currentUsage": usage_data["totalUses"]}
        
    except Exception as e:
        logger.error(f"Failed to record usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to record usage")

@router.post("/start-trial")
async def start_template_trial(
    request: TrialRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start trial for protected template"""
    try:
        template_id = request.templateId
        
        if template_id not in PROTECTED_TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_config = PROTECTED_TEMPLATES[template_id]
        
        # Check if trial already started
        usage_data = await get_license_usage(template_id, request.userId)
        
        if usage_data.get("trialStarted"):
            remaining_uses = usage_data.get("trialUsesRemaining", 0)
            return {
                "message": "Trial already active",
                "trialUsesRemaining": remaining_uses,
                "trialStarted": usage_data["trialStarted"]
            }
        
        # Start new trial
        trial_data = {
            "totalUses": 0,
            "trialStarted": datetime.now().isoformat(),
            "trialUsesRemaining": template_config["maxTrialUses"],
            "userEmail": request.email,
            "templateId": template_id
        }
        
        await update_license_usage(template_id, request.userId, trial_data)
        
        logger.info(f"Started trial for {template_id} for user {request.userId}")
        return {
            "message": "Trial started successfully",
            "trialDays": template_config["trialDays"],
            "trialUsesRemaining": template_config["maxTrialUses"],
            "purchaseUrl": template_config["purchaseUrl"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start trial: {e}")
        raise HTTPException(status_code=500, detail="Failed to start trial")

@router.get("/license-info/{template_id}")
async def get_template_license_info(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get license information for a template"""
    try:
        if template_id not in PROTECTED_TEMPLATES:
            return {"licenseRequired": False, "templateId": template_id}
        
        template_config = PROTECTED_TEMPLATES[template_id]
        
        return {
            "licenseRequired": True,
            "templateId": template_id,
            "templateName": template_config["name"],
            "licenseType": template_config["licenseType"],
            "trialDays": template_config["trialDays"],
            "maxTrialUses": template_config["maxTrialUses"],
            "features": template_config["features"],
            "purchaseUrl": template_config["purchaseUrl"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get license info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get license info")

@router.get("/user-licenses/{user_id}")
async def get_user_licenses(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all license information for a user"""
    try:
        user_licenses = {}
        
        for template_id in PROTECTED_TEMPLATES.keys():
            usage_data = await get_license_usage(template_id, user_id)
            
            user_licenses[template_id] = {
                "templateName": PROTECTED_TEMPLATES[template_id]["name"],
                "totalUses": usage_data.get("totalUses", 0),
                "trialActive": bool(usage_data.get("trialStarted") and usage_data.get("trialUsesRemaining", 0) > 0),
                "trialUsesRemaining": usage_data.get("trialUsesRemaining", 0),
                "lastUsed": usage_data.get("lastUsed"),
                "purchaseUrl": PROTECTED_TEMPLATES[template_id]["purchaseUrl"]
            }
        
        return {"userLicenses": user_licenses, "userId": user_id}
        
    except Exception as e:
        logger.error(f"Failed to get user licenses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user licenses")

# Export router
__all__ = ["router"]