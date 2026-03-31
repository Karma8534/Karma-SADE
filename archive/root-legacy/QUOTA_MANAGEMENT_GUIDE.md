# Karma SADE - Quota Management System

## 📊 Overview

Your $15 Claude API credit is now **managed and protected** with a comprehensive quota system that tracks usage across ALL paid APIs!

### Budget Allocation (2-Week Maximization)

**Total Budget**: $15 for Claude over 14 days = **$1.07/day**

**Daily Quota Limits**:
- **Claude**: 71 queries/day (max budget: $15/14 days ÷ $0.015/query)
- **OpenAI**: 150 queries/day
- **GLM-5**: 250 queries/day (cheapest paid option)
- **Perplexity**: 100 queries/day (research specialist)

### Strategy:
✅ **95% FREE** - Ollama + GLM-4-Flash + Gemini handle most queries
✅ **4% CHEAP** - GLM-5 ($0.004) and Perplexity ($0.001) for complex tasks
✅ **1% PREMIUM** - Claude ($0.015) ONLY for critical architecture/design

---

## 🎯 7-Tier Smart Routing

### Tier 1: Ollama (FREE)
- **Cost**: $0.00
- **Quota**: Unlimited
- **When**: Simple/medium tasks, code generation
- **Models**: llama3.1, deepseek-coder:6.7b

### Tier 2: Z.ai GLM-4-Flash (FREE)
- **Cost**: $0.00
- **Quota**: Unlimited
- **When**: Cloud backup when Ollama fails
- **Best for**: Fast inference, simple code

### Tier 3: Gemini (FREE)
- **Cost**: $0.00
- **Quota**: 1,500 requests/day
- **When**: Research, Google integration
- **Best for**: General queries, explanations

### Tier 4: Z.ai GLM-5 (PAID - Cheapest)
- **Cost**: ~$0.004/query
- **Quota**: 250 queries/day
- **When**: Complex code, architecture
- **Best for**: Code generation, reasoning
- **Triggers**: "complex", "design", "refactor", "integrate"

### Tier 5: OpenAI (PAID)
- **Cost**: ~$0.0025/query (gpt-4o-mini)
- **Quota**: 150 queries/day
- **When**: Complex tasks if GLM-5 fails
- **Best for**: General complex reasoning

### Tier 6: Perplexity (PAID - Research)
- **Cost**: ~$0.001/query
- **Quota**: 100 queries/day
- **When**: Research queries, web search needed
- **Triggers**: "research", "compare", "analyze"

### Tier 7: Claude (PREMIUM - Save for Critical!)
- **Cost**: ~$0.015/query
- **Quota**: **71 queries/day** ($15/14 days)
- **When**: ONLY premium tasks!
- **Best for**: Architecture, system design, deep analysis
- **Triggers**: "architect", "design system", "evaluate approach", "deep analysis"

---

## 🔐 Quota Protection Features

### 1. **Daily Limits**
- Automatic blocking when daily quota reached
- Logs quota exhaustion events
- Prevents overspending

### 2. **Monthly Limits**
- Tracks cumulative monthly usage
- Prevents unexpected monthly overages
- Safety net for daily limit bypasses

### 3. **Warning Thresholds**
- Warns at 80% of daily quota
- Helps you track usage before limits hit
- Logged warnings for review

### 4. **Cost Tracking**
- Tracks actual token usage (Claude, OpenAI)
- Estimates costs for Z.ai and Perplexity
- Real-time cost accumulation

### 5. **SQLite Persistence**
- All usage stored in database
- Survives backend restarts
- Historical tracking for analysis

---

## 📈 Checking Your Quota Usage

### Option 1: API Endpoints

#### Get Stats (JSON):
```bash
curl http://localhost:9401/api/quota/stats
```

Returns detailed stats for all APIs:
```json
{
  "claude": {
    "daily": {
      "count": 15,
      "cost": 0.225,
      "limit": 71,
      "remaining": 56,
      "percent_used": 21.1
    },
    "monthly": {
      "count": 234,
      "cost": 3.51,
      "limit": 1000,
      "remaining": 766,
      "percent_used": 23.4
    }
  }
}
```

#### Get Report (Formatted):
```bash
curl http://localhost:9401/api/quota/report
```

Returns formatted text report + stats.

### Option 2: Python Script

```python
from karma_quota_manager import quota_manager

# Print report
print(quota_manager.get_usage_report())

# Check specific API
can_use, reason = quota_manager.check_quota("claude")
print(f"Claude available: {can_use} - {reason}")

# Get stats
stats = quota_manager.get_all_usage_stats()
print(f"Claude used today: {stats['claude']['daily']['count']}/71")
```

### Option 3: Backend Logs

Check the logs on startup and after each paid query:

```bash
tail -f C:\Users\raest\Documents\Karma_SADE\Logs\karma-backend.log
```

Look for:
```
[QUOTA] Today's usage: Claude=15/71, OpenAI=23/150, GLM-5=45/250, Perplexity=12/100
[QUOTA] claude: $0.0152 | Today: 16 queries
```

---

## ⚙️ Adjusting Quota Limits

### Update via API:

```bash
# Increase Claude daily limit to 100
curl -X POST "http://localhost:9401/api/quota/update?api_name=claude&daily_limit=100"

# Decrease OpenAI monthly limit
curl -X POST "http://localhost:9401/api/quota/update?api_name=openai&monthly_limit=2000"
```

### Update via Python:

```python
from karma_quota_manager import quota_manager

# Update daily limit
quota_manager.update_quota("claude", daily_limit=100)

# Update monthly limit
quota_manager.update_quota("openai", monthly_limit=2000)

# Disable an API completely
quota_manager.disable_api("perplexity")

# Re-enable an API
quota_manager.enable_api("perplexity")
```

---

## 💡 Usage Tips

### Maximize Your $15 Claude Budget:

1. **Use Premium Keywords Strategically**
   - "architect" → triggers Claude
   - "design" → triggers GLM-5 (cheaper!)
   - "design system" → triggers Claude

2. **Rephrase for Cheaper APIs**
   - ❌ "Architect a microservices system" → Claude ($0.015)
   - ✅ "Design a microservices system" → GLM-5 ($0.004)

3. **Let FREE Tiers Handle Most Work**
   - Simple queries → Ollama/GLM-4-Flash (FREE)
   - Medium complexity → Gemini (FREE)
   - Complex code → GLM-5 ($0.004)
   - Architecture → Claude ($0.015)

4. **Check Quota Before Big Sessions**
   ```bash
   curl http://localhost:9401/api/quota/stats | jq
   ```

5. **Monitor Daily Usage**
   - 71 queries/day = ~3 queries/hour
   - Save Claude for critical decisions
   - Use GLM-5 for complex code (4x cheaper!)

---

## 📊 Expected Usage Patterns

### Optimal Budget Spread (2 weeks):

**Week 1**:
- Day 1-3: Learning period, ~20 Claude queries/day
- Day 4-7: Optimization, ~50 Claude queries/day

**Week 2**:
- Day 8-11: Heavy usage, ~70 Claude queries/day
- Day 12-14: Final sprint, ~71 Claude queries/day (max budget)

**Total**: ~700-800 Claude queries over 14 days = ~$10.50-$12.00

**Buffer**: $2.50-$4.50 for contingency

### Cost Breakdown (Daily):

**FREE (95% of queries)**:
- Ollama: 50 queries → $0.00
- GLM-4-Flash: 30 queries → $0.00
- Gemini: 15 queries → $0.00

**CHEAP (4% of queries)**:
- GLM-5: 5 queries → $0.02
- Perplexity: 2 queries → $0.002

**PREMIUM (1% of queries)**:
- Claude: 1-2 queries → $0.015-$0.030

**Daily Total**: ~$0.04-$0.05 (without Claude overuse)

---

## 🚨 Quota Warnings

### You'll see warnings in logs when:

1. **Approaching Daily Limit** (80% threshold):
   ```
   [ROUTE] Using Claude (PAID - QUOTA: 56/71 queries today)
   ```

2. **Daily Limit Exceeded**:
   ```
   [QUOTA] Claude blocked: Daily limit exceeded (71/71)
   [ROUTE] Claude quota exceeded, trying fallback...
   ```

3. **Monthly Limit Approaching**:
   ```
   [QUOTA] WARNING: Claude monthly usage at 850/1000
   ```

### Fallback Behavior:

When Claude quota exceeded:
1. Try OpenAI gpt-4o (if quota available)
2. Try GLM-5 (if quota available)
3. Return quota error if all exhausted

---

## 📁 Database Location

**Quota Database**: `C:\Users\raest\Documents\Karma_SADE\Data\karma_quotas.db`

### Tables:
- `api_usage` - Every API call logged with cost, tokens, timestamp
- `quota_config` - Quota limits per API
- `daily_stats` - Cached daily statistics

### Backup Your Data:

```bash
# Backup quota database
cp Data/karma_quotas.db Data/karma_quotas_backup_$(date +%Y%m%d).db

# View raw data (SQLite)
sqlite3 Data/karma_quotas.db "SELECT * FROM api_usage WHERE api_name='claude' ORDER BY timestamp DESC LIMIT 10"
```

---

## 🎉 Success Indicators

You'll know the quota system is working when you see:

✅ **On Startup**:
```
[OK] Claude available (PAID - QUOTA: 71/day, premium tier)
[QUOTA] Paid API quota management enabled
[QUOTA] Today's usage: Claude=0/71, OpenAI=0/150, GLM-5=0/250, Perplexity=0/100
```

✅ **During Usage**:
```
[ROUTE] PREMIUM TASK - Using Claude (quota: 71/day, $15 budget)
[OK] Claude response - tokens: 1234, cost: $0.0152
[QUOTA] claude: $0.0152 | Today: 1 queries
```

✅ **Quota Protection**:
```
[QUOTA] Claude blocked: Daily limit exceeded (71/71)
[FALLBACK] Trying OpenAI as final fallback
```

---

## 📞 Troubleshooting

### Quota Not Tracking?

1. Check database exists:
   ```bash
   ls -la Data/karma_quotas.db
   ```

2. Restart backend:
   ```bash
   # Stop current backend
   # Start fresh
   python Scripts/karma_backend.py
   ```

3. Check for errors:
   ```bash
   tail -f Logs/karma-backend.log | grep -i quota
   ```

### Reset Quota Manually:

```python
from karma_quota_manager import QuotaManager
import sqlite3

# Delete today's usage (emergency reset)
conn = sqlite3.connect("Data/karma_quotas.db")
cursor = conn.cursor()
cursor.execute("DELETE FROM daily_stats WHERE date = date('now')")
cursor.execute("DELETE FROM api_usage WHERE date(timestamp) = date('now')")
conn.commit()
conn.close()

print("Today's quota reset!")
```

---

## 🎯 Summary

**Your $15 Claude budget is now protected and optimized for 2 weeks!**

- ✅ 71 Claude queries/day ($1.07/day budget)
- ✅ FREE tiers handle 95% of queries
- ✅ Automatic quota tracking and blocking
- ✅ Real-time cost monitoring
- ✅ Smart routing saves expensive APIs for critical tasks
- ✅ Fallback protection prevents service disruption

**Expected outcome**: $10-12 used over 14 days, with $3-5 buffer remaining!

---

**Created**: 2026-02-12
**Status**: Production-ready with quota management
**Next**: Add your Claude API key and start using the system!
