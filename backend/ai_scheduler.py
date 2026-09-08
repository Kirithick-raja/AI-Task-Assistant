import os
import json
from datetime import datetime
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a scheduling assistant inside a task management app.
You will be given:
1. A list of pending tasks (not yet done)
2. A history of past completed tasks with a focus_score (1-5) showing when the
   user tends to concentrate best
3. The user's working hours and break preferences

Your job: assign each pending task a suggested_start and suggested_end time.

Rules:
- Never schedule outside work_start / work_end
- Higher priority and higher energy_level tasks should go into the time windows
  where past focus_score has been highest
- Respect each task's deadline (never schedule after it)
- Leave at least break_minutes between two scheduled tasks
- Do not overlap any two tasks
- Only schedule tasks starting from today's date forward

Respond with ONLY valid JSON (no markdown, no explanation text) in this exact shape:
[
  {"task_id": 1, "suggested_start": "2026-09-01T09:00:00", "suggested_end": "2026-09-01T09:30:00", "reasoning": "short reason"}
]
"""


def generate_schedule(tasks, behavior_logs, preferences):
    """Ask Claude to build an optimal schedule from tasks + behavior history."""
    today = datetime.now().strftime("%Y-%m-%d")

    user_message = f"""
Today's date: {today}

Pending tasks:
{json.dumps(tasks, default=str, indent=2)}

Past behavior logs (for learning productive time windows):
{json.dumps(behavior_logs, default=str, indent=2)}

User preferences:
{json.dumps(preferences, default=str, indent=2)}
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw_text = response.content[0].text.strip()

    # Claude sometimes wraps JSON in ```json fences even when told not to — strip them defensively
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        schedule = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"Claude did not return valid JSON: {raw_text}")

    return schedule
