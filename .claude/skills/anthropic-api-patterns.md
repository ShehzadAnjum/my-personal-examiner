# Skill: Anthropic Claude API Integration Patterns

**Domain**: LLM Integration & Production Patterns
**Purpose**: Best practices for Claude Sonnet 4.5 integration in production teaching system
**Created**: 2025-12-21
**Phase**: III (AI Teaching Roles)

---

## Overview

This skill documents production-ready patterns for integrating Anthropic Claude (primary LLM) with fallback to OpenAI GPT-4 and Google Gemini.

**Implemented in**: `backend/src/ai_integration/anthropic_client.py`, `backend/src/ai_integration/llm_fallback.py`

---

## Client Configuration

### API Key Management

**Environment Variables**:
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

**Never**:
- ❌ Hardcode API keys in code
- ❌ Commit `.env` to git
- ❌ Log API keys (even in debug mode)

**Always**:
- ✅ Use environment variables
- ✅ Validate keys at startup
- ✅ Rotate keys periodically

---

### Client Initialization

```python
from anthropic import Anthropic

class AnthropicClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.default_max_tokens = 4096
        self.default_temperature = 0.7
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = None,
        temperature: float = None,
    ) -> str:
        """Generate completion with Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
```

---

## Model Selection

### Claude Sonnet 4.5 (Primary)

**Model ID**: `claude-sonnet-4-20250514`

**Use For**:
- PhD-level concept explanations (Teacher Agent)
- Socratic questioning (Coach Agent)
- Economics marking (Marker Agent)
- Feedback generation (Reviewer Agent)
- Model answer creation (Reviewer Agent)

**Strengths**:
- Superior reasoning quality
- Better at following complex instructions
- Excellent at Economics domain knowledge
- More nuanced evaluation

**Costs**: ~$3 per million input tokens, ~$15 per million output tokens

---

### GPT-4 (Fallback)

**Model ID**: `gpt-4-turbo-2024-04-09`

**Use For**:
- Fallback when Claude is unavailable
- Faster responses (if needed)

**Strengths**:
- Slightly faster
- Good reasoning quality

**Costs**: ~$10 per million input tokens, ~$30 per million output tokens

---

### Gemini Pro (Second Fallback)

**Model ID**: `gemini-1.5-pro`

**Use For**:
- Second fallback only
- When both Claude and GPT-4 fail

**Strengths**:
- Free tier available
- Long context window

**Costs**: Free up to 1500 requests/day

---

## Prompt Engineering Best Practices

### System Prompt Structure

**Template**:
```python
system_prompt = f"""
You are a PhD-level {role} for Cambridge International A-Level Economics (9708).

Your Expertise:
- {specific_domain_knowledge}
- Evidence-based pedagogy (Socratic method, spaced repetition)
- Cambridge A* grading standards (AO1/AO2/AO3)

Your Task:
{specific_task_description}

Constitutional Requirements:
- Subject accuracy is non-negotiable (match Cambridge syllabi exactly)
- A* standard marking always (PhD-level rigor)
- Constructive feedback (explain WHY and HOW to improve)

Output Format:
{expected_json_schema_or_structure}
"""
```

**Example** (Teacher Agent):
```python
system_prompt = """
You are a PhD-level Economics teacher for Cambridge International A-Level Economics (9708).

Your Expertise:
- Comprehensive knowledge of 9708 syllabus (microeconomics, macroeconomics, international economics)
- Evidence-based pedagogy (Socratic method, cognitive load management)
- Visual explanation skills (diagrams, graphs, step-by-step construction)

Your Task:
Explain economic concepts at A* level using:
1. Clear definitions with economic terminology
2. Real-world examples
3. Diagrams with annotations
4. Practice problems

Constitutional Requirements:
- Subject accuracy non-negotiable
- PhD-level pedagogical quality
- Explain WHY, not just WHAT

Output Format: JSON
{
  "explanation": "...",
  "key_concepts": [...],
  "real_world_examples": [...],
  "visual_aids": [...],
  "practice_problems": [...]
}
"""
```

---

### User Prompt Construction

**Best Practices**:
1. **Be specific**: "Explain supply/demand equilibrium" not "Explain economics"
2. **Provide context**: Include student level, previous performance
3. **Set constraints**: "Max 300 words", "Include diagram", "A* standard"
4. **Request structured output**: JSON schema enforcement

**Example**:
```python
user_prompt = f"""
Concept: {syllabus_point.learning_outcome}
Syllabus Code: {syllabus_point.code}
Student Level: AS Level (first year)
Previous Performance: 70% average (B grade, needs improvement to A*)

Explain this concept with:
- Definition (AO1)
- Real-world example (AO2)
- Diagram showing mechanism
- 2 practice problems (increasing difficulty)

Target: 250-350 words
Standard: A* level (comprehensive, accurate, perceptive)
"""
```

---

## JSON Output Parsing

### Request Structured Output

**Method 1: Schema in System Prompt**:
```python
system_prompt = """
...
Output Format (strict JSON):
{
  "marks_awarded": int,
  "max_marks": int,
  "ao1_score": int,
  "ao2_score": int,
  "ao3_score": int,
  "feedback": str,
  "errors": [{"type": str, "description": str}]
}

CRITICAL: Respond ONLY with valid JSON. No markdown, no explanations outside JSON.
"""
```

**Method 2: Post-Processing with Regex**:
```python
import json
import re

def extract_json(llm_response: str) -> dict:
    """Extract JSON from LLM response (handles markdown wrappers)"""
    # Try direct parse first
    try:
        return json.loads(llm_response)
    except json.JSONDecodeError:
        pass
    
    # Extract from ```json ... ``` wrapper
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', llm_response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Extract first {...} block
    json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not extract valid JSON from response: {llm_response[:200]}...")
```

---

## Error Handling & Fallback

### LLM Fallback Orchestrator

**Strategy**: Primary (Claude) → Retry → Fallback 1 (GPT-4) → Fallback 2 (Gemini)

```python
class LLMFallbackOrchestrator:
    def __init__(self):
        self.claude_client = AnthropicClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        self.gemini_client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        self.max_retries = 2
        self.retry_delay = 1.0  # seconds
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> tuple[str, str]:  # (response, model_used)
        """Generate with fallback chain"""
        
        # Try Claude (primary)
        for attempt in range(self.max_retries):
            try:
                response = await self.claude_client.generate(
                    system_prompt, user_prompt, max_tokens
                )
                return response, "claude-sonnet-4.5"
            except Exception as e:
                logger.warning(f"Claude attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        # Fallback to GPT-4
        try:
            response = await self.openai_client.generate(
                system_prompt, user_prompt, max_tokens
            )
            logger.info("Fell back to GPT-4")
            return response, "gpt-4"
        except Exception as e:
            logger.warning(f"GPT-4 fallback failed: {e}")
        
        # Fallback to Gemini
        try:
            response = await self.gemini_client.generate(
                system_prompt, user_prompt, max_tokens
            )
            logger.info("Fell back to Gemini")
            return response, "gemini-1.5-pro"
        except Exception as e:
            logger.error(f"All LLMs failed: {e}")
            raise LLMUnavailableError("All LLM providers are currently unavailable")
```

---

## Rate Limiting & Timeouts

### Timeout Configuration

```python
# Timeouts by agent type
TIMEOUTS = {
    "teacher": 10.0,      # Concept explanation: 10 seconds
    "coach": 8.0,         # Socratic question: 8 seconds
    "marker": 15.0,       # Marking: 15 seconds (complex analysis)
    "reviewer": 12.0,     # Feedback generation: 12 seconds
    "planner": 5.0,       # Schedule generation: 5 seconds (mostly algorithmic)
}

async def generate_with_timeout(client, prompt, timeout):
    try:
        return await asyncio.wait_for(
            client.generate(prompt),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise LLMTimeoutError(f"LLM did not respond within {timeout}s")
```

---

### Rate Limit Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(RateLimitError)
)
async def generate_with_retry(client, prompt):
    return await client.generate(prompt)
```

---

## Constitutional Alignment

- **Principle II**: A* Standard Marking → Use best available LLM (Claude Sonnet 4.5)
- **Quality Over Speed**: Fallback ensures availability without compromising too much on quality

---

**Version**: 1.0.0 | **Created**: 2025-12-21
**Primary LLM**: Claude Sonnet 4.5
**Fallbacks**: GPT-4 → Gemini
**Status**: Production-ready integration
