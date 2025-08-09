#!/usr/bin/env python3
"""
SPEC-3 Week 3: CLI Bug Reporting Tool
Implements `hl bug` command for terminal-based bug reporting
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List

def get_build_hash() -> str:
    """Get current build hash from git or fallback"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    # Fallback to timestamp-based hash
    timestamp = datetime.now().isoformat()
    import hashlib
    return hashlib.md5(timestamp.encode()).hexdigest()[:8]

def get_system_info() -> dict:
    """Gather system information for bug context"""
    import platform
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'architecture': platform.machine(),
        'hostname': platform.node(),
        'timestamp': datetime.now().isoformat()
    }

def validate_file_attachment(file_path: str) -> bool:
    """Validate file attachment"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    if not file_path.is_file():
        print(f"❌ Path is not a file: {file_path}")
        return False
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if file_path.stat().st_size > max_size:
        print(f"❌ File too large: {file_path} (max 10MB)")
        return False
    
    # Check file extension
    allowed_extensions = {'.txt', '.log', '.png', '.jpg', '.jpeg', '.pdf', '.json'}
    if file_path.suffix.lower() not in allowed_extensions:
        print(f"❌ Unsupported file type: {file_path.suffix}")
        print(f"   Allowed types: {', '.join(allowed_extensions)}")
        return False
    
    return True

def submit_bug_report(
    title: str,
    description: str,
    category: str = 'bug',
    attachments: Optional[List[str]] = None,
    api_url: str = 'http://localhost:8000'
) -> dict:
    """Submit bug report to API"""
    
    # Prepare form data
    form_data = {
        'title': title,
        'description': description,
        'category': category,
        'page_ctx': json.dumps({
            'context': 'CLI',
            'command': ' '.join(sys.argv),
            'system_info': get_system_info()
        }),
        'build_hash': get_build_hash(),
        'user_role': 'user'
    }
    
    # Prepare files
    files = []
    if attachments:
        for attachment_path in attachments:
            file_path = Path(attachment_path)
            if validate_file_attachment(attachment_path):
                files.append(('attachments', (file_path.name, open(file_path, 'rb'))))
    
    try:
        # Submit to API
        response = requests.post(
            f"{api_url}/api/bugs",
            data=form_data,
            files=files,
            timeout=30
        )
        
        # Close file handles
        for _, (_, file_handle) in files:
            file_handle.close()
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': "Could not connect to Hearthlink API. Is the application running?"
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': "Request timed out. Please try again."
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }

def interactive_bug_report():
    """Interactive bug report creation"""
    print("🐛 Hearthlink Bug Report Tool")
    print("=" * 40)
    
    # Category selection
    categories = {
        '1': ('bug', 'Bug Report - Something is broken'),
        '2': ('feature', 'Feature Request - Suggest improvement'),
        '3': ('UI', 'UI/UX Issue - Interface problem'),
        '4': ('performance', 'Performance Issue - Speed/efficiency')
    }
    
    print("\nSelect category:")
    for key, (value, description) in categories.items():
        print(f"  {key}. {description}")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        if choice in categories:
            category = categories[choice][0]
            break
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # Title input
    while True:
        title = input("\nBug title (max 200 chars): ").strip()
        if title and len(title) <= 200:
            break
        if not title:
            print("Title is required.")
        else:
            print("Title too long. Please keep it under 200 characters.")
    
    # Description input
    print("\nDescription (max 10,000 chars):")
    print("Enter your description. Press Ctrl+D or Ctrl+Z when done:")
    
    description_lines = []
    try:
        while True:
            line = input()
            description_lines.append(line)
    except EOFError:
        pass
    
    description = '\n'.join(description_lines).strip()
    
    if not description:
        print("Description is required.")
        return None
    
    if len(description) > 10000:
        print("Description too long. Please keep it under 10,000 characters.")
        return None
    
    # Attachments
    attachments = []
    while True:
        attachment = input("\nAttachment file path (press Enter to skip): ").strip()
        if not attachment:
            break
        
        if validate_file_attachment(attachment):
            attachments.append(attachment)
            print(f"✅ Added: {attachment}")
        
        if len(attachments) >= 5:  # Reasonable limit
            print("Maximum 5 attachments allowed.")
            break
    
    return {
        'title': title,
        'description': description,
        'category': category,
        'attachments': attachments
    }

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='hl bug',
        description='Hearthlink Bug Reporting CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hl bug --title "App crashes on startup" --desc "Detailed description"
  hl bug --title "Feature request" --desc "Description" --category feature
  hl bug --interactive
  hl bug --title "UI Issue" --desc "Button broken" --attach ./screenshot.png
        """
    )
    
    parser.add_argument(
        '--title',
        help='Bug report title (required unless --interactive)',
        type=str
    )
    
    parser.add_argument(
        '--desc', '--description',
        help='Bug report description (required unless --interactive)',
        type=str
    )
    
    parser.add_argument(
        '--category',
        help='Bug category',
        choices=['bug', 'feature', 'UI', 'performance'],
        default='bug'
    )
    
    parser.add_argument(
        '--attach', '--attachment',
        help='File to attach (can be used multiple times)',
        action='append',
        dest='attachments'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        help='Interactive mode for guided bug reporting',
        action='store_true'
    )
    
    parser.add_argument(
        '--api-url',
        help='Hearthlink API URL',
        default='http://localhost:8000'
    )
    
    parser.add_argument(
        '--dry-run',
        help='Show what would be submitted without actually submitting',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        bug_data = interactive_bug_report()
        if not bug_data:
            print("❌ Bug report creation cancelled.")
            return 1
    else:
        # Validate required arguments
        if not args.title or not args.desc:
            print("❌ Error: --title and --desc are required (or use --interactive)")
            parser.print_help()
            return 1
        
        bug_data = {
            'title': args.title,
            'description': args.desc,
            'category': args.category,
            'attachments': args.attachments or []
        }
    
    # Validate attachments
    valid_attachments = []
    if bug_data['attachments']:
        for attachment in bug_data['attachments']:
            if validate_file_attachment(attachment):
                valid_attachments.append(attachment)
    bug_data['attachments'] = valid_attachments
    
    # Show what will be submitted
    print("\n" + "=" * 50)
    print("📋 Bug Report Summary")
    print("=" * 50)
    print(f"Title: {bug_data['title']}")
    print(f"Category: {bug_data['category']}")
    print(f"Description: {bug_data['description'][:100]}{'...' if len(bug_data['description']) > 100 else ''}")
    print(f"Attachments: {len(bug_data['attachments'])} files")
    if bug_data['attachments']:
        for attachment in bug_data['attachments']:
            print(f"  - {attachment}")
    print(f"Build Hash: {get_build_hash()}")
    print("=" * 50)
    
    if args.dry_run:
        print("🔍 Dry run - would submit the above bug report")
        return 0
    
    # Confirm submission
    if args.interactive:
        confirm = input("\nSubmit this bug report? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Bug report submission cancelled.")
            return 1
    
    # Submit bug report
    print("\n📤 Submitting bug report...")
    result = submit_bug_report(
        title=bug_data['title'],
        description=bug_data['description'],
        category=bug_data['category'],
        attachments=bug_data['attachments'],
        api_url=args.api_url
    )
    
    if result['success']:
        data = result['data']
        print("✅ Bug report submitted successfully!")
        print(f"   Bug ID: {data['bug_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Timestamp: {data['timestamp']}")
        print(f"\n💡 Save this Bug ID for reference: {data['bug_id']}")
        return 0
    else:
        print(f"❌ Failed to submit bug report: {result['error']}")
        return 1

if __name__ == '__main__':
    sys.exit(main())