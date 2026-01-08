import re

file_path = 'daily_learning/2026-01-12.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Specific replacements for common variable names
replacements = [
    (r'(?<![\\$])\\\dot{{m}}(?![\\$])', r'\\$\dot{{m}}$'),
    (r'(?<![\\$])\\nabla(?!\\$)', r'\\$\\nabla$'),
    (r'(?<![\\$])\\alpha(?!\\$)', r'\\$\\alpha$'),
    (r'(?<![\\$])\\rho(?!\\$)', r'\\$\\rho$'),
    (r'(?<![\\$])\\tau(?!\\$)', r'\\$\\tau$'),
    (r'(?<![\\$])\\phi(?!\\$)', r'\\$\\phi$'),
    (r'(?<![\\$])\\le(?!\\$)', r'\\$\\le$'),
    (r'(?<![\\$])\\partial(?!\\$)', r'\\$\\partial$'),
    (r'(?<![\\$])\\mu(?!\\$)', r'\\$\\mu$'),
    (r'(?<![\\$])\\nu(?!\\$)', r'\\$\\nu$'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

# Additional simple replacements for safety
content = content.replace('ṁ', '$\dot{m}$')
content = content.replace('∇', '$\nabla$')
content = content.replace('α', '$\alpha$')
content = content.replace('ρ', '$\rho$')
content = content.replace('τ', '$\tau$')
content = content.replace('ϕ', '$\phi$')
content = content.replace('≤', '$\le$')
content = content.replace('∂', '$\partial$')
content = content.replace('µ', '$\mu$')
content = content.replace('ν', '$\nu$')

# Fix mixed math/text like $\rho$_l -> $\rho_l$
content = re.sub(r'\\$\s*\\\(\\w+\\)\\s*\$(\_[a-zA-Z0-9]+)', r'\\\\1\\2$', content) 
content = re.sub(r'\\$\s*\\\(\\w+\\)\\s*\$(\^[a-zA-Z0-9]+)', r'\\\\1\\2$', content) 

# Fix broken double dollars
content = content.replace('$$$\', '$$\\')
content = content.replace('$$ \', '$$ \')

# Fix specific issues seen in text
content = content.replace('$\rho$_l', '$\rho_l$')
content = content.replace('$\rho$_v', '$\rho_v$')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)