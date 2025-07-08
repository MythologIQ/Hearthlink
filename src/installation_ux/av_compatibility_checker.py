"""
AV Compatibility Checker - Antivirus Detection System

Detects antivirus software and provides guidance for compatibility
and exclusion configuration to ensure smooth Hearthlink operation.
"""

import os
import platform
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AVDetection:
    """Antivirus detection result."""
    name: str
    detected: bool
    version: Optional[str] = None
    path: Optional[str] = None

class AVCompatibilityChecker:
    """
    Detects antivirus software and provides compatibility guidance.
    
    Identifies common antivirus software and provides step-by-step
    instructions for adding Hearthlink to exclusions.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize AV Compatibility Checker.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # AV detection methods
        self.av_detectors = {
            'windows_defender': self._check_windows_defender,
            'norton': self._check_norton,
            'mcafee': self._check_mcafee,
            'avast': self._check_avast,
            'avg': self._check_avg,
            'kaspersky': self._check_kaspersky,
            'bitdefender': self._check_bitdefender,
            'malwarebytes': self._check_malwarebytes
        }
        
        self._log("av_checker_initialized", "system", None, "system", None, {})
    
    def check_all_av_software(self) -> List[AVDetection]:
        """
        Check for all known antivirus software.
        
        Returns:
            List of AVDetection objects for detected software
        """
        try:
            detections = []
            
            for av_name, detector in self.av_detectors.items():
                if detector():
                    detection = AVDetection(
                        name=av_name.replace('_', ' ').title(),
                        detected=True
                    )
                    detections.append(detection)
            
            self._log("av_scan_completed", "system", None, "av_check", 
                     {"detected_count": len(detections)})
            
            return detections
            
        except Exception as e:
            self._log("av_scan_failed", "system", None, "av_check", {}, "error", e)
            return []
    
    def generate_exclusion_instructions(self, av_name: str) -> List[str]:
        """
        Generate step-by-step instructions for AV exclusions.
        
        Args:
            av_name: Name of the antivirus software
            
        Returns:
            List of step-by-step instructions
        """
        instructions = {
            'windows_defender': [
                "1. Open Windows Security",
                "2. Click 'Virus & threat protection'",
                "3. Click 'Manage settings' under 'Virus & threat protection settings'",
                "4. Click 'Add or remove exclusions'",
                "5. Click 'Add an exclusion' and select 'Folder'",
                "6. Browse to your Hearthlink installation folder and select it"
            ],
            'norton': [
                "1. Open Norton Security",
                "2. Click 'Settings'",
                "3. Click 'Antivirus'",
                "4. Click 'Scans and Risks'",
                "5. Click 'Exclusions / Low Risks'",
                "6. Click 'Add' and browse to your Hearthlink folder"
            ],
            'mcafee': [
                "1. Open McAfee Security",
                "2. Click 'Settings'",
                "3. Click 'Real-Time Scanning'",
                "4. Click 'Excluded Files and Folders'",
                "5. Click 'Add' and browse to your Hearthlink folder"
            ],
            'avast': [
                "1. Open Avast Antivirus",
                "2. Click 'Menu' > 'Settings'",
                "3. Click 'General' > 'Exclusions'",
                "4. Click 'Add' and browse to your Hearthlink folder"
            ],
            'avg': [
                "1. Open AVG Antivirus",
                "2. Click 'Menu' > 'Settings'",
                "3. Click 'General' > 'Exclusions'",
                "4. Click 'Add' and browse to your Hearthlink folder"
            ],
            'kaspersky': [
                "1. Open Kaspersky Security",
                "2. Click 'Settings'",
                "3. Click 'Additional' > 'Threats and Exclusions'",
                "4. Click 'Exclusions' > 'Add'",
                "5. Browse to your Hearthlink folder and select it"
            ],
            'bitdefender': [
                "1. Open Bitdefender",
                "2. Click 'Settings'",
                "3. Click 'Protection' > 'Antivirus'",
                "4. Click 'Exclusions'",
                "5. Click 'Add' and browse to your Hearthlink folder"
            ],
            'malwarebytes': [
                "1. Open Malwarebytes",
                "2. Click 'Settings'",
                "3. Click 'Security'",
                "4. Click 'Add Exclusion'",
                "5. Browse to your Hearthlink folder and select it"
            ]
        }
        
        return instructions.get(av_name.lower().replace(' ', '_'), [
            "Please consult your antivirus software documentation for exclusion instructions.",
            "Look for settings related to 'Exclusions', 'Trusted Files', or 'Whitelist'."
        ])
    
    def _check_windows_defender(self) -> bool:
        """Check if Windows Defender is active."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Windows Security service
            import subprocess
            result = subprocess.run(['powershell', 'Get-MpComputerStatus'], 
                                  capture_output=True, text=True)
            return 'RealTimeProtectionEnabled : True' in result.stdout
            
        except Exception:
            return False
    
    def _check_norton(self) -> bool:
        """Check if Norton is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Norton processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'norton' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_mcafee(self) -> bool:
        """Check if McAfee is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for McAfee processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'mcafee' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_avast(self) -> bool:
        """Check if Avast is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Avast processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'avast' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_avg(self) -> bool:
        """Check if AVG is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for AVG processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'avg' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_kaspersky(self) -> bool:
        """Check if Kaspersky is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Kaspersky processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'kaspersky' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_bitdefender(self) -> bool:
        """Check if Bitdefender is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Bitdefender processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'bitdefender' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _check_malwarebytes(self) -> bool:
        """Check if Malwarebytes is installed."""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Check for Malwarebytes processes
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'malwarebytes' in proc.info['name'].lower():
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log AV checker events."""
        log_entry = {
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"AV Checker: {action} - {result}")
        
        if error:
            self.logger.error(f"AV Checker error: {str(error)}") 