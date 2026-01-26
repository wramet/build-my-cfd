---
description: Switch context to a specific agent and execute a task
---

# /delegate

Use this command to delegate a task to a specialized agent.

## Usage

```
/delegate [agent_name] "[instruction]"
```

Example:
```
/delegate architect "Plan the content for Day 03"
/delegate engineer "Debug the compilation error in mySolver.C"
```

## Logic

1.  **Load Agent Profile:** Read the agent definition from `.claude/agents/[agent_name].md`.
2.  **Context Switch:** Adopt the persona, tools, and constraints of that agent.
3.  **Execute:** Perform the requested instruction using the agent's specific capabilities.

---

**System Instruction:**
When the user runs `/delegate [agent] [task]`:
1.  Check if `.claude/agents/[agent].md` exists.
2.  If yes, read it and say: "**Activating [Agent Name]...**".
3.  Then, execute the `[task]` strictly following the instructions in that agent file.
4.  If the agent file doesn't exist, list available agents in `.claude/agents/`.
