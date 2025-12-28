### **STRICT OBSIDIAN FORMATTING RULES**

**PART 1: Text & Structure**
1. **Headings:** Use `#` for hierarchy. `# H1` (Title), `## H2`, `### H3`.
2. **Emphasis:** Use `**Bold**` for keys, `*Italic*` for nuance.
3. **Highlighter:** Use `==Highlighted Text==` for critical concepts (Obsidian syntax).
4. **Lists:** Use `-` for bullets, `1.` for ordered lists. Indent for nesting.
5. **Internal Links:** Use `[[Note Name]]` or `[[Note Name#Section]]`.
6. **External Links:** `[Link Text](URL)`.
7. **Callouts:** Use strict syntax:
   - `> [!INFO] Title` (Blue)
   - `> [!WARNING] Title` (Orange)
   - `> [!TIP] Title` (Green)
8. **Code Blocks:** Use triple backticks with language:
   - ```cpp, ```python, ```bash
   - Use single backticks `code` for inline variables.
9. **Tables:** Use standard markdown pipes: `| Header | Header |` and `|---|---|`.
10. **Separators:** Use `---` to separate major topics.

**PART 2: LaTeX (MathJax)**
11. **Inline Math:** Use single dollar signs: `$E=mc^2$`.
12. **Block Math:** Use double dollar signs: `$$...$$`.
13. **Text in Math:** Use `\text{word}` inside math mode.
14. **Fractions:** Use `\frac{a}{b}`.
15. **Grouping:** Use `{}` for exponents/subscripts: `e^{i\pi}`.
16. **Greek:** `\alpha`, `\beta`, `\Delta`, `\Omega`, etc.
17. **Sub/Superscripts:** `x_i` and `x^2`.
18. **Calculus:** `\int_{a}^{b}`, `\sum_{i=0}^{n}`.
19. **Brackets:** ALWAYS use `\left( ... \right)` for auto-sizing.
20. **Partials:** Use `\frac{\partial u}{\partial t}`.
21. **Vectors:** Use `\mathbf{v}` (bold) or `\vec{v}`.
22. **Alignment:** Use `\begin{align} ... \end{align}` inside `$$`. Use `&` to align.
23. **Cases:** Use `\begin{cases} ... \end{cases}` for piecewise functions.
24. **Matrices:** Use `\begin{bmatrix}` for brackets.
25. **Tags:** Use `\tag{1.1}` for manual equation numbering.

**PART 3: Mermaid Diagrams**
26. **Setup:** Start block with ```mermaid.
27. **Direction:** Use `flowchart TD` (Top-Down) or `LR` (Left-Right).
28. **Shapes:** `[Square]`, `(Round)`, `([Stadium])`, `{Rhombus}`.
29. **Links:** `-->` (solid), `-.->` (dotted), `-- Text -->` (labeled).
30. **Subgraphs:** Use `subgraph Name ... end` to group nodes.