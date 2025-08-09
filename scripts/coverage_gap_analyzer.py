#!/usr/bin/env python3
"""
SPEC-3 Week 2: Coverage Gap Analysis
Identifies orphaned functions without tests or invocation paths and generates recommendations
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CoverageGap:
    """Represents a function or endpoint with coverage gaps"""
    name: str
    module: str
    file_path: str
    line_number: int
    function_type: str
    gap_types: List[str]  # ['test', 'ui_invocation', 'cli_invocation']
    recommendations: List[str]
    priority: str  # 'critical', 'high', 'medium', 'low'
    is_public: bool = True
    is_exported: bool = False
    signature: str = ""
    class_name: Optional[str] = None

class CoverageGapAnalyzer:
    """Analyzes function inventory to identify coverage gaps and orphaned functions"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.inventory_file = project_root / 'function_inventory.json'
        self.coverage_gaps: List[CoverageGap] = []
        self.inventory_data = None
        
        # Critical modules that require higher coverage
        self.critical_modules = {
            'src.core', 'src.vault', 'src.synapse', 'src.database',
            'src.personas.alden', 'src.personas.alice', 'src.personas.sentry',
            'ipcHandlers', 'services'
        }
        
        # Function patterns that should have invocation paths
        self.invocation_required_patterns = [
            r'.*_api$', r'.*_endpoint$', r'handle_.*', r'process_.*',
            r'create_.*', r'update_.*', r'delete_.*', r'get_.*',
            r'.*_command$', r'execute_.*', r'run_.*'
        ]
    
    def load_inventory(self) -> bool:
        """Load the function inventory data"""
        if not self.inventory_file.exists():
            print(f"❌ Function inventory not found: {self.inventory_file}")
            return False
        
        try:
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                self.inventory_data = json.load(f)
            print(f"✅ Loaded inventory: {len(self.inventory_data['functions'])} functions, {len(self.inventory_data['endpoints'])} endpoints")
            return True
        except Exception as e:
            print(f"❌ Failed to load inventory: {e}")
            return False
    
    def analyze_coverage_gaps(self) -> Dict[str, Any]:
        """Analyze all coverage gaps and generate recommendations"""
        if not self.inventory_data:
            return {"error": "No inventory data loaded"}
        
        print("🔍 Analyzing coverage gaps...")
        
        # Analyze function coverage gaps
        self._analyze_function_gaps()
        
        # Analyze endpoint coverage gaps
        self._analyze_endpoint_gaps()
        
        # Generate priority classification
        self._classify_gap_priorities()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Create analysis report
        report = self._generate_coverage_report()
        
        return report
    
    def _analyze_function_gaps(self):
        """Analyze functions for coverage gaps"""
        functions = self.inventory_data['functions']
        
        for func_data in functions:
            gap_types = []
            
            # Check test coverage
            if not func_data.get('has_coverage', False):
                gap_types.append('test')
            
            # Check UI invocation
            if not func_data.get('ui_triggers', []):
                gap_types.append('ui_invocation')
            
            # Check CLI invocation
            if not func_data.get('cli_triggers', []):
                gap_types.append('cli_invocation')
            
            # Only consider gaps if function should have coverage
            if gap_types and self._should_have_coverage(func_data):
                gap = CoverageGap(
                    name=func_data['name'],
                    module=func_data['module'],
                    file_path=func_data['file_path'],
                    line_number=func_data['line_number'],
                    function_type=func_data['function_type'],
                    gap_types=gap_types,
                    recommendations=[],
                    priority='medium',
                    is_public=func_data.get('is_public', True),
                    is_exported=func_data.get('is_exported', False),
                    signature=func_data.get('signature', ''),
                    class_name=func_data.get('class_name')
                )
                self.coverage_gaps.append(gap)
    
    def _analyze_endpoint_gaps(self):
        """Analyze endpoints for coverage gaps"""
        endpoints = self.inventory_data['endpoints']
        
        for endpoint_data in endpoints:
            gap_types = []
            
            # Check test coverage
            if not endpoint_data.get('has_coverage', False):
                gap_types.append('test')
            
            # Check UI calls
            if not endpoint_data.get('ui_calls', []):
                gap_types.append('ui_invocation')
            
            # All endpoints should have some form of invocation
            if gap_types:
                gap = CoverageGap(
                    name=f"{endpoint_data['method']} {endpoint_data['path']}",
                    module=endpoint_data['module'],
                    file_path=endpoint_data['file_path'],
                    line_number=endpoint_data['line_number'],
                    function_type='endpoint',
                    gap_types=gap_types,
                    recommendations=[],
                    priority='high',  # Endpoints are typically high priority
                    is_public=True,
                    is_exported=True,
                    signature=endpoint_data.get('handler_signature', '')
                )
                self.coverage_gaps.append(gap)
    
    def _should_have_coverage(self, func_data: Dict[str, Any]) -> bool:
        """Determine if a function should have test/invocation coverage"""
        # Skip private functions (starting with _)
        if func_data['name'].startswith('_'):
            return False
        
        # Skip test functions themselves
        if 'test_' in func_data['name'] or func_data['name'].endswith('_test'):
            return False
        
        # Skip common utility functions that don't need direct invocation
        skip_patterns = [
            r'__.*__',  # Dunder methods
            r'.*_helper$', r'.*_util$', r'.*_decorator$',
            r'setup.*', r'teardown.*', r'cleanup.*'
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, func_data['name']):
                return False
        
        # Public exported functions should have coverage
        if func_data.get('is_exported', False) and func_data.get('is_public', True):
            return True
        
        # Functions in critical modules should have coverage
        module = func_data.get('module', '')
        if any(module.startswith(critical) for critical in self.critical_modules):
            return True
        
        # Functions matching invocation patterns should have invocation paths
        for pattern in self.invocation_required_patterns:
            if re.match(pattern, func_data['name']):
                return True
        
        # React components should have UI coverage
        if func_data.get('function_type') == 'react_component':
            return True
        
        # API endpoints should have coverage
        if 'endpoint' in func_data.get('function_type', ''):
            return True
        
        return False
    
    def _classify_gap_priorities(self):
        """Classify coverage gaps by priority"""
        for gap in self.coverage_gaps:
            priority_score = 0
            
            # Critical modules get higher priority
            if any(gap.module.startswith(critical) for critical in self.critical_modules):
                priority_score += 3
            
            # Exported functions get higher priority
            if gap.is_exported:
                priority_score += 2
            
            # Functions with multiple gap types get higher priority
            priority_score += len(gap.gap_types)
            
            # Endpoints get higher priority
            if gap.function_type == 'endpoint':
                priority_score += 2
            
            # Functions matching important patterns get higher priority
            for pattern in self.invocation_required_patterns:
                if re.match(pattern, gap.name):
                    priority_score += 2
                    break
            
            # React components get medium priority
            if gap.function_type == 'react_component':
                priority_score += 1
            
            # Classify based on score
            if priority_score >= 6:
                gap.priority = 'critical'
            elif priority_score >= 4:
                gap.priority = 'high'
            elif priority_score >= 2:
                gap.priority = 'medium'
            else:
                gap.priority = 'low'
    
    def _generate_recommendations(self):
        """Generate specific recommendations for each coverage gap"""
        for gap in self.coverage_gaps:
            recommendations = []
            
            # Test coverage recommendations
            if 'test' in gap.gap_types:
                if gap.function_type == 'endpoint':
                    recommendations.append(f"Add Playwright test in tests/e2e/ hitting {gap.name}")
                elif gap.function_type == 'react_component':
                    recommendations.append(f"Add React Testing Library test in tests/components/ for {gap.name}")
                elif gap.module.startswith('src') and gap.file_path.endswith('.py'):
                    recommendations.append(f"Add pytest unit test in tests/unit/ for {gap.name}")
                elif gap.file_path.endswith('.js') or gap.file_path.endswith('.ts'):
                    recommendations.append(f"Add Jest unit test for {gap.name}")
                else:
                    recommendations.append(f"Add appropriate unit test for {gap.name}")
            
            # UI invocation recommendations
            if 'ui_invocation' in gap.gap_types:
                if gap.function_type == 'react_component':
                    recommendations.append(f"Ensure {gap.name} component is imported and used in parent components")
                elif 'api' in gap.name.lower() or gap.function_type == 'endpoint':
                    recommendations.append(f"Add UI button/form calling {gap.name} in appropriate React component")
                elif gap.module.startswith('src.core'):
                    recommendations.append(f"Add Core interface control for {gap.name} in CoreInterface.js")
                elif gap.module.startswith('src.vault'):
                    recommendations.append(f"Add Vault interface control for {gap.name} in VaultInterface.js")
                elif gap.module.startswith('src.synapse'):
                    recommendations.append(f"Add Synapse interface control for {gap.name} in SynapseGateway.js")
                else:
                    recommendations.append(f"Consider adding UI control for {gap.name} if user-facing")
            
            # CLI invocation recommendations
            if 'cli_invocation' in gap.gap_types:
                if gap.function_type == 'endpoint':
                    recommendations.append(f"Add CLI command in scripts/cli_tools.py calling {gap.name}")
                elif 'process' in gap.name.lower() or 'execute' in gap.name.lower():
                    recommendations.append(f"Add CLI command wrapper for {gap.name}")
                elif gap.module.startswith('src.database'):
                    recommendations.append(f"Add database CLI command for {gap.name} in scripts/db_tools.py")
                elif gap.module.startswith('src.core'):
                    recommendations.append(f"Add core management CLI command for {gap.name}")
                else:
                    recommendations.append(f"Consider adding CLI command for {gap.name} if appropriate")
            
            gap.recommendations = recommendations
    
    def _generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage gap report"""
        # Group gaps by priority and type
        gaps_by_priority = {'critical': [], 'high': [], 'medium': [], 'low': []}
        gaps_by_type = {'test': [], 'ui_invocation': [], 'cli_invocation': []}
        gaps_by_module = {}
        
        for gap in self.coverage_gaps:
            gaps_by_priority[gap.priority].append(gap)
            
            for gap_type in gap.gap_types:
                gaps_by_type[gap_type].append(gap)
            
            if gap.module not in gaps_by_module:
                gaps_by_module[gap.module] = []
            gaps_by_module[gap.module].append(gap)
        
        # Calculate statistics
        total_functions = len(self.inventory_data['functions'])
        total_endpoints = len(self.inventory_data['endpoints'])
        total_gaps = len(self.coverage_gaps)
        
        # Function gaps by type
        test_gaps = len([g for g in self.coverage_gaps if 'test' in g.gap_types])
        ui_gaps = len([g for g in self.coverage_gaps if 'ui_invocation' in g.gap_types])
        cli_gaps = len([g for g in self.coverage_gaps if 'cli_invocation' in g.gap_types])
        
        # Coverage percentages
        covered_functions = total_functions + total_endpoints - total_gaps
        coverage_percentage = (covered_functions / (total_functions + total_endpoints)) * 100 if total_functions + total_endpoints > 0 else 0
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'inventory_file': str(self.inventory_file),
            'statistics': {
                'total_functions': total_functions,
                'total_endpoints': total_endpoints,
                'total_items': total_functions + total_endpoints,
                'total_gaps': total_gaps,
                'coverage_percentage': round(coverage_percentage, 2),
                'test_gaps': test_gaps,
                'ui_invocation_gaps': ui_gaps,
                'cli_invocation_gaps': cli_gaps,
                'critical_gaps': len(gaps_by_priority['critical']),
                'high_priority_gaps': len(gaps_by_priority['high']),
                'medium_priority_gaps': len(gaps_by_priority['medium']),
                'low_priority_gaps': len(gaps_by_priority['low'])
            },
            'gaps_by_priority': {
                priority: [self._gap_to_dict(gap) for gap in gaps]
                for priority, gaps in gaps_by_priority.items()
            },
            'gaps_by_type': {
                gap_type: [self._gap_to_dict(gap) for gap in gaps]
                for gap_type, gaps in gaps_by_type.items()
            },
            'gaps_by_module': {
                module: [self._gap_to_dict(gap) for gap in gaps]
                for module, gaps in gaps_by_module.items()
            }
        }
        
        return report
    
    def _gap_to_dict(self, gap: CoverageGap) -> Dict[str, Any]:
        """Convert CoverageGap to dictionary"""
        return {
            'name': gap.name,
            'module': gap.module,
            'file_path': gap.file_path,
            'line_number': gap.line_number,
            'function_type': gap.function_type,
            'gap_types': gap.gap_types,
            'recommendations': gap.recommendations,
            'priority': gap.priority,
            'is_public': gap.is_public,
            'is_exported': gap.is_exported,
            'signature': gap.signature,
            'class_name': gap.class_name
        }
    
    def generate_coverage_gaps_md(self, report: Dict[str, Any]) -> str:
        """Generate coverage_gaps.md markdown report"""
        md_content = []
        
        # Header
        md_content.append("# Coverage Gaps Analysis")
        md_content.append("")
        md_content.append(f"**Generated:** {report['analysis_timestamp']}")
        md_content.append(f"**Project:** {report['project_root']}")
        md_content.append("")
        
        # Executive Summary
        stats = report['statistics']
        md_content.append("## Executive Summary")
        md_content.append("")
        md_content.append(f"- **Total Functions/Endpoints:** {stats['total_items']}")
        md_content.append(f"- **Coverage Gaps:** {stats['total_gaps']}")
        md_content.append(f"- **Current Coverage:** {stats['coverage_percentage']:.1f}%")
        md_content.append(f"- **Target Coverage:** ≥95%")
        md_content.append("")
        
        # Gap Breakdown
        md_content.append("### Gap Breakdown")
        md_content.append("")
        md_content.append(f"- **Test Coverage Gaps:** {stats['test_gaps']}")
        md_content.append(f"- **UI Invocation Gaps:** {stats['ui_invocation_gaps']}")
        md_content.append(f"- **CLI Invocation Gaps:** {stats['cli_invocation_gaps']}")
        md_content.append("")
        
        # Priority Breakdown
        md_content.append("### Priority Breakdown")
        md_content.append("")
        md_content.append(f"- **Critical:** {stats['critical_gaps']}")
        md_content.append(f"- **High:** {stats['high_priority_gaps']}")
        md_content.append(f"- **Medium:** {stats['medium_priority_gaps']}")
        md_content.append(f"- **Low:** {stats['low_priority_gaps']}")
        md_content.append("")
        
        # Critical Gaps (Immediate Action Required)
        md_content.append("## Critical Gaps (Immediate Action Required)")
        md_content.append("")
        critical_gaps = report['gaps_by_priority']['critical']
        if critical_gaps:
            for gap in critical_gaps:
                md_content.append(f"### {gap['name']}")
                md_content.append(f"**File:** `{gap['file_path']}:{gap['line_number']}`")
                md_content.append(f"**Module:** `{gap['module']}`")
                md_content.append(f"**Type:** {gap['function_type']}")
                md_content.append(f"**Missing:** {', '.join(gap['gap_types'])}")
                md_content.append("")
                md_content.append("**Recommendations:**")
                for rec in gap['recommendations']:
                    md_content.append(f"- {rec}")
                md_content.append("")
        else:
            md_content.append("No critical gaps found.")
            md_content.append("")
        
        # High Priority Gaps
        md_content.append("## High Priority Gaps")
        md_content.append("")
        high_gaps = report['gaps_by_priority']['high']
        if high_gaps:
            for gap in high_gaps:
                md_content.append(f"### {gap['name']}")
                md_content.append(f"**File:** `{gap['file_path']}:{gap['line_number']}`")
                md_content.append(f"**Module:** `{gap['module']}`")
                md_content.append(f"**Missing:** {', '.join(gap['gap_types'])}")
                md_content.append("")
                md_content.append("**Recommendations:**")
                for rec in gap['recommendations']:
                    md_content.append(f"- {rec}")
                md_content.append("")
        else:
            md_content.append("No high priority gaps found.")
            md_content.append("")
        
        # Module Summary
        md_content.append("## Coverage Gaps by Module")
        md_content.append("")
        gaps_by_module = report['gaps_by_module']
        for module, gaps in sorted(gaps_by_module.items()):
            if gaps:
                md_content.append(f"### {module}")
                md_content.append(f"**Gaps:** {len(gaps)}")
                md_content.append("")
                for gap in gaps:
                    gap_types_str = ', '.join(gap['gap_types'])
                    md_content.append(f"- `{gap['name']}` ({gap['priority']}) - Missing: {gap_types_str}")
                md_content.append("")
        
        # Quick Action Items
        md_content.append("## Quick Action Items")
        md_content.append("")
        md_content.append("### Immediate (Critical + High Priority)")
        immediate_gaps = critical_gaps + high_gaps
        if immediate_gaps:
            md_content.append("")
            md_content.append("1. **Add missing tests:**")
            test_gaps = [g for g in immediate_gaps if 'test' in g['gap_types']]
            for gap in test_gaps[:10]:  # Limit to first 10
                md_content.append(f"   - Add test for `{gap['name']}` in `{gap['file_path']}`")
            
            md_content.append("")
            md_content.append("2. **Add UI invocation paths:**")
            ui_gaps = [g for g in immediate_gaps if 'ui_invocation' in g['gap_types']]
            for gap in ui_gaps[:10]:  # Limit to first 10
                md_content.append(f"   - Add UI control for `{gap['name']}`")
            
            md_content.append("")
            md_content.append("3. **Add CLI invocation paths:**")
            cli_gaps = [g for g in immediate_gaps if 'cli_invocation' in g['gap_types']]
            for gap in cli_gaps[:10]:  # Limit to first 10
                md_content.append(f"   - Add CLI command for `{gap['name']}`")
        
        md_content.append("")
        md_content.append("---")
        md_content.append("*Generated by SPEC-3 Week 2 Coverage Gap Analyzer*")
        
        return '\n'.join(md_content)
    
    def save_reports(self, report: Dict[str, Any]):
        """Save coverage gap reports to files"""
        # Save JSON report
        json_file = self.project_root / 'coverage_gaps.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save Markdown report
        md_content = self.generate_coverage_gaps_md(report)
        md_file = self.project_root / 'coverage_gaps.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 Coverage gap reports saved:")
        print(f"   JSON: {json_file}")
        print(f"   Markdown: {md_file}")

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    # Initialize analyzer
    analyzer = CoverageGapAnalyzer(project_root)
    
    # Load inventory
    if not analyzer.load_inventory():
        return False
    
    # Analyze coverage gaps
    report = analyzer.analyze_coverage_gaps()
    
    if 'error' in report:
        print(f"❌ Analysis failed: {report['error']}")
        return False
    
    # Save reports
    analyzer.save_reports(report)
    
    # Print summary
    stats = report['statistics']
    print("\n" + "=" * 60)
    print("📊 COVERAGE GAP ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Items: {stats['total_items']}")
    print(f"Coverage Gaps: {stats['total_gaps']}")
    print(f"Current Coverage: {stats['coverage_percentage']:.1f}%")
    print(f"Target Coverage: ≥95%")
    print()
    print("Gap Types:")
    print(f"  Test Coverage: {stats['test_gaps']} gaps")
    print(f"  UI Invocation: {stats['ui_invocation_gaps']} gaps")
    print(f"  CLI Invocation: {stats['cli_invocation_gaps']} gaps")
    print()
    print("Priority Distribution:")
    print(f"  Critical: {stats['critical_gaps']}")
    print(f"  High: {stats['high_priority_gaps']}")
    print(f"  Medium: {stats['medium_priority_gaps']}")
    print(f"  Low: {stats['low_priority_gaps']}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)