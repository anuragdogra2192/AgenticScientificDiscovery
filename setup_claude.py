#!/usr/bin/env python3
"""
Setup script for Claude Haiku API integration.

This script:
1. Loads environment variables from .env.local
2. Validates the API key
3. Tests Claude connection
4. Provides setup instructions
"""

import os
import sys
from pathlib import Path


def load_env_local():
    """Load environment variables from .env.local"""
    env_file = Path(".env.local")

    if env_file.exists():
        print(f"📂 Loading from .env.local...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
                        if "KEY" in key:
                            print(f"   ✓ {key.strip()} = {value.strip()[:20]}...")
                        else:
                            print(f"   ✓ {key.strip()} = {value.strip()}")
    else:
        print("⚠️  .env.local not found")
        print("   Please copy .env.local.example to .env.local and fill in your API key")
        return False

    return True


def validate_api_key():
    """Validate that API key is set"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("\nSetup steps:")
        print("1. Copy .env.local.example to .env.local")
        print("   $ cp .env.local.example .env.local")
        print("\n2. Get your API key from: https://console.anthropic.com/")
        print("\n3. Edit .env.local and add your key:")
        print("   ANTHROPIC_API_KEY=sk-ant-v1-...")
        print("\n4. Run this script again:")
        print("   $ python setup_claude.py")
        return False

    if not api_key.startswith("sk-"):
        print("⚠️  API key format looks unusual (should start with 'sk-')")
        print(f"   Got: {api_key[:20]}...")

    return True


def test_claude_connection():
    """Test connection to Claude API"""
    print("\n🧪 Testing Claude Haiku connection...")

    try:
        from anthropic import Anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=api_key)

        # Simple test message
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Claude is ready' and nothing else."}
            ]
        )

        result = response.content[0].text.strip()

        if "Claude is ready" in result or "ready" in result.lower():
            print("✅ Claude Haiku connection successful!")
            print(f"   Response: {result}")
            return True
        else:
            print(f"⚠️  Unexpected response: {result}")
            return True  # Still counts as working

    except ImportError:
        print("❌ anthropic library not installed")
        print("   Install with: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- No internet connection")
        print("- API rate limit exceeded")
        print("- Account quota exceeded")
        return False


def show_next_steps():
    """Show what to do next"""
    print("\n" + "="*60)
    print("🚀 SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now run:")
    print("  • python run_discovery_loop.py")
    print("    (full drug discovery pipeline with Claude)")
    print("\n  • python agents/literature_agent/examples_drug_discovery.py")
    print("    (test literature search)")
    print("\n  • python test_biomedical_apis.py")
    print("    (test biomedical APIs)")
    print("\nClaude will be used automatically for:")
    print("  ✓ Hypothesis generation")
    print("  ✓ Experiment design")
    print("  ✓ Result analysis (ready to implement)")
    print("  ✓ Report generation (ready to implement)")
    print("\nOr run without Claude API key for rule-based logic.")
    print("="*60 + "\n")


def main():
    """Main setup flow"""
    print("\n" + "="*60)
    print("🤖 CLAUDE HAIKU API SETUP")
    print("="*60 + "\n")

    # Step 1: Load .env.local
    print("Step 1️⃣  Loading environment configuration...")
    if not load_env_local():
        return False

    # Step 2: Validate API key
    print("\nStep 2️⃣  Validating API key...")
    if not validate_api_key():
        return False

    print("✅ API key configured")

    # Step 3: Test connection
    print("\nStep 3️⃣  Testing Claude connection...")
    if not test_claude_connection():
        print("\n⚠️  Connection test failed, but setup is complete.")
        print("   Check your API key and try again.")
        return False

    # All good!
    show_next_steps()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
