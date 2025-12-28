# Chemkin Parsing

การใช้งาน Chemkin Files

---

## Overview

> **Chemkin** = Standard format for chemistry

---

## 1. Files

| File | Content |
|------|---------|
| thermo.dat | Thermo properties |
| chem.inp | Reactions |
| tran.dat | Transport |

---

## 2. Convert to OpenFOAM

```bash
chemkinToFoam chem.inp thermo.dat constant/reactions constant/thermo
```

---

## 3. Reaction Format

```
CH4 + 2O2 => CO2 + 2H2O   1.5E11  0.0  24370
```

---

## 4. Usage

```cpp
// constant/chemistryProperties
chemistryReader chemkinReader;
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Convert | chemkinToFoam |
| Read | chemkinReader |

---

## Concept Check

<details>
<summary><b>1. Chemkin ใช้ทำไม?</b></summary>

**Standard format** สำหรับ chemistry mechanisms
</details>

---

## Related Documents

- **ภาพรวม:** [00_Overview.md](00_Overview.md)