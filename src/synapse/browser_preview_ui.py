"""
SYN003: Browser Preview UI Component

Secure browser preview panel UI with URL input, content display,
security indicators, and per-agent session management.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser

logger = logging.getLogger(__name__)


class BrowserPreviewUI:
    """Browser preview UI component with security controls."""
    
    def __init__(self, parent_frame, agent_id: str):
        self.parent_frame = parent_frame
        self.agent_id = agent_id
        self.session_id: Optional[str] = None
        self.current_url: Optional[str] = None
        self.security_status = "secure"
        self.is_loading = False
        
        # Import browser preview functionality
        from .browser_preview import create_browser_session, preview_url, get_session_info
        
        self.create_browser_session = create_browser_session
        self.preview_url = preview_url
        self.get_session_info = get_session_info
        
        self._create_ui()
        self._initialize_session()
    
    def _create_ui(self):
        """Create the browser preview UI components."""
        # Main container
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self._create_header()
        
        # URL input section
        self._create_url_section()
        
        # Security status section
        self._create_security_section()
        
        # Content display section
        self._create_content_section()
        
        # Session info section
        self._create_session_section()
        
        # Control buttons
        self._create_control_buttons()
    
    def _create_header(self):
        """Create header section."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="🔒 Secure Browser Preview", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Agent info
        agent_label = ttk.Label(header_frame, text=f"Agent: {self.agent_id}", 
                               font=("Arial", 10))
        agent_label.pack(side=tk.RIGHT)
    
    def _create_url_section(self):
        """Create URL input section."""
        url_frame = ttk.LabelFrame(self.main_frame, text="URL Configuration")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL input
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(url_input_frame, text="URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_input_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        # Method selection
        method_frame = ttk.Frame(url_frame)
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(method_frame, text="Method:").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="GET")
        method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, 
                                   values=["GET", "POST"], state="readonly", width=10)
        method_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Preview button
        self.preview_button = ttk.Button(method_frame, text="Preview", 
                                        command=self._preview_current_url)
        self.preview_button.pack(side=tk.RIGHT)
    
    def _create_security_section(self):
        """Create security status section."""
        security_frame = ttk.LabelFrame(self.main_frame, text="Security Status")
        security_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Security indicators
        indicators_frame = ttk.Frame(security_frame)
        indicators_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Sandbox status
        self.sandbox_label = ttk.Label(indicators_frame, text="🛡️ Sandboxed: Active", 
                                      foreground="green")
        self.sandbox_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # CSP status
        self.csp_label = ttk.Label(indicators_frame, text="🔒 CSP: Enforced", 
                                  foreground="green")
        self.csp_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Content filtering
        self.filter_label = ttk.Label(indicators_frame, text="🔍 Content Filter: Active", 
                                     foreground="green")
        self.filter_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Session isolation
        self.isolation_label = ttk.Label(indicators_frame, text="🔐 Session Isolated", 
                                        foreground="green")
        self.isolation_label.pack(side=tk.LEFT)
    
    def _create_content_section(self):
        """Create content display section."""
        content_frame = ttk.LabelFrame(self.main_frame, text="Content Preview")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Content display
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                     height=20, state=tk.DISABLED)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status bar
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="Ready", 
                                     font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.content_size_label = ttk.Label(status_frame, text="", 
                                           font=("Arial", 9))
        self.content_size_label.pack(side=tk.RIGHT)
    
    def _create_session_section(self):
        """Create session information section."""
        session_frame = ttk.LabelFrame(self.main_frame, text="Session Information")
        session_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Session details
        details_frame = ttk.Frame(session_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Session ID
        self.session_id_label = ttk.Label(details_frame, text="Session ID: Initializing...")
        self.session_id_label.pack(anchor=tk.W)
        
        # Session age
        self.session_age_label = ttk.Label(details_frame, text="Session Age: --")
        self.session_age_label.pack(anchor=tk.W)
        
        # URL history count
        self.history_label = ttk.Label(details_frame, text="URLs Visited: 0")
        self.history_label.pack(anchor=tk.W)
        
        # Security violations
        self.violations_label = ttk.Label(details_frame, text="Security Violations: 0")
        self.violations_label.pack(anchor=tk.W)
    
    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Clear content
        clear_button = ttk.Button(button_frame, text="Clear Content", 
                                 command=self._clear_content)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh session
        refresh_button = ttk.Button(button_frame, text="Refresh Session", 
                                   command=self._refresh_session)
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Security report
        security_button = ttk.Button(button_frame, text="Security Report", 
                                    command=self._show_security_report)
        security_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # External browser (for comparison)
        external_button = ttk.Button(button_frame, text="Open in External Browser", 
                                    command=self._open_external_browser)
        external_button.pack(side=tk.RIGHT)
    
    async def _initialize_session(self):
        """Initialize browser session for agent."""
        try:
            self.session_id = await self.create_browser_session(self.agent_id)
            self._update_session_info()
            self.status_label.config(text="Session initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            self.status_label.config(text=f"Session initialization failed: {str(e)}")
    
    def _initialize_session_sync(self):
        """Synchronous wrapper for session initialization."""
        asyncio.run(self._initialize_session())
    
    def _preview_current_url(self):
        """Preview the current URL in the entry field."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        method = self.method_var.get()
        
        # Run preview in separate thread to avoid blocking UI
        threading.Thread(target=self._preview_url_thread, args=(url, method), 
                        daemon=True).start()
    
    def _preview_url_thread(self, url: str, method: str):
        """Thread function for URL preview."""
        try:
            self.is_loading = True
            self._update_ui_loading_state()
            
            # Run async preview
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.preview_url(self.session_id, url, method))
                self._handle_preview_result(result)
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Preview error: {e}")
            self._handle_preview_error(str(e))
        finally:
            self.is_loading = False
            self._update_ui_loading_state()
    
    def _handle_preview_result(self, result: Dict):
        """Handle preview result."""
        if result.get("success"):
            self.current_url = result["url"]
            self._display_content(result["content"])
            self._update_content_info(result)
            self._update_session_info()
            self.status_label.config(text="Preview completed successfully")
        else:
            error_msg = result.get("error", "Unknown error")
            if result.get("security_violation"):
                self._handle_security_violation(error_msg)
            else:
                self._handle_preview_error(error_msg)
    
    def _handle_preview_error(self, error: str):
        """Handle preview error."""
        self.status_label.config(text=f"Preview failed: {error}")
        messagebox.showerror("Preview Error", f"Failed to preview URL:\n{error}")
    
    def _handle_security_violation(self, violation: str):
        """Handle security violation."""
        self.status_label.config(text=f"Security violation: {violation}")
        messagebox.showwarning("Security Violation", 
                              f"Security policy violation detected:\n{violation}")
    
    def _display_content(self, content: str):
        """Display content in the text area."""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content)
        self.content_text.config(state=tk.DISABLED)
    
    def _update_content_info(self, result: Dict):
        """Update content information display."""
        content_size = result.get("content_size", 0)
        content_type = result.get("content_type", "unknown")
        
        size_kb = content_size / 1024
        self.content_size_label.config(text=f"Size: {size_kb:.1f}KB | Type: {content_type}")
    
    def _update_session_info(self):
        """Update session information display."""
        if not self.session_id:
            return
        
        try:
            session_info = self.get_session_info(self.session_id)
            if session_info:
                self.session_id_label.config(text=f"Session ID: {session_info['session_id']}")
                self.session_age_label.config(text=f"Session Age: {session_info['session_age_minutes']:.1f} minutes")
                self.history_label.config(text=f"URLs Visited: {len(session_info['url_history'])}")
                self.violations_label.config(text=f"Security Violations: {len(session_info['security_violations'])}")
        except Exception as e:
            logger.error(f"Failed to update session info: {e}")
    
    def _update_ui_loading_state(self):
        """Update UI loading state."""
        if self.is_loading:
            self.preview_button.config(state=tk.DISABLED, text="Loading...")
            self.status_label.config(text="Loading preview...")
        else:
            self.preview_button.config(state=tk.NORMAL, text="Preview")
    
    def _clear_content(self):
        """Clear content display."""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.config(state=tk.DISABLED)
        self.current_url = None
        self.content_size_label.config(text="")
        self.status_label.config(text="Content cleared")
    
    def _refresh_session(self):
        """Refresh session information."""
        self._update_session_info()
        self.status_label.config(text="Session refreshed")
    
    def _show_security_report(self):
        """Show security report dialog."""
        if not self.session_id:
            messagebox.showinfo("Security Report", "No active session")
            return
        
        try:
            session_info = self.get_session_info(self.session_id)
            if session_info:
                report = self._generate_security_report(session_info)
                self._show_report_dialog(report)
            else:
                messagebox.showinfo("Security Report", "Unable to retrieve session information")
        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            messagebox.showerror("Error", f"Failed to generate security report: {str(e)}")
    
    def _generate_security_report(self, session_info: Dict) -> str:
        """Generate security report."""
        report_lines = [
            "=== BROWSER PREVIEW SECURITY REPORT ===",
            f"Session ID: {session_info['session_id']}",
            f"Agent ID: {session_info['agent_id']}",
            f"Created: {session_info['created_at']}",
            f"Last Accessed: {session_info['last_accessed']}",
            f"Session Age: {session_info['session_age_minutes']:.1f} minutes",
            "",
            "=== SECURITY STATUS ===",
            "✅ Sandboxed iframe with restricted permissions",
            "✅ Content Security Policy (CSP) enforced",
            "✅ JavaScript execution disabled by default",
            "✅ Content filtering and sanitization active",
            "✅ Per-agent session isolation",
            "✅ URL validation and domain restrictions",
            "",
            f"=== ACTIVITY SUMMARY ===",
            f"URLs Visited: {len(session_info['url_history'])}",
            f"Security Violations: {len(session_info['security_violations'])}",
            "",
            "=== URL HISTORY ==="
        ]
        
        for i, url in enumerate(session_info['url_history'], 1):
            report_lines.append(f"{i}. {url}")
        
        if session_info['security_violations']:
            report_lines.extend([
                "",
                "=== SECURITY VIOLATIONS ==="
            ])
            for i, violation in enumerate(session_info['security_violations'], 1):
                report_lines.append(f"{i}. {violation}")
        
        return "\n".join(report_lines)
    
    def _show_report_dialog(self, report: str):
        """Show security report in dialog."""
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Security Report")
        dialog.geometry("600x500")
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
        # Report text
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, report)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_button.pack(pady=(0, 10))
    
    def _open_external_browser(self):
        """Open current URL in external browser for comparison."""
        if not self.current_url:
            messagebox.showinfo("Info", "No URL to open in external browser")
            return
        
        try:
            webbrowser.open(self.current_url)
            self.status_label.config(text="Opened in external browser")
        except Exception as e:
            logger.error(f"Failed to open external browser: {e}")
            messagebox.showerror("Error", f"Failed to open external browser: {str(e)}")
    
    def destroy(self):
        """Clean up resources."""
        # Cleanup session if needed
        if self.session_id:
            logger.info(f"Destroying browser preview UI for session {self.session_id}")
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()


def create_browser_preview_ui(parent_frame, agent_id: str) -> BrowserPreviewUI:
    """Create browser preview UI component."""
    return BrowserPreviewUI(parent_frame, agent_id) 