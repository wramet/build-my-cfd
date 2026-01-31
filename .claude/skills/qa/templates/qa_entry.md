# Q&A Entry Templates

## Single Q&A Entry Template

```markdown
### {EMOJI} {QUESTION_TYPE} Question
**Section:** {SECTION_NAME} | **Asked:** {TIMESTAMP}

**Question:**
{QUESTION_TEXT}

**Answer:**
{AI_ANSWER}

**Tags:** {TAG_LIST}

**Related Content:**
> {CONTEXT_SNIPPET}

---
```

## Emoji Mapping

| Question Type | Emoji | Description |
|---------------|-------|-------------|
| clarification | 💬 | Request for explanation of unclear concepts |
| deeper-dive | 🔍 | Explore beyond current content |
| implementation | 💻 | Practical coding/implementation questions |
| debugging | 🐛 | Troubleshooting help |
| connection | 🔗 | Link to other topics/concepts |

## Section Template (for insertion into walkthrough)

```markdown
---

## Active Learning Q&A

*Your questions and answers from learning sessions*

> 💡 **Tip:** Use `/qa --day {N} "your question"` to ask questions and have them recorded here!

---
```

## Multi-View Organization Template

```markdown
## Active Learning Q&A

*Your personal learning journey captured as questions and answers*

---

### 📚 By Learning Session (Chronological)

#### Session {TIMESTAMP}

**{EMOJI} {SECTION} Section - {TYPE}**

**Question:**
{QUESTION}

**Answer:**
{ANSWER}
*(Answered by {MODEL})*

**Tags:** {TAGS}

---

### 🎯 By Content Section

#### Theory Questions ({COUNT} questions)

**Q1:** {QUESTION_SUMMARY}
*(Asked: {TIMESTAMP})*
[View Answer]

#### Code Questions ({COUNT} questions)

**Q1:** {QUESTION_SUMMARY}
*(Asked: {TIMESTAMP})*
[View Answer]

#### Implementation Questions ({COUNT} questions)

**Q1:** {QUESTION_SUMMARY}
*(Asked: {TIMESTAMP})*
[View Answer]

---

### 🏷️ By Topic

#### {TOPIC_NAME} ({COUNT} questions)

**Q1:** {QUESTION_SUMMARY}
*({SECTION} section, {TIMESTAMP})*
[View Answer]

#### {TOPIC_NAME} ({COUNT} questions)

...

---

### 🔍 Search Your Q&A

> **Tip:** Questions are tagged for easy search. Common topics: `FVM`, `discretization`, `boundary`, `turbulence`, `mesh`
```
