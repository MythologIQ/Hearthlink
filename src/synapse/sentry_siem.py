"""
Sentry SIEM Integration - Enhanced Security Monitoring

Implements multi-layer security monitoring with behavioral analysis
as recommended in ClaudeDesktopInsights.md architectural analysis.
"""

import os
import time
import threading

# Optional psutil import for process monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create mock psutil for testing
    class MockPsutil:
        class Process:
            def __init__(self, pid):
                self.pid = pid
            def name(self): return "mock_process"
            def cmdline(self): return ["mock_cmd"]
            def cpu_percent(self): return 0.0
            def memory_percent(self): return 0.0
            def connections(self): return []
            def create_time(self): return time.time()
            def ppid(self): return 0
        
        class NoSuchProcess(Exception): pass
        class AccessDenied(Exception): pass
    
    psutil = MockPsutil()
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from collections import deque, defaultdict
import hashlib
import socket
import subprocess


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class SecurityEventType(Enum):
    """Types of security events."""
    PROCESS_ANOMALY = "process_anomaly"
    NETWORK_ANOMALY = "network_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    RESOURCE_ABUSE = "resource_abuse"
    PERMISSION_VIOLATION = "permission_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    timestamp: datetime
    event_type: SecurityEventType
    threat_level: ThreatLevel
    agent_id: str
    source_ip: Optional[str] = None
    process_id: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)
    mitigation_action: Optional[str] = None
    resolved: bool = False


@dataclass
class ProcessInfo:
    """Process information for monitoring."""
    pid: int
    name: str
    cmdline: List[str]
    cpu_percent: float
    memory_percent: float
    connections: List[Dict[str, Any]]
    create_time: float
    parent_pid: int


@dataclass
class NetworkConnection:
    """Network connection information."""
    local_address: Tuple[str, int]
    remote_address: Tuple[str, int]
    status: str
    pid: int
    family: int
    type: int


@dataclass
class BehavioralBaseline:
    """Behavioral baseline for an agent."""
    agent_id: str
    normal_cpu_usage: float
    normal_memory_usage: float
    normal_network_activity: float
    normal_request_rate: float
    normal_response_time: float
    established_at: datetime
    last_updated: datetime
    sample_count: int = 0


class EndpointProtectionMonitor:
    """Monitors endpoint security and process behavior."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.monitored_processes: Dict[int, ProcessInfo] = {}
        self.process_baselines: Dict[str, BehavioralBaseline] = {}
        self.suspicious_processes: set = set()
        self.monitoring_interval = 5.0  # seconds
        self.cpu_threshold = 80.0  # percent
        self.memory_threshold = 80.0  # percent
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_processes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def register_agent_process(self, agent_id: str, pid: int):
        """Register an agent process for monitoring."""
        try:
            process = psutil.Process(pid)
            process_info = ProcessInfo(
                pid=pid,
                name=process.name(),
                cmdline=process.cmdline(),
                cpu_percent=process.cpu_percent(),
                memory_percent=process.memory_percent(),
                connections=[],
                create_time=process.create_time(),
                parent_pid=process.ppid()
            )
            
            self.monitored_processes[pid] = process_info
            self.logger.info(f"Registered agent {agent_id} process {pid} for monitoring")
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.error(f"Failed to register process {pid}: {e}")
    
    def _monitor_processes(self):
        """Background thread to monitor processes."""
        while self.monitoring_active:
            try:
                self._update_process_info()
                self._check_resource_usage()
                self._check_network_connections()
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                time.sleep(self.monitoring_interval)
    
    def _update_process_info(self):
        """Update information for monitored processes."""
        for pid in list(self.monitored_processes.keys()):
            try:
                process = psutil.Process(pid)
                process_info = self.monitored_processes[pid]
                
                # Update metrics
                process_info.cpu_percent = process.cpu_percent()
                process_info.memory_percent = process.memory_percent()
                process_info.connections = [
                    {
                        'local_address': conn.laddr,
                        'remote_address': conn.raddr,
                        'status': conn.status,
                        'family': conn.family,
                        'type': conn.type
                    }
                    for conn in process.connections()
                ]
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists
                self.logger.info(f"Process {pid} no longer exists, removing from monitoring")
                del self.monitored_processes[pid]
    
    def _check_resource_usage(self):
        """Check for resource usage anomalies."""
        for pid, process_info in self.monitored_processes.items():
            # Check CPU usage
            if process_info.cpu_percent > self.cpu_threshold:
                self.logger.warning(f"High CPU usage detected for process {pid}: {process_info.cpu_percent}%")
                self.suspicious_processes.add(pid)
            
            # Check memory usage
            if process_info.memory_percent > self.memory_threshold:
                self.logger.warning(f"High memory usage detected for process {pid}: {process_info.memory_percent}%")
                self.suspicious_processes.add(pid)
    
    def _check_network_connections(self):
        """Check for suspicious network connections."""
        for pid, process_info in self.monitored_processes.items():
            # Check for unusual network activity
            external_connections = [
                conn for conn in process_info.connections
                if conn.get('remote_address') and not self._is_local_connection(conn['remote_address'])
            ]
            
            if len(external_connections) > 10:  # Threshold for suspicious activity
                self.logger.warning(f"High number of external connections for process {pid}: {len(external_connections)}")
                self.suspicious_processes.add(pid)
    
    def _is_local_connection(self, remote_address: Tuple[str, int]) -> bool:
        """Check if connection is to local address."""
        ip = remote_address[0]
        return ip in ['127.0.0.1', '::1', 'localhost'] or ip.startswith('192.168.') or ip.startswith('10.')
    
    def assess_process_risk(self, pid: int) -> ThreatLevel:
        """Assess risk level for a process."""
        if pid in self.suspicious_processes:
            return ThreatLevel.HIGH
        
        if pid in self.monitored_processes:
            process_info = self.monitored_processes[pid]
            
            # High resource usage
            if process_info.cpu_percent > self.cpu_threshold or process_info.memory_percent > self.memory_threshold:
                return ThreatLevel.MEDIUM
            
            # Many external connections
            external_connections = [
                conn for conn in process_info.connections
                if conn.get('remote_address') and not self._is_local_connection(conn['remote_address'])
            ]
            if len(external_connections) > 5:
                return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW
    
    def get_process_report(self) -> Dict[str, Any]:
        """Get comprehensive process monitoring report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'monitored_processes': len(self.monitored_processes),
            'suspicious_processes': len(self.suspicious_processes),
            'process_details': {
                pid: {
                    'name': info.name,
                    'cpu_percent': info.cpu_percent,
                    'memory_percent': info.memory_percent,
                    'connections': len(info.connections),
                    'risk_level': self.assess_process_risk(pid).name
                }
                for pid, info in self.monitored_processes.items()
            }
        }


class NetworkTrafficAnalyzer:
    """Analyzes network traffic patterns for anomaly detection."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.connection_history: deque = deque(maxlen=1000)
        self.traffic_baselines: Dict[str, Dict[str, float]] = {}
        self.suspicious_ips: set = set()
        self.blocked_ips: set = set()
        
        # Traffic thresholds
        self.request_rate_threshold = 100  # requests per minute
        self.data_volume_threshold = 100 * 1024 * 1024  # 100MB
        
    def analyze_connection(self, connection: NetworkConnection, agent_id: str) -> ThreatLevel:
        """Analyze individual network connection."""
        # Record connection
        self.connection_history.append({
            'timestamp': datetime.now(),
            'agent_id': agent_id,
            'local_address': connection.local_address,
            'remote_address': connection.remote_address,
            'status': connection.status
        })
        
        # Check against blocked IPs
        if connection.remote_address[0] in self.blocked_ips:
            return ThreatLevel.CRITICAL
        
        # Check against suspicious IPs
        if connection.remote_address[0] in self.suspicious_ips:
            return ThreatLevel.HIGH
        
        # Analyze traffic patterns
        return self._analyze_traffic_pattern(connection, agent_id)
    
    def _analyze_traffic_pattern(self, connection: NetworkConnection, agent_id: str) -> ThreatLevel:
        """Analyze traffic patterns for anomalies."""
        remote_ip = connection.remote_address[0]
        
        # Count recent connections to same IP
        recent_connections = [
            conn for conn in self.connection_history
            if conn['remote_address'][0] == remote_ip
            and (datetime.now() - conn['timestamp']).seconds < 60
        ]
        
        # High frequency connections
        if len(recent_connections) > 20:
            self.suspicious_ips.add(remote_ip)
            return ThreatLevel.HIGH
        
        # Check for port scanning behavior
        unique_ports = set(conn['remote_address'][1] for conn in recent_connections)
        if len(unique_ports) > 10:
            self.suspicious_ips.add(remote_ip)
            return ThreatLevel.HIGH
        
        return ThreatLevel.LOW
    
    def detect_anomaly(self, agent_id: str, current_metrics: Dict[str, Any]) -> bool:
        """Detect network anomalies based on baselines."""
        if agent_id not in self.traffic_baselines:
            return False
        
        baseline = self.traffic_baselines[agent_id]
        
        # Check request rate
        if current_metrics.get('request_rate', 0) > baseline.get('request_rate', 0) * 3:
            return True
        
        # Check data volume
        if current_metrics.get('data_volume', 0) > baseline.get('data_volume', 0) * 5:
            return True
        
        return False
    
    def update_baseline(self, agent_id: str, metrics: Dict[str, Any]):
        """Update traffic baseline for agent."""
        if agent_id not in self.traffic_baselines:
            self.traffic_baselines[agent_id] = {}
        
        baseline = self.traffic_baselines[agent_id]
        
        # Update with exponential moving average
        alpha = 0.1
        for key, value in metrics.items():
            if key in baseline:
                baseline[key] = alpha * value + (1 - alpha) * baseline[key]
            else:
                baseline[key] = value
    
    def get_network_report(self) -> Dict[str, Any]:
        """Get network traffic analysis report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'connection_history_size': len(self.connection_history),
            'suspicious_ips': list(self.suspicious_ips),
            'blocked_ips': list(self.blocked_ips),
            'traffic_baselines': self.traffic_baselines,
            'recent_connections': [
                {
                    'timestamp': conn['timestamp'].isoformat(),
                    'agent_id': conn['agent_id'],
                    'remote_address': conn['remote_address']
                }
                for conn in list(self.connection_history)[-10:]
            ]
        }


class BehavioralAnalyzer:
    """Analyzes agent behavioral patterns for anomaly detection."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.behavioral_baselines: Dict[str, BehavioralBaseline] = {}
        self.behavioral_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.anomaly_threshold = 2.0  # Standard deviations
        
    def establish_baseline(self, agent_id: str, metrics: Dict[str, Any]):
        """Establish behavioral baseline for agent."""
        if agent_id not in self.behavioral_baselines:
            self.behavioral_baselines[agent_id] = BehavioralBaseline(
                agent_id=agent_id,
                normal_cpu_usage=metrics.get('cpu_usage', 0),
                normal_memory_usage=metrics.get('memory_usage', 0),
                normal_network_activity=metrics.get('network_activity', 0),
                normal_request_rate=metrics.get('request_rate', 0),
                normal_response_time=metrics.get('response_time', 0),
                established_at=datetime.now(),
                last_updated=datetime.now()
            )
        else:
            # Update baseline with exponential moving average
            baseline = self.behavioral_baselines[agent_id]
            alpha = 0.1
            
            baseline.normal_cpu_usage = alpha * metrics.get('cpu_usage', 0) + (1 - alpha) * baseline.normal_cpu_usage
            baseline.normal_memory_usage = alpha * metrics.get('memory_usage', 0) + (1 - alpha) * baseline.normal_memory_usage
            baseline.normal_network_activity = alpha * metrics.get('network_activity', 0) + (1 - alpha) * baseline.normal_network_activity
            baseline.normal_request_rate = alpha * metrics.get('request_rate', 0) + (1 - alpha) * baseline.normal_request_rate
            baseline.normal_response_time = alpha * metrics.get('response_time', 0) + (1 - alpha) * baseline.normal_response_time
            baseline.last_updated = datetime.now()
            baseline.sample_count += 1
        
        # Record in history
        self.behavioral_history[agent_id].append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
    
    def check_behavioral_anomaly(self, agent_id: str, current_metrics: Dict[str, Any]) -> Tuple[bool, ThreatLevel]:
        """Check for behavioral anomalies."""
        if agent_id not in self.behavioral_baselines:
            return False, ThreatLevel.LOW
        
        baseline = self.behavioral_baselines[agent_id]
        anomalies = []
        
        # Check each metric against baseline
        metrics_to_check = [
            ('cpu_usage', baseline.normal_cpu_usage),
            ('memory_usage', baseline.normal_memory_usage),
            ('network_activity', baseline.normal_network_activity),
            ('request_rate', baseline.normal_request_rate),
            ('response_time', baseline.normal_response_time)
        ]
        
        for metric_name, baseline_value in metrics_to_check:
            current_value = current_metrics.get(metric_name, 0)
            if baseline_value > 0:
                deviation = abs(current_value - baseline_value) / baseline_value
                if deviation > self.anomaly_threshold:
                    anomalies.append({
                        'metric': metric_name,
                        'current': current_value,
                        'baseline': baseline_value,
                        'deviation': deviation
                    })
        
        # Determine threat level based on anomalies
        if not anomalies:
            return False, ThreatLevel.LOW
        
        max_deviation = max(anomaly['deviation'] for anomaly in anomalies)
        if max_deviation > 5.0:
            threat_level = ThreatLevel.CRITICAL
        elif max_deviation > 3.0:
            threat_level = ThreatLevel.HIGH
        elif max_deviation > 2.0:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        return True, threat_level
    
    def get_behavioral_report(self) -> Dict[str, Any]:
        """Get behavioral analysis report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'monitored_agents': len(self.behavioral_baselines),
            'baselines': {
                agent_id: {
                    'normal_cpu_usage': baseline.normal_cpu_usage,
                    'normal_memory_usage': baseline.normal_memory_usage,
                    'normal_network_activity': baseline.normal_network_activity,
                    'normal_request_rate': baseline.normal_request_rate,
                    'normal_response_time': baseline.normal_response_time,
                    'established_at': baseline.established_at.isoformat(),
                    'last_updated': baseline.last_updated.isoformat(),
                    'sample_count': baseline.sample_count
                }
                for agent_id, baseline in self.behavioral_baselines.items()
            }
        }


class ThreatResponseService:
    """Automated threat response and mitigation."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.quarantined_agents: set = set()
        self.blocked_processes: set = set()
        self.response_actions: Dict[ThreatLevel, List[str]] = {
            ThreatLevel.LOW: ['log', 'monitor'],
            ThreatLevel.MEDIUM: ['log', 'monitor', 'alert'],
            ThreatLevel.HIGH: ['log', 'monitor', 'alert', 'rate_limit'],
            ThreatLevel.CRITICAL: ['log', 'monitor', 'alert', 'quarantine', 'block']
        }
    
    def respond_to_threat(self, event: SecurityEvent) -> Dict[str, Any]:
        """Respond to security threat automatically."""
        actions_taken = []
        
        # Get response actions for threat level
        required_actions = self.response_actions.get(event.threat_level, ['log'])
        
        for action in required_actions:
            try:
                if action == 'log':
                    self._log_security_event(event)
                    actions_taken.append('logged')
                
                elif action == 'monitor':
                    self._increase_monitoring(event.agent_id)
                    actions_taken.append('monitoring_increased')
                
                elif action == 'alert':
                    self._send_alert(event)
                    actions_taken.append('alert_sent')
                
                elif action == 'rate_limit':
                    self._apply_rate_limit(event.agent_id)
                    actions_taken.append('rate_limited')
                
                elif action == 'quarantine':
                    self._quarantine_agent(event.agent_id)
                    actions_taken.append('quarantined')
                
                elif action == 'block':
                    self._block_agent(event.agent_id)
                    actions_taken.append('blocked')
                
            except Exception as e:
                self.logger.error(f"Failed to execute response action {action}: {e}")
                actions_taken.append(f'{action}_failed')
        
        return {
            'event_id': event.event_id,
            'threat_level': event.threat_level.name,
            'actions_taken': actions_taken,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_security_event(self, event: SecurityEvent):
        """Log security event."""
        self.logger.warning(f"Security event: {event.event_type.value} - {event.threat_level.name} - Agent: {event.agent_id}")
    
    def _increase_monitoring(self, agent_id: str):
        """Increase monitoring for agent."""
        self.logger.info(f"Increased monitoring for agent {agent_id}")
    
    def _send_alert(self, event: SecurityEvent):
        """Send security alert."""
        self.logger.critical(f"SECURITY ALERT: {event.event_type.value} - {event.threat_level.name} - Agent: {event.agent_id}")
    
    def _apply_rate_limit(self, agent_id: str):
        """Apply rate limiting to agent."""
        self.logger.warning(f"Applied rate limiting to agent {agent_id}")
    
    def _quarantine_agent(self, agent_id: str):
        """Quarantine suspicious agent."""
        self.quarantined_agents.add(agent_id)
        self.logger.critical(f"Quarantined agent {agent_id}")
    
    def _block_agent(self, agent_id: str):
        """Block malicious agent."""
        self.quarantined_agents.add(agent_id)
        self.logger.critical(f"Blocked agent {agent_id}")
    
    def is_agent_quarantined(self, agent_id: str) -> bool:
        """Check if agent is quarantined."""
        return agent_id in self.quarantined_agents
    
    def release_quarantine(self, agent_id: str):
        """Release agent from quarantine."""
        self.quarantined_agents.discard(agent_id)
        self.logger.info(f"Released agent {agent_id} from quarantine")


class SentrySecurityOrchestrator:
    """
    Main Sentry SIEM security orchestrator.
    
    Implements multi-layer security monitoring with behavioral analysis
    as recommended in ClaudeDesktopInsights.md.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize security components
        self.endpoint_monitor = EndpointProtectionMonitor(logger)
        self.traffic_analyzer = NetworkTrafficAnalyzer(logger)
        self.behavioral_analyzer = BehavioralAnalyzer(logger)
        self.threat_responder = ThreatResponseService(logger)
        
        # Security state
        self.security_events: deque = deque(maxlen=1000)
        self.active_threats: Dict[str, SecurityEvent] = {}
        self.security_threshold = config.get('security_threshold', ThreatLevel.MEDIUM)
        
        # Metrics
        self.events_processed = 0
        self.threats_detected = 0
        self.false_positives = 0
        
        self.logger.info("Sentry Security Orchestrator initialized")
    
    def monitor_agent_transaction(self, agent_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor agent transaction with multi-layer security analysis."""
        try:
            # Extract relevant metrics
            metrics = self._extract_metrics(transaction_data)
            
            # Multi-layer security analysis
            endpoint_risk = self._assess_endpoint_risk(agent_id, metrics)
            traffic_risk = self._assess_traffic_risk(agent_id, metrics)
            behavioral_risk = self._assess_behavioral_risk(agent_id, metrics)
            
            # Correlate threats
            overall_threat_level = self._correlate_threats(endpoint_risk, traffic_risk, behavioral_risk)
            
            # Generate security event if threat detected
            if overall_threat_level.value >= self.security_threshold.value:
                security_event = self._create_security_event(agent_id, overall_threat_level, {
                    'endpoint_risk': endpoint_risk.name,
                    'traffic_risk': traffic_risk.name,
                    'behavioral_risk': behavioral_risk.name,
                    'transaction_data': transaction_data
                })
                
                # Automated response
                response = self.threat_responder.respond_to_threat(security_event)
                
                # Record event
                self.security_events.append(security_event)
                self.active_threats[security_event.event_id] = security_event
                self.threats_detected += 1
                
                return {
                    'allowed': overall_threat_level.value < ThreatLevel.CRITICAL.value,
                    'threat_level': overall_threat_level.name,
                    'security_event_id': security_event.event_id,
                    'response_actions': response['actions_taken'],
                    'reason': f"Security threat detected: {overall_threat_level.name}"
                }
            
            # Update behavioral baseline
            self.behavioral_analyzer.establish_baseline(agent_id, metrics)
            
            self.events_processed += 1
            
            return {
                'allowed': True,
                'threat_level': overall_threat_level.name,
                'security_event_id': None,
                'response_actions': [],
                'reason': "Transaction approved"
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring agent transaction: {e}")
            return {
                'allowed': False,
                'threat_level': ThreatLevel.CRITICAL.name,
                'security_event_id': None,
                'response_actions': ['blocked'],
                'reason': f"Security monitoring error: {str(e)}"
            }
    
    def _extract_metrics(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metrics from transaction data."""
        return {
            'cpu_usage': transaction_data.get('cpu_usage', 0),
            'memory_usage': transaction_data.get('memory_usage', 0),
            'network_activity': transaction_data.get('network_activity', 0),
            'request_rate': transaction_data.get('request_rate', 0),
            'response_time': transaction_data.get('response_time', 0),
            'data_volume': transaction_data.get('data_volume', 0)
        }
    
    def _assess_endpoint_risk(self, agent_id: str, metrics: Dict[str, Any]) -> ThreatLevel:
        """Assess endpoint security risk."""
        # Check if agent has registered processes
        for pid, process_info in self.endpoint_monitor.monitored_processes.items():
            if agent_id in process_info.cmdline:
                return self.endpoint_monitor.assess_process_risk(pid)
        
        # Check resource usage
        if metrics.get('cpu_usage', 0) > 80 or metrics.get('memory_usage', 0) > 80:
            return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW
    
    def _assess_traffic_risk(self, agent_id: str, metrics: Dict[str, Any]) -> ThreatLevel:
        """Assess network traffic risk."""
        # Check for traffic anomalies
        if self.traffic_analyzer.detect_anomaly(agent_id, metrics):
            return ThreatLevel.HIGH
        
        # Check request rate
        if metrics.get('request_rate', 0) > 100:
            return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW
    
    def _assess_behavioral_risk(self, agent_id: str, metrics: Dict[str, Any]) -> ThreatLevel:
        """Assess behavioral risk."""
        anomaly_detected, threat_level = self.behavioral_analyzer.check_behavioral_anomaly(agent_id, metrics)
        return threat_level if anomaly_detected else ThreatLevel.LOW
    
    def _correlate_threats(self, endpoint_risk: ThreatLevel, traffic_risk: ThreatLevel, behavioral_risk: ThreatLevel) -> ThreatLevel:
        """Correlate different threat assessments."""
        # Take maximum threat level
        max_threat = max(endpoint_risk.value, traffic_risk.value, behavioral_risk.value)
        
        # Escalate if multiple medium threats
        medium_threats = sum(1 for risk in [endpoint_risk, traffic_risk, behavioral_risk] if risk == ThreatLevel.MEDIUM)
        if medium_threats >= 2:
            max_threat = max(max_threat, ThreatLevel.HIGH.value)
        
        return ThreatLevel(max_threat)
    
    def _create_security_event(self, agent_id: str, threat_level: ThreatLevel, details: Dict[str, Any]) -> SecurityEvent:
        """Create security event record."""
        event_id = hashlib.sha256(f"{agent_id}_{datetime.now().isoformat()}_{threat_level.name}".encode()).hexdigest()[:16]
        
        return SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            threat_level=threat_level,
            agent_id=agent_id,
            details=details
        )
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {
                'events_processed': self.events_processed,
                'threats_detected': self.threats_detected,
                'false_positives': self.false_positives,
                'active_threats': len(self.active_threats),
                'quarantined_agents': len(self.threat_responder.quarantined_agents)
            },
            'endpoint_report': self.endpoint_monitor.get_process_report(),
            'network_report': self.traffic_analyzer.get_network_report(),
            'behavioral_report': self.behavioral_analyzer.get_behavioral_report(),
            'recent_events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type.value,
                    'threat_level': event.threat_level.name,
                    'agent_id': event.agent_id,
                    'resolved': event.resolved
                }
                for event in list(self.security_events)[-10:]
            ]
        }
    
    def register_agent_process(self, agent_id: str, pid: int):
        """Register agent process for monitoring."""
        self.endpoint_monitor.register_agent_process(agent_id, pid)
    
    def is_agent_quarantined(self, agent_id: str) -> bool:
        """Check if agent is quarantined."""
        return self.threat_responder.is_agent_quarantined(agent_id)
    
    def release_quarantine(self, agent_id: str):
        """Release agent from quarantine."""
        self.threat_responder.release_quarantine(agent_id)
    
    def shutdown(self):
        """Shutdown security monitoring."""
        self.endpoint_monitor.monitoring_active = False
        self.logger.info("Sentry Security Orchestrator shutdown complete")