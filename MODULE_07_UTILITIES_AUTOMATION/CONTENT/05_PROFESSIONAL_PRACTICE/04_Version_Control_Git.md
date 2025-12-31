# Version Control with Git

การควบคุมเวอร์ชันด้วย Git

---

## 🎯 Learning Objectives

เป้าหมายการเรียนรู้

- **เข้าใจหลักการ** เข้าใจความสำคัญและประโยชน์ของการใช้ Git ในการจัดการ OpenFOAM projects
- **ใช้งานพื้นฐาน** สามารถใช้คำสั่ง Git พื้นฐานเพื่อ track changes และ collaborate กับทีมได้
- **จัดการ .gitignore** สามารถตั้งค่า .gitignore ที่เหมาะสมสำหรับ OpenFOAM projects ได้อย่างถูกต้อง
- **ใช้งาน Git workflow** สามารถใช้ branches, commits, และ merging ในการพัฒนา features ได้อย่างมีประสิทธิภาพ

---

## Overview

> **Git** = Track changes, collaborate effectively

> **Git** = ติดตามการเปลี่ยนแปลง, ทำงานร่วมกันอย่างมีประสิทธิภาพ

---

## 📌 What is Version Control?

Version Control คือระบบสำหรับ tracking changes ในไฟล์และโฟลเดอร์ของ project ตลอดเวลา

**Version Control คือ** ระบบที่ใช้บันทึกและติดตามการเปลี่ยนแปลงทั้งหมดใน project ของคุณ เพื่อให้สามารถ:

- **Track history** ดูประวัติการเปลี่ยนแปลงทั้งหมดได้ตลอดเวลา
- **Compare versions** เปรียบเทียบเวอร์ชันต่างๆ ได้ง่าย
- **Restore previous** กู้คืนเวอร์ชันก่อนหน้าได้หากเกิดข้อผิดพลาด
- **Collaborate** ทำงานร่วมกับทีมได้อย่างมีประสิทธิภาพ
- **Experiment** ทดลอง features ใหม่ๆ โดยไม่กระทบ main version

---

## 💡 Why Use Git for OpenFOAM?

Git จำเป็นอย่างยิ่งสำหรับ OpenFOAM projects เพราะ:

**1. Track Simulation Evolution**
- บันทึกการเปลี่ยนแปลงของ boundary conditions, mesh settings, solver parameters
- ดูได้ว่าเวลาไหนที่ settings ให้ผลลัพธ์ดีที่สุด
- สามารถย้อนกลับไปใช้ settings ที่ผ่านมาได้

**2. Case Versioning**
- แยก versions ของ simulation cases ได้อย่างชัดเจน
- บันทึก validated cases ไว้ reference ในอนาคต
- สร้าง tags สำหรับ cases ที่ผ่าน validation

**3. Collaboration**
- ทำงานร่วมกับทีมได้อย่างมีประสิทธิภาพ
- แก้ไข conflicts ได้ง่ายด้วย merge tools
- Track contributions ของแต่ละคนในทีม

**4. Experimentation Safety**
- สร้าง branches สำหรับ experiments ใหม่ๆ
- ทดลอง solver settings โดยไม่กระทบ main case
- ลบ experiments ที่ล้มเหลวได้อย่างปลอดภัย

**5. Backup & Recovery**
- เก็บ copies ไว้ทั้ง local และ remote (GitHub/GitLab)
- กู้คืน project ได้หากเกิด corruption หรือ data loss
- Remote repositories ทำหน้าที่เป็น backup

---

## 🔧 How to Use Git for OpenFOAM Projects

### Phase 1: Initial Setup

#### 1.1 Initialize Repository

```bash
# Navigate to project directory
cd ~/OpenFOAM/water_tank_case

# Initialize Git
git init

# Check status
git status
```

#### 1.2 Configure .gitignore for OpenFOAM

Create `.gitignore` file:

```bash
# OpenFOAM specific patterns

# Time directories (except 0/)
[0-9]*
!0/

# Parallel processing directories
processor*/

# Post-processing and logs
postProcessing/
log.*
log.*
*.foam

# Compiled objects and libraries
*.o
*.so
*.a

# IDE and editor files
.vscode/
.idea/
*.swp
*~

# OS files
.DS_Store
Thumbs.db
```

**Explanation:**
- `[0-9]*` — Ignore time directories (0.1, 1, 2.5, etc.)
- `!0/` — Keep initial conditions directory
- `processor*/` — Ignore parallel processor directories
- `log.*` — Ignore solver logs
- `.foam` — Ignore ParaView session files

#### 1.3 First Commit

```bash
# Add all tracked files
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial commit: water tank simulation case"
```

---

### Phase 2: Basic Git Workflow

#### 2.1 Understanding Git States

```
Untracked → Staged → Committed
    ↓           ↓         ↓
  git add   git add   git commit
```

**Example Scenario:**

```bash
# 1. Modify boundary condition file
vim constant/polyMesh/boundary

# 2. Check status (shows modified files)
git status

# 3. Stage the change
git add constant/polyMesh/boundary

# 4. Commit with descriptive message
git commit -m "Change inlet BC from fixedValue to zeroGradient"
```

#### 2.2 Working with Branches

Branches ใช้สำหรับแยก development work ออกจาก main line:

```bash
# Create new branch for feature
git checkout -b feature/turbulence-model

# Make changes to turbulence model
vim constant/turbulenceProperties

# Commit changes
git add constant/turbulenceProperties
git commit -m "Switch from kEpsilon to kOmegaSST"

# Return to main branch
git checkout master

# Merge feature branch
git merge feature/turbulence-model

# Delete feature branch (optional)
git branch -d feature/turbulence-model
```

**Best Practices:**
- สร้าง branch ใหม่สำหรับแต่ละ feature/experiment
- ใช้ descriptive branch names
- Merge กลับเข้า main branch เมื่อ feature เสร็จสมบูรณ์

#### 2.3 Viewing History

```bash
# Show commit history
git log

# Show history with graph
git log --graph --oneline --all

# Show changes in specific commit
git show <commit-hash>

# Show differences between commits
git diff HEAD~1 HEAD
```

---

### Phase 3: Remote Collaboration

#### 3.1 Connect to Remote Repository

```bash
# Add remote repository (GitHub/GitLab)
git remote add origin git@github.com:username/openfoam-cases.git

# Verify remote
git remote -v

# Push to remote
git push -u origin master
```

#### 3.2 Pull Latest Changes

```bash
# Fetch and merge changes from remote
git pull origin master

# Or fetch and rebase (cleaner history)
git pull --rebase origin master
```

#### 3.3 Handling Merge Conflicts

เมื่อเกิด conflicts:

```bash
# 1. Git will mark conflicts in files
<<<<<<< HEAD
inlet    { type zeroGradient; }
=======
inlet    { type fixedValue; value uniform 10; }
>>>>>>> feature/new-bc

# 2. Edit to resolve conflict manually
inlet    { type fixedValue; value uniform 10; }

# 3. Stage resolved file
git add constant/polyMesh/boundary

# 4. Complete merge
git commit
```

---

### Phase 4: Git Tags for Validated Cases

Tags ใช้สำหรับ mark important milestones ใน OpenFOAM projects:

```bash
# 1. Create annotated tag
git tag -a v1.0 -m "Validated: Results match experimental data within 5%"

# 2. Add details to tag
git tag -a v1.1 -m "Improved mesh quality: max non-orthogonality 65°"

# 3. Push tags to remote
git push origin v1.0
git push --tags

# 4. Show tag information
git show v1.0

# 5. List all tags
git tag -l

# 6. Checkout specific tag (review past results)
git checkout v1.0
```

**When to Use Tags:**
- ✅ After successful validation against experimental data
- ✅ When publishing simulation results
- ✅ Before major refactoring
- ✅ For case studies or benchmarks
- ✅ Release of solver customization

---

### Phase 5: Practical OpenFOAM Git Workflow

#### 5.1 Typical Development Cycle

```bash
# Step 1: Start from stable baseline
git checkout -b experiment/higher-resolution-mesh

# Step 2: Modify mesh parameters
vim system/blockMeshDict

# Step 3: Generate new mesh
blockMesh

# Step 4: Check changes
git status
git diff system/blockMeshDict

# Step 5: Commit if satisfied
git add system/blockMeshDict
git commit -m "Increase mesh resolution: 200k cells → 400k cells"

# Step 6: Run simulation
simpleFoam > log.simpleFoam &

# Step 7: After completion, check results
paraFoam -builtin

# Step 8: If good, merge back
git checkout master
git merge experiment/higher-resolution-mesh
git branch -d experiment/higher-resolution-mesh

# Step 9: Tag validated version
git tag -a v2.0 -m "Validated: Mesh independence study completed"
```

#### 5.2 Collaborative Workflow Example

```bash
# Team Member A: Create feature branch
git checkout -b feature/wave-boundary-condition

# Make changes, commit regularly
git add 0/
git commit -m "Implement wave BC at inlet"

# Push branch to remote for review
git push -u origin feature/wave-boundary-condition

# Team Member B: Pull latest changes
git fetch origin
git checkout feature/wave-boundary-condition
# Review and suggest changes...

# Team Member A: Incorporate feedback
git add constant/polyMesh/boundary
git commit -m "Adjust wave frequency based on feedback"

# Merge to master after approval
git checkout master
git merge feature/wave-boundary-condition
git push origin master
```

---

## 📚 Quick Reference

### Common Git Commands

| Task | Command | Description |
|------|---------|-------------|
| **Initialize** | `git init` | Create new repository |
| **Clone** | `git clone <url>` | Copy remote repository |
| **Status** | `git status` | Show working tree status |
| **Add** | `git add <file>` | Stage changes |
| **Commit** | `git commit -m "msg"` | Save staged changes |
| **Push** | `git push` | Send commits to remote |
| **Pull** | `git pull` | Fetch and merge from remote |
| **Branch** | `git branch <name>` | Create new branch |
| **Checkout** | `git checkout <branch>` | Switch to branch |
| **Merge** | `git merge <branch>` | Combine branches |
| **Log** | `git log` | Show commit history |
| **Diff** | `git diff` | Show changes |
| **Tag** | `git tag -a v1.0 -m "msg"` | Create annotated tag |

### OpenFOAM-Specific Workflow

| Scenario | Commands |
|----------|----------|
| **New Case** | `git init`, create `.gitignore`, `git add .`, `git commit -m "Initial"` |
| **Test New BC** | `git checkout -b test/new-bc`, edit files, `git commit -am "Test new BC"` |
| **Validated Case** | `git tag -a v1.0 -m "Validated: ..."` |
| **Parallel Ready** | Add `processor*/` to `.gitignore` |
| **Clean Working Dir** | `git clean -fd` (remove untracked files) |

---

## 🎯 Key Takeaways

สรุปสิ่งสำคัญ

**1. Version Control is Essential**
- Git track การเปลี่ยนแปลงทั้งหมดใน OpenFOAM projects
- สามารถย้อนกลับไปใช้ settings ที่ผ่านมาได้
- Collaboration กับทีมทำได้อย่างมีประสิทธิภาพ

**2. Proper .gitignore Configuration**
- Exclude generated files: time directories, processor dirs, logs
- Keep essential files: 0/, constant/, system/, Allrun*, Allclean*
- Prevent repository bloat with OpenFOAM-specific patterns

**3. Branching Strategy**
- Use branches for experiments and features
- Keep main branch stable at all times
- Merge only validated changes back to main

**4. Commit Discipline**
- Write descriptive commit messages
- Commit frequently with logical changes
- One logical change per commit

**5. Tag Validated Cases**
- Use tags to mark validated simulation cases
- Include validation details in tag messages
- Tags serve as quality checkpoints

**6. Remote Repositories**
- Use GitHub/GitLab for backup and collaboration
- Push regularly to prevent data loss
- Pull before starting work to stay synchronized

**7. OpenFOAM-Specific Best Practices**
- Track solver configurations, not results
- Use branches for mesh studies, parameter sweeps
- Tag cases that match experimental data
- Document validation criteria in commit messages

---

## 🧠 Concept Check

<details>
<summary><b>1. .gitignore สำหรับ OpenFOAM ควร include อะไรบ้าง?</b></summary>

**Generated and temporary files:**
- Time directories: `[0-9]*` (but keep `!0/`)
- Parallel processing: `processor*/`
- Logs and processing: `log.*`, `postProcessing/`
- ParaView: `*.foam`

**Reason:** ไฟล์เหล่านี้ generate ใหม่ได้เสมอ และขนาดใหญ่ ไม่ควรเก็บใน Git
</details>

<details>
<summary><b>2. เมื่อไหร่ควรใช้ git tags ใน OpenFOAM projects?</b></summary>

**ใช้ tags เมื่อ:**
- ✅ Simulation results validated against experimental data
- ✅ เสร็จสิ้น mesh independence study
- ✅ Publishing ผลงานวิจัย
- ✅ สร้าง benchmark case สำหรับ reference
- ✅ ก่อนทำ major refactoring

**Tags ทำหน้าที่เป็น quality checkpoints** และช่วย identify ว่า which versions ถูก validate แล้ว
</details>

<details>
<summary><b>3. Branch workflow ที่ดีสำหรับ OpenFOAM คืออะไร?</b></summary>

**Recommended workflow:**

```bash
# 1. Create branch for experiment
git checkout -b experiment/<name>

# 2. Make changes, test, commit
git commit -am "Describe change and results"

# 3. If experiment successful:
git checkout master
git merge experiment/<name>

# 4. If experiment failed:
git branch -D experiment/<name>  # Just delete it
```

**Benefits:**
- Master branch 始终保持 stable
- Failed experiments ไม่สร้าง clutter
- Easy to track which changes produced which results
</details>

<details>
<summary><b>4. ทำไม commit messages ถึงสำคัญใน OpenFOAM?</b></summary>

**Good commit messages:**
```
❌ Bad: "update files"
✅ Good: "Change inlet BC to match experimental conditions (Re=5000)"
✅ Better: "Tune kEpsilon model: Cmu=0.09 improves convergence (residuals < 1e-5)"
```

**Why important:**
- Track ว่า parameter changes ไหน affect results อย่างไร
- ย้อนกลับไปหา settings ที่ให้ผลดีได้
- Team members เข้าใจ context ของ changes
- Debugging และ reproducibility ทำได้ง่ายขึ้น

**Best practice:** ใส่ physical meaning และ impact on results ใน commit messages
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Project Organization:** [01_Project_Organization.md](01_Project_Organization.md)
- **Documentation Standards:** [02_Documentation_Standards.md](02_Documentation_Standards.md)
- **Testing & Validation:** [05_Testing_Validation.md](05_Testing_Validation.md)