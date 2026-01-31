#!/usr/bin/env python3
"""
Smart Reader for Large Files - RAG-Style Content Loading

Loads only relevant sections from large files to prevent context overflow.
Designed for AI agents that need to query large markdown/technical files.

Usage:
    python3 smart_reader.py <query> <file_path> [context_lines]
    python3 smart_reader.py "fvMesh" daily_learning/Phase_02_Geometry_Mesh/15.md

Author: CFD Engine Development Project
Date: 2026-01-28
"""

import sys
import os
from typing import List, Tuple


def smart_read(file_path: str, query: str = None, context_lines: int = 50) -> str:
    """
    Scan a large file and return only relevant sections.

    Strategy:
    1. ALWAYS return file head (first 50 lines) - provides structure/context
    2. Find matches for query keyword with ±context_lines
    3. If no match found, list all headers (#) for navigation
    4. Stop after ~300 lines to prevent token overflow

    Args:
        file_path: Path to the file to read
        query: Keyword to search for (case-insensitive)
        context_lines: Number of lines before/after each match

    Returns:
        String containing relevant file sections
    """
    if not os.path.exists(file_path):
        return f"Error: File not found: {file_path}"

    results = []
    total_lines_read = 0
    max_output_lines = 300  # Prevent token overflow

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)
        file_name = os.path.basename(file_path)

        # === PHASE 1: File Head (Context/Structure) ===
        results.append(f"### 📄 FILE: {file_name}")
        results.append(f"### 📊 Total Lines: {total_lines}")
        results.append(f"### 🔍 Query: {query or 'None (listing structure)'}")
        results.append("")
        results.append("--- FILE HEAD (First 50 lines) ---")

        head_lines = min(50, total_lines)
        results.extend(lines[:head_lines])
        total_lines_read += head_lines

        if total_lines > 50:
            results.append("\n... [content skipped] ...\n")

        # === PHASE 2: Query Search (if provided) ===
        found_matches = False
        match_count = 0
        max_matches = 3  # Limit to prevent overflow

        if query:
            query_lower = query.lower()

            for i, line in enumerate(lines):
                # Skip the head section we already read
                if i < 50:
                    continue

                if query_lower in line.lower():
                    found_matches = True
                    match_count += 1

                    # Calculate safe bounds
                    start = max(50, i - context_lines)  # Don't overlap with head
                    end = min(total_lines, i + context_lines)

                    results.append(f"--- MATCH {match_count} AT LINE {i} ---")
                    results.extend(lines[start:end])
                    total_lines_read += (end - start)

                    results.append("\n... [content skipped] ...\n")

                    # Stop if we've hit our limits
                    if match_count >= max_matches or total_lines_read >= max_output_lines:
                        break

        # === PHASE 3: Fallback - List Headers ===
        if not found_matches:
            if query:
                results.append(f"\n[⚠️] Keyword '{query}' not found in file.")
                results.append(f"Listing all headers for navigation:\n")

            results.append("--- FILE HEADERS (Table of Contents) ---")

            header_pattern = ('#', '##', '###', '####', '#####')
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(header_pattern):
                    results.append(f"Line {i:5d}: {stripped}")

        # === PHASE 4: Token Summary ===
        estimated_tokens = total_lines_read * 15  # Rough estimate: ~15 tokens/line
        results.append(f"\n--- SUMMARY ---")
        results.append(f"Total output lines: {total_lines_read}/{total_lines}")
        results.append(f"Estimated tokens: ~{estimated_tokens:,}")
        results.append(f"Matches found: {match_count if found_matches else 0}")

        return "".join(results)

    except Exception as e:
        return f"Error reading file: {str(e)}"


def find_best_matching_file(query: str, directory: str) -> Tuple[str, int]:
    """
    Find the file in directory with the most matches for query.

    Args:
        query: Keyword to search for
        directory: Directory to search in

    Returns:
        Tuple of (best_file_path, match_count)
    """
    best_file = None
    best_matches = 0

    if not os.path.exists(directory):
        return (None, 0)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        matches = content.count(query.lower())

                        if matches > best_matches:
                            best_matches = matches
                            best_file = file_path
                except Exception:
                    continue

    return (best_file, best_matches)


# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Smart Reader - RAG-Style File Content Loader")
        print("")
        print("Usage:")
        print(f"  {sys.argv[0]} <query> <file_path> [context_lines]")
        print("")
        print("Examples:")
        print(f"  {sys.argv[0]} fvMesh daily_learning/Phase_02_Geometry_Mesh/15.md")
        print(f"  {sys.argv[0]} 'finite volume' MODULE_01/CONTENT/01/02.md")
        print(f"  {sys.argv[0]} boundaryConditions daily_learning/Phase_01/05.md 100")
        print("")
        print("Options:")
        print("  query        - Keyword to search for (required)")
        print("  file_path    - Path to file to read (required)")
        print("  context_lines- Lines before/after match (default: 50)")
        sys.exit(1)

    query_arg = sys.argv[1]
    file_path_arg = sys.argv[2]
    context_lines_arg = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    result = smart_read(file_path_arg, query_arg, context_lines_arg)
    print(result)
