#!/usr/bin/env python3
"""
Interactive Walkthrough Mode - Section-by-section reading with real-time Q&A

Allows users to read walkthroughs interactively and ask questions as they go.
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Add parent directories to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
MCP_DIR = Path(__file__).parent.parent.parent / "mcp"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(MCP_DIR))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Import QAManager
from qa_manager import QAManager


class InteractiveWalkthrough:
    """Interactive walkthrough reader with Q&A capture."""

    def __init__(self, day: int):
        self.day = day
        self.walkthrough_file = PROJECT_ROOT / f"daily_learning/walkthroughs/day_{day:02d}_walkthrough.md"
        self.qa_manager = QAManager(day)
        self.session_start = datetime.now()

        # Session tracking
        self.questions_asked = []
        self.current_section = None

    def run(self) -> None:
        """Run the interactive walkthrough session."""
        if not self.walkthrough_file.exists():
            print(f"Error: Walkthrough file not found: {self.walkthrough_file}")
            sys.exit(1)

        # Read and parse walkthrough
        with open(self.walkthrough_file, "r") as f:
            self.content = f.read()

        # Extract sections
        self.sections = self._parse_sections()

        # Welcome message
        self._print_welcome()

        # Interactive loop
        self._interactive_loop()

        # Session summary
        self._print_session_summary()

    def _parse_sections(self) -> List[Dict]:
        """Parse walkthrough into sections."""
        sections = []

        # Find all H2 headers
        h2_pattern = r"^## (.+)$"
        matches = list(re.finditer(h2_pattern, self.content, re.MULTILINE))

        for i, match in enumerate(matches):
            title = match.group(1)
            start = match.end()

            # Find end of section (next H2 or end of file)
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(self.content)

            section_content = self.content[start:end].strip()

            sections.append({
                "title": title,
                "content": section_content,
                "lines": len(section_content.split("\n"))
            })

        return sections

    def _print_welcome(self) -> None:
        """Print welcome message and instructions."""
        print("\n" + "="*70)
        print(f"  INTERACTIVE WALKTHROUGH: Day {self.day}")
        print("="*70)
        print(f"\n📖 File: {self.walkthrough_file.name}")
        print(f"📅 Session: {self.session_start.strftime('%Y-%m-%d %H:%M')}")
        print(f"\n📚 Sections: {len(self.sections)}")

        print("\n" + "-"*70)
        print("CONTROLS:")
        print("  [N]ext section    - Go to next section")
        print("  [P]revious section - Go to previous section")
        print("  [Q]uestion       - Ask a question about current section")
        print("  [J]ump           - Jump to specific section")
        print("  [S]ummary        - Show session summary")
        print("  [H]elp           - Show this help")
        print("  [E]xit / [C]trl-D - Save and exit")
        print("-"*70 + "\n")

    def _interactive_loop(self) -> None:
        """Main interactive loop."""
        self.section_index = 0

        while True:
            # Display current section
            self._display_section(self.section_index)

            # Get user input
            try:
                cmd = input("\n>>> ").strip().lower()
            except EOFError:
                print("\n")
                break

            # Process command
            if cmd in ["e", "exit", "q", "quit"]:
                break
            elif cmd in ["n", "next"]:
                self._next_section()
            elif cmd in ["p", "prev", "previous"]:
                self._prev_section()
            elif cmd in ["q", "question"]:
                self._ask_question()
            elif cmd in ["j", "jump"]:
                self._jump_to_section()
            elif cmd in ["s", "summary"]:
                self._print_session_summary()
            elif cmd in ["h", "help"]:
                self._print_help()
            elif cmd == "":
                # Empty input = next section
                self._next_section()
            else:
                print(f"Unknown command: {cmd}. Press [H] for help.")

    def _display_section(self, index: int) -> None:
        """Display a section with pagination."""
        if index < 0 or index >= len(self.sections):
            print(f"Invalid section index: {index}")
            return

        section = self.sections[index]
        self.current_section = section["title"]

        # Clear screen (print newlines for readability)
        print("\n" * 2)

        # Section header
        print("="*70)
        print(f"  {section['title']} ({index + 1}/{len(self.sections)})")
        print("="*70)

        # Display content with pagination
        lines = section["content"].split("\n")
        page_size = 25  # Lines per page

        for i, line in enumerate(lines):
            print(line)

            # Pause every page_size lines
            if (i + 1) % page_size == 0 and i + 1 < len(lines):
                input(f"\n--- Press Enter to continue ({i + 1}/{len(lines)} lines) ---\n")

        print("\n" + "-"*70)

    def _next_section(self) -> None:
        """Move to next section."""
        if self.section_index < len(self.sections) - 1:
            self.section_index += 1
        else:
            print("Already at last section.")

    def _prev_section(self) -> None:
        """Move to previous section."""
        if self.section_index > 0:
            self.section_index -= 1
        else:
            print("Already at first section.")

    def _ask_question(self) -> None:
        """Handle question input from user."""
        print("\n" + "-"*70)
        print("ASK A QUESTION")
        print("-"*70)

        # Get question
        question = input("\nYour question: ").strip()

        if not question:
            print("No question entered.")
            return

        # Get question type
        print("\nQuestion type:")
        print("  [1] Clarification - Explain unclear concepts")
        print("  [2] Deeper Dive    - Explore beyond content")
        print("  [3] Implementation - Practical coding questions")
        print("  [4] Debugging      - Troubleshooting help")
        print("  [5] Connection     - Link to other topics")

        type_choice = input("\nSelect type [1-5, default=1]: ").strip() or "1"

        type_map = {
            "1": "clarification",
            "2": "deeper-dive",
            "3": "implementation",
            "4": "debugging",
            "5": "connection"
        }

        question_type = type_map.get(type_choice, "clarification")

        # Update Q&A manager with current section
        self.qa_manager.section = self.current_section

        # Capture and answer question
        print("\nGenerating answer...")
        qa_entry = self.qa_manager.capture_question(question, question_type)

        # Display answer
        print("\n" + "="*70)
        print("ANSWER")
        print("="*70)
        print(qa_entry["answer"])
        print(f"\n(Model: {qa_entry['model_used']}, Tags: {', '.join(qa_entry['tags']) or 'None'})")

        # Confirm save
        save = input("\nSave this Q&A? [Y/n]: ").strip().lower()

        if save != "n":
            if self.qa_manager.append_to_walkthrough(qa_entry):
                print("✅ Q&A saved!")
                self.questions_asked.append(qa_entry)
            else:
                print("❌ Failed to save Q&A")
        else:
            print("Q&A not saved.")

    def _jump_to_section(self) -> None:
        """Jump to a specific section."""
        print("\nAvailable sections:")
        for i, section in enumerate(self.sections):
            print(f"  {i + 1:2d}. {section['title']}")

        try:
            choice = input("\nJump to section number: ").strip()
            index = int(choice) - 1

            if 0 <= index < len(self.sections):
                self.section_index = index
            else:
                print(f"Invalid section number: {choice}")
        except ValueError:
            print("Invalid input.")

    def _print_session_summary(self) -> None:
        """Print session summary."""
        duration = datetime.now() - self.session_start
        minutes = int(duration.total_seconds() / 60)

        print("\n" + "="*70)
        print("  SESSION SUMMARY")
        print("="*70)
        print(f"  Day: {self.day}")
        print(f"  Duration: {minutes} minutes")
        print(f"  Questions asked: {len(self.questions_asked)}")

        if self.questions_asked:
            print("\n  Questions:")
            for i, qa in enumerate(self.questions_asked, 1):
                print(f"    {i}. [{qa['type']}] {qa['question'][:50]}...")

        print("="*70 + "\n")

    def _print_help(self) -> None:
        """Print help message."""
        print("\n" + "-"*70)
        print("HELP")
        print("-"*70)
        print("\nCommands:")
        print("  [N]ext        - Go to next section")
        print("  [P]revious    - Go to previous section")
        print("  [Q]uestion    - Ask a question about the current section")
        print("  [J]ump        - Jump to a specific section by number")
        print("  [S]ummary     - Show session summary (questions asked, time)")
        print("  [H]elp        - Show this help message")
        print("  [E]xit        - Save session and exit")
        print("\nTips:")
        print("  - Press Enter to move to next section quickly")
        print("  - Questions are automatically saved to the walkthrough")
        print("  - Use Ctrl+C to exit without saving")
        print("-"*70 + "\n")


def main():
    """Main entry point for interactive mode."""
    parser = argparse.ArgumentParser(
        description="Interactive walkthrough mode with real-time Q&A"
    )
    parser.add_argument("--day", type=int, required=True, help="Day number")

    args = parser.parse_args()

    try:
        interactive = InteractiveWalkthrough(args.day)
        interactive.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
