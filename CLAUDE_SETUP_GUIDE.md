# Claude Haiku Setup Guide

Complete instructions for setting up Claude Haiku 4.5 API integration.

---

## ⚡ Quick Start (2 Minutes)

### Step 1: Get API Key
1. Go to https://console.anthropic.com/
2. Sign in or create account
3. Click "API keys" in sidebar
4. Click "Create key"
5. Copy the key (starts with `sk-ant-v1-`)

### Step 2: Configure Locally
```bash
cp .env.local.example .env.local
# Edit .env.local and paste your API key
```

### Step 3: Test Setup
```bash
python setup_claude.py
```

Should show: ✅ Claude Haiku connection successful!

---

## 📋 Detailed Setup

### 1. Install Dependencies

```bash
# Install Anthropic SDK
pip install anthropic

# Verify installation
python -c "from anthropic import Anthropic; print('✓ anthropic installed')"
```

### 2. Get Anthropic API Key

**Go to:** https://console.anthropic.com/

**Steps:**
1. Click "Sign In" or "Sign Up"
2. Complete authentication
3. In the dashboard, find "API keys" section (left sidebar)
4. Click "Create new key"
5. Name it (e.g., "Drug Discovery Lab")
6. Copy the full key (format: `sk-ant-v1-...`)

**Important:** Keep this key secret! Don't commit to git.

### 3. Create `.env.local` File

```bash
# Copy template
cp .env.local.example .env.local

# Edit the file
nano .env.local
# or
vim .env.local
# or
open .env.local  # on macOS
```

**Add your key:**
```
ANTHROPIC_API_KEY=sk-ant-v1-YOUR_KEY_HERE
CLAUDE_MODEL=claude-haiku-4-5-20251001
CLAUDE_TIMEOUT=30
CLAUDE_DEBUG=false
```

### 4. Add `.env.local` to `.gitignore`

```bash
# Make sure .env.local is never committed
echo ".env.local" >> .gitignore
git rm --cached .env.local 2>/dev/null || true
```

### 5. Verify Setup

```bash
# Run setup verification script
python setup_claude.py
```

**Expected output:**
```
============================================================
🤖 CLAUDE HAIKU API SETUP
============================================================

Step 1️⃣  Loading environment configuration...
📂 Loading from .env.local...
   ✓ ANTHROPIC_API_KEY = sk-ant-v1-...
   ✓ CLAUDE_MODEL = claude-haiku-4-5-20251001

Step 2️⃣  Validating API key...
✅ API key configured

Step 3️⃣  Testing Claude connection...
🧪 Testing Claude Haiku connection...
✅ Claude Haiku connection successful!

🚀 SETUP COMPLETE!
```

---

## 🚀 Using Claude

### Option 1: Automatic (Recommended)
The agents automatically detect and use Claude when API key is set:

```bash
python run_discovery_loop.py
# Claude will be used automatically
```

### Option 2: Manual with .env.local
```python
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

from agents.hypothesis_agent import HypothesisAgent

agent = HypothesisAgent()
# Now uses Claude Haiku automatically
```

### Option 3: Direct Environment Setup
```bash
export ANTHROPIC_API_KEY='sk-ant-v1-...'
python run_discovery_loop.py
```

---

## 📊 What Uses Claude

When API key is set, these agents use Claude:

| Agent | Action | Speed | Quality |
|-------|--------|-------|---------|
| **Hypothesis** | Generates 5-7 testable hypotheses | 2-3s | Reasoning-based |
| **Experiment** | Designs rigorous experiments | 1-2s | Context-aware |
| **Analysis** | Ready to interpret results | - | Advanced stats |
| **Report** | Ready to generate papers | - | Academic writing |

---

## 🔧 Configuration Options

### `.env.local` Variables

```env
# REQUIRED: Your API key
ANTHROPIC_API_KEY=sk-ant-v1-...

# OPTIONAL: Which Claude model to use
# Options: claude-haiku-4-5-20251001 (default), claude-sonnet-5-5, claude-opus-5-5
CLAUDE_MODEL=claude-haiku-4-5-20251001

# OPTIONAL: Timeout for API requests (seconds)
CLAUDE_TIMEOUT=30

# OPTIONAL: Enable detailed logging
CLAUDE_DEBUG=false

# OPTIONAL: Max tokens per request
CLAUDE_MAX_TOKENS=2048
```

---

## ✅ Verification Checklist

- [ ] Installed `anthropic` package: `pip install anthropic`
- [ ] Got API key from https://console.anthropic.com/
- [ ] Created `.env.local` file
- [ ] Pasted API key into `.env.local`
- [ ] Added `.env.local` to `.gitignore`
- [ ] Ran `python setup_claude.py` successfully
- [ ] Saw "✅ Claude Haiku connection successful!"

---

## 🧪 Testing

### Test 1: Quick Test
```bash
python setup_claude.py
```
Should see: ✅ Claude Haiku connection successful!

### Test 2: Full Pipeline with Claude
```bash
python run_discovery_loop.py
```
Look for logs:
```
✓ Claude Haiku API initialized for hypothesis generation
✓ Using Claude Haiku for hypothesis generation
✓ Claude generated 5 hypotheses
✓ Using Claude Haiku for experiment design
✓ Claude designed experiment with budget: $25,353
```

### Test 3: Without Claude (Test Fallback)
```bash
# Remove or rename .env.local temporarily
mv .env.local .env.local.bak

# Run pipeline
python run_discovery_loop.py

# Should show:
# ⚠️ ANTHROPIC_API_KEY not set
# Using rule-based hypothesis generation

# Restore file
mv .env.local.bak .env.local
```

---

## 🛠️ Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
**Solution:**
```bash
# Check .env.local exists
ls -la .env.local

# Check it has the key
grep ANTHROPIC_API_KEY .env.local

# Verify it's exported
python -c "import os; print(os.environ.get('ANTHROPIC_API_KEY'))"
```

### Issue: "anthropic library not installed"
**Solution:**
```bash
pip install anthropic
pip show anthropic
```

### Issue: "401 Unauthorized"
**Possible causes:**
- Invalid API key (check format: should start with `sk-ant-v1-`)
- Expired key (regenerate from console)
- Key copied incorrectly (no extra spaces)

**Solution:**
1. Go to https://console.anthropic.com/
2. Delete the old key
3. Create a new key
4. Verify it starts with `sk-ant-v1-`
5. Update `.env.local` with new key
6. Run `python setup_claude.py` again

### Issue: "Rate limit exceeded"
**Causes:**
- Too many requests too quickly
- Using shared/limited API plan

**Solutions:**
- Wait a few minutes before retrying
- Upgrade API plan at https://console.anthropic.com/
- Use smaller `CLAUDE_MAX_TOKENS` value

### Issue: "Connection timeout"
**Causes:**
- Internet connection issues
- API server down
- Firewall blocking connection

**Solutions:**
- Check internet connection: `ping google.com`
- Check API status: https://status.anthropic.com/
- Check firewall settings
- Increase `CLAUDE_TIMEOUT` in `.env.local`

---

## 📚 Resources

| Resource | Link |
|----------|------|
| **Anthropic Console** | https://console.anthropic.com/ |
| **API Documentation** | https://docs.anthropic.com/ |
| **Claude Models** | https://docs.anthropic.com/claude/reference/getting-started-with-the-api |
| **Pricing** | https://www.anthropic.com/pricing |
| **Status Page** | https://status.anthropic.com/ |

---

## 💰 Pricing (Claude Haiku)

**Why Claude Haiku?**
- ✅ Fastest Claude model
- ✅ Most affordable
- ✅ Perfect for structured tasks
- ✅ 200K context window

**Approximate Costs:**
- Hypothesis generation: ~$0.01 per request
- Experiment design: ~$0.015 per request
- Full pipeline: ~$0.10 per run

(Exact pricing depends on API plan)

---

## 🚀 Next Steps

After setup, you can:

1. **Run full pipeline with Claude:**
   ```bash
   python run_discovery_loop.py
   ```

2. **Test drug discovery examples:**
   ```bash
   python agents/literature_agent/examples_drug_discovery.py
   ```

3. **Test APIs:**
   ```bash
   python test_biomedical_apis.py
   ```

4. **Use in your research:**
   ```python
   from agents.hypothesis_agent import HypothesisAgent
   
   agent = HypothesisAgent()
   hypotheses = await agent.generate_hypotheses(...)
   ```

---

## 🔐 Security Notes

- **Never** commit `.env.local` to git
- **Never** share your API key
- API key in `.gitignore` prevents accidental commits
- Consider rotating keys periodically
- Use separate keys for development/production

---

## 📞 Support

- **Setup issues?** Check TROUBLESHOOTING section above
- **API issues?** Visit https://console.anthropic.com/account/usage
- **Documentation?** See CLAUDE_API_INTEGRATION.md
- **Code issues?** Check agent-specific documentation

---

**Ready to use Claude Haiku?** 🚀

Run: `python setup_claude.py`

