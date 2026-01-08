
import re

file_path = 'daily_learning/2026-01-11.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements
replacements = [
    (r'(?<![\$])ṁ(?![$])', r'$\dot{m}$'),
    (r'(?<![\$])ρ(?![$])', r'$\rho$'),
    (r'(?<![\$])α(?![$])', r'$\alpha$'),
    (r'(?<![\$])φ(?![$])', r'$\phi$'),
    (r'(?<![\$])μ(?![$])', r'$\mu$'),
    (r'(?<![\$])∇(?![$])', r'$\nabla$'),
    (r'(?<![\$])≤(?![$])', r'$\le$'),
    (r'r_coeff', r'$r_{\text{coeff}}$'),
    (r'T_\{sat\}', r'T_{\text{sat}}'), # ensure consistency if needed
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

# Fix double math delimiters that might occur
content = re.sub(r'\$\$([^$]+)\$\$', r'$\1$', content)
# Fix potential triple dollars
content = re.sub(r'\$\$\$', r'$$', content)

# Fix specific instances in Section 8 (now 7)
content = content.replace(r'ṁ(1/ρ_v - 1/ρ_l)', r'$\dot{m}(1/\rho_v - 1/\rho_l)$')
content = content.replace(r'ṁ ∝ (T - T_{\text{sat}})', r'$\dot{m} \propto (T - T_{\text{sat}})$')
content = content.replace(r'ṁ ∝ α_l', r'$\dot{m} \propto \alpha_l$')

# Fix Section 8 heading to Section 7
content = content.replace(r'## 8. References & Related Days', r'## Section 7: References & Related Days')
content = content.replace(r'### 8.1 เอกสารอ้างอิงหลัก (Core References)', r'### 7.1 เอกสารอ้างอิงหลัก (Core References)')
content = content.replace(r'### 8.2 บทเรียนที่เกี่ยวข้องใน Phase 1 (Related Days in Phase 1)', r'### 7.2 บทเรียนที่เกี่ยวข้องใน Phase 1 (Related Days in Phase 1)')
content = content.replace(r'### 8.3 บทเรียนต่อไป (Forward Look: Day 12)', r'### 7.3 บทเรียนต่อไป (Forward Look: Day 12)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

