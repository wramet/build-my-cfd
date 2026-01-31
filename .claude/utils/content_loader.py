#!/usr/bin/env python3
"""
Safe Content Loader with Token Limits

Prevents context overflow by checking file sizes before reading.
Designed for AI agents that need to explore large codebases.

Usage:
    from content_loader import safe_read_file, check_file_size

    content = safe_read_file("large_file.md", max_lines=500)
    is_safe = check_file_size("another_file.md", max_lines=1000)

Author: CFD Engine Development Project
Date: 2026-01-28
"""

import os
from typing import Optional, Dict, List


# Default limits (configurable via agent_limits.json)
DEFAULT_MAX_LINES = 1000
DEFAULT_MAX_TOKENS = 100000
APPROX_TOKENS_PER_LINE = 15  # Rough estimate for technical content


class FileSizeWarning(Exception):
    """Raised when file exceeds size limits."""
    pass


def check_file_size(file_path: str, max_lines: int = DEFAULT_MAX_LINES) -> Dict[str, any]:
    """
    Check if file is safe to read without context overflow.

    Args:
        file_path: Path to file to check
        max_lines: Maximum allowed lines

    Returns:
        Dict with file info: {'safe': bool, 'lines': int, 'tokens': int}
    """
    if not os.path.exists(file_path):
        return {'safe': False, 'error': f'File not found: {file_path}'}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)

        estimated_tokens = line_count * APPROX_TOKENS_PER_LINE

        return {
            'safe': line_count <= max_lines,
            'lines': line_count,
            'estimated_tokens': estimated_tokens,
            'max_lines': max_lines,
            'file_path': file_path
        }
    except Exception as e:
        return {'safe': False, 'error': str(e)}


def safe_read_file(
    file_path: str,
    max_lines: int = DEFAULT_MAX_LINES,
    prefer: str = None
) -> str:
    """
    Safely read file with size limits.

    Strategy:
    1. Check file size first
    2. If safe (< max_lines), read full content
    3. If too large, read:
       - First 100 lines (header/context)
       - Last 50 lines (footer/conclusions)
       - Or use smart_reader if query provided

    Args:
        file_path: Path to file to read
        max_lines: Maximum lines before truncating
        prefer: Optional keyword to search for (uses smart_reader)

    Returns:
        File content (or truncated version)
    """
    if prefer:
        # Use smart_reader for keyword search
        try:
            from smart_reader import smart_read
            return smart_read(file_path, prefer)
        except ImportError:
            pass

    # Check file size
    info = check_file_size(file_path, max_lines)

    if not info.get('safe'):
        if 'error' in info:
            return f"[Error] {info['error']}"

        # File is too large - truncate
        return truncate_file(file_path, head_lines=100, tail_lines=50)

    # Safe to read full file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file]: {str(e)}"


def truncate_file(
    file_path: str,
    head_lines: int = 100,
    tail_lines: int = 50
) -> str:
    """
    Read only header and footer of large file.

    Args:
        file_path: Path to file
        head_lines: Lines to read from start
        tail_lines: Lines to read from end

    Returns:
        Truncated file content with marker
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)

        result = []
        result.append(f"[⚠️] File too large ({total_lines} lines)")
        result.append(f"[ℹ️] Showing first {head_lines} and last {tail_lines} lines\n")

        # Head
        result.append("--- FILE HEADER ---")
        result.extend(lines[:head_lines])

        result.append("\n... [middle content skipped] ...\n")

        # Tail
        result.append("--- FILE FOOTER ---")
        result.extend(lines[-tail_lines:])

        return "".join(result)

    except Exception as e:
        return f"[Error truncating file]: {str(e)}"


def batch_check_files(file_paths: List[str], max_lines: int = DEFAULT_MAX_LINES) -> List[Dict]:
    """
    Check multiple files and return safety report.

    Args:
        file_paths: List of file paths to check
        max_lines: Maximum allowed lines

    Returns:
        List of file info dicts, sorted by size (largest first)
    """
    results = []

    for path in file_paths:
        info = check_file_size(path, max_lines)
        results.append(info)

    # Sort by line count (descending) to identify largest files first
    results.sort(key=lambda x: x.get('lines', 0), reverse=True)

    return results


def generate_size_report(directory: str, pattern: str = "*.md", max_lines: int = DEFAULT_MAX_LINES) -> str:
    """
    Generate a report on file sizes in directory.

    Useful for identifying files that might cause context overflow.

    Args:
        directory: Directory to scan
        pattern: Glob pattern (default: *.md)
        max_lines: Warning threshold

    Returns:
        Formatted report string
    """
    import glob

    report = []
    report.append(f"## File Size Report: {directory}")
    report.append(f"Warning threshold: {max_lines} lines (~{max_lines * APPROX_TOKENS_PER_LINE:,} tokens)")
    report.append("")

    files = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    results = batch_check_files(files, max_lines)

    # Group by safety
    safe_files = [f for f in results if f.get('safe', False)]
    unsafe_files = [f for f in results if not f.get('safe', True)]

    # Report unsafe files (these will cause overflow!)
    if unsafe_files:
        report.append(f"### ⚠️ OVERSIZED FILES ({len(unsafe_files)} files)")
        report.append("")
        for f in unsafe_files[:10]:  # Top 10 largest
            if 'error' not in f:
                report.append(f"- {f['file_path']}: {f['lines']:,} lines (~{f['estimated_tokens']:,} tokens)")
        report.append("")

    # Report safe files
    if safe_files:
        report.append(f"### ✅ SAFE FILES ({len(safe_files)} files)")
        report.append("")
        for f in safe_files[:5]:  # First 5
            report.append(f"- {f['file_path']}: {f['lines']:,} lines")

    return "\n".join(report)


# CLI Interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Safe Content Loader")
        print("")
        print("Usage:")
        print("  python content_loader.py <file_path> [max_lines]")
        print("  python content_loader.py --report <directory> [pattern]")
        print("")
        print("Examples:")
        print("  python content_loader.py daily_learning/Phase_02/15.md")
        print("  python content_loader.py large_file.md 500")
        print("  python content_loader.py --report daily_learning/ '*.md'")
        sys.exit(1)

    if sys.argv[1] == "--report":
        directory = sys.argv[2] if len(sys.argv) > 2 else "."
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*.md"
        report = generate_size_report(directory, pattern)
        print(report)
    else:
        file_path = sys.argv[1]
        max_lines_arg = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_LINES

        content = safe_read_file(file_path, max_lines_arg)
        print(content)
