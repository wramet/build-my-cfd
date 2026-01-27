#!/usr/bin/env python3
"""
Test suite for walkthrough verification gates.

Tests all 6 verification gates independently and in combination.
"""

import unittest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".claude" / "scripts"))

from walkthrough_orchestrator import WalkthroughOrchestrator, VerificationGate


class TestVerificationGate(unittest.TestCase):
    """Test VerificationGate class."""

    def test_gate_initialization(self):
        """Test gate initialization from config."""
        config = {
            "name": "test_gate",
            "description": "Test verification gate",
            "required": True,
            "checks": ["check1", "check2"],
            "thresholds": {"min_value": 5},
            "on_failure": "stop"
        }

        gate = VerificationGate(1, config)

        self.assertEqual(gate.gate_id, 1)
        self.assertEqual(gate.name, "test_gate")
        self.assertEqual(gate.description, "Test verification gate")
        self.assertTrue(gate.required)
        self.assertEqual(gate.checks, ["check1", "check2"])
        self.assertEqual(gate.thresholds, {"min_value": 5})
        self.assertEqual(gate.on_failure, "stop")
        self.assertEqual(gate.status, "pending")

    def test_gate_pass(self):
        """Test marking gate as passed."""
        gate = VerificationGate(1, {"name": "test"})
        gate.pass_gate("All good")

        self.assertEqual(gate.status, "PASS")
        self.assertEqual(gate.details, "All good")

    def test_gate_fail(self):
        """Test marking gate as failed."""
        gate = VerificationGate(1, {"name": "test"})
        gate.fail("Bad thing happened")

        self.assertEqual(gate.status, "FAILED")
        self.assertEqual(gate.details, "Bad thing happened")

    def test_is_critical(self):
        """Test critical gate detection."""
        gate1 = VerificationGate(1, {
            "name": "critical",
            "required": True,
            "on_failure": "stop"
        })
        self.assertTrue(gate1.is_critical())

        gate2 = VerificationGate(2, {
            "name": "non_critical",
            "required": False,
            "on_failure": "continue"
        })
        self.assertFalse(gate2.is_critical())


class TestGate1FileStructure(unittest.TestCase):
    """Test Gate 1: File Structure Verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_file_not_found(self):
        """Test failure when input file doesn't exist."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Mock the path to non-existent file
        with patch.object(orchestrator, 'day_file', Path("/nonexistent/file.md")):
            result = orchestrator.gate1_file_structure()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[0].status, "FAILED")
        self.assertIn("not found", orchestrator.gates[0].details.lower())

    def test_missing_sections(self):
        """Test failure when required sections are missing."""
        # Create a file with missing sections
        test_file = self.temp_path / "test.md"
        test_file.write_text("""
# Test File

## Some Section

Content here.

## Code Section

Some code.

""")

        orchestrator = WalkthroughOrchestrator(day=99, strict=False)
        with patch.object(orchestrator, 'day_file', test_file):
            result = orchestrator.gate1_file_structure()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[0].status, "FAILED")

    def test_valid_sections(self):
        """Test success when all required sections are present."""
        # Create a valid file
        test_file = self.temp_path / "test.md"
        test_file.write_text("""
# Test File

## Theory Section

Some theory.

## Code Section

Some code.

## Implementation Section

Some implementation.

""")

        orchestrator = WalkthroughOrchestrator(day=99, strict=False)
        with patch.object(orchestrator, 'day_file', test_file):
            result = orchestrator.gate1_file_structure()

        self.assertTrue(result)
        self.assertEqual(orchestrator.gates[0].status, "PASS")


class TestGate2GroundTruth(unittest.TestCase):
    """Test Gate 2: Ground Truth Extraction."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create mock extract_facts.py
        scripts_dir = self.temp_path / "scripts"
        scripts_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_missing_ground_truth(self):
        """Test failure when ground truth extraction fails."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Mock extract_facts.py failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="Extraction failed")
            with patch.object(orchestrator, 'day_file', Path(self.temp_path / "test.md")):
                result = orchestrator.gate2_ground_truth()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[1].status, "FAILED")

    def test_insufficient_facts(self):
        """Test failure when insufficient facts are extracted."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Mock ground truth with insufficient facts
        gt_file = Path("/tmp/verified_facts.json")
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                    "facts": ["fact1", "fact2"],
                    "classes": {"Class1": {}},
                    "methods": {}
                })
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout="")
                    with patch.object(orchestrator, 'day_file', Path(self.temp_path / "test.md")):
                        result = orchestrator.gate2_ground_truth()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[1].status, "FAILED")


class TestGate3TheoryEquations(unittest.TestCase):
    """Test Gate 3: Theory Equations Verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_nested_latex(self):
        """Test failure on nested LaTeX delimiters."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Content with nested LaTeX
        content = """
## Theory

This has $$nested $inline$ math$$ which is forbidden.
"""
        orchestrator.content_sections = {"theory": content}

        result = orchestrator.gate3_theory_equations()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[2].status, "FAILED")

    def test_valid_latex(self):
        """Test success with valid LaTeX."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Valid content - using raw strings for proper backslashes
        content = r"""
## Theory

Display: $$\nabla \cdot \mathbf{U} = 0$$

Inline: The gradient $\nabla \phi$ is important.
"""
        orchestrator.content_sections = {"theory": content}

        result = orchestrator.gate3_theory_equations()

        self.assertTrue(result)
        self.assertEqual(orchestrator.gates[2].status, "PASS")


class TestGate4CodeStructure(unittest.TestCase):
    """Test Gate 4: Code Structure Verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_unbalanced_code_blocks(self):
        """Test failure on unbalanced code blocks."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Content with unbalanced code block - only opening marker
        content = """
## Code

```cpp
int x = 5;
// No closing marker
"""

        orchestrator.content_sections = {"code": content}
        orchestrator.ground_truth = None  # No ground truth to check against

        result = orchestrator.gate4_code_structure()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[3].status, "FAILED")

    def test_valid_code_structure(self):
        """Test success with valid code structure."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Valid content
        content = """
## Code

```cpp
class MyClass {
    void method();
};
```
"""

        orchestrator.content_sections = {"code": content}

        result = orchestrator.gate4_code_structure()

        self.assertTrue(result)
        self.assertEqual(orchestrator.gates[3].status, "PASS")


class TestGate5Implementation(unittest.TestCase):
    """Test Gate 5: Implementation Verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_missing_implementation_section(self):
        """Test failure when implementation section is missing."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)
        orchestrator.content_sections = {}  # No implementation section

        result = orchestrator.gate5_implementation()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[4].status, "FAILED")

    def test_valid_implementation(self):
        """Test success with valid implementation."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        content = """
## Implementation

```bash
wmake
```

File: `openfoam_temp/src/file.H`
"""

        orchestrator.content_sections = {"implementation": content}

        result = orchestrator.gate5_implementation()

        self.assertTrue(result)
        self.assertEqual(orchestrator.gates[4].status, "PASS")


class TestGate6FinalCoherence(unittest.TestCase):
    """Test Gate 6: Final Coherence Verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_no_verified_markers(self):
        """Test failure when no verified markers are present."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        content = "No verified markers here."
        orchestrator.content_sections = {"intro": content}

        result = orchestrator.gate6_final_coherence()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[5].status, "FAILED")

    def test_truncated_content(self):
        """Test failure on truncated content."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # Content with truncated line ending in **
        content = """
Some content

**This is truncated
"""

        orchestrator.content_sections = {"intro": content}

        result = orchestrator.gate6_final_coherence()

        self.assertFalse(result)
        self.assertEqual(orchestrator.gates[5].status, "FAILED")

    def test_valid_coherence(self):
        """Test success with valid coherent content."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        content = "⭐ Verified fact here. Some more content."

        orchestrator.content_sections = {"intro": content}

        result = orchestrator.gate6_final_coherence()

        self.assertTrue(result)
        self.assertEqual(orchestrator.gates[5].status, "PASS")


class TestModelFallback(unittest.TestCase):
    """Test model fallback mechanisms."""

    def test_primary_unavailable(self):
        """Test fallback when primary model is unavailable."""
        orchestrator = WalkthroughOrchestrator(day=99, strict=False)

        # In a full implementation, this would test the model routing
        # For now, we verify the configuration is correct
        theory_config = orchestrator.model_config.get("models", {}).get("theory", {})
        self.assertEqual(theory_config.get("primary"), "deepseek-reasoner")
        self.assertEqual(theory_config.get("backup"), "glm-4.7")


class TestPartialOutputCleanup(unittest.TestCase):
    """Test cleanup of partial outputs on failure."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_cleanup_on_gate_failure(self):
        """Test that partial output is cleaned up on failure."""
        # Create a mock output file
        output_file = self.temp_path / "day_99_walkthrough.md"
        output_file.write_text("Partial output")

        orchestrator = WalkthroughOrchestrator(day=99, strict=False)
        with patch.object(orchestrator, 'output_file', output_file):
            orchestrator._cleanup_on_failure()

        # File should be deleted
        self.assertFalse(output_file.exists())


if __name__ == "__main__":
    unittest.main()
