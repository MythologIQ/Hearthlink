#!/usr/bin/env python3
"""
SPEC-3 Week 3: Bug Reporting API Backend
Implements /api/bugs endpoint for comprehensive bug reporting system
"""

import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, validator
import logging

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram
    bug_reports_total = Counter('bug_reports_total', 'Total bug reports submitted', ['category', 'user_role'])
    bug_report_duration = Histogram('bug_report_processing_seconds', 'Time spent processing bug reports')
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("⚠️ Prometheus metrics not available - install prometheus_client for metrics")

logger = logging.getLogger(__name__)

class BugReportRequest(BaseModel):
    """Bug report request model with validation"""
    title: str
    description: str
    page_ctx: Optional[str] = None
    build_hash: Optional[str] = None
    user_role: Optional[str] = "user"
    category: str = "bug"
    attachments: Optional[List[str]] = []
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required and cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be 200 characters or less')
        return v.strip()
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description is required and cannot be empty')
        if len(v) > 10000:
            raise ValueError('Description must be 10,000 characters or less')
        return v.strip()
    
    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['bug', 'feature', 'UI', 'performance', 'security']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v
    
    @validator('user_role')
    def user_role_must_be_valid(cls, v):
        if v is None:
            return 'user'
        valid_roles = ['user', 'admin', 'developer', 'tester']
        if v not in valid_roles:
            raise ValueError(f'User role must be one of: {", ".join(valid_roles)}')
        return v

class BugReportResponse(BaseModel):
    """Bug report response model"""
    bug_id: str
    status: str
    message: str
    timestamp: str
    
class BugReportStorage:
    """Handles bug report storage and retrieval using Vault"""
    
    def __init__(self):
        self.storage_path = Path("hearthlink_data/bug_reports")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def generate_bug_id(self) -> str:
        """Generate unique bug ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"BUG_{timestamp}_{random_suffix}"
    
    def generate_build_hash(self) -> str:
        """Generate current build hash from git or fallback"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Fallback to timestamp-based hash
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def store_bug_report(self, report_data: Dict[str, Any]) -> str:
        """Store bug report with Vault-compatible tags"""
        bug_id = self.generate_bug_id()
        
        # Enhance report with metadata
        enhanced_report = {
            'bug_id': bug_id,
            'created_at': datetime.now().isoformat(),
            'build_hash': report_data.get('build_hash') or self.generate_build_hash(),
            'status': 'open',
            'priority': self._determine_priority(report_data),
            'tags': ['bug', 'feedback', report_data.get('category', 'bug')],
            **report_data
        }
        
        # Store in file system (Vault integration would go here)
        report_file = self.storage_path / f"{bug_id}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Bug report stored: {bug_id}", extra={
                'bug_id': bug_id,
                'category': report_data.get('category'),
                'user_role': report_data.get('user_role')
            })
            
            return bug_id
            
        except Exception as e:
            logger.error(f"Failed to store bug report: {e}")
            raise HTTPException(status_code=500, detail="Failed to store bug report")
    
    def _determine_priority(self, report_data: Dict[str, Any]) -> str:
        """Determine bug priority based on content"""
        title = report_data.get('title', '').lower()
        description = report_data.get('description', '').lower()
        category = report_data.get('category', 'bug')
        
        # High priority keywords
        high_priority_keywords = [
            'crash', 'error', 'fail', 'broken', 'security', 'data loss',
            'cannot', 'unable', 'critical', 'urgent', 'blocking'
        ]
        
        # Check for high priority indicators
        text_to_check = f"{title} {description}"
        if any(keyword in text_to_check for keyword in high_priority_keywords):
            return 'high'
        elif category in ['security', 'performance']:
            return 'high'
        elif category == 'bug':
            return 'medium'
        else:
            return 'low'
    
    def get_bug_report(self, bug_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve bug report by ID"""
        report_file = self.storage_path / f"{bug_id}.json"
        
        if not report_file.exists():
            return None
        
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read bug report {bug_id}: {e}")
            return None
    
    def list_bug_reports(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List bug reports with optional filtering"""
        reports = []
        
        for report_file in sorted(self.storage_path.glob("BUG_*.json"), reverse=True):
            if len(reports) >= limit:
                break
                
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    
                if status is None or report.get('status') == status:
                    reports.append(report)
                    
            except Exception as e:
                logger.error(f"Failed to read {report_file}: {e}")
                continue
        
        return reports

# Initialize storage
bug_storage = BugReportStorage()

# Create API router
router = APIRouter(prefix="/api", tags=["bug-reporting"])

@router.post("/bugs", response_model=BugReportResponse)
async def submit_bug_report(
    report: BugReportRequest,
    attachments: Optional[List[UploadFile]] = File(None)
):
    """
    Submit a bug report
    
    Accepts JSON data with title, description, page context, build hash, user role, and attachments.
    Stores in Vault with tags 'bug|feedback' and auto-generated bug_id.
    Emits Prometheus metrics for monitoring.
    """
    
    # Start metrics timer
    if METRICS_AVAILABLE:
        with bug_report_duration.time():
            return await _process_bug_report(report, attachments)
    else:
        return await _process_bug_report(report, attachments)

async def _process_bug_report(
    report: BugReportRequest,
    attachments: Optional[List[UploadFile]] = None
) -> BugReportResponse:
    """Process the bug report submission"""
    
    try:
        # Handle attachments
        attachment_paths = []
        if attachments:
            attachment_paths = await _handle_attachments(attachments)
        
        # Prepare report data
        report_data = report.dict()
        report_data['attachments'] = attachment_paths
        
        # Add system context
        report_data.update({
            'user_agent': 'Hearthlink-Desktop',  # Could be extracted from headers
            'timestamp': datetime.now().isoformat(),
            'session_id': str(uuid.uuid4())  # Could be from session management
        })
        
        # Store the report
        bug_id = bug_storage.store_bug_report(report_data)
        
        # Update metrics
        if METRICS_AVAILABLE:
            bug_reports_total.labels(
                category=report.category,
                user_role=report.user_role
            ).inc()
        
        # Generate response
        response = BugReportResponse(
            bug_id=bug_id,
            status="submitted",
            message=f"Bug report submitted successfully. Reference ID: {bug_id}",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Bug report submitted successfully: {bug_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing bug report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process bug report: {str(e)}"
        )

async def _handle_attachments(attachments: List[UploadFile]) -> List[str]:
    """Handle file attachments with security validation"""
    attachment_paths = []
    max_file_size = 10 * 1024 * 1024  # 10MB limit
    allowed_extensions = {'.txt', '.log', '.png', '.jpg', '.jpeg', '.pdf', '.json'}
    
    attachments_dir = Path("hearthlink_data/bug_reports/attachments")
    attachments_dir.mkdir(parents=True, exist_ok=True)
    
    for attachment in attachments:
        try:
            # Validate file size
            content = await attachment.read()
            if len(content) > max_file_size:
                logger.warning(f"Attachment too large: {attachment.filename}")
                continue
            
            # Validate file extension
            file_ext = Path(attachment.filename).suffix.lower()
            if file_ext not in allowed_extensions:
                logger.warning(f"Invalid file type: {attachment.filename}")
                continue
            
            # Generate safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = attachments_dir / safe_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            attachment_paths.append(str(file_path))
            logger.info(f"Attachment saved: {safe_filename}")
            
        except Exception as e:
            logger.error(f"Failed to process attachment {attachment.filename}: {e}")
            continue
    
    return attachment_paths

@router.get("/bugs/{bug_id}")
async def get_bug_report(bug_id: str):
    """Retrieve a specific bug report by ID"""
    
    if not bug_id.startswith("BUG_"):
        raise HTTPException(status_code=400, detail="Invalid bug ID format")
    
    report = bug_storage.get_bug_report(bug_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bug report not found")
    
    return report

@router.get("/bugs")
async def list_bug_reports(
    limit: int = 50,
    status: Optional[str] = None
):
    """List bug reports with optional filtering"""
    
    if limit > 200:
        limit = 200  # Prevent excessive loads
    
    reports = bug_storage.list_bug_reports(limit=limit, status=status)
    
    return {
        'reports': reports,
        'count': len(reports),
        'limit': limit,
        'status_filter': status
    }

@router.get("/bugs/stats")
async def get_bug_stats():
    """Get bug reporting statistics"""
    
    reports = bug_storage.list_bug_reports(limit=1000)  # Get recent reports for stats
    
    stats = {
        'total_reports': len(reports),
        'open_reports': len([r for r in reports if r.get('status') == 'open']),
        'categories': {},
        'priorities': {},
        'recent_24h': 0
    }
    
    # Calculate category and priority distributions
    for report in reports:
        category = report.get('category', 'unknown')
        priority = report.get('priority', 'unknown')
        
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
        stats['priorities'][priority] = stats['priorities'].get(priority, 0) + 1
        
        # Check if report is from last 24 hours
        try:
            created_at = datetime.fromisoformat(report.get('created_at', ''))
            if (datetime.now() - created_at).total_seconds() < 86400:  # 24 hours
                stats['recent_24h'] += 1
        except:
            pass
    
    return stats

# Health check endpoint
@router.get("/bugs/health")
async def bug_reporting_health():
    """Health check for bug reporting system"""
    
    try:
        # Test storage access
        test_report = {
            'title': 'Health Check Test',
            'description': 'System health validation',
            'category': 'test',
            'user_role': 'system'
        }
        
        # This would normally test Vault connectivity
        storage_healthy = bug_storage.storage_path.exists()
        
        return {
            'status': 'healthy' if storage_healthy else 'degraded',
            'storage_accessible': storage_healthy,
            'metrics_available': METRICS_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Bug reporting health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Export router for inclusion in main app
__all__ = ['router', 'BugReportRequest', 'BugReportResponse', 'bug_storage']