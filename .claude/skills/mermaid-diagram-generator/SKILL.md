---
name: Mermaid Diagram Generator
description: |
  Use this skill when: creating Mermaid diagrams for documentation, visualizing workflows, class hierarchies, data flows, or algorithm steps.
  
  This skill provides templates and best practices for creating clear, readable Mermaid diagrams in markdown.
---

# Mermaid Diagram Generator

This skill provides guidance for creating effective Mermaid diagrams in documentation.

## Diagram Types

### Flowchart (Most Common)

For workflows, decision trees, algorithm steps:

```mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Class Diagram

For class hierarchies, inheritance:

```mermaid
classDiagram
    class BaseClass {
        +attribute: type
        +method()
    }
    BaseClass <|-- DerivedClass
```

### Sequence Diagram

For interactions, message passing:

```mermaid
sequenceDiagram
    participant A as Component A
    participant B as Component B
    A->>B: Request
    B-->>A: Response
```

### State Diagram

For state machines, transitions:

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2: event
    State2 --> [*]
```

## Best Practices

### Naming Conventions

- Use descriptive node IDs: `phaseSystem` not `A`
- Keep labels concise but clear
- Use PascalCase for classes, camelCase for variables

### Styling

Use classDef for visual differentiation:

```mermaid
flowchart TD
    classDef implicit fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef explicit fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    A[Implicit]:::implicit
    B[Explicit]:::explicit
```

### Common Patterns

#### Solver Selection Flowchart

```mermaid
flowchart TD
    Start[Check Topology] --> Sep{Large Interface?}
    Sep -->|Yes| VOF[VOF: interFoam]
    Sep -->|No| Disp{Dispersed?}
    Disp -->|Yes| Dense{Dense?}
    Dense -->|Yes| EE[multiphaseEulerFoam]
    Dense -->|No| DPM[DPMFoam]
```

#### Class Hierarchy

```mermaid
flowchart TD
    A[Base Class] --> B[Derived 1]
    A --> C[Derived 2]
    B --> D[Concrete 1]
    B --> E[Concrete 2]
```

#### PIMPLE Loop Structure

```mermaid
flowchart TD
    A[Time Loop] --> B{PIMPLE Loop}
    B --> C[1. alphaEqns]
    C --> D[2. UEqns]
    D --> E[3. pEqn]
    E --> F[4. EEqns]
    F --> G[5. Turbulence]
    G --> H{Converged?}
    H -->|No| B
    H -->|Yes| I[Write Results]
    I --> A
```

## Syntax Notes

### Avoid Common Errors

1. **Quote labels with special characters**:
   - ✅ `A["Label (with parens)"]`
   - ❌ `A[Label (with parens)]`

2. **Escape HTML in labels**:
   - Use `\n` for newlines, not `<br>`
   - Avoid HTML tags in labels

3. **Direction options**:
   - `TD` = Top to Down
   - `LR` = Left to Right
   - `BT` = Bottom to Top
   - `RL` = Right to Left

### Sub-graphs

Group related nodes:

```mermaid
flowchart TD
    subgraph Phase System
        A[phaseModel]
        B[phasePair]
    end
    subgraph Interfacial Models
        C[dragModel]
        D[liftModel]
    end
    A --> C
```

## When to Use Diagrams

| Content Type | Diagram Type |
|--------------|--------------|
| Algorithm flow | Flowchart TD |
| Class hierarchy | Flowchart or classDiagram |
| Solver comparison | Flowchart with subgraphs |
| State transitions | stateDiagram |
| Communication | sequenceDiagram |
| Data flow | Flowchart LR |

## Integration with Content

Always include:
1. Caption/explanation above or below diagram
2. Reference in surrounding text
3. Key legend if using custom styles
