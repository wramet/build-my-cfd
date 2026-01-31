#!/usr/bin/env python3
"""
Q&A Manager for active learning during walkthrough reading.
Captures user questions and routes to specialist AI models.
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# Add parent directories to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
MCP_DIR = Path(__file__).parent.parent.parent / "mcp"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(MCP_DIR))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class QAManager:
    """Manages Q&A capture and routing for walkthrough learning."""

    def __init__(self, day: int, section: Optional[str] = None):
        self.day = day
        self.section = section
        self.walkthrough_file = PROJECT_ROOT / f"daily_learning/walkthroughs/day_{day:02d}_walkthrough.md"

        # Model routing based on question type and section
        self.model_map = {
            "theory": "deepseek-reasoner",      # DeepSeek R1 for math/derivations
            "code": "deepseek-chat",             # DeepSeek Chat for code analysis
            "implementation": "deepseek-chat",   # DeepSeek Chat for practical steps
            "general": "deepseek-chat"           # Default
        }

        # Question type categories
        self.question_types = {
            "clarification": "Request for explanation of unclear concepts",
            "deeper-dive": "Explore beyond current content",
            "implementation": "Practical coding/implementation questions",
            "debugging": "Troubleshooting help",
            "connection": "Link to other topics/concepts"
        }

        # Topic keywords for auto-tagging
        self.topic_keywords = {
            "RTT": ["reynolds transport", "rtt", "transport theorem"],
            "control-volume": ["control volume", "cv", "eulerian"],
            "FVM": ["finite volume", "fvm", "fvc", "flux", "divergence"],
            "discretization": ["discretization", "scheme", "upwind", "linear", "central"],
            "boundary": ["boundary condition", "patch", "inlet", "outlet", "bc"],
            "turbulence": ["turbulence", "k-epsilon", "rans", "les"],
            "mesh": ["mesh", "grid", "cell", "face", "polyMesh"],
            "gradient": ["gradient", "grad", "tgrad"],
            "time-derivative": ["time derivative", "ddt", "unsteady", "transient"],
            "conservation": ["conservation", "mass", "momentum", "energy"],
            "gauss": ["gauss", "divergence theorem", "integration"],
            "openfoam": ["openfoam", "solver", "field", "tmp", "geometricfield"],
            "matrix": ["matrix", "fvmatrix", "ldu", "solver"],
        }

    def capture_question(self, question: str, question_type: str = "clarification") -> Dict:
        """Capture question with context and route to specialist model."""
        self.log(f"Capturing question: {question[:50]}...")

        # Extract context from walkthrough
        context = self._extract_context()

        # Select appropriate model
        model = self._select_model(context, question_type)

        # Generate answer
        answer = self._generate_answer(question, context, model)

        # Extract tags
        tags = self._extract_tags(question, context)

        # Create Q&A entry
        qa_entry = {
            "timestamp": datetime.now().isoformat(),
            "day": self.day,
            "section": self.section or "general",
            "type": question_type,
            "question": question,
            "answer": answer,
            "model_used": model,
            "context_snippet": context.get("snippet", ""),
            "tags": tags
        }

        return qa_entry

    def _extract_context(self) -> Dict:
        """Extract relevant context from walkthrough file."""
        if not self.walkthrough_file.exists():
            return {"snippet": "", "section_type": "general"}

        with open(self.walkthrough_file, "r") as f:
            content = f.read()

        # Find the relevant section
        if self.section:
            # Look for section headers
            section_pattern = rf"## .*{self.section}.*"
            matches = list(re.finditer(section_pattern, content, re.IGNORECASE))

            if matches:
                # Get content from first match to next header or end
                start = matches[0].end()
                next_header = re.search(r"\n## ", content[start:])
                end = start + next_header.start() if next_header else len(content)
                snippet = content[start:end].strip()[:500]  # Limit snippet size
            else:
                snippet = ""
        else:
            snippet = ""

        # Determine section type for model routing
        section_type = self._determine_section_type(content)

        return {
            "snippet": snippet,
            "section_type": section_type,
            "file_path": str(self.walkthrough_file)
        }

    def _determine_section_type(self, content: str) -> str:
        """Determine the type of section for model routing."""
        content_lower = content.lower()

        if self.section:
            section_lower = self.section.lower()
            if "theory" in section_lower or "mathematical" in section_lower:
                return "theory"
            elif "code" in section_lower or "implementation" in section_lower:
                return "code"
            elif "implementation" in section_lower:
                return "implementation"

        # Fallback: analyze content
        if "```cpp" in content or "```mermaid" in content:
            return "code"
        elif any(term in content_lower for term in ["equation", "theorem", "derivation"]):
            return "theory"

        return "general"

    def _select_model(self, context: Dict, question_type: str) -> str:
        """Select appropriate specialist model based on context and question type."""
        section_type = context.get("section_type", "general")

        # Map question types to models
        if question_type == "deeper-dive" and section_type == "theory":
            return "deepseek-reasoner"  # Use R1 for deep theoretical questions
        elif question_type == "debugging":
            return "deepseek-chat"  # Use Chat for practical debugging

        # Use section-based routing
        return self.model_map.get(section_type, self.model_map["general"])

    def _generate_answer(self, question: str, context: Dict, model: str) -> str:
        """Generate answer using the selected model."""
        try:
            # Try MCP first
            if model == "deepseek-reasoner":
                return self._call_deepseek_reasoner(question, context)
            else:
                return self._call_deepseek_chat(question, context)
        except Exception as e:
            self.log(f"Error generating answer: {e}", "ERROR")
            return f"> **Error generating answer:** {e}"

    def _call_deepseek_reasoner(self, question: str, context: Dict) -> str:
        """Call DeepSeek R1 for theoretical analysis."""
        try:
            from mcp_client import DeepSeekMCPClient
            client = DeepSeekMCPClient()

            if not client.is_available():
                raise Exception("MCP client not available")

            prompt = self._build_reasoner_prompt(question, context)
            response = client.call_reasoner(prompt)

            return response or "No response from DeepSeek R1"
        except Exception as e:
            # Fallback to placeholder
            return f"> **DeepSeek R1 Answer:**\n\n[Reasoning-based answer to: {question}]\n\n*Context from: {context.get('section', 'general section')}*"

    def _call_deepseek_chat(self, question: str, context: Dict) -> str:
        """Call DeepSeek Chat for code/implementation analysis."""
        try:
            from mcp_client import DeepSeekMCPClient
            client = DeepSeekMCPClient()

            if not client.is_available():
                raise Exception("MCP client not available")

            prompt = self._build_chat_prompt(question, context)
            response = client.call_chat(prompt)

            return response or "No response from DeepSeek Chat"
        except Exception as e:
            # Fallback to placeholder
            return f"> **DeepSeek Chat Answer:**\n\n[Answer to: {question}]\n\n*Context from: {context.get('section', 'general section')}*"

    def _build_reasoner_prompt(self, question: str, context: Dict) -> str:
        """Build prompt for DeepSeek R1 (reasoning-focused)."""
        snippet = context.get("snippet", "")[:800]

        prompt = f"""You are analyzing a CFD (Computational Fluid Dynamics) walkthrough document and answering a student's question.

**Student's Question:** {question}

**Relevant Context from Walkthrough:**
{snippet if snippet else "(No specific context provided)"}

**Your Role:**
Provide a clear, step-by-step explanation that:
1. Directly addresses the question
2. Explains the reasoning behind the answer
3. Connects to the relevant theory/concepts
4. Uses appropriate mathematical notation (LaTeX-style: $...$ for inline, $$...$$ for display)
5. Is thorough but concise (aim for 150-300 words)

**Important:**
- If the question involves mathematical derivations, show your steps
- Reference the context when relevant
- Explain not just WHAT, but WHY
- Use verified facts from OpenFOAM when applicable

Provide your answer now:"""

        return prompt

    def _build_chat_prompt(self, question: str, context: Dict) -> str:
        """Build prompt for DeepSeek Chat (practical-focused)."""
        snippet = context.get("snippet", "")[:800]

        prompt = f"""You are helping a student learning CFD with OpenFOAM. Answer their question about the walkthrough content.

**Student's Question:** {question}

**Relevant Context:**
{snippet if snippet else "(No specific context provided)"}

**Your Role:**
Provide a practical, clear answer that:
1. Directly addresses the question
2. Gives practical examples or code snippets when relevant
3. Explains implementation details
4. References OpenFOAM specifics when applicable
5. Is concise but thorough (aim for 100-250 words)

**Important:**
- Focus on practical understanding
- Use code examples when helpful
- Reference OpenFOAM classes/methods when relevant
- Keep explanations actionable

Provide your answer now:"""

        return prompt

    def _extract_tags(self, question: str, context: Dict) -> List[str]:
        """Extract topic tags for organization."""
        tags = []
        question_lower = question.lower()
        section_lower = (self.section or "").lower()
        context_snippet = context.get("snippet", "").lower()

        # Check each topic
        for topic, keywords in self.topic_keywords.items():
            # Match against question, section, or context
            if any(kw in question_lower or kw in section_lower or
                   (context_snippet and kw in context_snippet)
                   for kw in keywords):
                tags.append(topic)

        return tags

    def append_to_walkthrough(self, qa_entry: Dict) -> bool:
        """Append Q&A entry to the walkthrough document."""
        try:
            # Read existing content
            if self.walkthrough_file.exists():
                with open(self.walkthrough_file, "r") as f:
                    content = f.read()
            else:
                content = self._create_walkthrough_skeleton()
                self.log(f"Created new walkthrough skeleton")

            # Check if Q&A section exists
            qa_section_pattern = r"## Active Learning Q&A"
            qa_exists = re.search(qa_section_pattern, content)

            if not qa_exists:
                # Add Q&A section before "Verification Summary" or at the end
                content = self._insert_qa_section(content)

            # Format Q&A entry
            formatted_entry = self._format_qa_entry(qa_entry)

            # Find the insertion point (after the Q&A header and tip)
            # We want to insert after the tip line but before the next ## header
            qa_header_pattern = r"(## Active Learning Q&A.*?\n---\n)"
            qa_match = re.search(qa_header_pattern, content, re.DOTALL)

            if qa_match:
                # Insert right after the Q&A header section
                insert_pos = qa_match.end()
                content = content[:insert_pos] + "\n\n" + formatted_entry + content[insert_pos:]
            else:
                # Fallback: append at end
                content += "\n\n" + formatted_entry

            # Write updated content
            with open(self.walkthrough_file, "w") as f:
                f.write(content)

            self.log(f"Q&A appended to {self.walkthrough_file}")
            return True

        except Exception as e:
            self.log(f"Error appending to walkthrough: {e}", "ERROR")
            return False

    def _create_walkthrough_skeleton(self) -> str:
        """Create a basic walkthrough skeleton if file doesn't exist."""
        return f"""# Day {self.day} Walkthrough

**Source File:** `daily_learning/Phase_01_Foundation_Theory/{self.day:02d}.md`
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Verification Status:** ⚠️ Generated from Q&A (no full walkthrough)

---

## Active Learning Q&A

*Your questions and answers from learning sessions*

---

## Marker Legend

- ⭐ = Verified from ground truth source
- ⚠️ = Unverified (documentation source only)
- ❌ = Incorrect/Common misconception

---

*Generated by Q&A Manager*
"""

    def _insert_qa_section(self, content: str) -> str:
        """Insert Q&A section into existing walkthrough."""
        # Find the position before "## Verification Summary" or at the end
        verification_pattern = r"\n## Verification Summary"
        verification_match = re.search(verification_pattern, content)

        if verification_match:
            insert_pos = verification_match.start()
            qa_section = """

---

## Active Learning Q&A

*Your questions and answers from learning sessions*

> 💡 **Tip:** Use `/qa --day {N} "your question"` to ask questions and have them recorded here!

---
"""
            return content[:insert_pos] + qa_section + content[insert_pos:]
        else:
            # Append at the end
            qa_section = """

---

## Active Learning Q&A

*Your questions and answers from learning sessions*

> 💡 **Tip:** Use `/qa --day {N} "your question"` to ask questions and have them recorded here!

---
"""
            return content + qa_section

    def _format_qa_entry(self, qa_entry: Dict) -> str:
        """Format a Q&A entry for markdown."""
        type_emoji = {
            "clarification": "💬",
            "deeper-dive": "🔍",
            "implementation": "💻",
            "debugging": "🐛",
            "connection": "🔗"
        }

        emoji = type_emoji.get(qa_entry["type"], "❓")
        timestamp = datetime.fromisoformat(qa_entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
        tags_str = " ".join(f"`{tag}`" for tag in qa_entry["tags"]) if qa_entry["tags"] else ""

        entry = f"""### {emoji} {qa_entry["type"].replace("-", " ").title()} Question
**Section:** {qa_entry["section"].replace("_", " ").title()} | **Asked:** {timestamp}

**Question:**
{qa_entry["question"]}

**Answer:**
{qa_entry["answer"]}

**Tags:** {tags_str if tags_str else "None"}

**Related Content:**
> {qa_entry["context_snippet"][:200] if qa_entry["context_snippet"] else "No specific context"}

---
"""

        return entry

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message to stderr."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)


def main():
    """Main entry point for Q&A manager."""
    parser = argparse.ArgumentParser(
        description="Q&A Manager for active learning during walkthroughs"
    )
    parser.add_argument("--day", type=int, required=True, help="Day number")
    parser.add_argument("--section", type=str, help="Section name (theory, code, etc.)")
    parser.add_argument("--type", type=str, default="clarification",
                       choices=["clarification", "deeper-dive", "implementation",
                               "debugging", "connection"],
                       help="Question type")
    parser.add_argument("--question", type=str, help="Question to ask")

    args = parser.parse_args()

    # Get question from argument or stdin
    question = args.question
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()

    if not question:
        print("Error: No question provided. Use --question or pipe from stdin.", file=sys.stderr)
        sys.exit(1)

    # Create Q&A manager and process question
    manager = QAManager(args.day, args.section)
    qa_entry = manager.capture_question(question, args.type)

    # Append to walkthrough
    if manager.append_to_walkthrough(qa_entry):
        print(f"\n✅ Q&A saved to day_{args.day:02d}_walkthrough.md")
        print(f"   Type: {qa_entry['type']}")
        print(f"   Model: {qa_entry['model_used']}")
        print(f"   Tags: {', '.join(qa_entry['tags']) if qa_entry['tags'] else 'None'}")
        print(f"\n---\n")
        print(qa_entry["answer"])
        sys.exit(0)
    else:
        print("Error: Failed to save Q&A", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
