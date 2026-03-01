#!/usr/bin/env python3
"""
Detect natural C++/DSA content in OpenFOAM for enhanced lab generation.

This script analyzes ground truth or source code to identify which C++ and DSA
topics naturally appear, ensuring authentic learning experiences.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


# Natural C++/DSA indicators in OpenFOAM
NATURAL_INDICATORS = {
    'templates': {
        'patterns': [
            r'tmp<\s*\w+>',
            r'autoPtr<\s*\w+>',
            r'refPtr<\s*\w+>',
            r'Field<\s*Type\s*>',
            r'fvMatrix<\s*\w+>',
            r'volScalarField',
            r'volVectorField',
            r'surfaceScalarField',
            r'template\s*<\s*class',
            r'template\s*<\s*typename'
        ],
        'label': 'Templates',
        'priority': 'high'
    },
    'smart_pointers': {
        'patterns': [
            r'tmp<\s*\w+>',
            r'autoPtr',
            r'refPtr',
            r'uniquePtr',
            r'refPtr\[\]',
            r'\.ref\(\)',
            r'\.ptr\(\)',
            r'\.valid\(\)',
            r'\.clear\(\)',
            r'\.move\(\)'
        ],
        'label': 'Smart Pointers',
        'priority': 'high'
    },
    'containers': {
        'patterns': [
            r'\bUList\b',
            r'\bList\b',
            r'\bDynamicList\b',
            r'\bHashTable\b',
            r'\bHashSet\b',
            r'\bMap\b',
            r'\bDictionary\b',
            r'\bPtrList\b',
            r'\bIDLList\b'
        ],
        'label': 'Containers (List, HashTable, Map)',
        'priority': 'high'
    },
    'sparse_matrices': {
        'patterns': [
            r'\bLduMatrix\b',
            r'\blduMatrix\b',
            r'\blduAddressing\b',
            r'\blowerPtr_\b',
            r'\bdiagPtr_\b',
            r'\bupperPtr_\b',
            r'\.lower\(\)',
            r'\.diag\(\)',
            r'\.upper\(\)',
            r'\bsolver\b',
            r'\bpreconditioner\b'
        ],
        'label': 'Sparse Matrices (LduMatrix)',
        'priority': 'high'
    },
    'graph_structures': {
        'patterns': [
            r'\bmesh\.C\(\)',
            r'\bmesh\.owner\(\)',
            r'\bmesh\.neighbour\(\)',
            r'\bcellCells\b',
            r'\bcellPoints\b',
            r'\bpointCells\b',
            r'\bfaceCells\b',
            r'\bcellFaces\b',
            r'\bowner\b',
            r'\bneighbour\b',
            r'\blduAddressing\b'
        ],
        'label': 'Graph Structures (Mesh Connectivity)',
        'priority': 'medium',
        'note': 'Structure only, not algorithms'
    },
    'trees': {
        'patterns': [
            r'\boctree\b',
            r'\bcellTree\b',
            r'\bindexedOctree\b',
            r'\bdynamicIndexedOctree\b',
            r'\bboundBox\b.*tree',
            r'\btreeDataCell\b',
            r'\btreeDataPoint\b'
        ],
        'label': 'Trees (Octree for Spatial Search)',
        'priority': 'high'
    },
    'sorting': {
        'patterns': [
            r'\bstableSort\b',
            r'\bSortableList\b',
            r'\bsort\b',
            r'\.sort\(\)',
            r'\.sorted\(\)'
        ],
        'label': 'Sorting (stableSort)',
        'priority': 'medium'
    },
    'iterators': {
        'patterns': [
            r'\bforAll\b',
            r'\bforAllIter\b',
            r'\biterator\b',
            r'\bconst_iterator\b',
            r'\bbegin\(\)',
            r'\bend\(\)',
            r'\bcbegin\(\)',
            r'\bcend\(\)'
        ],
        'label': 'Iterators (forAll, iterator patterns)',
        'priority': 'medium'
    },
    'operators': {
        'patterns': [
            r'\boperator\+\b',
            r'\boperator\|\b',
            r'\boperator\*\b',
            r'\boperator==\b',
            r'\boperator\(\)\b',
            r'\boperator\[\]\b'
        ],
        'label': 'Operator Overloading',
        'priority': 'medium'
    }
}


# Topics NOT natural to OpenFOAM (for reference)
UNNATURAL_TOPICS = {
    'graph_algorithms': ['BFS', 'DFS', 'Dijkstra', 'A*', 'shortest path', 'topological sort'],
    'dynamic_programming': ['memoization', 'optimal substructure', 'overlapping subproblems'],
    'backtracking': ['N-Queens', 'sudoku', 'constraint satisfaction'],
    'advanced_trees': ['BST', 'AVL', 'red-black', 'B-tree', 'heap', 'binary heap'],
    'heaps': ['priority queue', 'binary heap', 'binomial heap', 'fibonacci heap'],
    'search_algorithms': ['binary search', 'interpolation search', 'exponential search']
}


def detect_patterns(content: str, category: str) -> Tuple[int, List[str]]:
    """
    Detect how many patterns from a category appear in the content.

    Returns:
        Tuple of (count, list_of_matched_patterns)
    """
    if category not in NATURAL_INDICATORS:
        return 0, []

    patterns = NATURAL_INDICATORS[category]['patterns']
    matched = []

    for pattern in patterns:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            matched.append(pattern)

    return len(matched), matched


def analyze_content(content: str) -> Dict:
    """
    Analyze content for natural C++/DSA topics.

    Returns:
        Dictionary with detection results
    """
    results = {
        'detected': {},
        'missing': {},
        'score': 0,
        'max_score': len(NATURAL_INDICATORS),
        'duration_recommendation': '3 hours',
        'topics_to_include': []
    }

    total_weighted_score = 0
    max_weighted_score = 0

    for category, config in NATURAL_INDICATORS.items():
        count, matched = detect_patterns(content, category)

        # Weight by priority
        weight = 2 if config['priority'] == 'high' else 1
        max_weighted_score += weight

        if count > 0:
            detected_score = min(weight, count * weight)
            total_weighted_score += detected_score

            results['detected'][category] = {
                'label': config['label'],
                'count': count,
                'patterns': matched,
                'priority': config['priority'],
                'note': config.get('note', '')
            }

            if config['priority'] == 'high' or count >= 2:
                results['topics_to_include'].append(config['label'])
        else:
            results['missing'][category] = {
                'label': config['label'],
                'priority': config['priority']
            }

    results['score'] = total_weighted_score
    results['max_score'] = max_weighted_score

    # Determine duration recommendation
    score_ratio = total_weighted_score / max_weighted_score if max_weighted_score > 0 else 0

    if score_ratio >= 0.7:
        results['duration_recommendation'] = '6-8 hours'
    elif score_ratio >= 0.4:
        results['duration_recommendation'] = '4-5 hours'
    else:
        results['duration_recommendation'] = '3 hours'

    return results


def load_ground_truth(day: str) -> str:
    """
    Load ground truth for a given day.
    """
    gt_path = Path(f'/tmp/lab_ground_truth_{day}.json')

    if gt_path.exists():
        with open(gt_path, 'r') as f:
            gt_data = json.load(f)

        # Extract relevant content
        content = json.dumps(gt_data, indent=2)
        return content

    # Try to find source files
    source_dir = Path('openfoam_temp/src')
    if source_dir.exists():
        # Collect all C++ source content
        content_parts = []
        for cpp_file in source_dir.rglob('*.H'):
            try:
                with open(cpp_file, 'r') as f:
                    content_parts.append(f.read())
            except:
                pass
        return '\n'.join(content_parts)

    return ""


def print_results(results: Dict, output_format: str = 'text'):
    """
    Print detection results.
    """
    if output_format == 'json':
        print(json.dumps(results, indent=2))
        return

    # Text output
    print(f"\n{'='*70}")
    print(f"Natural C++/DSA Detection Results")
    print(f"{'='*70}\n")

    print(f"Score: {results['score']}/{results['max_score']} ")
    print(f"Recommended Lab Duration: {results['duration_recommendation']}\n")

    print(f"{'='*70}")
    print(f"Detected Natural Topics:")
    print(f"{'='*70}")

    for category, info in results['detected'].items():
        status = '✅'
        priority = info['priority'].upper()
        print(f"\n{status} {info['label']} [{priority}]")
        print(f"   Patterns found: {info['count']}")

        if info.get('note'):
            print(f"   Note: {info['note']}")

    if results['missing']:
        print(f"\n{'='*70}")
        print(f"Not Detected:")
        print(f"{'='*70}")

        for category, info in results['missing'].items():
            status = '❌'
            priority = info['priority'].upper()
            print(f"\n{status} {info['label']} [{priority}]")

    print(f"\n{'='*70}")
    print(f"Topics to Include in Lab:")
    print(f"{'='*70}")

    if results['topics_to_include']:
        for topic in results['topics_to_include']:
            print(f"  • {topic}")
    else:
        print(f"  (Minimal C++/DSA content - focus on CFD)")

    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Detect natural C++/DSA content for enhanced lab generation'
    )
    parser.add_argument(
        '--day',
        type=str,
        help='Day number (loads from /tmp/lab_ground_truth_XX.json)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Analyze specific file'
    )
    parser.add_argument(
        '--content',
        type=str,
        help='Analyze directly provided content'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    # Load content
    content = ""

    if args.content:
        content = args.content
    elif args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
        else:
            print(f"Error: File not found: {args.file}")
            return 1
    elif args.day:
        content = load_ground_truth(args.day)
        if not content:
            print(f"Warning: No ground truth found for day {args.day}")
            print("Searching OpenFOAM source files...")
    else:
        # Default: analyze OpenFOAM source
        source_dir = Path('openfoam_temp/src')
        if source_dir.exists():
            print("Analyzing OpenFOAM source code...")
            for cpp_file in source_dir.rglob('*.H'):
                try:
                    with open(cpp_file, 'r') as f:
                        content += f.read() + '\n'
                except:
                    pass
        else:
            print("Error: No content source specified")
            return 1

    if not content:
        print("Error: No content to analyze")
        return 1

    # Analyze
    results = analyze_content(content)

    # Print results
    print_results(results, args.output)

    # Save results
    if args.day:
        output_path = Path(f'/tmp/natural_cpp_dsa_detection_{args.day}.json')
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
