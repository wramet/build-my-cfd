with open('daily_learning/2026-01-05.md', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            print(f"{i+1}: {line.strip()}")
