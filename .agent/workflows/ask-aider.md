---
description: Run Aider to generate content or answer questions in a specific file
---
1. Prepare the environment and run Aider. Replace `<TARGET_FILE>` with the absolute path and `<INSTRUCTION>` with your prompt.

```bash
source ~/.zshrc && use-aider-glm && \
aider --model anthropic/claude-3-opus-20240229 \
    --yes \
    --no-auto-commits \
    --file "<TARGET_FILE>" \
    --map-tokens 4096 \
    --message "<INSTRUCTION>"
```

2. **Refine and Polish**: After Aider finishes, YOU (the agent) must review and refine the generated content.
   - Check for correct Thai translation (Engineering Thai style).
   - Verify formatting (headers, code blocks).
   - Remove any conversational filler from Aider.
   - Ensure it fits seamlessly into the existing document.

3. **Cross-Reference (If applicable)**: If the explanation/content is generated in a separate file (e.g., `daily_learning/questions/...`):
   - Add a link in the **original file** pointing to the new explanation file.
   - Example: `See detailed explanation in: [[questions/new_file.md]]` or `[Link](questions/new_file.md)`.
