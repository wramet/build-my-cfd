# 📺 YouTube Resources — Phase 1: Modern C++ Foundation (Days 01–14)

> **How to use:**
> - Paste the search query into YouTube search — no direct links (they change)
> - ⭐ = watch this BEFORE or DURING the session — concept is hard without visuals
> - 💡 = watch AFTER if still confused
> - Sessions without video markers are fine from text alone

---

## Channels Quick Reference

| Channel | Handle | Best for |
|---------|--------|----------|
| The Cherno | `@TheCherno` | Visual OOP, templates, smart pointers — great starting point |
| C++ Weekly (Jason Turner) | `@cppweekly` | Short clips, C++20 focused, concise |
| CppCon | `@CppCon` | Conference talks, authoritative — search "Back to Basics: [topic]" |
| Nicolai Josuttis | search his name on CppCon | Move semantics specialist — wrote the definitive book |
| Klaus Iglberger | search his name on CppCon | Software design, CRTP, policy patterns |

---

## Day 01 — Templates & Generic Programming

### Part 1 — Pattern Identification

| Priority | Topic | Concept | Search Query |
|----------|-------|---------|--------------|
| 💡 | 1.2 Templates — The Solution | Class template syntax, `template<typename T>` | `"Back to Basics Templates" CppCon` |
| 💡 | 1.2 Templates — The Solution | Beginner visual walkthrough of class templates | `"C++ templates tutorial" The Cherno` |
| 💡 | 1.3 Our Design vs OpenFOAM | Why `std::vector<T>` is safer than raw `new[]` | `"C++ std::vector vs raw array"` |
| 💡 | 1.3 Our Design vs OpenFOAM | Owning vs non-owning memory — visual | `"C++ RAII ownership explained" CppCon Back to Basics` |
| ⭐ | 1.4 Template Instantiation | What the compiler actually generates per type | `"C++ template instantiation explained" CppCon` |

### Part 2 — OpenFOAM Source: Historical Comparison

| Priority | Topic | Concept | Search Query |
|----------|-------|---------|--------------|
| 💡 | 2.1 OpenFOAM C++98 style | Why raw `new`/`delete` is dangerous | `"C++ new delete problems" The Cherno` |
| 💡 | 2.2 Macro loops | X-macros pattern (how OpenFOAM avoids code duplication without templates) | `"C++ X macros tutorial"` |
| ⭐ | 2.3 Type Aliases | `typedef` vs `using` — modern alias syntax + template aliases | `"C++ typedef vs using alias" Jason Turner` |

### Part 3 — C++ Mechanics Explained

| Priority | Topic | Concept | Search Query |
|----------|-------|---------|--------------|
| ⭐ | 3.1 Two-Phase Compilation | Why template errors are delayed to call site | `"C++ two phase lookup templates" CppCon` |
| 💡 | 3.2 C++20 Concepts (intro) | Brief intro — full coverage is Day 02 | `"C++20 concepts quick intro" Jason Turner C++ Weekly` |
| ⭐ | 3.3 Template Argument Deduction | How compiler deduces `T` — CTAD in C++17 | `"C++ template argument deduction CTAD" CppCon` |
| ⭐ | 3.4 Why Not virtual? | vtable cost — why CRTP beats virtual for hot loops | `"C++ virtual function overhead vtable" CppCon` |

### Part 4 & 5 — Implementation & Exercises

| Priority | Topic | Concept | Search Query |
|----------|-------|---------|--------------|
| 💡 | 4.1 Build Field<T> | `std::ranges::transform` and `std::reduce` usage | `"C++20 std ranges transform reduce" Jason Turner` |
| 💡 | 5.2–5.3 magnitude/normalize | `std::sqrt`, `std::inner_product` in templates | `"C++ numeric algorithms tutorial"` |

**Notes:**
- Start with Part 1 videos (template syntax) before Part 3 (mechanics)
- **3.4 (Why Not virtual)** is important — connects directly to Day 04 (CRTP). Watch it here so Day 04 makes sense immediately
- **2.3 (typedef vs using)** — very short topic but `using` is everywhere in modern C++, worth 5 min of video
- The Cherno's template series is multi-part — watch in order

---

## Day 02 — C++20 Concepts & Constraints

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | What `concept` and `requires` do | `"C++20 concepts tutorial" CppCon` |
| ⭐ | Why concepts are better than SFINAE | `"Back to Basics Concepts Constraints" CppCon` |
| 💡 | Short concept examples | `"C++20 concepts" Jason Turner C++ Weekly` |

**Notes:**
- C++20 Concepts talks from CppCon 2021–2023 are the clearest — specify year in search
- Jason Turner's C++ Weekly has many short concept clips (5–10 min each)

---

## Day 03 — Mesh-to-Field Relationship

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | Ownership — who is responsible for memory | `"C++ ownership RAII" CppCon Back to Basics` |
| 💡 | Struct layout in memory | `"C++ struct memory layout" CppCon` |
| 💡 | Stack vs heap visual | `"C++ stack heap memory" The Cherno` |

**Notes:**
- No YouTube video covers mesh-to-field specifically (CFD-specific design)
- Focus search on **ownership** and **RAII** — these are the transferable concepts
- "Stack vs heap" by The Cherno is short (~10 min) and uses good diagrams

---

## Day 04 — CRTP — Static Polymorphism

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | What CRTP is and why it exists | `"CRTP C++ tutorial" CppCon` |
| ⭐ | Static vs dynamic dispatch comparison | `"C++ static polymorphism CRTP" Klaus Iglberger` |
| 💡 | vtable overhead (what CRTP avoids) | `"C++ vtable virtual function overhead"` |

**Notes:**
- Klaus Iglberger has excellent talks on design patterns including CRTP
- Search: `"Klaus Iglberger C++ software design CppCon"` — look for his design talk series
- CRTP clicks much faster with a side-by-side diagram of vtable vs direct call

---

## Day 05 — Policy-Based Design

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| 💡 | Policy-based design concept | `"policy based design C++ CppCon"` |
| 💡 | Template template parameters | `"C++ template template parameter tutorial"` |
| 💡 | Pluggable behavior via templates | `"C++ policy classes Andrei Alexandrescu"` |

**Notes:**
- This pattern comes from "Modern C++ Design" by Andrei Alexandrescu (2001) — foundational
- CppCon talks by Alexandrescu are dense but worth watching even at 0.75x speed
- Less YouTube coverage than other topics — the session file is the primary source here

---

## Day 06 — Smart Pointers

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | unique_ptr — ownership, move-only | `"C++ unique_ptr tutorial" The Cherno` |
| ⭐ | RAII pattern visually | `"Back to Basics RAII" CppCon` |
| 💡 | shared_ptr reference counting | `"C++ shared_ptr weak_ptr" The Cherno` |
| 💡 | Why raw new/delete is dangerous | `"C++ smart pointers vs raw pointers"` |

**Notes:**
- The Cherno's smart pointer video is one of the best on YouTube — visual and clear
- Watch `unique_ptr` first, then `shared_ptr`
- **This is the best day to watch video BEFORE reading the session**

---

## Day 07 — Move Semantics

**⭐ HIGHEST PRIORITY VIDEO DAY — text alone is not enough for this topic**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐⭐ | rvalue vs lvalue — what they are | `"lvalue rvalue C++ explained" The Cherno` |
| ⭐⭐ | Move constructor — memory address stays the same | `"C++ move semantics tutorial" The Cherno` |
| ⭐⭐ | Why move is O(1) but copy is O(n) | `"Back to Basics Move Semantics" CppCon 2019` |
| ⭐ | std::move — what it actually does | `"std::move C++ explained" Jason Turner` |
| 💡 | Move semantics in depth (advanced) | `"Nicolai Josuttis move semantics CppCon"` |

**Recommended watch order:**
1. The Cherno — lvalue/rvalue (foundation)
2. The Cherno — move semantics (the main concept)
3. CppCon Back to Basics: Move Semantics (full picture)
4. Josuttis (if still confused after 1–3)

**Notes:**
- You mentioned being stuck here — **watch The Cherno's lvalue/rvalue video first**, then move semantics
- Key visual to look for: a diagram showing the vector's internal pointer *transferring* to the new object without copying the data
- `std::move` does NOT move anything — it just casts to rvalue reference. The move constructor does the actual work.

---

## Day 08 — Perfect Forwarding

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | Universal references (T&&) | `"C++ universal reference forwarding reference CppCon"` |
| ⭐ | std::forward vs std::move | `"std::forward C++ explained" Jason Turner` |
| 💡 | Forwarding reference collapse rules | `"C++ reference collapsing rules CppCon"` |

**Notes:**
- Perfect forwarding builds directly on Day 07 (move semantics) — watch Day 07 videos first
- The difference between `T&&` in template context (forwarding ref) vs non-template (rvalue ref) is confusing — watch a video specifically on this
- Scott Meyers coined "universal reference" — search his name for the original talk

---

## Day 09 — Expression Templates Part 1

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | The temporaries problem (why a+b+c allocates 2 times) | `"C++ expression templates lazy evaluation"` |
| ⭐ | Expression tree mental model | `"C++ expression templates CppCon"` |
| 💡 | Eigen library as a real-world example | `"Eigen C++ expression templates lazy evaluation"` |

**Notes:**
- This is an advanced topic — less beginner content on YouTube
- The Eigen library (used in scientific computing) is the canonical example — searching "Eigen expression templates" shows the real-world payoff
- Focus on understanding the **problem** (N allocations) before the solution

---

## Day 10 — C++20 Modules

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | Modules vs #include — what changes | `"C++20 modules tutorial CppCon"` |
| ⭐ | export module syntax | `"C++20 modules import export" Jason Turner` |
| 💡 | Module interface units | `"C++20 module interface unit CppCon 2021"` |

**Notes:**
- Modules are new (C++20) — look for videos from 2021–2024 specifically
- Jason Turner's C++ Weekly has multiple episodes on modules — search `"C++ Weekly modules"`
- CppCon 2021 and 2022 have good introductory module talks

---

## Day 11 — C++20 Ranges

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | std::views pipeline — what it looks like | `"C++20 ranges views tutorial" CppCon` |
| ⭐ | Lazy evaluation in ranges | `"C++20 ranges lazy" Jason Turner C++ Weekly` |
| 💡 | Range adaptor composition | `"C++20 range adaptors" CppCon` |

**Notes:**
- Jason Turner's C++ Weekly has many short range episodes — excellent for this day
- Search: `"C++ Weekly ranges"` for a list of his range episodes
- Ranges replace raw loops — the visual of a pipeline is key to understanding composition

---

## Day 12 — Type Traits & SFINAE

**Topics that need video:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | What type_traits are and why they exist | `"C++ type traits tutorial" CppCon Back to Basics` |
| ⭐ | if constexpr — compile-time branching | `"if constexpr C++17 explained" Jason Turner` |
| 💡 | SFINAE — how it works and why if constexpr replaced it | `"SFINAE C++ tutorial CppCon"` |

**Notes:**
- "Back to Basics: Templates" CppCon covers SFINAE clearly
- `if constexpr` is the modern replacement for SFINAE — watch it after SFINAE so you understand what problem it solves
- Type traits are used heavily in the Day 13–14 mini-project

---

## Days 13–14 — Mini-Project (Field<T> Library)

**Not C++ concept videos — these are tooling videos for building and testing:**

| Priority | Concept | Search Query |
|----------|---------|--------------|
| ⭐ | Modern CMake project structure | `"Modern CMake tutorial" CppCon` |
| ⭐ | Google Test basics | `"Google Test tutorial C++ gtest"` |
| 💡 | CMake target-based approach | `"CMake targets modern" vector-of-bool` |
| 💡 | Catch2 as alternative to gtest | `"Catch2 tutorial C++ testing"` |

**Notes:**
- "vector-of-bool" YouTube channel has the clearest Modern CMake tutorial
- Google Test ("gtest") is the most common test framework — learn `TEST()`, `EXPECT_EQ()`, `EXPECT_NEAR()`
- Watch CMake video BEFORE Day 13 — you'll need to set up the project structure first

---

## Summary — Watch Priority Order for Phase 1

If you only have time for a few videos, watch these first:

| Order | Day | Topic | Why |
|-------|-----|-------|-----|
| 1 | 07 | Move Semantics (The Cherno) | Foundation of modern C++ resource management |
| 2 | 06 | Smart Pointers (The Cherno) | Builds directly on move semantics |
| 3 | 07 | Back to Basics: Move Semantics (CppCon) | Completes the picture |
| 4 | 04 | CRTP (Klaus Iglberger CppCon) | Hardest mental model without visuals |
| 5 | 09 | Expression Templates (CppCon) | Abstract concept, needs diagram |
| 6 | 13 | Modern CMake (vector-of-bool) | Needed for the mini-project |

---

*Updated: 2026-03-09 | Phase 1 only — Phase 2+ resources added when reached*
