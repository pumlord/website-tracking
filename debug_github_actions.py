#!/usr/bin/env python3
"""
GitHub Actions debugging helper
"""

import json
import os
import sys
from datetime import datetime

def check_github_actions_setup():
    """Check if GitHub Actions is set up correctly."""
    print("🤖 GitHub Actions Setup Check")
    print("="*40)
    
    issues = []
    
    # Check workflow file
    workflow_path = '.github/workflows/website-tracker.yml'
    if os.path.exists(workflow_path):
        print("✅ Workflow file exists")
        
        with open(workflow_path, 'r') as f:
            content = f.read()
            
        # Check for key components
        if '--heartbeat' in content:
            print("✅ Heartbeat flag found in workflow")
        else:
            print("❌ Heartbeat flag missing from workflow")
            issues.append("Add --heartbeat flag to workflow")
            
        if 'DISCORD_WEBHOOK_URL' in content:
            print("✅ Discord webhook secret referenced in workflow")
        else:
            print("❌ Discord webhook secret not referenced")
            issues.append("Add DISCORD_WEBHOOK_URL secret reference")
            
    else:
        print("❌ Workflow file missing")
        issues.append("Create .github/workflows/website-tracker.yml")
    
    # Check template config
    if os.path.exists('config.template.json'):
        print("✅ Template config exists")
        
        with open('config.template.json', 'r') as f:
            template = json.load(f)
            
        if template['notification']['discord_webhook_url'] == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            print("✅ Template has placeholder webhook URL")
        else:
            print("⚠️ Template webhook URL is not placeholder")
            
    else:
        print("❌ Template config missing")
        issues.append("Create config.template.json")
    
    # Check gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
            
        if 'config.json' in gitignore:
            print("✅ config.json is in .gitignore (good for security)")
        else:
            print("⚠️ config.json not in .gitignore (potential security risk)")
            
    return issues

def generate_github_actions_debug_info():
    """Generate debug information for GitHub Actions."""
    print("\n🔍 GitHub Actions Debug Information")
    print("="*40)
    
    print("Repository Setup Checklist:")
    print("1. ✅ Repository created at github.com/pumlord/website-tracking")
    print("2. ❓ DISCORD_WEBHOOK_URL secret added to repository")
    print("3. ❓ GitHub Actions enabled")
    print("4. ❓ Workflow permissions set to 'Read and write permissions'")
    
    print("\nTo check these in GitHub:")
    print("• Go to your repository on GitHub")
    print("• Settings → Secrets and variables → Actions")
    print("• Verify DISCORD_WEBHOOK_URL secret exists")
    print("• Settings → Actions → General")
    print("• Verify 'Read and write permissions' is selected")
    
    print("\nTo check workflow runs:")
    print("• Go to Actions tab in your repository")
    print("• Look for 'Website Tracker' workflows")
    print("• Click on latest run to see logs")
    print("• Look for 'Discord heartbeat notification sent' in logs")

def create_manual_test_workflow():
    """Create a simple test workflow for manual debugging."""
    print("\n🧪 Creating Manual Test Workflow")
    print("="*40)
    
    test_workflow = """name: Test Website Tracker

on:
  workflow_dispatch: # Manual trigger only

jobs:
  test-tracker:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create config from template
      run: |
        cp config.template.json config.json
        python3 << 'EOF'
        import json
        import os
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['notification']['discord_webhook_url'] = os.environ['DISCORD_WEBHOOK_URL']
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        EOF
      env:
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
    
    - name: Debug config
      run: |
        echo "Config file contents (webhook URL hidden):"
        python3 << 'EOF'
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['notification']['discord_webhook_url'] = '[HIDDEN]'
        print(json.dumps(config, indent=2))
        EOF
    
    - name: Test Discord notification
      run: |
        python main.py --test-notification
    
    - name: Run single check with heartbeat
      run: |
        python main.py --check --heartbeat
"""
    
    os.makedirs('.github/workflows', exist_ok=True)
    
    with open('.github/workflows/test-tracker.yml', 'w') as f:
        f.write(test_workflow)
    
    print("✅ Created test workflow: .github/workflows/test-tracker.yml")
    print("📋 This workflow can be triggered manually from GitHub Actions tab")
    print("🔧 Use this to debug issues before fixing the main workflow")

def main():
    """Main debugging function."""
    print("🔧 GitHub Actions Debugging Tool")
    print("="*50)
    
    # Check current setup
    issues = check_github_actions_setup()
    
    if issues:
        print(f"\n⚠️ Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ Local setup looks good!")
    
    # Generate debug info
    generate_github_actions_debug_info()
    
    # Create test workflow
    create_manual_test_workflow()
    
    print("\n🎯 Next Steps:")
    print("1. Run local tests: python test_full_system.py")
    print("2. Commit and push the test workflow")
    print("3. Go to GitHub Actions tab and run 'Test Website Tracker' manually")
    print("4. Check the logs for any errors")
    print("5. Verify DISCORD_WEBHOOK_URL secret is set correctly")

if __name__ == "__main__":
    main()
