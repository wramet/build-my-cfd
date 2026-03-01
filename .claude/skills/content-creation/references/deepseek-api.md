# DeepSeek API Integration

Details on integrating DeepSeek models via direct API calls for content creation.

## Model Assignment

| Stage | Model | API Method | Purpose |
|-------|--------|-------------|---------|
| 1-2 | GLM-4.7 | Via Claude | Ground truth extraction + Skeleton creation |
| 2.5 | - | Python Script | Generate structural blueprint (progressive overload) |
| 3 | DeepSeek R1 | **Direct API** | Verify skeleton + blueprint against ground truth |
| 4 | DeepSeek Chat V3 | **Direct API** | Expand to full English content (follows blueprint) |
| 5 | DeepSeek R1 | **Direct API** | Final technical verification |
| 6 | - | Python Script | Syntax QC |

## Why Direct API?

**Benefits:**
- ✅ Guaranteed DeepSeek execution (no Task tool delegation issues)
- ✅ Interactive prompts at each stage
- ✅ Error handling and verification
- ✅ Clear progress indicators
- ✅ Summary of all outputs

## Integration Script

**Script:** `.claude/scripts/run_content_workflow.sh`

**Usage:**
```bash
bash .claude/scripts/run_content_workflow.sh 05 "Spatial Discretization Schemes"
```

**The script combines:**
1. **Claude Main Agent** for stages 1-2 (WebSearch + Roadmap reading)
2. **Python Wrapper** for stages 3-5 (Direct DeepSeek API calls)
3. **Python QC Script** for stage 6 (Syntax validation)

## Direct API Usage

### Manual Stage 3: Verify Skeleton

```bash
cat > /tmp/stage3_prompt.txt << 'PROMPT'
Verify skeleton for Day XX

SKELETON: $(cat daily_learning/skeletons/dayXX_skeleton.json)
GROUND TRUTH: $(cat /tmp/verified_facts_dayXX.json)

Verification tasks:
1. Class hierarchy matches ground truth exactly
2. Formulas match ground truth (check operators!)
3. No hallucinated classes or methods
4. All ⭐ facts are verified

Output format:
- PASS if all checks succeed
- FAIL with specific issues if any mismatch found
PROMPT

python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage3_prompt.txt \
  > /tmp/verification_report_dayXX.txt
```

### Manual Stage 4: Generate Content

```bash
cat > /tmp/stage4_prompt.txt << 'PROMPT'
Expand Day XX: [TOPIC] - ENGLISH ONLY

SKELETON: $(cat daily_learning/skeletons/dayXX_skeleton.json)
BLUEPRINT: $(cat daily_learning/blueprints/dayXX_blueprint.json)

[Include detailed content requirements...]

PROMPT

python3 .claude/scripts/deepseek_content.py \
  deepseek-chat \
  /tmp/stage4_prompt.txt \
  > daily_learning/Phase_01_Foundation_Theory/XX.md
```

### Manual Stage 5: Final Verify

```bash
cat > /tmp/stage5_prompt.txt << 'PROMPT'
Final verification for Day XX

CONTENT: $(cat daily_learning/Phase_01_Foundation_Theory/XX.md)
GROUND TRUTH: $(cat /tmp/verified_facts_dayXX.json)
BLUEPRINT: $(cat daily_learning/blueprints/dayXX_blueprint.json)

[Include verification tasks...]

PROMPT

python3 .claude/scripts/deepseek_content.py \
  deepseek-reasoner \
  /tmp/stage5_prompt.txt \
  > /tmp/final_verification_dayXX.txt
```

## Troubleshooting

### Script Fails

```bash
# Make script executable
chmod +x .claude/scripts/run_content_workflow.sh

# Check Python is available
python3 --version

# Test DeepSeek API directly
python3 .claude/scripts/deepseek_content.py deepseek-chat <(echo "test")
```

### Content Quality Issues

If DeepSeek generates poor content:
1. **Review prompt** - Ensure constraints are clear
2. **Check ground truth** - Verify skeleton JSON structure
3. **Adjust prompt** - Edit stage prompt files in `/tmp/`
4. **Retry** - Re-run that specific stage

### Verification

```bash
# Verify DeepSeek was used directly (not through proxy)
grep -c "deepseek-chat" proxy.log  # Should return 0
grep -c "deepseek-reasoner" proxy.log  # Should return 0

# Verify direct API calls were made
ls -la /tmp/stage*_prompt.txt
ls -la /tmp/*verification*.txt
```

## MCP Integration

**Location:** `.claude/mcp/deepseek_mcp_server.py`

**Configuration in `.mcp.json`:**
```json
{
  "mcpServers": {
    "deepseek": {
      "command": "python3",
      "args": [".claude/mcp/deepseek_mcp_server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "...",
        "PROMPT_CACHE_ENABLED": "true",
        "CACHE_SIZE_MB": "100",
        "CACHE_DIR": "/tmp/prompt_cache"
      }
    }
  }
}
```

**Features:**
- Response caching (100MB cache, /tmp/prompt_cache)
- Context overflow handling
- Direct API integration bypassing proxy
