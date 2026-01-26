# 🎥 Animation Techniques: From OpenFOAM Data to Professional Video

> **[!TIP] Why Animation Matters for CFD Engineers**
> Animation is not just about aesthetics—it's a **powerful communication tool** that helps:
> - **Engineers recognize** complex flow patterns (Vortex shedding, Recirculation zones) invisible in static images
> - **Managers/clients understand** results instantly without reading dozens of graphs
> - **Detect errors** more easily (e.g., Unphysical oscillations) when viewed as motion
> - **Validate findings** by comparing flow patterns with theory or experiments

**Learning Objectives**: Create smooth, meaningful, and engaging CFD result videos with emphasis on storytelling through motion graphics
**Difficulty Level**: Intermediate-Advanced
**Prerequisites**: 
- Completed [01_ParaView_Visualization.md](01_ParaView_Visualization.md) §4-5 (Advanced ParaView operations)
- Basic understanding of time-dependent OpenFOAM simulations
- Familiarity with video editing software (DaVinci Resolve, Premiere, or similar)

---

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Plan animations** using industry-standard storyboarding templates
2. **Configure OpenFOAM** output settings specifically for animation production
3. **Choose appropriate frame rates** and export formats based on project requirements
4. **Create professional animations** combining flow visualization with data overlays
5. **Synchronize audio** narration with visual elements
6. **Export production-ready videos** using optimal encoding settings

---

## 🔧 Prerequisites Check

Before proceeding, ensure you have:

- [ ] OpenFOAM case with time-dependent results (or ability to run transient simulation)
- [ ] ParaView 5.9+ with animation tools enabled
- [ ] FFmpeg installed for video encoding (`ffmpeg -version` in terminal)
- [ ] Video editing software (DaVinci Resolve [free], Adobe Premiere, or similar)
- [ ] At least 10GB free disk space for render output (typical animation project)
- [ ] Completed the visualization pipeline from [01_ParaView_Visualization.md](01_ParaView_Visualization.md)

---

## 🎯 The 3W Framework: Animation Production

### WHAT is Animation Production?

Animation production transforms raw OpenFOAM data into compelling visual narratives by:
- Sequencing visual data over time or space
- Adding camera movement and transitions
- Incorporating data overlays (graphs, annotations)
- Applying professional post-processing (color grading, audio)

### WHY Use Animation?

| Application | Benefit | Example Use Case |
|-------------|---------|------------------|
| **Technical Analysis** | Spot transient phenomena, verify convergence | Detect vortex shedding frequency, monitor shock wave propagation |
| **Design Communication** | Convey complex results to non-technical stakeholders | Present HVAC airflow patterns to architects, show combustion efficiency to clients |
| **Conference Presentation** | Engage audience, stand out from static-image presenters | AIAA/ASME presentations with 60-second result previews |
| **Educational Content** | Build intuition for flow physics | Online course modules demonstrating boundary layer development |

### WHEN to Use Each Animation Type?

| Animation Type | Data Requirement | Typical Duration | Production Time |
|----------------|------------------|------------------|-----------------|
| **Temporal** | Time directories (0/, 0.1/, 0.2/...) | 5-30 seconds | 2-8 hours |
| **Spatial (Fly-through)** | Single time snapshot | 10-60 seconds | 4-12 hours |
| **Parameter Sweep** | Multiple cases or sampled data | 15-45 seconds | 6-16 hours |
| **Combined (Hybrid)** | Time + spatial movement | 20-90 seconds | 8-24 hours |

---

## 📋 Step 1: Storyboarding Template

> **[!IMPORTANT] Don't Skip Planning!**
> Professional animists spend 60-70% of time planning. A good storyboard prevents:
> - Rendering animations you'll discard
> - Missing key visual moments
> - Inconsistent pacing and narrative flow

### Storyboarding Template

Copy and adapt this template for your animation:

```markdown
# Animation Storyboard: [Case Name]
## Metadata
- **Total Duration**: ___ seconds
- **Target Audience**: [Technical / Non-technical / Mixed]
- **Primary Message**: [One sentence describing main takeaway]
- **Audio**: [Voiceover / Music only / Live presentation]

## Scene Breakdown

| Scene | Duration | Visual Description | Camera Action | Data Overlay | Audio/Text |
|-------|----------|-------------------|---------------|--------------|------------|
| 1 | 0-3s | Establish shot: full geometry view | Slow zoom in | Case name, parameters | Narrator: "This simulation shows..." |
| 2 | 3-8s | Velocity magnitude, slice at critical plane | Pan across section | Real-time flow rate display | Music swells |
| 3 | 8-15s | Vortex shedding visualization | Orbit around vortex | Frequency counter | "Notice the periodic shedding at..." |
| 4 | 15-22s | Particle tracers following flow | Follow particle stream | Path lines | Text: Key insight #1 |
| 5 | 22-30s | Summary: comparison with experiment | Split view: sim vs exp | Error percentage | "Results match within 5%" |

## Key Moments to Emphasize
- [ ] Time ___: Peak velocity reaches
- [ ] Time ___: Recirculation zone forms
- [ ] Time ___: Steady state achieved

## Technical Notes
- Time range: [0 to ___ seconds]
- Write interval: ___ (must capture key moments)
- Critical views: [list specific ParaView states to save]
```

### Storyboarding Example: Cylinder Wake Animation

```markdown
# Animation Storyboard: Vortex Shedding Behind Cylinder (Re=1000)
## Metadata
- **Total Duration**: 20 seconds
- **Target Audience**: Technical (fluid dynamics conference)
- **Primary Message**: Demonstrates Strouhal number validation
- **Audio**: Voiceover with background ambient music

| Scene | Duration | Visual Description | Camera Action | Data Overlay | Audio/Text |
|-------|----------|-------------------|---------------|--------------|------------|
| 1 | 0-3s | Full domain: cylinder + wake | Static wide shot | Re=1000, geometry dims | "At Reynolds number 1000..." |
| 2 | 3-8s | Vorticity contours, z-slice | Slow orbit around cylinder | Real-time vorticity range | "Vortices shed alternately..." |
| 3 | 8-14s | Probe point data: lift coefficient history | Zoom to graph view | Cl(t) curve with vertical time marker | "Lift coefficient oscillates at..." |
| 4 | 14-17s | Particle tracers from cylinder surface | Follow particle stream | St = f·D/U calculation | "Giving Strouhal number 0.21" |
| 5 | 17-20s | Side-by-side: simulation vs Williamson (1996) | Split view | St_exp=0.21, St_sim=0.21 | "Matching literature within 1%" |

## Key Moments to Emphasize
- [x] Time 2.0s: First vortex detaches
- [x] Time 5.0s: Periodic shedding established
- [x] Time 10.0s: Stable Cl oscillation amplitude

## Technical Notes
- Time range: [0 to 15 seconds]
- Write interval: 0.05 (300 time directories for smooth motion)
- Critical views: 
  1. Wide angle (camera position: [5, 5, 5])
  2. Close-up vortex (camera position: [0.5, 2, 0])
```

---

## 📝 Step 2: Configure OpenFOAM for Animation

> **[!NOTE] OpenFOAM Context: Data Storage for Animation**
> Before creating animations, configure result storage in `system/controlDict` for animation production:
> - **`writeInterval`**: Controls output frequency (e.g., `0.01;` for detailed transient cases)
> - **`writeFormat`**: Use `binary` instead of `ascii` to save space and write faster
> - **`writeCompression`**: Use `on;` to compress files (but ParaView may read slightly slower)
>
> **Function Objects** for Animation:
> ```cpp
> // In system/controlDict
> functions
> {
>     // For Real-time Graph Plotting
>     probeLocation
>     {
>         type        sets;
>         set         probeCell;
>         surface     sampleSurface;
>         fields      (p U);
>     }
> }
> ```

### Complete controlDict Template for Animation

```cpp
// system/controlDict - Optimized for Animation Production
application simpleFoam;

startFrom latestTime;

startTime 0;

endTime 10.0;  // Adjust based on physical time needed

deltaT 0.001;  // Small time step for accuracy

writeControl timeStep;
writeInterval 100;  // Output every 0.1s (100 * 0.001)

// CRITICAL FOR ANIMATION: Consistent output timing
writeFormat binary;
writePrecision 10;
writeCompression off;  // Faster write, decompress manually if needed

timeFormat general;
timePrecision 6;

runTimeModifiable yes;

// ========================================
// FUNCTION OBJECTS FOR ANIMATION DATA
// ========================================
functions
{
    // 1. Probe Points for Graph Overlays
    probes
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        outputControl   timeStep;
        outputInterval  100;  // Match writeInterval
        probeLocations
        (
            (0.05 0.0 0.0)     // Point 1: Near inlet
            (0.5 0.0 0.0)      // Point 2: Mid-domain
            (0.95 0.0 0.0)     // Point 3: Near outlet
        );
        fields          (p U k epsilon omega);
        setFormat       csv;
        interpolationScheme cellPoint;
    }
    
    // 2. Surface Sampling for Cross-section Animation
    cuttingPlaneMid
    {
        type            surfaces;
        functionObjectLibs ("libsampling.so");
        outputControl   outputTime;
        surfaceFormat   vtk;
        fields          (p U);
        interpolationScheme cellPoint;
        
        surfaces
        {
            zMidPlane
            {
                type        cuttingPlane;
                plane       pointAndNormal;
                pointAndNormalDict
                {
                    basePoint       (0 0 0);
                    normalVector    (0 0 1);
                }
                interpolate true;
            }
        }
    }
    
    // 3. Force Coefficients for Lift/Drag Graphs
    forceCoeffs
    {
        type        forceCoeffs;
        functionObjectLibs ("libforces.so");
        outputControl   timeStep;
        outputInterval  100;
        
        patches     (cylinder);  // Adjust to your geometry
        rho         rhoInf;
        rhoInf      1.225;  // kg/m³
        CofR        (0 0 0);  // Center of rotation
        liftDir     (0 1 0);
        dragDir     (1 0 0);
        pitchAxis   (0 0 1);
        magUInf     10.0;
        lRef        0.1;    // Reference length
        Aref        0.01;   // Reference area
    }
    
    // 4. Flow Rate for Mass Conservation Check
    flowRate
    {
        type            surfaceRegion;
        functionObjectLibs ("libsurfaceFunctionObjects.so");
        outputControl   timeStep;
        outputInterval  100;
        
        operation       sum;
        surfaceFormat   none;
        regionType      patch;
        name            inlet;
        fields          (phi);
    }
}
```

### Decision Guide: Write Interval Selection

| Desired Output | Physical Time | Recommended writeInterval | Resulting Files |
|----------------|---------------|---------------------------|-----------------|
| **Slow diffusion** (0-100s) | 100s | 1.0 | 100 files |
| **Moderate flow** (0-10s) | 10s | 0.05 | 200 files |
| **Fast transient** (0-1s) | 1s | 0.005 | 200 files |
| **Vortex shedding** (0-5s) | 5s | 0.02 | 250 files |
| **High-frequency** (0-0.5s) | 0.5s | 0.001 | 500 files |

**Formula**: `Number of Time Directories = (endTime - startTime) / writeInterval`

> **[!WARNING] Storage Considerations**
> - Binary format: ~10-50 MB per directory (3D case)
> - 500 directories × 30 MB = **15 GB** typical project
> - Plan 2-3× working space for temporary render files

---

## 🎬 Step 3: Frame Rate Decision Guide

> **[!NOTE] OpenFOAM Context: Real Time vs. Animation Time**
> Understanding "time" in OpenFOAM vs Animation:
> - **OpenFOAM Time (`startTime`, `endTime`)**: Set in `controlDict` via `startFrom` and `stopAt`
> - **Time Step (`deltaT`)**: Set in `controlDict` (or adaptive time stepping)
> - **Write Interval**: Set in `controlDict` (e.g., `writeInterval 0.01;`) → **This is the number of Time directories ParaView will see**
> - **Animation Frames**: Purely a ParaView/Export concern (unrelated to OpenFOAM)
>
> **Example**: If `writeInterval` = 0.1s and `endTime` = 10s → 100 Time directories → For 30fps animation lasting 5 seconds → Need 150 frames → ParaView will interpolate between 100 Time directories to get 150 frames

### Frame Rate Comparison Table

| Frame Rate | Best Use Cases | Pros | Cons | File Size (1 min video) |
|------------|----------------|------|------|------------------------|
| **24 fps** | Cinematic presentations, film-like aesthetic | Traditional film speed, lower render time | May appear choppy for fast flows | ~80 MB (H.264, CRF 20) |
| **30 fps** | **Standard choice** for technical presentations | Smooth motion, standard for web video | Slightly larger files | ~100 MB |
| **48 fps** | Fast transient phenomena (shock waves, rapid vortex shedding) | Very smooth, captures fast motion | Large files, longer render | ~150 MB |
| **60 fps** | Ultra-detailed analysis, high-quality final output | Extremely smooth, professional | **2× render time**, very large files | ~180 MB |

### Decision Tree: Choosing Your Frame Rate

```
Is this for...
├─ Technical analysis (frame-by-frame review)?
│  └─ Use 48-60 fps (capture every detail)
│
├─ Conference presentation (standard projector)?
│  └─ Use 30 fps (balanced quality/size)
│
├─ Web video (YouTube, Vimeo)?
│  └─ Use 30 fps (platform standard)
│
├─ Quick draft/preview?
│  └─ Use 15-24 fps (faster iteration)
│
└─ Cinematic/artsistic visualization?
   └─ Use 24 fps (film aesthetic)
```

### Calculating Required Frames

**Scenario**: You have 200 time directories covering 10 physical seconds, and want a 30 fps animation:

```
Option 1: Real-time playback (1:1 time scaling)
- Desired video duration = 10 seconds
- Frame rate = 30 fps
- Required frames = 10 s × 30 fps = 300 frames
- ParaView interpolates: 300 frames / 200 directories = 1.5 frames per directory

Option 2: Slow-motion (2:1 time scaling)
- Desired video duration = 20 seconds (slow down by 2×)
- Frame rate = 30 fps
- Required frames = 20 s × 30 fps = 600 frames
- ParaView interpolates: 600 frames / 200 directories = 3 frames per directory

Option 3: Time-lapse (1:4 time scaling)
- Desired video duration = 2.5 seconds (speed up by 4×)
- Frame rate = 30 fps
- Required frames = 2.5 s × 30 fps = 75 frames
- ParaView skips: 75 frames / 200 directories = 0.375 (skips 60% of data)
```

**Recommendation**: For most CFD animations, use **30 fps with 2×-4× slow-motion** to let viewers appreciate flow details.

---

## 📊 Step 4: ParaView Animation Setup

### 4.1 Animation View Interface

The **Animation View** (View → Animation View) is your control center:

### 4.2 Animation Modes: Sequence vs Real Time

| Mode | Description | When to Use | Settings |
|------|-------------|-------------|----------|
| **Sequence** | Fixed number of frames, ParaView calculates time per frame | **Video production** (standard choice) | Set NumberOfFrames to match: `Video Duration (s) × Frame Rate` |
| **Real Time** | Plays back at simulation time speed | Debugging, analysis only | NOT recommended for export (inconsistent timing) |

### 4.3 Keyframing Workflow

**Step 1: Create Camera Track**
```
Animation View → Click "+" next to "Camera" → Rename to "MainCamera"
```

**Step 2: Set Keyframes**
1. Scrub timeline to desired time (e.g., 0.0s)
2. Position camera using 3D controls
3. Click keyframe icon (diamond) OR press `K`
4. Repeat for 3-5 keyframe positions

**Step 3: Easing (Optional)**
- Right-click keyframe → Interpolation type
- **Linear**: Constant speed (jerkier motion)
- **Spline/Bezier**: Smooth acceleration (professional look)

### 4.4 Temporal Interpolation

When your write interval is coarse but you want smooth animation:

**When to Use Temporal Interpolator**:
- Write interval ≥ 0.1s (choppy animation)
- Want 60fps but have <100 time directories
- Need to slow down fast phenomena

**Implementation**:
```
Filters → Temporal Interpolator
- Interpolation Method: Linear (default) or Cubic (smoother)
- Relative Tolerance: 0.01 (default)
```

> **[!WARNING] Interpolation Limitations**
> Temporal Interpolator uses **Linear Interpolation** between time steps:
> - For fast-changing flows (high-frequency fluctuations), interpolated data may not match physics
> - For dynamic meshes, topology errors may occur
> - **Best practice**: Always validate by comparing interpolated frames with actual time snapshots

### 4.5 Creating Data Overlays

#### A. Plot Selection Over Time

**Use Case**: Show how a variable evolves at a specific location

```python
# 1. Select point(s) of interest using Interactive Selection
# 2. Filters → Plot Selection Over Time
# 3. In Animation View, add "Time Marker" to show current position on graph
```

#### B. Programmable Annotation

**Use Case**: Display custom real-time data (e.g., Reynolds number, flow rate)

```python
# Programmable Filter (Output: vtkTable)
# Script:

import numpy as np

# Get current time
t = inputs[0].Information.Get(vtk.vtkDataObject.DATA_TIME_STEP())

# Calculate custom metric (example: calculate max velocity)
input_data = inputs[0].GetPointData()
U = input_data.GetArray('U')
vel_mag = np.sqrt(U[:,0]**2 + U[:,1]**2 + U[:,2]**2)
max_vel = np.max(vel_mag)

# Create output table
output.RowData.append(t, "Time (s)")
output.RowData.append(max_vel, "Max Velocity (m/s)")

# Add derived metrics
Re = (max_vel * 0.1) / 1.5e-5  # Re = ρUL/μ (simplified)
output.RowData.append(Re, "Reynolds Number")
```

Then use **Text Source** or **Python Annotation** to display:
```
Time:1${Time (s):.2f} s
Max Velocity:1${Max Velocity (m/s):.2f} m/s
Re:1${Reynolds Number:.0f}
```

#### C. Graph Synchronization

**Goal**: Vertical time marker on graph moves with animation

```
Animation View → Add Track → Select "PlotSelectionOverTime1" → Set Mode to "Time"
```

---

## 🎥 Step 5: Export Format Comparison

> **[!TIP] Workflow Recommendation**
> **ALWAYS export as Image Sequence (PNG) first**, then encode to video. Never export AVI/MP4 directly from ParaView.

### Format Comparison Table

| Format | Use Case | Quality | File Size | Editability | Compatibility |
|--------|----------|---------|-----------|-------------|---------------|
| **PNG Sequence** | **Intermediate format** (recommended) | Lossless (100%) | Large (5-10 MB/frame) | Fully editable | Universal |
| **TIFF Sequence** | Archival, print publication | Lossless | Very Large (15-30 MB/frame) | Fully editable | Limited |
| **MP4 (H.264)** | Final delivery (web, presentation) | High (CRF 18-23) | Small (1-3 MB/min) | Hard to edit | Universal |
| **WebM (VP9)** | Web video, modern browsers | Very High | Very Small (0.5-1 MB/min) | Hard to edit | Chrome, Firefox |
| **AVI (Uncompressed)** | Legacy compatibility | Lossless | Massive (100+ MB/min) | Easy to edit | Windows |
| **GIF** | Quick previews, email embedding | Low (256 colors) | Medium (5-10 MB/min) | Hard to edit | Universal |

### Quality vs. Size Tradeoffs

**For MP4 (H.264) encoding**:
```
CRF Value | Quality        | File Size | Use Case
----------|----------------|-----------|----------
0-15      | Lossless-near  | Very Large | Master archive (not recommended)
18        | Excellent      | Large     | Professional presentation
20        | Very Good      | Medium    | Standard delivery
23        | Good           | Small     | Web video
28+       | Acceptable     | Very Small | Mobile/low-bandwidth
```

**Recommendation**: Use **CRF 20** for most applications.

### Recommended Export Workflow

```
Step 1: ParaView → Export Image Sequence
├─ Format: PNG
├─ Magnification: 1-2 (1 = screen resolution, 2 = 2× resolution)
└─ Frame rate: 30 (this sets playback speed in video editor)

Step 2: Quality Check
├─ Open frames 1, middle, last in image viewer
├─ Check for artifacts, color banding, text readability
└─ Re-render if needed (ParaView batch mode)

Step 3: Encode to Video (FFmpeg)
├─ Standard: ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -crf 20 -pix_fmt yuv420p output.mp4
├─ High quality: ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p output.mp4
└─ Web optimized: ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart output.mp4

Step 4: Post-Production (Optional)
├─ Import MP4 into DaVinci Resolve / Premiere
├─ Add intro/outro, transitions, additional graphics
├─ Add audio (see Section 6)
└─ Export final video
```

---

## 🔊 Step 6: Audio Synchronization Basics

> **[!IMPORTANT] Legal Note**
> Always use royalty-free music or obtain proper licenses. Recommended sources:
> - YouTube Audio Library (free)
> - Epidemic Sound (subscription)
> - Artlist (subscription)

### 6.1 Audio Planning Workflow

**Step 1: Script Your Narration (if any)**
```
Total video duration: 30 seconds
Narration: ~75 words (normal speaking rate = 150 words/min)

[0-5s]   "This animation shows airflow over a NACA 0012 airfoil at 10 degrees angle of attack."
[5-12s]  "Velocity contours reveal flow separation starting at 30% chord, indicated by the blue region."
[12-20s] "The separation bubble grows until reaching 60% chord, where turbulent reattachment occurs."
[20-27s] "Pressure distribution on the lower surface shows the characteristic leading-edge suction peak."
[27-30s] "These results match experimental data from Abbott & von Doenhoff within 3%."
```

**Step 2: Create Audio Track**
- Record narration using Audacity (free) or similar
- Export as WAV (lossless) for editing
- Add background music at **-18 to -15 LUFS** (quieter than narration)

### 6.2 Synchronization Techniques

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| **Waveform Sync** | Align audio peaks with visual events | Precise synchronization (music beats, sound effects) |
| **Time Markers** | Place markers at key seconds | Quick alignment for narration |
| **Tap Sync** | Manually tap rhythm to set tempo | Music-driven animations |

### 6.3 Practical Example: Narration-Driven Animation

**Scenario**: 30-second animation with voiceover

**Storyboard with Audio**:
```
Time | Visual Action | Narration | Audio Cue
-----|---------------|-----------|-----------
0-5s | Establish shot (zoom in) | "This animation shows..." | Music fade in
5s   | Show velocity magnitude | "Velocity contours reveal..." | Highlight sound effect
12s  | Highlight separation zone | "Flow separation starting at..." | Arrow graphic appears
20s  | Switch to pressure view | "Pressure distribution shows..." | Transition whoosh
27s  | Show error metrics | "Results match within 3%" | Success chime
30s  | Fade to black + contact info | [Silence] | Music fade out
```

**Implementation in Video Editor**:
1. Import PNG sequence (creates 30-second video at 30fps = 900 frames)
2. Import audio narration track
3. Drag audio to align with visual markers
4. Add background music on Track 2, reduce volume to -20dB
5. Export final video with audio embedded

### 6.4 Audio-Visual Sync Checklist

- [ ] Narration matches visual content (describe what viewer sees)
- [ ] Speaking rate ≈ 150 words/minute (natural pace)
- [ ] Background music volume ≤ -18 LUFS (doesn't compete with voice)
- [ ] Key visual transitions aligned with audio cues (±0.5s tolerance)
- [ ] Silence (0.5-1s) at start and end for clean editing
- [ ] Test playback on multiple devices (laptop, phone, projector)

---

## 🎯 Complete Case Study: From Raw Data to Final Animation

### Problem Statement

Create a **30-second professional animation** of vortex shedding behind a circular cylinder at Re=1000. Animation must include:
- Full-domain view and close-up vortex detail
- Real-time lift coefficient graph overlay
- Voiceover narration explaining Strouhal number validation
- Final MP4 output for conference presentation

### Part 1: OpenFOAM Setup (controlDict)

```cpp
// system/controlDict
application pimpleFoam;

startFrom latestTime;
startTime 0;
endTime 15.0;  // 15 physical seconds to capture stable shedding

deltaT 0.001;  // 1ms time step
adjustTimeStep yes;
maxCo 0.5;     // Courant number limit

writeControl timeStep;
writeInterval 50;  // Output every 0.05s (300 time directories total)

writeFormat binary;
writeCompression off;
timePrecision 8;

runTimeModifiable yes;

// ==========================================
// FUNCTION OBJECTS FOR ANIMATION DATA
// ==========================================
functions
{
    // 1. Force Coefficients (Cl, Cd) for Graph
    forceCoeffsCylinder
    {
        type            forceCoeffs;
        functionObjectLibs ("libforces.so");
        outputControl   timeStep;
        outputInterval  50;  // Match writeInterval
        
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          1.0;       // Water at 20°C
        CofR            (0 0 0);   // Cylinder center
        liftDir         (0 1 0);   // y-direction (lift)
        dragDir         (1 0 0);   // x-direction (drag)
        pitchAxis       (0 0 1);
        magUInf         1.0;       // 1 m/s freestream
        lRef            1.0;       // Cylinder diameter = 1m
        Aref            1.0;       // D × 1m depth
        log             yes;
    }
    
    // 2. Probe Points for Velocity Monitoring
    probePoints
    {
        type            probes;
        functionObjectLibs ("libsampling.so");
        outputControl   timeStep;
        outputInterval  50;
        
        probeLocations
        (
            (2.5 0.0 0.0)     // Wake monitoring point (2.5D downstream)
        );
        fields          (p U);
        setFormat       csv;
        interpolationScheme cellPoint;
    }
    
    // 3. Surface Sampling for Slice Animation
    midPlaneSlice
    {
        type            surfaces;
        functionObjectLibs ("libsampling.so");
        outputControl   outputTime;
        surfaceFormat   vtk;
        fields          (p U omega);
        
        surfaces
        {
            zNormal
            {
                type            cuttingPlane;
                plane           pointAndNormal;
                pointAndNormalDict
                {
                    basePoint       (0 0 0);
                    normalVector    (0 0 1);
                }
                interpolate true;
            }
        }
    }
}
```

**Run the simulation**:
```bash
# Terminal
cd /path/to/cylinderCase
blockMesh
snappyHexMesh -overwrite
pimpleFoam > log &
tail -f log  # Monitor progress
```

**Expected output**:
- 300 time directories: `0/`, `0.05/`, `0.1/`, ..., `14.95/`, `15.0/`
- Force coefficient data: `postProcessing/forceCoeffsCylinder/0/coefficient.dat`
- Probe data: `postProcessing/probePoints/0/probePoints.csv`

### Part 2: ParaView Animation Setup

**Step 1: Load Data**
```
File → Open → select cylinderCase.foam
Properties:
├─ Mesh Regions: internalMesh, cylinder, inlet, outlet, walls
├─ Time directories: Read all (0 to 15s)
└─ Apply
```

**Step 2: Create Primary Visualization**
```
1. Apply "Warp By Vector" filter (Vector: U, Scale: 1)
2. Add "Contour" filter (Contour By: vorticity, Isosurfaces: ±2)
3. Color by: vorticity magnitude
4. Set Color Map: Cool to Warm (Blue=Negative, Red=Positive)
5. Reset View to fit data
```

**Step 3: Set Up Animation Scene**
```
View → Animation View

Animation Scene Properties:
├─ Mode: Sequence
├─ NumberOfFrames: 900  (30s × 30fps)
├─ Animation Time:
│   - StartTime: 0.0
│   - EndTime: 15.0
└─ Play Mode: Snap to TimeSteps
```

**Step 4: Create Camera Keyframes**
```
Camera Track → Add Keyframes:
├─ Frame 0 (t=0s): Position = [5, 5, 5], Focal Point = [0, 0, 0]
├─ Frame 300 (t=10s): Position = [2, 3, 2], Focal Point = [1, 0, 0]
└─ Frame 600 (t=20s): Position = [3, 1, 1], Focal Point = [2, 0, 0]

Interpolation: Spline (smooth camera motion)
```

**Step 5: Add Graph Overlay**
```
1. Load coefficient data: File → Open → postProcessing/forceCoeffsCylinder/0/coefficient.dat
2. Filters → Plot Selection Over Time
3. In Properties → X Axis Name: "Time (s)", Y Axis Name: "Cl"
4. View → Animation View → Add Track → Select "PlotSelectionOverTime1"
5. Set Mode: "Time" (adds vertical time marker)
```

**Step 6: Configure Export**
```
File → Save Animation
├─ File Name: frame_%04d.png
├─ Image Resolution: 1920×1080 (Full HD)
├─ Frame Rate: 30
├─ Frame Window: 0 to 900 (all frames)
├─ Save as: Image Series
└─ Magnification: 1 (screen resolution)
```

**Render**: Click "OK" and wait (~15-30 minutes for 900 frames)

### Part 3: Video Encoding

**Step 1: Verify Frames**
```bash
# Count frames
ls frame_*.png | wc -l  # Should show 900

# Spot check
open frame_0001.png  # First frame
open frame_0450.png  # Mid-frame
open frame_0900.png  # Last frame
```

**Step 2: Encode to MP4**
```bash
# High-quality encoding (CRF 18)
ffmpeg -framerate 30 -i frame_%04d.png \
       -c:v libx264 -preset slow -crf 18 \
       -pix_fmt yuv420p \
       -vf "scale=1920:1080" \
       cylinder_shedding_raw.mp4

# Check output
ffprobe cylinder_shedding_raw.mp4
```

**Expected file size**: ~300 MB for 30 seconds at 1080p

### Part 4: Audio Post-Production

**Step 1: Record Narration**
```
Script (30 seconds, ~75 words):
[0-5s]   "This animation simulates vortex shedding behind a circular cylinder at Reynolds number 1000."
[5-12s]  "Vorticity contours reveal alternating shedding from the cylinder surface."
[12-20s] "The lift coefficient oscillates sinusoidally, indicating periodic vortex formation."
[20-27s] "Analysis shows a Strouhal number of 0.21, matching the classical Williamson correlation."
[27-30s] "This validates our numerical approach for unsteady flow prediction."

Record using: Audacity, QuickTime Player, or similar
Export as: narration.wav (WAV, 48000 Hz, 16-bit)
```

**Step 2: Sync Audio with Video**

Using DaVinci Resolve (free):
```
1. Create New Project: "Cylinder Animation"
2. Media Pool → Import:
   - cylinder_shedding_raw.mp4
   - narration.wav
   - background_music.mp3 (royalty-free)
3. Timeline → Drag video to Video Track 1
4. Drag narration to Audio Track 2
5. Sync: Align narration waveform with visual events
   - "Alternating shedding" → Frame 150 (t=5s, visible vortex)
   - "Lift coefficient" → Frame 360 (t=12s, graph shows oscillation)
   - "Strouhal number 0.21" → Frame 600 (t=20s, text overlay)
6. Add background music to Audio Track 3
   - Reduce volume to -20dB (doesn't compete with voice)
   - Add fade-in (0-2s) and fade-out (28-30s)
```

**Step 3: Add Text Overlays** (Optional)
```
Timeline → Generator → Text → Add to Video Track 2

Text 1 (Frame 100-200): "Re = 1000"
Text 2 (Frame 200-400): "St = f·D/U = 0.21"
Text 3 (Frame 400-500): "Validation: Williamson (1996)"
Text 4 (Frame 850-900): "CFD Simulation: OpenFOAM v10"

Style: White text, black outline, Arial Bold, 48pt
```

**Step 4: Export Final Video**
```
Deliver → Render Settings:
├─ Format: MP4
├─ Codec: H.264
├─ Resolution: 1920×1080
├─ Frame Rate: 30
├─ Quality: Automatic (Target: 20 Mbps)
└─ Audio: AAC, 48000 Hz, Stereo

Add to Render Queue → Start Render
```

**Final Output**: `cylinder_shedding_final.mp4` (~150 MB)

### Part 5: Quality Checklist

- [ ] Video plays smoothly at 30fps (no stuttering)
- [ ] Colors appear consistent across all frames
- [ ] Graph overlay is legible (text size ≥ 24pt equivalent)
- [ ] Narration is clear and synchronized with visuals (±0.5s)
- [ ] Background music doesn't overpower voice
- [ ] File size is reasonable for intended use (email vs. presentation)
- [ ] Test playback on target system (conference laptop, web player)

---

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: Choppy Animation Despite 60fps Export

**Cause**: Write interval too large relative to flow time scales

**Solution**:
```cpp
// In controlDict, reduce writeInterval
writeInterval 10;  // Was 50, now output 5× more frequently
```

**Tradeoff**: 5× larger storage requirements

### Pitfall 2: Video Colors Look Washed Out

**Cause**: Color space mismatch (ParaView uses RGB, video uses YUV)

**Solution**:
```bash
# Add color space conversion to FFmpeg
ffmpeg -framerate 30 -i frame_%04d.png \
       -c:v libx264 -crf 20 \
       -pix_fmt yuv420p \
       -colorspace bt709 \
       -color_trc bt709 \
       -color_primaries bt709 \
       output.mp4
```

### Pitfall 3: Audio Out of Sync After Export

**Cause**: Variable frame rate video or incorrect timecode

**Solution**:
```bash
# Force constant frame rate
ffmpeg -framerate 30 -i frame_%04d.png \
       -c:v libx264 -crf 20 \
       -r 30 \  # Force output frame rate
       -vsync cfr \  # Constant frame rate
       -pix_fmt yuv420p \
       output.mp4
```

### Pitfall 4: Text Overlays Unreadable on Projector

**Cause**: Thin fonts, insufficient contrast

**Solution**:
- Use **bold sans-serif fonts** (Arial Black, Impact, Futura Bold)
- Add **black outline** (stroke width ≥ 2px)
- Ensure **contrast ratio ≥ 4.5:1** (WCAG AA standard)
- Test on actual projector before presentation

### Pitfall 5: File Too Large for Email/Upload

**Cause**: Unnecessarily high resolution or bitrate

**Solution**:
```bash
# Reduce resolution for web delivery
ffmpeg -i input.mp4 \
       -vf "scale=1280:720" \  # 720p instead of 1080p
       -c:v libx264 -crf 28 \  # Higher CRF = smaller file
       -pix_fmt yuv420p \
       output_web.mp4
```

**Expected size reduction**: 1080p→720p saves ~50%; CRF 20→28 saves ~60%

---

## 🎓 Key Takeaways

### Decision Matrix: When to Use Each Tool

| Scenario | Recommended Tool | Why |
|----------|------------------|-----|
| **Quick technical review** | ParaView → AVI export | Fastest workflow, no post-processing |
| **Conference presentation** | ParaView → PNG → FFmpeg → Video Editor | Full control over timing, audio, text |
| **Publication figure** | ParaView → High-res PNG (600 DPI) | Publication-quality still image |
| **Web video (YouTube)** | ParaView → PNG → FFmpeg (CRF 23) | Optimized for streaming |
| **Artsistic visualization** | ParaView → Blender → Render | Advanced lighting, materials |
| **Automated batch processing** | ParaView Python script (`pvbatch`) | No GUI, runs on HPC clusters |

### Best Practices Summary

1. **ALWAYS export image sequences** (PNG), never direct video from ParaView
2. **Plan your storyboard** before rendering (saves hours of re-renders)
3. **Use 30 fps** for standard presentations (balance quality/size)
4. **Synchronize audio first**, then align visuals (easier than reversing)
5. **Test on target hardware** (projector, web player) before deadline
6. **Keep raw PNG files** until final approval (allows re-encoding at different quality)

### Performance Optimization

| Optimization | Render Time Savings | Quality Impact |
|--------------|---------------------|----------------|
| Reduce magnification (2→1) | 75% faster | Minimal (if 1080p sufficient) |
| Use MJPEG preview (CRF 28) | 40% faster | Noticeable (use for draft only) |
| Reduce frame count (900→600) | 33% faster | Depends on pacing |
| Use GPU rendering (ParaView 5.11+) | 2-5× faster | None (if available) |

---

## 📝 Practice Exercises

### Exercise 1: Basic Temporal Animation (Beginner)

**Task**: Create a 10-second animation of your existing OpenFOAM case showing velocity magnitude evolution.

**Requirements**:
- Duration: 10 seconds
- Frame rate: 30 fps
- Single camera angle (no movement)
- Color bar legend visible
- Export as MP4 (CRF 20)

**Time Estimate**: 1-2 hours

**Solution Outline**:
```
1. Open case in ParaView
2. Apply "Color By" → U_magnitude
3. Animation View → Set NumberOfFrames = 300
4. File → Save Animation → PNG sequence
5. FFmpeg encode to MP4
```

### Exercise 2: Camera Movement Animation (Intermediate)

**Task**: Create a 15-second "fly-through" animation with 3 camera keyframes showing different regions of your flow.

**Requirements**:
- Duration: 15 seconds
- 3 camera positions (wide, close-up, side view)
- Smooth camera transition (spline interpolation)
- Text overlay showing current view name
- Narration script (optional)

**Time Estimate**: 3-4 hours

**Solution Outline**:
```
1. Storyboard 3 scenes with timing
2. Create camera track with 3 keyframes at frames 0, 225, 450
3. Set interpolation to "Spline"
4. Add text sources for each view
5. Render + encode
```

### Exercise 3: Data Overlay Animation (Advanced)

**Task**: Create a 20-second animation synchronized with force coefficient graph from `controlDict` function objects.

**Requirements**:
- Duration: 20 seconds
- Real-time graph overlay (vertical time marker)
- Annotations for key events (e.g., "Peak Cl = 0.45 at t=5.2s")
- Voiceover narration synchronized with graph
- Background music (royalty-free)

**Time Estimate**: 6-8 hours

**Solution Outline**:
```
1. Set up forceCoeffs function object in controlDict
2. Re-run simulation (or extract existing postProcessing data)
3. Load .dat file into ParaView
4. Create Plot Selection Over Time
5. Add time marker track in Animation View
6. Record narration (script events from graph)
7. Edit in DaVinci Resolve (sync audio, add music)
```

### Exercise 4: Complete Production Pipeline (Expert)

**Task**: Create a 60-second documentary-style animation with:
- Multiple visualization techniques (contours, streamlines, vectors)
- Animated text overlays
- Professional voiceover
- Background music with dynamics
- Intro/outro branding

**Time Estimate**: 15-20 hours

**Deliverables**:
- Final MP4 (1080p, 30fps, ≤200 MB)
- Storyboard document
- Script document
- Project files (DaVinci/Premiere)

---

## 🔗 Cross-References

### Within This Module

- **ParaView Basics**: See [01_ParaView_Visualization.md](01_ParaView_Visualization.md) §4-5 for advanced ParaView operations
- **Python Plotting**: See [02_Python_Plotting.md](02_Python_Plotting.md) §3 for creating custom graphs from OpenFOAM data
- **Blender Rendering**: See [03_Blender_Rendering.md](03_Blender_Rendering.md) §5 for importing OpenFOAM data into Blender for cinematic rendering
- **Visualization Overview**: See [00_Overview.md](00_Overview.md) for the complete learning path

### External Resources

- **ParaView Animation**: [ParaView Wiki - Animation](https://wiki.paraview.org/Wiki/Animation)
- **FFmpeg Guide**: [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- **Video Encoding**: [FFmpeg Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/H.264)
- **Storytelling Techniques**: [The Hero's Journey in Technical Presentations](https://www.youtube.com/watch?v=KHiBpTtBzRY)
- **Royalty-Free Music**: [YouTube Audio Library](https://www.youtube.com/audiolibrary)

---

## 📚 Shared Assets

### Sample Dataset Downloads

For practice exercises, download these OpenFOAM cases:

| Dataset | Description | Size | Download |
|---------|-------------|------|----------|
| **cylinderRe1000** | 2D cylinder vortex shedding (tutorial case) | 50 MB | [Download](https://develop.openfoam.com/Developers/openfoam/-/wikis/cylinder2D) |
| **airfoilNACA0012** | 3D airfoil boundary layer | 200 MB | [Download](https://turbmodels.larc.nasa.gov/naca0012_val.html) |
| **cavityLidDriven** | 2D lid-driven cavity | 15 MB | Included in OpenFOAM tutorials |

### Keyboard Shortcut Cheatsheet

#### ParaView Animation View
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open Animation View | `View` → `Animation View` | Same |
| Add Keyframe | `K` or click diamond icon | Same |
| Play Animation | `Space` | Same |
| Scrub Timeline | Drag time marker | Same |
| Toggle Real-time/Sequence | Right-click → `Mode` | Same |

#### FFmpeg Common Commands
```bash
# Basic conversion
ffmpeg -i input.mov output.mp4

# Extract frames
ffmpeg -i video.mp4 frame_%04d.png

# Create video from frames
ffmpeg -framerate 30 -i frame_%04d.png output.mp4

# Resize video
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# Extract audio
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# Combine audio + video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -strict experimental output.mp4
```

### Troubleshooting FAQ

**Q: ParaView crashes when rendering animation**
- **A**: Reduce image resolution or use batch mode (`pvbatch --sym=script.py`)

**Q: FFmpeg encoding fails with "pixel format not supported"**
- **A**: Add `-pix_fmt yuv420p` to your FFmpeg command

**Q: Video plays correctly in VLC but not in QuickTime**
- **A**: QuickTime requires `-pix_fmt yuv420p -movflags +faststart`

**Q: Audio is out of sync in final video**
- **A**: Ensure constant frame rate: `-r 30 -vsync cfr`

**Q: File size is too large for email**
- **A**: Increase CRF value (20→28) or reduce resolution (1080p→720p)

**Q: Colors look different in exported video vs ParaView**
- **A**: Add color space flags to FFmpeg: `-colorspace bt709 -color_primaries bt709`

**Q: Animation is too fast/slow**
- **A**: Adjust `NumberOfFrames` in ParaView or use `-framerate` in FFmpeg

**Q: Graph overlay disappears in some frames**
- **A**: Check graph visibility range in Properties → "Visibility Toggle"

---

## 📖 Further Reading

- **Narrative Visualization**: "Storytelling with Data" by Cole Nussbaumer Knaflic
- **Video Production**: "The Filmmaker's Eye" by Gustavo Mercado
- **FFmpeg Mastery**: "FFmpeg Basics" by Frantisek Korbel
- **Scientific Animation**: "The Art of Scientific Animation" by Bess A. Barlow

---

## 🎬 Next Steps

After completing this module, you should be able to:

1. ✅ Plan animations using structured storyboards
2. ✅ Configure OpenFOAM output for animation production
3. ✅ Create professional animations in ParaView with camera movement and data overlays
4. ✅ Export and encode video using optimal settings
5. ✅ Synchronize audio narration with visual elements
6. ✅ Produce publication-ready animations for technical presentations

**Recommended Next Module**: 
- For advanced rendering techniques, see [03_Blender_Rendering.md](03_Blender_Rendering.md) §5-6 (Cinematic rendering with imported OpenFOAM data)
- For automated visualization workflows, see [02_Python_Plotting.md](02_Python_Plotting.md) §4 (Batch processing with Python scripts)

---

**Module Version**: 2.0
**Last Updated**: 2024
**Contributors**: OpenFOAM Visualization Working Group
**License**: CC BY-SA 4.0