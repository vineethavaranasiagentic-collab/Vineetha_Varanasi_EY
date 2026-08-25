"""Universal natural-language requirement to goals and tasks generator.

Usage:
    python generate_goals_tasks.py --goals 5 --tasks-per-goal 5

The script always prompts for the requirement when it starts. This prevents a
previous command-line requirement from being reused accidentally.

The script uses OpenRouter when OPENROUTER_API_KEY is configured. Without an
API key, it uses a generic local fallback so the application remains runnable.
The fallback is domain-neutral and does not contain banking- or healthcare-
specific logic.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any
from urllib import error, request

DEFAULT_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are a Universal Requirements Analyst and Goal/Task Planner.

Analyze any project requirement, regardless of its domain. Identify meaningful,
specific, action-oriented outcomes and create practical tasks that contribute to
each outcome.

Rules:
- Create exactly the requested number of goals.
- Create exactly the requested number of tasks under every goal.
- Do not use domain-specific assumptions that are not supported by the requirement.
- Do not repeat a goal as a task.
- Keep tasks concrete, logically ordered, and easy to understand.
- Generate the domain, goals, goal success criteria, tasks, task dependencies,
  task-specific tools, input parameters, expected output parameters, and a
  workflow.
- Include a realistic sample_value for every input and expected output parameter,
  not only its type.
- Select only tools genuinely needed by each task; do not repeat a fixed tool
    list across every task.
- Derive all names, tools, parameters, outputs, dependencies, and approval
    requirements from the user's requirement.
- Every parameter must have a meaningful name, description, type, and (for
    inputs) required flag. Do not use vague names such as "data" or "value" when
    a more specific name can be derived from the task.
- Return only valid JSON. Do not include Markdown fences or commentary.

Required JSON shape:
{
  "project_title": "...",
  "project_summary": "...",
    "domain": "...",
  "goals": [
    {
      "goal_id": "G001",
      "goal_name": "...",
      "goal_description": "...",
    "success_criteria": ["..."],
      "tasks": [
        {
          "task_id": "G001-T001",
          "task_name": "...",
                    "task_description": "...",
          "depends_on": [],
                    "tools": [
                        {"name": "...", "description": "...", "purpose": "..."}
                    ],
                    "input_parameters": [
                        {"name": "...", "description": "...", "type": "...", "required": true, "sample_value": "..."}
                    ],
                    "expected_output_parameters": [
                        {"name": "...", "description": "...", "type": "...", "sample_value": "..."}
                    ],
                    "human_approval_required": false
        }
      ]
    }
    ],
    "workflow": [
        {"from": "...", "to": "...", "relationship": "..."}
    ]
}
"""


def build_user_prompt(requirement: str, goal_count: int, tasks_per_goal: int) -> str:
    return (
        f"Project requirement:\n{requirement}\n\n"
        f"Generate exactly {goal_count} goals and exactly {tasks_per_goal} tasks "
        "under each goal. For every task, include the tools that might be needed, "
        "the named input parameters needed to perform it, and the named expected output parameters it "
        "should produce. Each parameter needs a meaningful name, description, "
        "type, required flag for inputs, and a realistic sample_value showing "
        "the expected data. Include success criteria for each goal, dependencies "
        "when logically required, human_approval_required for every task, and a "
        "workflow list connecting requirements, goals, tasks, tools, outputs, and "
        "dependencies. Do not assign the same tools or generic parameters to "
        "every task. "
        "Return only the required JSON object."
    )


def call_llm(requirement: str, goal_count: int, tasks_per_goal: int) -> str:
    """Call OpenRouter and return the model's content as text."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    payload = {
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(requirement, goal_count, tasks_per_goal)},
        ],
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost/universal-goal-task-generator",
        "X-Title": "Universal Goal and Task Generator",
    }
    http_request = request.Request(OPENROUTER_URL, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(http_request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error while calling OpenRouter: {exc.reason}") from exc

    try:
        return str(result["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("OpenRouter returned an unexpected response") from exc


def extract_json(raw_text: str) -> dict[str, Any]:
    """Parse JSON directly or extract the first JSON object from model output."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("The model response did not contain a JSON object")
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError("The model returned malformed JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("The generated result must be a JSON object")
    return parsed


def validate_generated_result(result: dict[str, Any], goal_count: int, tasks_per_goal: int) -> None:
    """Validate the required structure and exact requested counts."""
    for field in ("project_title", "project_summary", "domain", "goals", "workflow"):
        if not result.get(field):
            raise ValueError(f"Generated result is missing '{field}'")
    if not isinstance(result.get("goals"), list):
        raise ValueError("Generated result is missing a goals list")
    if len(result["goals"]) != goal_count:
        raise ValueError(f"Expected {goal_count} goals but received {len(result['goals'])}")

    for goal_index, goal in enumerate(result["goals"], start=1):
        if not isinstance(goal, dict):
            raise ValueError(f"Goal {goal_index} is not an object")
        for field in ("goal_id", "goal_name", "goal_description", "success_criteria", "tasks"):
            if not goal.get(field):
                raise ValueError(f"Goal {goal_index} is missing '{field}'")
        if not isinstance(goal["success_criteria"], list):
            raise ValueError(f"Goal {goal_index} success_criteria must be a list")
        if not isinstance(goal["tasks"], list) or len(goal["tasks"]) != tasks_per_goal:
            actual = len(goal["tasks"]) if isinstance(goal["tasks"], list) else 0
            raise ValueError(
                f"Goal {goal_index} must contain {tasks_per_goal} tasks but received {actual}"
            )
        for task_index, task in enumerate(goal["tasks"], start=1):
            if not isinstance(task, dict):
                raise ValueError(f"Task {goal_index}.{task_index} is not an object")
            for field in (
                "task_id",
                "task_name",
                "task_description",
                "depends_on",
                "tools",
                "input_parameters",
                "expected_output_parameters",
                "human_approval_required",
            ):
                if field not in task or (field != "human_approval_required" and task[field] is None):
                    raise ValueError(f"Task {goal_index}.{task_index} is missing '{field}'")
            if not isinstance(task["depends_on"], list):
                raise ValueError(f"Task {goal_index}.{task_index} field 'depends_on' must be a list")
            for parameter_field in ("input_parameters", "expected_output_parameters"):
                if not isinstance(task[parameter_field], list):
                    raise ValueError(
                        f"Task {goal_index}.{task_index} field '{parameter_field}' must be a list"
                    )
                for parameter in task[parameter_field]:
                    if not isinstance(parameter, dict) or not parameter.get("name") or not parameter.get("description") or not parameter.get("type"):
                        raise ValueError(
                            f"Task {goal_index}.{task_index} has an invalid {parameter_field} entry"
                        )
                    if "sample_value" not in parameter or parameter["sample_value"] in (None, ""):
                        raise ValueError(
                            f"Task {goal_index}.{task_index} {parameter_field} entries must include sample_value"
                        )
            if not isinstance(task["tools"], list):
                raise ValueError(f"Task {goal_index}.{task_index} field 'tools' must be a list")
            for tool in task["tools"]:
                if not isinstance(tool, dict) or not tool.get("name") or not tool.get("description") or not tool.get("purpose"):
                    raise ValueError(f"Task {goal_index}.{task_index} has an invalid tools entry")
            if not 1 <= len(task["tools"]) <= 4:
                raise ValueError(f"Task {goal_index}.{task_index} must have between 1 and 4 tools")
    if not isinstance(result["workflow"], list) or not result["workflow"]:
        raise ValueError("Workflow must be a non-empty list")
    for step in result["workflow"]:
        if not isinstance(step, dict) or not step.get("from") or not step.get("to") or not step.get("relationship"):
            raise ValueError("Every workflow step must include from, to, and relationship")


def _requirement_title(requirement: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", requirement)
    return " ".join(words[:8]) or "Project Plan"


def local_fallback(requirement: str, goal_count: int, tasks_per_goal: int) -> dict[str, Any]:
    """Create a generic offline result when no LLM key is available."""
    title = _requirement_title(requirement)
    goal_templates = [
        ("Clarify the project outcome", "Define the intended result, users, and success criteria."),
        ("Understand requirements and constraints", "Organize the needs, assumptions, dependencies, and limitations."),
        ("Design the solution approach", "Select a practical approach that addresses the stated requirement."),
        ("Build the core solution", "Implement the essential capabilities needed to deliver the intended outcome."),
        ("Validate the solution", "Test the result against requirements, quality expectations, and user needs."),
        ("Prepare the solution for use", "Document, demonstrate, and prepare the solution for its intended users."),
        ("Measure and improve results", "Evaluate performance and identify improvements based on observed results."),
        ("Manage delivery and sustainability", "Establish ownership, maintenance, risks, and a path for continued operation."),
        ("Deliver the final project", "Complete the remaining work and deliver a usable result."),
        ("Review project outcomes", "Confirm that the project achieved its intended objectives and lessons learned."),
    ]
    task_templates = [
        "Review the requirement and identify the main outcome",
        "List the users, stakeholders, and key assumptions",
        "Define measurable acceptance criteria",
        "Identify dependencies, risks, and constraints",
        "Document the decisions needed before implementation",
        "Break the goal into deliverable work items",
        "Implement the highest-priority work item",
        "Review the work against the acceptance criteria",
        "Address gaps and record unresolved issues",
        "Prepare a concise status and next-steps summary",
    ]
    goals = []
    for goal_number in range(1, goal_count + 1):
        name, description = goal_templates[(goal_number - 1) % len(goal_templates)]
        tasks = []
        for task_number in range(1, tasks_per_goal + 1):
            task_name = task_templates[(task_number - 1) % len(task_templates)]
            tasks.append(
                {
                    "task_id": f"G{goal_number:03d}-T{task_number:03d}",
                    "task_name": task_name,
                    "task_description": f"Complete this step for the project described as: {title}.",
                    "depends_on": [] if task_number == 1 else [f"G{goal_number:03d}-T{task_number - 1:03d}"],
                    "tools": [
                        {
                            "name": "data_collection_tool",
                            "description": "A tool for collecting the source information required by a task.",
                            "purpose": "Gather and organize the inputs needed for the task.",
                        },
                        {
                            "name": "calculation_tool",
                            "description": "A tool for applying formulas, comparisons, counts, or scoring rules to task inputs.",
                            "purpose": "Calculate objective values used in the expected output.",
                        },
                        {
                            "name": "validation_tool",
                            "description": "A tool for checking input quality and verifying task results.",
                            "purpose": "Detect missing, invalid, or inconsistent data before reporting the output.",
                        },
                        {
                            "name": "documentation_tool",
                            "description": "A tool for recording findings, decisions, and task results.",
                            "purpose": "Capture the completed output in a reusable project record.",
                        },
                    ][: 1 + (task_number % 4)],
                    "input_parameters": [
                        {
                            "name": "requirement_context",
                            "description": "The relevant context from the user's project requirement for this task.",
                            "type": "string",
                            "required": True,
                            "sample_value": "The project requirement supplied by the user.",
                        },
                        {
                            "name": "task_dependencies",
                            "description": "Any information or completed work needed before starting this task.",
                            "type": "list[string]",
                            "required": False,
                            "sample_value": ["Previously completed task result"],
                        },
                    ],
                    "expected_output_parameters": [
                        {
                            "name": "completed_task_result",
                            "description": "The specific result produced after completing this task.",
                            "type": "string",
                            "sample_value": "A completed result with relevant findings and decisions.",
                        },
                        {
                            "name": "completion_status",
                            "description": "Whether the task was completed successfully or needs follow-up.",
                            "type": "string",
                            "sample_value": "completed",
                        },
                    ],
                    "human_approval_required": False,
                }
            )
        goals.append(
            {
                "goal_id": f"G{goal_number:03d}",
                "goal_name": name,
                "goal_description": description,
                "success_criteria": [
                    "The goal produces a verifiable result relevant to the requirement.",
                    "All associated tasks are completed or clearly marked for follow-up.",
                ],
                "tasks": tasks,
            }
        )
    return {
        "project_title": title,
        "project_summary": requirement.strip(),
        "domain": "derived from the user requirement",
        "goals": goals,
        "workflow": [
            {"from": "requirement", "to": goal["goal_id"], "relationship": "supports"}
            for goal in goals
        ] + [
            {"from": task["task_id"], "to": goal["goal_id"], "relationship": "contributes to"}
            for goal in goals for task in goal["tasks"]
        ],
    }


def generate_goals_and_tasks(requirement: str, goal_count: int = 5, tasks_per_goal: int = 5) -> dict[str, Any]:
    """Generate and validate a universal goals/tasks JSON object."""
    requirement = requirement.strip()
    if not requirement:
        raise ValueError("Requirement cannot be empty")
    if not 1 <= goal_count <= 10:
        raise ValueError("goal_count must be between 1 and 10")
    if not 3 <= tasks_per_goal <= 10:
        raise ValueError("tasks_per_goal must be between 3 and 10")

    try:
        result = extract_json(call_llm(requirement, goal_count, tasks_per_goal))
        validate_generated_result(result, goal_count, tasks_per_goal)
        return result
    except (RuntimeError, ValueError) as exc:
        if os.getenv("UNIVERSAL_GENERATOR_STRICT", "").lower() in {"1", "true", "yes"}:
            raise RuntimeError(f"Could not generate a valid LLM result: {exc}") from exc
        result = local_fallback(requirement, goal_count, tasks_per_goal)
        validate_generated_result(result, goal_count, tasks_per_goal)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate universal project goals and tasks as JSON.")
    parser.add_argument("--goals", type=int, default=5, help="Number of goals, from 1 to 10")
    parser.add_argument("--tasks-per-goal", type=int, default=5, help="Tasks per goal, from 3 to 10")
    parser.add_argument(
        "--show-summary",
        action="store_true",
        help="Print a readable goal and task list before the JSON output",
    )
    return parser.parse_args()


def read_requirement() -> str:
    """Read a single- or multi-line requirement from an interactive terminal."""
    print("Paste your requirement below. Type END on a new line when finished.")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main() -> int:
    args = parse_args()
    requirement = read_requirement()
    try:
        result = generate_goals_and_tasks(requirement, args.goals, args.tasks_per_goal)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.show_summary:
        print("\nGENERATED GOALS AND TASKS\n")
        for goal in result["goals"]:
            print(f"{goal['goal_id']}: {goal['goal_name']}")
            print(f"  {goal['goal_description']}")
            for task in goal["tasks"]:
                print(f"  {task['task_id']}: {task['task_name']}")
            print()
        print("GENERATED JSON\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
