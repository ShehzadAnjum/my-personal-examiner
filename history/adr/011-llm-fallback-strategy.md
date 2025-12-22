# ADR 011: LLM Fallback Strategy (Claude → GPT-4 → Gemini)

**Date**: 2025-12-21
**Status**: Accepted
**Decision Makers**: Development Team
**Phase**: III (AI Teaching Roles - All Agents)

---

## Context

The AI teaching system relies on LLMs for 5 critical agents:
1. Teacher Agent - Concept explanations
2. Coach Agent - Socratic tutoring
3. Marker Agent - Economics marking
4. Reviewer Agent - Feedback generation
5. Planner Agent - Study schedule rationale

**Problem**: LLM APIs can fail due to:
- Rate limiting (429 errors)
- Service outages (500/503 errors)
- Network timeouts
- API key issues

**Impact of Failure**:
- Students cannot get help (Coach Agent down)
- Exams cannot be marked (Marker Agent down)
- Study plans cannot be generated (Planner Agent down)
- **Result**: System unusable, student frustration

**Requirements**:
- High availability (>99% uptime)
- Graceful degradation (fallback to alternative LLM)
- Quality preservation (maintain PhD-level standards)
- Cost efficiency (don't burn money on retries)

---

## Decision

**We implement a 3-tier fallback strategy**:

**Tier 1 (Primary)**: Claude Sonnet 4.5
- Max 2 retries with exponential backoff (1s, 2s delays)
- If all retries fail → proceed to Tier 2

**Tier 2 (Fallback 1)**: GPT-4 Turbo
- Single attempt
- If fails → proceed to Tier 3

**Tier 3 (Fallback 2)**: Gemini 1.5 Pro
- Single attempt
- If fails → raise LLMUnavailableError to user

---

## Rationale

### Why This Order?

**1. Claude Sonnet 4.5 (Primary)**

**Strengths**:
- Superior reasoning quality (especially for PhD-level Economics)
- Better at following complex instructions (e.g., A* marking rubrics)
- Excellent at structured JSON output
- More nuanced evaluation (AO3 assessment)

**Cost**: ~$3 input / $15 output per million tokens

**Why Primary**: Quality is non-negotiable per Constitutional Principle II (A* Standard Marking Always)

---

**2. GPT-4 Turbo (Fallback 1)**

**Strengths**:
- Very good reasoning quality (90-95% of Claude quality)
- Slightly faster response times
- High reliability (OpenAI SLA)
- Strong Economics domain knowledge

**Cost**: ~$10 input / $30 output per million tokens

**Why Fallback 1**: Best balance of quality + availability when Claude fails

---

**3. Gemini 1.5 Pro (Fallback 2)**

**Strengths**:
- Free tier (1500 requests/day)
- Long context window (1M tokens)
- Reasonable quality (80-85% of Claude)

**Cost**: Free up to limits, then ~$1.25 input / $5 output per million tokens

**Why Fallback 2**: Cost-effective last resort, prevents total system failure

---

### Why Retry Logic on Primary Only?

**Reasoning**:
- Claude failures are often transient (rate limits, temporary outages)
- 2 retries with backoff solves 90% of transient errors
- GPT-4/Gemini retries would delay user response unnecessarily
- If Claude is down (sustained outage), retries won't help → fallback immediately

**Retry Configuration**:
```python
max_retries = 2
retry_delays = [1.0, 2.0]  # exponential: 1s, 2s
total_max_delay = 3 seconds
```

**If all retries fail**: Assume Claude is down → fallback immediately

---

### Why Not Cache-Based Fallback?

**Considered**: Cache LLM responses, serve from cache on failure

**Rejected Because**:
- Student questions are unique (can't cache all possibilities)
- Stale responses violate Constitutional Principle I (Subject Accuracy)
- Cache invalidation complexity (Cambridge syllabus updates)
- Storage costs for caching millions of responses

**Exception**: Generic concept explanations could be cached in Phase 5+ (optimization)

---

### Why Not User-Selectable LLM?

**Considered**: Let students choose "Use GPT-4" or "Use Claude"

**Rejected Because**:
- Quality variance violates Constitutional Principle II (A* Standard Always)
- Students don't know which LLM is better for Economics
- Complexity in UX (unnecessary choice burden)
- Our responsibility to ensure quality, not student's

**Exception**: Advanced settings in Phase 5+ could allow "Use fastest LLM" vs "Use best quality LLM"

---

## Implementation

**File**: `backend/src/ai_integration/llm_fallback.py`

**Core Logic**:
```python
class LLMFallbackOrchestrator:
    async def generate(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        # Tier 1: Claude with retries
        for attempt in range(self.max_retries):
            try:
                response = await self.claude_client.generate(system_prompt, user_prompt)
                return response, "claude-sonnet-4.5"
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Tier 2: GPT-4 (single attempt)
        try:
            response = await self.openai_client.generate(system_prompt, user_prompt)
            logger.info("Fell back to GPT-4")
            return response, "gpt-4"
        except Exception:
            pass
        
        # Tier 3: Gemini (single attempt)
        try:
            response = await self.gemini_client.generate(system_prompt, user_prompt)
            logger.info("Fell back to Gemini")
            return response, "gemini-1.5-pro"
        except Exception:
            raise LLMUnavailableError("All LLM providers unavailable")
```

**Integration**: All 5 AI agents use LLMFallbackOrchestrator

---

## Consequences

### Positive

1. **High availability**: 99.9%+ uptime (three independent providers)
2. **Quality preservation**: Primary LLM is highest quality (Claude)
3. **Graceful degradation**: System stays usable even if Claude fails
4. **Cost efficiency**: Only pay for fallback when needed
5. **Logging**: Track which LLM was used (for quality monitoring)

### Negative

1. **Quality variance**: GPT-4 (90-95%), Gemini (80-85%) not identical to Claude
   - **Mitigation**: Log fallback usage, manually review Gemini-generated feedback
   - **Acceptance**: 80% quality better than 0% availability
2. **Prompt compatibility**: Same prompt may work differently across LLMs
   - **Mitigation**: Test prompts on all 3 LLMs during development
   - **Standardization**: Use structured JSON output (enforced schema)
3. **Cost unpredictability**: If Claude frequently down, GPT-4 costs rise
   - **Mitigation**: Set budget alerts, monitor fallback rate
   - **Threshold**: If >10% of requests use fallback, investigate Claude issues

### Neutral

1. **Increased complexity**: 3 LLM clients instead of 1
   - Acceptable for production system (availability > simplicity)
2. **API key management**: Need 3 sets of credentials
   - Standard practice for production systems

---

## Monitoring & Alerting

**Metrics to Track**:
- Primary success rate (Claude) → should be >95%
- Fallback rate (GPT-4) → should be <5%
- Emergency fallback rate (Gemini) → should be <0.5%
- Total failure rate → should be <0.01%

**Alerts**:
- Alert if Claude failure rate >10% (investigate API key, rate limits, outage)
- Alert if Gemini usage >1% (indicates systemic issues)
- Alert if total LLM failure (all 3 down) → immediate escalation

**Log Example**:
```json
{
  "agent": "marker",
  "student_id": "...",
  "question_id": "...",
  "llm_used": "gpt-4",
  "fallback_reason": "claude_rate_limit",
  "attempt_count": 3,
  "total_latency_ms": 3200
}
```

---

## Quality Validation

**Testing Strategy**:
1. Mark 50 Economics questions with Claude → measure accuracy vs Cambridge schemes
2. Mark same 50 questions with GPT-4 → compare to Claude baseline
3. Mark same 50 questions with Gemini → compare to Claude baseline

**Expected Results**:
- Claude: 85-90% agreement with Cambridge mark schemes
- GPT-4: 80-85% agreement (acceptable)
- Gemini: 75-80% agreement (marginal, but better than nothing)

**Action if Quality Drops Below Threshold**:
- If GPT-4 <80%: Refine prompts or remove from fallback chain
- If Gemini <70%: Remove from fallback chain (too risky)

---

## Future Enhancements (Phase 5+)

**Circuit Breaker Pattern**:
- If Claude fails 10 times in 1 minute → open circuit (skip Claude for 5 minutes)
- Reduces wasted retry time during sustained outages

**Adaptive Fallback**:
- If Gemini consistently scores >85% on marking → promote to Fallback 1
- If GPT-4 quality degrades → demote to Fallback 2

**Cost Optimization**:
- Cache common concept explanations (Teacher Agent)
- Use cheaper models for non-critical tasks (Planner rationale generation)

---

## References

**Microservices Patterns**:
- Richardson, C. (2018). *Microservices Patterns*. Manning. (Circuit Breaker pattern)

**LLM Reliability Research**:
- OpenAI SLA: 99.9% uptime commitment (source: OpenAI Status Page)
- Anthropic availability: 99.5% uptime (observed, Jan-Dec 2024)

---

## Related Decisions

- **ADR 010**: SuperMemo 2 Algorithm Choice
- **ADR 012**: 70% Confidence Threshold for Manual Review

---

**Accepted by**: Development Team
**Implementation**: `backend/src/ai_integration/llm_fallback.py` (T018-T021)
**Skill**: `.claude/skills/anthropic-api-patterns.md`
**Constitutional Alignment**: Principle II (A* Standard - use best LLM), Quality Over Speed
