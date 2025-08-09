"""
MCP Plugin Executor
Implements actual Model Context Protocol plugin execution
"""

import os
import json
import subprocess
import tempfile
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPExecutor:
    """Executes MCP plugins with real functionality"""
    
    def __init__(self, base_path: str = "/mnt/g/mythologiq/hearthlink"):
        self.base_path = Path(base_path)
        self.allowed_paths = [
            self.base_path,
            Path("/tmp/hearthlink"),
            Path("./workspace"),
            Path("./outputs")
        ]
        
    def execute_filesystem_mcp(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filesystem MCP operations"""
        try:
            if tool == "list_directory":
                return self._list_directory(parameters.get("path", "."))
            elif tool == "read_file":
                return self._read_file(parameters.get("path"))
            elif tool == "write_file":
                return self._write_file(parameters.get("path"), parameters.get("content", ""))
            elif tool == "create_directory":
                return self._create_directory(parameters.get("path"))
            elif tool == "get_file_info":
                return self._get_file_info(parameters.get("path"))
            elif tool == "search_files":
                return self._search_files(parameters.get("path", "."), parameters.get("pattern", "*"))
            elif tool == "list_allowed_directories":
                return self._list_allowed_directories()
            else:
                return {"success": False, "error": f"Unknown filesystem tool: {tool}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_github_mcp(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub MCP operations (requires GitHub token)"""
        try:
            # Check for GitHub token
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                return {"success": False, "error": "GitHub token not configured. Set GITHUB_TOKEN environment variable."}
            
            if tool == "search_repositories":
                return self._search_github_repos(parameters.get("query", ""))
            elif tool == "get_file_contents":
                return self._get_github_file(
                    parameters.get("owner"), 
                    parameters.get("repo"), 
                    parameters.get("path"),
                    parameters.get("branch", "main")
                )
            elif tool == "create_issue":
                return self._create_github_issue(
                    parameters.get("owner"),
                    parameters.get("repo"),
                    parameters.get("title"),
                    parameters.get("body")
                )
            elif tool == "list_issues":
                return self._list_github_issues(
                    parameters.get("owner"),
                    parameters.get("repo"),
                    parameters.get("state", "open")
                )
            elif tool == "get_repository":
                return self._get_github_repository(
                    parameters.get("owner"),
                    parameters.get("repo")
                )
            elif tool == "list_commits":
                return self._list_github_commits(
                    parameters.get("owner"),
                    parameters.get("repo"),
                    parameters.get("sha", "main")
                )
            else:
                return {"success": False, "error": f"GitHub tool '{tool}' not implemented yet"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_gmail_calendar_mcp(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail/Calendar MCP operations (requires OAuth)"""
        try:
            # Check for Google OAuth credentials
            google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
            google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            if not google_client_id or not google_client_secret:
                return {
                    "success": False, 
                    "error": "Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
                }
            
            if tool == "list_emails":
                return self._list_gmail_emails(parameters.get("query", ""), parameters.get("max_results", 10))
            elif tool == "send_email":
                return self._send_gmail_email(
                    parameters.get("to"),
                    parameters.get("subject"),
                    parameters.get("body"),
                    parameters.get("attachments", [])
                )
            elif tool == "search_emails":
                return self._search_gmail_emails(
                    parameters.get("query", ""),
                    parameters.get("labels", []),
                    parameters.get("date_range", {})
                )
            elif tool == "list_calendar_events":
                return self._list_calendar_events(
                    parameters.get("calendar_id", "primary"),
                    parameters.get("time_min"),
                    parameters.get("time_max"),
                    parameters.get("max_results", 10)
                )
            elif tool == "create_calendar_event":
                return self._create_calendar_event(
                    parameters.get("calendar_id", "primary"),
                    parameters.get("summary"),
                    parameters.get("start"),
                    parameters.get("end"),
                    parameters.get("description", ""),
                    parameters.get("attendees", [])
                )
            elif tool == "update_calendar_event":
                return self._update_calendar_event(
                    parameters.get("calendar_id", "primary"),
                    parameters.get("event_id"),
                    parameters.get("updates", {})
                )
            elif tool == "delete_calendar_event":
                return self._delete_calendar_event(
                    parameters.get("calendar_id", "primary"),
                    parameters.get("event_id")
                )
            else:
                return {"success": False, "error": f"Unknown Gmail/Calendar tool: {tool}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Filesystem operations implementation
    def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path does not exist: {path}"}
            
            if not target_path.is_dir():
                return {"success": False, "error": f"Path is not a directory: {path}"}
            
            items = []
            for item in target_path.iterdir():
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": stat.st_mtime
                    })
                except OSError:
                    # Skip items we can't access
                    continue
                    
            return {
                "success": True,
                "path": str(target_path.absolute()),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Directory listing failed: {str(e)}"}
    
    def _read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            if not target_path.exists():
                return {"success": False, "error": f"File does not exist: {path}"}
            
            if not target_path.is_file():
                return {"success": False, "error": f"Path is not a file: {path}"}
            
            # Check file size (limit to 1MB)
            if target_path.stat().st_size > 1024 * 1024:
                return {"success": False, "error": "File too large (max 1MB)"}
            
            content = target_path.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "path": str(target_path.absolute()),
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
            
        except UnicodeDecodeError:
            return {"success": False, "error": "File is not valid UTF-8 text"}
        except Exception as e:
            return {"success": False, "error": f"File read failed: {str(e)}"}
    
    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write file contents"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            target_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "path": str(target_path.absolute()),
                "size": len(content),
                "lines": content.count('\n') + 1
            }
            
        except Exception as e:
            return {"success": False, "error": f"File write failed: {str(e)}"}
    
    def _create_directory(self, path: str) -> Dict[str, Any]:
        """Create directory"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            target_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "path": str(target_path.absolute()),
                "created": not target_path.existed()
            }
            
        except Exception as e:
            return {"success": False, "error": f"Directory creation failed: {str(e)}"}
    
    def _get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path does not exist: {path}"}
            
            stat = target_path.stat()
            
            return {
                "success": True,
                "path": str(target_path.absolute()),
                "name": target_path.name,
                "type": "directory" if target_path.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:],
                "exists": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"File info failed: {str(e)}"}
    
    def _search_files(self, path: str, pattern: str) -> Dict[str, Any]:
        """Search for files matching pattern"""
        try:
            target_path = Path(path)
            if not self._is_path_allowed(target_path):
                return {"success": False, "error": f"Access denied to path: {path}"}
            
            if not target_path.exists():
                return {"success": False, "error": f"Path does not exist: {path}"}
            
            matches = []
            if target_path.is_dir():
                for item in target_path.rglob(pattern):
                    if self._is_path_allowed(item):
                        try:
                            stat = item.stat()
                            matches.append({
                                "path": str(item.relative_to(target_path)),
                                "absolute_path": str(item.absolute()),
                                "type": "directory" if item.is_dir() else "file",
                                "size": stat.st_size if item.is_file() else None
                            })
                        except OSError:
                            continue
            
            return {
                "success": True,
                "search_path": str(target_path.absolute()),
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {"success": False, "error": f"File search failed: {str(e)}"}
    
    def _list_allowed_directories(self) -> Dict[str, Any]:
        """List allowed directories for the filesystem plugin"""
        allowed = []
        for path in self.allowed_paths:
            allowed.append({
                "path": str(path.absolute()),
                "exists": path.exists(),
                "readable": path.exists() and os.access(path, os.R_OK),
                "writable": path.exists() and os.access(path, os.W_OK)
            })
        
        return {
            "success": True,
            "allowed_directories": allowed,
            "count": len(allowed)
        }
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        try:
            path_abs = path.resolve()
            for allowed_path in self.allowed_paths:
                try:
                    allowed_abs = allowed_path.resolve()
                    # Check if path is within allowed directory
                    path_abs.relative_to(allowed_abs)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False
    
    # GitHub operations implementation
    def _search_github_repos(self, query: str) -> Dict[str, Any]:
        """Search GitHub repositories"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/search/repositories'
            params = {'q': query, 'per_page': 10}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            repositories = []
            for repo in data.get('items', []):
                repositories.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'url': repo['html_url'],
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', ''),
                    'updated_at': repo['updated_at']
                })
            
            return {
                "success": True,
                "query": query,
                "total_count": data.get('total_count', 0),
                "repositories": repositories,
                "count": len(repositories)
            }
            
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub search failed: {str(e)}"}
    
    def _get_github_file(self, owner: str, repo: str, path: str, branch: str = "main") -> Dict[str, Any]:
        """Get file from GitHub repository"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            params = {'ref': branch}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('type') == 'file':
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
                
                return {
                    "success": True,
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "branch": branch,
                    "content": content,
                    "size": data['size'],
                    "sha": data['sha'],
                    "url": data['html_url']
                }
            else:
                return {"success": False, "error": f"Path is not a file: {path}"}
                
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub file access failed: {str(e)}"}
    
    def _create_github_issue(self, owner: str, repo: str, title: str, body: str) -> Dict[str, Any]:
        """Create GitHub issue"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/issues'
            data = {
                'title': title,
                'body': body
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            issue_data = response.json()
            
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "issue_number": issue_data['number'],
                "title": issue_data['title'],
                "body": issue_data['body'],
                "state": issue_data['state'],
                "url": issue_data['html_url'],
                "created_at": issue_data['created_at']
            }
            
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub issue creation failed: {str(e)}"}
    
    def _list_github_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List GitHub repository issues"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/issues'
            params = {'state': state, 'per_page': 20}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            issues_data = response.json()
            
            issues = []
            for issue in issues_data:
                issues.append({
                    'number': issue['number'],
                    'title': issue['title'],
                    'state': issue['state'],
                    'body': issue.get('body', '')[:200] + '...' if issue.get('body') else '',
                    'url': issue['html_url'],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'user': issue['user']['login']
                })
            
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "state": state,
                "issues": issues,
                "count": len(issues)
            }
            
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub issues listing failed: {str(e)}"}
    
    def _get_github_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get GitHub repository information"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            repo_data = response.json()
            
            return {
                "success": True,
                "name": repo_data['name'],
                "full_name": repo_data['full_name'],
                "description": repo_data.get('description', ''),
                "url": repo_data['html_url'],
                "clone_url": repo_data['clone_url'],
                "ssh_url": repo_data['ssh_url'],
                "default_branch": repo_data['default_branch'],
                "language": repo_data.get('language', ''),
                "stars": repo_data['stargazers_count'],
                "forks": repo_data['forks_count'],
                "open_issues": repo_data['open_issues_count'],
                "size": repo_data['size'],
                "private": repo_data['private'],
                "created_at": repo_data['created_at'],
                "updated_at": repo_data['updated_at'],
                "pushed_at": repo_data['pushed_at']
            }
            
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub repository access failed: {str(e)}"}
    
    def _list_github_commits(self, owner: str, repo: str, sha: str = "main") -> Dict[str, Any]:
        """List GitHub repository commits"""
        try:
            import requests
            
            headers = {
                'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/commits'
            params = {'sha': sha, 'per_page': 10}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            commits_data = response.json()
            
            commits = []
            for commit in commits_data:
                commits.append({
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date'],
                    'url': commit['html_url']
                })
            
            return {
                "success": True,
                "owner": owner,
                "repo": repo,
                "branch": sha,
                "commits": commits,
                "count": len(commits)
            }
            
        except ImportError:
            return {"success": False, "error": "requests library not available"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"GitHub commits listing failed: {str(e)}"}

    # Gmail/Calendar operations implementation
    def _list_gmail_emails(self, query: str = "", max_results: int = 10) -> Dict[str, Any]:
        """List Gmail emails (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Gmail integration requires OAuth 2.0 setup",
            "setup_required": {
                "step_1": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables",
                "step_2": "Configure OAuth consent screen in Google Cloud Console",
                "step_3": "Install Google API client: pip install google-auth google-auth-oauthlib google-api-python-client",
                "step_4": "Implement OAuth flow for user authentication",
                "scopes_needed": [
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/gmail.modify"
                ]
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
                ]
            }
        }
    
    def _send_gmail_email(self, to: str, subject: str, body: str, attachments: list = None) -> Dict[str, Any]:
        """Send Gmail email (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Gmail sending requires OAuth 2.0 authentication",
            "setup_required": {
                "oauth_flow": "User must authenticate with Google",
                "scopes": ["https://www.googleapis.com/auth/gmail.send"],
                "api_setup": "Google API client library required"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
        }
    
    def _search_gmail_emails(self, query: str, labels: list = None, date_range: dict = None) -> Dict[str, Any]:
        """Search Gmail emails with filters (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Gmail search requires full OAuth integration",
            "setup_required": {
                "authentication": "Google OAuth 2.0 flow",
                "credentials": "Stored user authentication tokens",
                "api_client": "Gmail API service object"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
                ]
            }
        }
    
    def _list_calendar_events(self, calendar_id: str = "primary", time_min: str = None, 
                            time_max: str = None, max_results: int = 10) -> Dict[str, Any]:
        """List Google Calendar events (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Calendar access requires Google OAuth 2.0 authentication",
            "setup_required": {
                "oauth_scopes": [
                    "https://www.googleapis.com/auth/calendar.readonly",
                    "https://www.googleapis.com/auth/calendar.events.readonly"
                ],
                "api_setup": "Google Calendar API client required",
                "user_consent": "User must authorize calendar access"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
                ]
            }
        }
    
    def _create_calendar_event(self, calendar_id: str, summary: str, start: str, 
                             end: str, description: str = "", attendees: list = None) -> Dict[str, Any]:
        """Create Google Calendar event (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Calendar event creation requires authenticated Google API access",
            "setup_required": {
                "authentication": "User OAuth 2.0 consent",
                "scopes": ["https://www.googleapis.com/auth/calendar.events"],
                "api_integration": "Google Calendar API service"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
        }
    
    def _update_calendar_event(self, calendar_id: str, event_id: str, updates: dict) -> Dict[str, Any]:
        """Update Google Calendar event (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Calendar event updates require Google API authentication",
            "setup_required": {
                "oauth_flow": "Complete user authentication",
                "permissions": "Calendar modification permissions",
                "api_client": "Authenticated Calendar service object"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
        }
    
    def _delete_calendar_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Delete Google Calendar event (requires OAuth setup)"""
        return {
            "success": False,
            "error": "Calendar event deletion requires authenticated API access",
            "setup_required": {
                "user_auth": "Google OAuth 2.0 authentication",
                "api_access": "Calendar API with delete permissions",
                "event_verification": "Confirm event exists and user has permission"
            },
            # Simulation removed - implement proper error handling
            raise NotImplementedError("This feature requires proper implementation")
        }