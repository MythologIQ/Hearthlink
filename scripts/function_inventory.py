#!/usr/bin/env python3
"""
SPEC-3 Week 2: Function Inventory & Coverage Analysis
Comprehensive scanner for all exported functions, methods, and REST endpoints
"""

import ast
import json
import re
import os
import sys
import glob
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FunctionInfo:
    """Information about a function or method"""
    name: str
    module: str
    file_path: str
    line_number: int
    signature: str
    function_type: str  # 'function', 'method', 'async_function', 'async_method', 'endpoint'
    class_name: Optional[str] = None
    is_exported: bool = False
    is_public: bool = True
    docstring: Optional[str] = None
    decorators: List[str] = None
    test_files: List[str] = None
    ui_triggers: List[str] = None
    cli_triggers: List[str] = None
    has_coverage: bool = False
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
        if self.test_files is None:
            self.test_files = []
        if self.ui_triggers is None:
            self.ui_triggers = []
        if self.cli_triggers is None:
            self.cli_triggers = []

@dataclass
class EndpointInfo:
    """Information about a REST endpoint"""
    path: str
    method: str
    function_name: str
    module: str
    file_path: str
    line_number: int
    handler_signature: str
    decorators: List[str] = None
    test_files: List[str] = None
    ui_calls: List[str] = None
    has_coverage: bool = False
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
        if self.test_files is None:
            self.test_files = []
        if self.ui_calls is None:
            self.ui_calls = []

class FunctionInventoryScanner:
    """Comprehensive function and endpoint scanner"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.functions: List[FunctionInfo] = []
        self.endpoints: List[EndpointInfo] = []
        self.modules_scanned: Set[str] = set()
        
        # Patterns for different types of exports and endpoints
        self.endpoint_patterns = [
            r'@app\.route\(["\']([^"\']+)["\'](?:,\s*methods=\[([^\]]+)\])?',
            r'@router\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@api\.route\(["\']([^"\']+)["\'](?:,\s*methods=\[([^\]]+)\])?',
            r'router\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'app\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        ]
        
        # Directories to scan
        self.scan_dirs = [
            'src',
            'electron',
            'preload', 
            'ipcHandlers',
            'services',
            'scripts'
        ]
        
        # Directories to exclude
        self.exclude_dirs = {
            'node_modules', '__pycache__', '.git', 'dist', 'build', 
            'coverage', 'Archive', 'ArchiveCode', 'backups', 'logs',
            'userData', 'vault', 'temp_node_modules'
        }
        
        # File extensions to scan
        self.python_extensions = {'.py'}
        self.js_extensions = {'.js', '.ts', '.jsx', '.tsx'}
        
    def scan_repository(self) -> Dict[str, Any]:
        """Scan the entire repository for functions and endpoints"""
        logger.info("Starting comprehensive repository scan...")
        
        # Scan Python files
        self._scan_python_files()
        
        # Scan JavaScript/TypeScript files
        self._scan_js_files()
        
        # Analyze test coverage
        self._analyze_test_coverage()
        
        # Find UI and CLI triggers
        self._find_invocation_paths()
        
        # Generate inventory report
        inventory = self._generate_inventory_report()
        
        logger.info(f"Scan complete: {len(self.functions)} functions, {len(self.endpoints)} endpoints")
        return inventory
    
    def _scan_python_files(self):
        """Scan all Python files for functions and endpoints"""
        logger.info("Scanning Python files...")
        
        for scan_dir in self.scan_dirs:
            scan_path = self.project_root / scan_dir
            if not scan_path.exists():
                continue
                
            for py_file in scan_path.rglob('*.py'):
                if self._should_exclude_file(py_file):
                    continue
                    
                try:
                    self._analyze_python_file(py_file)
                except Exception as e:
                    logger.warning(f"Failed to analyze {py_file}: {e}")
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Get module name
            module_name = self._get_module_name(file_path)
            self.modules_scanned.add(module_name)
            
            # Analyze the AST
            self._analyze_ast(tree, file_path, module_name, content)
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, module_name: str, content: str):
        """Analyze AST nodes for functions and endpoints"""
        content_lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._extract_function_info(
                    node, file_path, module_name, content_lines
                )
                if func_info:
                    self.functions.append(func_info)
                
                # Check for endpoint decorators
                endpoint_info = self._extract_endpoint_info(
                    node, file_path, module_name, content_lines
                )
                if endpoint_info:
                    self.endpoints.append(endpoint_info)
    
    def _extract_function_info(self, node: ast.AST, file_path: Path, module_name: str, 
                              content_lines: List[str]) -> Optional[FunctionInfo]:
        """Extract function information from AST node"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        
        # Determine function type
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Get class context if method
        class_name = None
        for parent in ast.walk(ast.parse('\n'.join(content_lines))):
            for child in ast.iter_child_nodes(parent):
                if child == node and isinstance(parent, ast.ClassDef):
                    class_name = parent.name
                    break
        
        function_type = 'async_method' if is_async and class_name else \
                       'method' if class_name else \
                       'async_function' if is_async else 'function'
        
        # Extract signature
        signature = self._get_function_signature(node)
        
        # Check if public (not starting with _)
        is_public = not node.name.startswith('_')
        
        # Check if exported (in __all__ or imported elsewhere)
        is_exported = self._is_function_exported(node.name, module_name)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract decorators
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        return FunctionInfo(
            name=node.name,
            module=module_name,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=node.lineno,
            signature=signature,
            function_type=function_type,
            class_name=class_name,
            is_exported=is_exported,
            is_public=is_public,
            docstring=docstring,
            decorators=decorators
        )
    
    def _extract_endpoint_info(self, node: ast.AST, file_path: Path, module_name: str,
                              content_lines: List[str]) -> Optional[EndpointInfo]:
        """Extract REST endpoint information from decorated functions"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        
        # Check decorators for endpoint patterns
        for decorator in node.decorator_list:
            decorator_str = self._get_decorator_string(decorator, content_lines)
            
            for pattern in self.endpoint_patterns:
                match = re.search(pattern, decorator_str)
                if match:
                    path = match.group(1)
                    methods = match.group(2) if len(match.groups()) > 1 else 'GET'
                    
                    if methods:
                        methods = [m.strip().strip('"\'') for m in methods.split(',')]
                    else:
                        # Infer method from decorator
                        if '.post(' in decorator_str:
                            methods = ['POST']
                        elif '.put(' in decorator_str:
                            methods = ['PUT']
                        elif '.delete(' in decorator_str:
                            methods = ['DELETE']
                        elif '.patch(' in decorator_str:
                            methods = ['PATCH']
                        else:
                            methods = ['GET']
                    
                    # Create endpoint info for each method
                    for method in methods:
                        endpoint = EndpointInfo(
                            path=path,
                            method=method.upper(),
                            function_name=node.name,
                            module=module_name,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            handler_signature=self._get_function_signature(node),
                            decorators=[self._get_decorator_name(dec) for dec in node.decorator_list]
                        )
                        return endpoint
        
        return None
    
    def _scan_js_files(self):
        """Scan JavaScript/TypeScript files for functions and React components"""
        logger.info("Scanning JavaScript/TypeScript files...")
        
        for scan_dir in self.scan_dirs:
            scan_path = self.project_root / scan_dir
            if not scan_path.exists():
                continue
                
            for ext in self.js_extensions:
                for js_file in scan_path.rglob(f'*{ext}'):
                    if self._should_exclude_file(js_file):
                        continue
                        
                    try:
                        self._analyze_js_file(js_file)
                    except Exception as e:
                        logger.warning(f"Failed to analyze {js_file}: {e}")
    
    def _analyze_js_file(self, file_path: Path):
        """Analyze JavaScript/TypeScript file for functions and components"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_name = self._get_module_name(file_path)
            self.modules_scanned.add(module_name)
            
            # Extract functions using regex patterns
            self._extract_js_functions(content, file_path, module_name)
            
            # Extract React components
            self._extract_react_components(content, file_path, module_name)
            
            # Extract IPC handlers
            self._extract_ipc_handlers(content, file_path, module_name)
            
        except Exception as e:
            logger.warning(f"Error analyzing JS file {file_path}: {e}")
    
    def _extract_js_functions(self, content: str, file_path: Path, module_name: str):
        """Extract JavaScript functions using regex"""
        patterns = [
            # Function declarations
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)',
            # Arrow functions
            r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            # Method definitions in classes
            r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',
            # React functional components
            r'(?:export\s+)?(?:const|function)\s+(\w+)\s*[=\(].*(?:React\.FC|FunctionComponent)',
        ]
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    func_name = match.group(1)
                    
                    # Skip if starts with underscore or is a common JS keyword
                    if func_name.startswith('_') or func_name in {'if', 'for', 'while', 'switch'}:
                        continue
                    
                    # Determine function type
                    is_async = 'async' in line
                    is_export = 'export' in line
                    is_component = any(keyword in line for keyword in ['React.FC', 'FunctionComponent', 'Component'])
                    
                    function_type = 'react_component' if is_component else \
                                   'async_function' if is_async else 'function'
                    
                    func_info = FunctionInfo(
                        name=func_name,
                        module=module_name,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=i,
                        signature=line.strip(),
                        function_type=function_type,
                        is_exported=is_export,
                        is_public=not func_name.startswith('_')
                    )
                    
                    self.functions.append(func_info)
    
    def _extract_react_components(self, content: str, file_path: Path, module_name: str):
        """Extract React components specifically"""
        # Component patterns
        component_patterns = [
            r'(?:export\s+(?:default\s+)?)?(?:const|function)\s+(\w+)\s*[=\(].*return\s*\(',
            r'class\s+(\w+)\s+extends\s+(?:React\.)?Component',
            r'(?:export\s+(?:default\s+)?)?const\s+(\w+)\s*:\s*React\.FC'
        ]
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in component_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    component_name = match.group(1)
                    
                    # React components should start with capital letter
                    if not component_name[0].isupper():
                        continue
                    
                    func_info = FunctionInfo(
                        name=component_name,
                        module=module_name,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=i,
                        signature=line.strip(),
                        function_type='react_component',
                        is_exported='export' in line,
                        is_public=True
                    )
                    
                    self.functions.append(func_info)
    
    def _extract_ipc_handlers(self, content: str, file_path: Path, module_name: str):
        """Extract Electron IPC handlers"""
        ipc_patterns = [
            r'ipcMain\.handle\(["\']([^"\']+)["\'],\s*([^)]+)\)',
            r'ipcMain\.on\(["\']([^"\']+)["\'],\s*([^)]+)\)',
            r'contextBridge\.exposeInMainWorld\(["\']([^"\']+)["\']'
        ]
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in ipc_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    channel_name = match.group(1)
                    handler = match.group(2) if len(match.groups()) > 1 else 'anonymous'
                    
                    endpoint_info = EndpointInfo(
                        path=f'/ipc/{channel_name}',
                        method='IPC',
                        function_name=handler,
                        module=module_name,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=i,
                        handler_signature=line.strip()
                    )
                    
                    self.endpoints.append(endpoint_info)
    
    def _analyze_test_coverage(self):
        """Analyze test files to determine function coverage"""
        logger.info("Analyzing test coverage...")
        
        test_dirs = ['tests', 'test', '__tests__']
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.test.ts', '*.spec.js', '*.spec.ts']
        
        # Find all test files
        test_files = []
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    test_files.extend(test_path.rglob(pattern))
        
        # Also check for test files in src directories
        for scan_dir in self.scan_dirs:
            scan_path = self.project_root / scan_dir
            if scan_path.exists():
                for pattern in test_patterns:
                    test_files.extend(scan_path.rglob(pattern))
        
        # Analyze each test file
        function_names = {func.name for func in self.functions}
        endpoint_names = {ep.function_name for ep in self.endpoints}
        
        for test_file in test_files:
            if self._should_exclude_file(test_file):
                continue
                
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                test_file_rel = str(test_file.relative_to(self.project_root))
                
                # Find function references in test content
                for func in self.functions:
                    if func.name in content:
                        func.test_files.append(test_file_rel)
                        func.has_coverage = True
                
                # Find endpoint references in test content
                for endpoint in self.endpoints:
                    if endpoint.function_name in content or endpoint.path in content:
                        endpoint.test_files.append(test_file_rel)
                        endpoint.has_coverage = True
                        
            except Exception as e:
                logger.warning(f"Error analyzing test file {test_file}: {e}")
    
    def _find_invocation_paths(self):
        """Find UI and CLI invocation paths for functions"""
        logger.info("Finding invocation paths...")
        
        # Scan UI files for function calls
        self._find_ui_invocations()
        
        # Scan CLI scripts for function calls
        self._find_cli_invocations()
    
    def _find_ui_invocations(self):
        """Find UI invocations of functions"""
        ui_dirs = ['src/components', 'src', 'electron', 'preload']
        
        for ui_dir in ui_dirs:
            ui_path = self.project_root / ui_dir
            if not ui_path.exists():
                continue
                
            for ui_file in ui_path.rglob('*.{js,ts,jsx,tsx}'):
                if self._should_exclude_file(ui_file):
                    continue
                    
                try:
                    with open(ui_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    ui_file_rel = str(ui_file.relative_to(self.project_root))
                    
                    # Find function calls in UI content
                    for func in self.functions:
                        if func.name in content:
                            func.ui_triggers.append(ui_file_rel)
                    
                    # Find API calls to endpoints
                    for endpoint in self.endpoints:
                        if endpoint.path in content:
                            endpoint.ui_calls.append(ui_file_rel)
                            
                except Exception as e:
                    logger.warning(f"Error analyzing UI file {ui_file}: {e}")
    
    def _find_cli_invocations(self):
        """Find CLI invocations of functions"""
        cli_dirs = ['scripts', 'cli']
        
        for cli_dir in cli_dirs:
            cli_path = self.project_root / cli_dir
            if not cli_path.exists():
                continue
                
            for cli_file in cli_path.rglob('*.py'):
                if self._should_exclude_file(cli_file):
                    continue
                    
                try:
                    with open(cli_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    cli_file_rel = str(cli_file.relative_to(self.project_root))
                    
                    # Find function calls in CLI content
                    for func in self.functions:
                        if func.name in content:
                            func.cli_triggers.append(cli_file_rel)
                            
                except Exception as e:
                    logger.warning(f"Error analyzing CLI file {cli_file}: {e}")
    
    def _generate_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        # Calculate statistics
        total_functions = len(self.functions)
        tested_functions = sum(1 for f in self.functions if f.has_coverage)
        public_functions = sum(1 for f in self.functions if f.is_public)
        exported_functions = sum(1 for f in self.functions if f.is_exported)
        
        total_endpoints = len(self.endpoints)
        tested_endpoints = sum(1 for e in self.endpoints if e.has_coverage)
        
        # Functions with invocation paths
        ui_invoked = sum(1 for f in self.functions if f.ui_triggers)
        cli_invoked = sum(1 for f in self.functions if f.cli_triggers)
        invoked_functions = len(set(f.name for f in self.functions if f.ui_triggers or f.cli_triggers))
        
        # Endpoints with invocation paths
        ui_called_endpoints = sum(1 for e in self.endpoints if e.ui_calls)
        
        # Coverage calculations
        test_coverage_percent = (tested_functions / total_functions * 100) if total_functions > 0 else 0
        invocation_coverage_percent = (invoked_functions / total_functions * 100) if total_functions > 0 else 0
        
        # Generate report
        inventory = {
            'scan_timestamp': str(datetime.now().isoformat()),
            'project_root': str(self.project_root),
            'modules_scanned': sorted(list(self.modules_scanned)),
            'statistics': {
                'total_functions': total_functions,
                'public_functions': public_functions,
                'exported_functions': exported_functions,
                'tested_functions': tested_functions,
                'test_coverage_percent': round(test_coverage_percent, 2),
                'ui_invoked_functions': ui_invoked,
                'cli_invoked_functions': cli_invoked,
                'total_invoked_functions': invoked_functions,
                'invocation_coverage_percent': round(invocation_coverage_percent, 2),
                'total_endpoints': total_endpoints,
                'tested_endpoints': tested_endpoints,
                'ui_called_endpoints': ui_called_endpoints
            },
            'functions': [asdict(func) for func in self.functions],
            'endpoints': [asdict(endpoint) for endpoint in self.endpoints]
        }
        
        return inventory
    
    # Helper methods
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning"""
        # Check if any parent directory is in exclude list
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return True
        
        # Check filename patterns to exclude
        exclude_patterns = [
            '.*',  # Hidden files
            '__pycache__',
            'node_modules',
            '.min.js',
            '.bundle.js'
        ]
        
        for pattern in exclude_patterns:
            if file_path.name.startswith(pattern) or pattern in str(file_path):
                return True
        
        return False
    
    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path"""
        relative_path = file_path.relative_to(self.project_root)
        parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(parts)
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature from AST node"""
        args = []
        
        # Handle arguments
        for arg in node.args.args:
            args.append(arg.arg)
        
        # Handle *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        # Handle **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        return f"{node.name}({', '.join(args)})"
    
    def _is_function_exported(self, func_name: str, module_name: str) -> bool:
        """Check if function is exported (simple heuristic)"""
        # This is a simplified check - in a real implementation,
        # you'd want to parse __all__ and check imports
        return not func_name.startswith('_')
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}" if hasattr(decorator.value, 'id') else str(decorator.attr)
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        else:
            return str(decorator)
    
    def _get_decorator_string(self, decorator: ast.AST, content_lines: List[str]) -> str:
        """Get full decorator string from source"""
        try:
            if hasattr(decorator, 'lineno'):
                line_idx = decorator.lineno - 1
                if 0 <= line_idx < len(content_lines):
                    return content_lines[line_idx].strip()
        except:
            pass
        return str(decorator)

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    # Initialize scanner
    scanner = FunctionInventoryScanner(project_root)
    
    # Run comprehensive scan
    inventory = scanner.scan_repository()
    
    # Save inventory to JSON file
    output_file = project_root / 'function_inventory.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    # Print summary
    stats = inventory['statistics']
    print("\n" + "=" * 60)
    print("📊 FUNCTION INVENTORY SUMMARY")
    print("=" * 60)
    print(f"Total Functions: {stats['total_functions']}")
    print(f"Public Functions: {stats['public_functions']}")
    print(f"Exported Functions: {stats['exported_functions']}")
    print(f"Test Coverage: {stats['tested_functions']}/{stats['total_functions']} ({stats['test_coverage_percent']:.1f}%)")
    print(f"Invocation Coverage: {stats['total_invoked_functions']}/{stats['total_functions']} ({stats['invocation_coverage_percent']:.1f}%)")
    print(f"REST Endpoints: {stats['total_endpoints']}")
    print(f"Modules Scanned: {len(inventory['modules_scanned'])}")
    print(f"\n📄 Full inventory saved to: {output_file}")
    print("=" * 60)
    
    return inventory

if __name__ == "__main__":
    from datetime import datetime
    main()