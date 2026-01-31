#!/usr/bin/env python3
"""
Load Project Context for Content Generation

Injects R410A evaporator project context into the content creation pipeline.
This ensures all generated content is aligned with the project target.

Usage:
    python3 .claude/scripts/load_project_context.py --day=XX
"""

import json
import yaml
import sys
from pathlib import Path


def load_project_context():
    """Load project context from YAML file."""
    context_file = Path(".claude/config/project_context.yaml")

    if not context_file.exists():
        print(f"Warning: Project context file not found: {context_file}")
        return None

    with open(context_file) as f:
        return yaml.safe_load(f)


def load_r410a_template():
    """Load R410A integration template."""
    template_file = Path(".claude/templates/r410a_integration_blueprint.json")

    if not template_file.exists():
        print(f"Warning: R410A template not found: {template_file}")
        return None

    with open(template_file) as f:
        return json.load(f)


def generate_stage4_prompt_with_context(day, topic, skeleton, blueprint, ground_truth):
    """
    Generate Stage 4 prompt with R410A project context.

    Args:
        day: Day number (e.g., "01")
        topic: Topic name (e.g., "Governing Equations")
        skeleton: Skeleton JSON content
        blueprint: Blueprint JSON content
        ground_truth: Ground truth JSON content

    Returns:
        Enhanced prompt string
    """
    project_ctx = load_project_context()
    r410a_template = load_r410a_template()

    if not project_ctx or not r410a_template:
        print("Warning: Could not load project context, using generic prompt")
        return None

    # Extract key information
    refrigerant = project_ctx["refrigerant"]
    properties = refrigerant["properties"]
    conditions = project_ctx["operating_conditions"]

    prompt = f"""Expand Day {day}: {topic} - ENGLISH ONLY

SKELETON:
{skeleton}

BLUEPRINT:
{blueprint}

GROUND TRUTH:
{ground_truth}

PROJECT CONTEXT (CRITICAL):
===========================
Target Application: {project_ctx["target_application"]["domain"]}
Component: {project_ctx["target_application"]["component"]}
Refrigerant: {refrigerant["name"]} ({refrigerant["type"]})

Operating Conditions:
- Pressure: {conditions["pressure"]}
- Temperature: {conditions["temperature"]}
- Quality Range: {conditions["quality_range"]}

Key Property Values:
Liquid Phase:
  - Density (ρ_l): {properties["liquid"]["density"]} kg/m³
  - Viscosity (μ_l): {properties["liquid"]["viscosity"]} Pa·s
  - Thermal Conductivity (k_l): {properties["liquid"]["thermal_conductivity"]} W/m·K
  - Specific Heat (c_p,l): {properties["liquid"]["specific_heat"]} J/kg·K

Vapor Phase:
  - Density (ρ_v): {properties["vapor"]["density"]} kg/m³
  - Viscosity (μ_v): {properties["vapor"]["viscosity"]} Pa·s
  - Thermal Conductivity (k_v): {properties["vapor"]["thermal_conductivity"]} W/m·K
  - Specific Heat (c_p,v): {properties["vapor"]["specific_heat"]} J/kg·K

Interface:
  - Surface Tension (σ): {properties["interface"]["surface_tension"]} N/m
  - Latent Heat (h_lv): {properties["interface"]["latent_heat"]} J/kg

Property Ratios:
  - Density: {properties["ratios"]["density"]}
  - Viscosity: {properties["ratios"]["viscosity"]}
  - Thermal Conductivity: {properties["ratios"]["thermal_conductivity"]}

CRITICAL REQUIREMENTS:
- ENGLISH-ONLY content (no Thai translation)
- Every theoretical concept MUST connect to R410A evaporator application
- Use concrete property values, not just symbols
- Show how standard equations need modification for two-phase flow
- Include property tables with actual values
- Provide R410A-specific code implementations

MANDATORY CONTENT:
1. Property Tables:
   - Include at least 6 R410A properties with actual values
   - Show both liquid and vapor phases
   - Indicate operating conditions

2. Equation Modifications:
   - Show standard form first
   - Then show R410A-modified form
   - Explain each added term (ṁ, F_σ, h_lv)
   - Use side-by-side comparison format

3. Phase Change Physics:
   - Explain evaporation/condensation
   - Show mass transfer calculation
   - Include latent heat effects

4. Surface Tension:
   - Explain CSF model
   - Show curvature calculation
   - Include magnitude (σ = {properties["interface"]["surface_tension"]} N/m)

5. OpenFOAM Implementation:
   - Complete code examples
   - Lee model implementation
   - CSF surface tension implementation
   - VOF transport with MULES

STRUCTURAL RULES:
- Part 1: Foundation Theory (25%) - Standard equations
- Part 2: R410A Properties (20%) - Concrete data
- Part 3: Equation Modifications (25%) - Standard vs. R410A
- Part 4: Implementation (30%) - Complete solver code

APPENDIX REQUIREMENT (MANDATORY):
- Every output MUST end with "## Appendix: Complete File Listings"
- Include complete, compilable code
- All files must be 100% copy-pasteable

Format:
- Use $$ for display math equations
- Use $ for inline math
- Include Mermaid diagrams for system visualization
- All code blocks must have language tags
- Headers in English only

Output complete markdown file content that is immediately applicable to R410A evaporator simulation.
"""

    return prompt


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 load_project_context.py --day=XX")
        sys.exit(1)

    # Parse arguments
    day = sys.argv[0].split("=")[1] if "=" in sys.argv[0] else "01"

    # Load context
    project_ctx = load_project_context()
    r410a_template = load_r410a_template()

    print("R410A Project Context Loaded:")
    print(f"  Refrigerant: {project_ctx['refrigerant']['name']}")
    print(f"  Density Ratio: {project_ctx['refrigerant']['properties']['ratios']['density']}")
    print(f"  Surface Tension: {project_ctx['refrigerant']['properties']['interface']['surface_tension']} N/m")
    print(f"  Latent Heat: {project_ctx['refrigerant']['properties']['interface']['latent_heat']} J/kg")
    print()
    print("✅ Project context ready for content generation")
    print()
    print("Key Models:")
    for model_name, model_info in project_ctx["key_models"].items():
        print(f"  - {model_info['name']}: {model_info['description']}")


if __name__ == "__main__":
    main()
