"""
Security UI Components for SYN004/SYN005

UI components for security monitoring, webhook management, and credential management
with proper security controls and audit displays.
"""

import asyncio
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .security_monitor import get_security_status, ActionType, SecurityLevel
from .webhook_manager import webhook_manager, WebhookCLITester, AuthType
from .credential_manager import credential_manager, CredentialType, InjectionMethod

logger = logging.getLogger(__name__)


class SecurityDashboardUI:
    """Main security dashboard UI."""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self._create_ui()
    
    def _create_ui(self):
        """Create the security dashboard UI."""
        # Main container
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🛡️ Security Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", 
                                   command=self._refresh_status)
        refresh_button.pack(side=tk.RIGHT)
        
        # Notebook for different security modules
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Security monitoring tab
        self._create_security_monitoring_tab()
        
        # Webhook management tab
        self._create_webhook_management_tab()
        
        # Credential management tab
        self._create_credential_management_tab()
        
        # Audit log tab
        self._create_audit_log_tab()
    
    def _create_security_monitoring_tab(self):
        """Create security monitoring tab."""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="Security Monitoring")
        
        # Rate limiting status
        rate_frame = ttk.LabelFrame(monitoring_frame, text="Rate Limiting Status")
        rate_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.rate_status_text = scrolledtext.ScrolledText(rate_frame, height=8, width=80)
        self.rate_status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Security hooks status
        hooks_frame = ttk.LabelFrame(monitoring_frame, text="Security Hooks")
        hooks_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.hooks_status_text = scrolledtext.ScrolledText(hooks_frame, height=6, width=80)
        self.hooks_status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Update status
        self._update_security_status()
    
    def _create_webhook_management_tab(self):
        """Create webhook management tab."""
        webhook_frame = ttk.Frame(self.notebook)
        self.notebook.add(webhook_frame, text="Webhook Management")
        
        # Webhook list
        list_frame = ttk.LabelFrame(webhook_frame, text="Configured Webhooks")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Webhook listbox
        self.webhook_listbox = tk.Listbox(list_frame, height=10)
        self.webhook_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.webhook_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.webhook_listbox.config(yscrollcommand=scrollbar.set)
        
        # Webhook buttons
        button_frame = ttk.Frame(webhook_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Add Webhook", 
                  command=self._show_add_webhook_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Edit Webhook", 
                  command=self._edit_webhook).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Webhook", 
                  command=self._delete_webhook).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Test Webhook", 
                  command=self._test_webhook).pack(side=tk.LEFT, padx=(0, 5))
        
        # Update webhook list
        self._update_webhook_list()
    
    def _create_credential_management_tab(self):
        """Create credential management tab."""
        cred_frame = ttk.Frame(self.notebook)
        self.notebook.add(cred_frame, text="Credential Management")
        
        # Credential list
        cred_list_frame = ttk.LabelFrame(cred_frame, text="Stored Credentials")
        cred_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Credential listbox
        self.credential_listbox = tk.Listbox(cred_list_frame, height=10)
        self.credential_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        cred_scrollbar = ttk.Scrollbar(cred_list_frame, orient=tk.VERTICAL, command=self.credential_listbox.yview)
        cred_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.credential_listbox.config(yscrollcommand=cred_scrollbar.set)
        
        # Credential buttons
        cred_button_frame = ttk.Frame(cred_frame)
        cred_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(cred_button_frame, text="Add Credential", 
                  command=self._show_add_credential_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cred_button_frame, text="Edit Credential", 
                  command=self._edit_credential).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cred_button_frame, text="Delete Credential", 
                  command=self._delete_credential).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cred_button_frame, text="Request Injection", 
                  command=self._request_injection).pack(side=tk.LEFT, padx=(0, 5))
        
        # Pending injections
        injection_frame = ttk.LabelFrame(cred_frame, text="Pending Injections")
        injection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.injection_listbox = tk.Listbox(injection_frame, height=6)
        self.injection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Injection scrollbar
        inj_scrollbar = ttk.Scrollbar(injection_frame, orient=tk.VERTICAL, command=self.injection_listbox.yview)
        inj_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.injection_listbox.config(yscrollcommand=inj_scrollbar.set)
        
        # Injection buttons
        inj_button_frame = ttk.Frame(cred_frame)
        inj_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(inj_button_frame, text="Approve Injection", 
                  command=self._approve_injection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inj_button_frame, text="Deny Injection", 
                  command=self._deny_injection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(inj_button_frame, text="Execute Injection", 
                  command=self._execute_injection).pack(side=tk.LEFT, padx=(0, 5))
        
        # Update lists
        self._update_credential_list()
        self._update_injection_list()
    
    def _create_audit_log_tab(self):
        """Create audit log tab."""
        audit_frame = ttk.Frame(self.notebook)
        self.notebook.add(audit_frame, text="Audit Log")
        
        # Log display
        log_frame = ttk.LabelFrame(audit_frame, text="Security Events")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.audit_text = scrolledtext.ScrolledText(log_frame, height=20, width=100)
        self.audit_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log controls
        log_control_frame = ttk.Frame(audit_frame)
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_control_frame, text="Refresh Log", 
                  command=self._refresh_audit_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_control_frame, text="Export Log", 
                  command=self._export_audit_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_control_frame, text="Clear Log", 
                  command=self._clear_audit_log).pack(side=tk.LEFT)
        
        # Load audit log
        self._load_audit_log()
    
    async def _update_security_status(self):
        """Update security status display."""
        try:
            status = await get_security_status()
            
            # Update rate limiting status
            rate_text = "Rate Limiting Status:\n"
            for key, info in status['rate_limits'].items():
                rate_text += f"\n{key.upper()}:\n"
                rate_text += f"  Current: {info['current_requests']}\n"
                rate_text += f"  Limit: {info['limit_per_minute']}/min\n"
                rate_text += f"  Remaining: {info['remaining']}\n"
            
            self.rate_status_text.config(state=tk.NORMAL)
            self.rate_status_text.delete(1.0, tk.END)
            self.rate_status_text.insert(1.0, rate_text)
            self.rate_status_text.config(state=tk.DISABLED)
            
            # Update hooks status
            hooks_text = "Security Hooks:\n"
            for action_type, count in status['hooks_registered'].items():
                hooks_text += f"  {action_type}: {count} hooks\n"
            
            self.hooks_status_text.config(state=tk.NORMAL)
            self.hooks_status_text.delete(1.0, tk.END)
            self.hooks_status_text.insert(1.0, hooks_text)
            self.hooks_status_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Failed to update security status: {e}")
    
    def _refresh_status(self):
        """Refresh security status."""
        asyncio.create_task(self._update_security_status())
    
    def _update_webhook_list(self):
        """Update webhook list display."""
        self.webhook_listbox.delete(0, tk.END)
        
        webhooks = webhook_manager.list_webhooks()
        for webhook in webhooks:
            status_icon = "✅" if webhook.status.value == "active" else "❌"
            self.webhook_listbox.insert(tk.END, f"{status_icon} {webhook.name} ({webhook.url})")
    
    def _update_credential_list(self):
        """Update credential list display."""
        self.credential_listbox.delete(0, tk.END)
        
        credentials = credential_manager.search_credentials()
        for cred in credentials:
            self.credential_listbox.insert(tk.END, f"{cred['name']} ({cred['domain']}) - {cred['username']}")
    
    def _update_injection_list(self):
        """Update injection list display."""
        self.injection_listbox.delete(0, tk.END)
        
        pending = credential_manager.get_pending_injections()
        for request in pending:
            self.injection_listbox.insert(tk.END, f"{request.credential_id} -> {request.target_domain}")
    
    def _show_add_webhook_dialog(self):
        """Show add webhook dialog."""
        dialog = WebhookDialog(self.parent_frame, webhook_manager)
        dialog.show()
        self._update_webhook_list()
    
    def _edit_webhook(self):
        """Edit selected webhook."""
        selection = self.webhook_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a webhook to edit")
            return
        
        # Get webhook ID from selection
        webhook_name = self.webhook_listbox.get(selection[0])
        # This is a simplified version - in practice, you'd need to map display names to IDs
        
        messagebox.showinfo("Info", "Edit webhook functionality would be implemented here")
    
    def _delete_webhook(self):
        """Delete selected webhook."""
        selection = self.webhook_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a webhook to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this webhook?"):
            # Delete webhook logic would go here
            self._update_webhook_list()
    
    def _test_webhook(self):
        """Test selected webhook."""
        selection = self.webhook_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a webhook to test")
            return
        
        # Test webhook logic would go here
        messagebox.showinfo("Info", "Webhook test functionality would be implemented here")
    
    def _show_add_credential_dialog(self):
        """Show add credential dialog."""
        dialog = CredentialDialog(self.parent_frame, credential_manager)
        dialog.show()
        self._update_credential_list()
    
    def _edit_credential(self):
        """Edit selected credential."""
        selection = self.credential_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credential to edit")
            return
        
        messagebox.showinfo("Info", "Edit credential functionality would be implemented here")
    
    def _delete_credential(self):
        """Delete selected credential."""
        selection = self.credential_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credential to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this credential?"):
            # Delete credential logic would go here
            self._update_credential_list()
    
    def _request_injection(self):
        """Request credential injection."""
        selection = self.credential_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a credential for injection")
            return
        
        messagebox.showinfo("Info", "Injection request functionality would be implemented here")
    
    def _approve_injection(self):
        """Approve selected injection."""
        selection = self.injection_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an injection to approve")
            return
        
        # Approve injection logic would go here
        self._update_injection_list()
    
    def _deny_injection(self):
        """Deny selected injection."""
        selection = self.injection_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an injection to deny")
            return
        
        # Deny injection logic would go here
        self._update_injection_list()
    
    def _execute_injection(self):
        """Execute selected injection."""
        selection = self.injection_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an injection to execute")
            return
        
        # Execute injection logic would go here
        self._update_injection_list()
    
    def _load_audit_log(self):
        """Load audit log from file."""
        try:
            log_file = Path("logs/synapse-actions.json")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    events = json.load(f)
                
                log_text = "Security Events:\n" + "="*50 + "\n\n"
                
                for event in events[-50:]:  # Show last 50 events
                    log_text += f"Event ID: {event['event_id']}\n"
                    log_text += f"Timestamp: {event['timestamp']}\n"
                    log_text += f"Action: {event['action_type']}\n"
                    log_text += f"Agent: {event['agent_id']}\n"
                    log_text += f"Success: {event['success']}\n"
                    
                    if event.get('error_message'):
                        log_text += f"Error: {event['error_message']}\n"
                    
                    log_text += "-"*30 + "\n"
                
                self.audit_text.config(state=tk.NORMAL)
                self.audit_text.delete(1.0, tk.END)
                self.audit_text.insert(1.0, log_text)
                self.audit_text.config(state=tk.DISABLED)
            else:
                self.audit_text.config(state=tk.NORMAL)
                self.audit_text.delete(1.0, tk.END)
                self.audit_text.insert(1.0, "No audit log found")
                self.audit_text.config(state=tk.DISABLED)
                
        except Exception as e:
            logger.error(f"Failed to load audit log: {e}")
    
    def _refresh_audit_log(self):
        """Refresh audit log display."""
        self._load_audit_log()
    
    def _export_audit_log(self):
        """Export audit log to file."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                log_file = Path("logs/synapse-actions.json")
                if log_file.exists():
                    import shutil
                    shutil.copy(log_file, filename)
                    messagebox.showinfo("Success", f"Audit log exported to {filename}")
                else:
                    messagebox.showwarning("Warning", "No audit log to export")
                    
        except Exception as e:
            logger.error(f"Failed to export audit log: {e}")
            messagebox.showerror("Error", f"Failed to export audit log: {e}")
    
    def _clear_audit_log(self):
        """Clear audit log."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the audit log?"):
            try:
                log_file = Path("logs/synapse-actions.json")
                if log_file.exists():
                    log_file.unlink()
                    self._load_audit_log()
                    messagebox.showinfo("Success", "Audit log cleared")
            except Exception as e:
                logger.error(f"Failed to clear audit log: {e}")
                messagebox.showerror("Error", f"Failed to clear audit log: {e}")


class WebhookDialog:
    """Dialog for adding/editing webhooks."""
    
    def __init__(self, parent, webhook_manager):
        self.parent = parent
        self.webhook_manager = webhook_manager
        self.dialog = None
    
    def show(self):
        """Show the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add Webhook")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create form
        self._create_form()
    
    def _create_form(self):
        """Create the webhook form."""
        # Name
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # URL
        ttk.Label(self.dialog, text="URL:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.url_entry = ttk.Entry(self.dialog, width=40)
        self.url_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Method
        ttk.Label(self.dialog, text="Method:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.method_var = tk.StringVar(value="POST")
        method_combo = ttk.Combobox(self.dialog, textvariable=self.method_var, 
                                   values=["GET", "POST", "PUT", "DELETE"], state="readonly")
        method_combo.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Auth Type
        ttk.Label(self.dialog, text="Auth Type:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.auth_var = tk.StringVar(value="none")
        auth_combo = ttk.Combobox(self.dialog, textvariable=self.auth_var,
                                 values=["none", "api_key", "bearer_token", "basic_auth"], state="readonly")
        auth_combo.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self._save_webhook).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def _save_webhook(self):
        """Save webhook configuration."""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        method = self.method_var.get()
        auth_type = AuthType(self.auth_var.get())
        
        if not name or not url:
            messagebox.showwarning("Warning", "Name and URL are required")
            return
        
        try:
            webhook_id = self.webhook_manager.create_webhook(name, url, method, auth_type)
            messagebox.showinfo("Success", f"Webhook created: {webhook_id}")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create webhook: {e}")


class CredentialDialog:
    """Dialog for adding/editing credentials."""
    
    def __init__(self, parent, credential_manager):
        self.parent = parent
        self.credential_manager = credential_manager
        self.dialog = None
    
    def show(self):
        """Show the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add Credential")
        self.dialog.geometry("500x450")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create form
        self._create_form()
    
    def _create_form(self):
        """Create the credential form."""
        # Name
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Type
        ttk.Label(self.dialog, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.type_var = tk.StringVar(value="website_login")
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var,
                                 values=["website_login", "api_key", "ssh_key", "database", "custom"], state="readonly")
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Domain
        ttk.Label(self.dialog, text="Domain:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.domain_entry = ttk.Entry(self.dialog, width=40)
        self.domain_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Username
        ttk.Label(self.dialog, text="Username:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.username_entry = ttk.Entry(self.dialog, width=40)
        self.username_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Password
        ttk.Label(self.dialog, text="Password:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.password_entry = ttk.Entry(self.dialog, width=40, show="*")
        self.password_entry.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Notes
        ttk.Label(self.dialog, text="Notes:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.notes_text = tk.Text(self.dialog, height=3, width=30)
        self.notes_text.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self._save_credential).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def _save_credential(self):
        """Save credential configuration."""
        name = self.name_entry.get().strip()
        cred_type = CredentialType(self.type_var.get())
        domain = self.domain_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        if not name or not domain or not username or not password:
            messagebox.showwarning("Warning", "Name, domain, username, and password are required")
            return
        
        try:
            cred_id = self.credential_manager.add_credential(
                name, cred_type, domain, username, password, notes
            )
            messagebox.showinfo("Success", f"Credential created: {cred_id}")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create credential: {e}")


def create_security_dashboard(parent_frame):
    """Create security dashboard UI."""
    return SecurityDashboardUI(parent_frame) 