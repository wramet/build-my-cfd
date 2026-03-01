#!/usr/bin/env python3
"""
Phase Mapping Utilities — Single source of truth for day-to-phase resolution.

All scripts that need to know which phase a day belongs to should import
from this module instead of hardcoding day ranges.

Usage:
    from phase_utils import get_phase_for_day, get_folder_for_day

    phase = get_phase_for_day(15)   # Returns full phase dict
    folder = get_folder_for_day(15) # Returns "Phase_02_DataStructuresMemory"
    tmpl = get_template_for_day(15) # Returns "cpp_deep_dive"
    lines = get_target_lines(15)    # Returns 1000
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List


# Resolve config path relative to this script's location
_CONFIG_DIR = Path(__file__).parent.parent / "config"
_PHASE_MAPPING_PATH = _CONFIG_DIR / "phase_mapping.yaml"

# Cache the loaded mapping to avoid repeated file reads
_cached_mapping: Optional[Dict] = None


def load_phase_mapping() -> Dict:
    """
    Load phase mapping from config file.

    Returns:
        Full phase mapping dictionary from phase_mapping.yaml

    Raises:
        FileNotFoundError: If phase_mapping.yaml doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    global _cached_mapping
    if _cached_mapping is not None:
        return _cached_mapping

    if not _PHASE_MAPPING_PATH.exists():
        raise FileNotFoundError(
            f"Phase mapping config not found: {_PHASE_MAPPING_PATH}\n"
            f"Expected at: .claude/config/phase_mapping.yaml"
        )

    with open(_PHASE_MAPPING_PATH, 'r') as f:
        _cached_mapping = yaml.safe_load(f)

    return _cached_mapping


def get_phases() -> List[Dict]:
    """Return list of all phase dictionaries."""
    return load_phase_mapping()["phases"]


def get_phase_for_day(day: int) -> Dict:
    """
    Get the full phase dictionary for a given day number.

    Args:
        day: Day number (1-based)

    Returns:
        Phase dictionary with id, name, days, folder, template, etc.

    Raises:
        ValueError: If day doesn't fall in any phase range
    """
    day = int(day)
    for phase in get_phases():
        start, end = phase["days"]
        if start <= day <= end:
            return phase

    raise ValueError(
        f"Day {day} not found in any phase. "
        f"Valid range: 1-{get_phases()[-1]['days'][1]}"
    )


def get_folder_for_day(day: int) -> str:
    """
    Get the daily_learning subdirectory name for a given day.

    Args:
        day: Day number

    Returns:
        Folder name, e.g. "Phase_01_CppThroughOpenFOAM"
    """
    return get_phase_for_day(day)["folder"]


def get_template_for_day(day: int) -> str:
    """
    Get the template name for a given day.

    Args:
        day: Day number

    Returns:
        Template key, e.g. "cpp_deep_dive"
    """
    return get_phase_for_day(day)["template"]


def get_target_lines(day: int) -> int:
    """
    Get the target line count for content generated on a given day.

    Args:
        day: Day number

    Returns:
        Target line count (int)
    """
    return get_phase_for_day(day)["target_lines"]


def get_phase_name(day: int) -> str:
    """
    Get the human-readable phase name for a given day.

    Args:
        day: Day number

    Returns:
        Phase name, e.g. "C++ Through OpenFOAM's Eyes"
    """
    return get_phase_for_day(day)["name"]


def get_content_focus(day: int) -> str:
    """
    Get the content focus tag for a given day.

    Args:
        day: Day number

    Returns:
        Content focus, e.g. "cpp_patterns", "data_structures", "optimization"
    """
    return get_phase_for_day(day)["content_focus"]


def get_source_targets(day: int) -> List[str]:
    """
    Get the OpenFOAM source paths relevant for a given day's phase.

    Args:
        day: Day number

    Returns:
        List of OpenFOAM source directory paths for source-first extraction
    """
    return get_phase_for_day(day).get("source_targets", [])


def get_learning_objectives() -> List[str]:
    """Return the top-level learning objectives for the curriculum."""
    return load_phase_mapping().get("learning_objectives", [])


def get_total_sessions() -> int:
    """Return total number of learning sessions."""
    return load_phase_mapping().get("total_sessions", 84)


def invalidate_cache():
    """Clear the cached mapping (useful for testing or after config edits)."""
    global _cached_mapping
    _cached_mapping = None


# --- CLI usage ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        day = int(sys.argv[1])
        phase = get_phase_for_day(day)
        print(f"Day {day}:")
        print(f"  Phase:   {phase['name']}")
        print(f"  Folder:  {phase['folder']}")
        print(f"  Template: {phase['template']}")
        print(f"  Focus:   {phase['content_focus']}")
        print(f"  Lines:   {phase['target_lines']}")
    else:
        print("Phase Mapping Summary:")
        print(f"Curriculum: {load_phase_mapping()['curriculum']}")
        print(f"Sessions:   {get_total_sessions()}")
        print()
        for p in get_phases():
            s, e = p["days"]
            print(f"  {p['name']}")
            print(f"    Days {s:02d}-{e:02d} | {p['folder']} | {p['template']}")
            print()
