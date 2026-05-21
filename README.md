# Evolutionary Creatures Mountain Climbing

[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![PyBullet](https://img.shields.io/badge/pybullet-physics-orange)]()
[![Status](https://img.shields.io/badge/status-complete-success)]()

## Overview

A genetic algorithm system that evolves simulated creatures to climb mountains in PyBullet physics simulator. The project explores fitness shaping, morphology encoding, and physical constraints through 15 controlled experiments, progressing from baseline exploitation detection to physical isolation testing.

**Module:** CM3020 Artificial Intelligence  
**Assessment:** Midterm Coursework (Part A: Essay + Part B: Implementation)  
**Date:** January 2026

## Key Results

| Aspect | Finding | Details |
|--------|---------|---------|
| **Baseline Behavior** | Wall/corner exploitation | Static giants lean on walls for stable height |
| **After Reward Shaping** | Centipede locomotion emerges | Multi-segment peristaltic movement toward slope |
| **Search Capacity** | Physical bottleneck, not search limit | Population/generation scaling doesn't enable climbing |
| **Physical Isolation** | Contact geometry is limiting factor | Friction, force, anchoring improvements insufficient |
| **Final State** | Approach → contact → stall | Creatures reach slope but cannot generate sustained ascent |

## What's Inside

**Complete evolutionary system** with creature morphology encoding, motor control, physics simulation, and comprehensive fitness metrics. Fifteen experiments progress from baseline exploitation detection through reward shaping refinement to physical isolation testing.

**Core modules:**
- `genome.py` - DNA encoding, mutation, crossover, URDF generation
- `creature.py` - Creature lifecycle, motor control, fitness calculation
- `population.py` - Genetic algorithm framework with selection and breeding
- `simulation.py` - PyBullet physics engine and evaluation loop
- `realtime_from_csv.py` - Visualization of evolved creatures

**Documentation:**
- Complete coursework report with 15 experiment analyses
- Presentation slides with visual explanations
- Demo video showing evolution in action

## Quick Start

### Prerequisites
- Python 3.8+
- Anaconda or Miniconda
- Download: https://www.anaconda.com/download

### Installation

**1. Clone repository**
```bash
git clone https://github.com/naveenlabs/Evolutionary-Creatures-Mountain-Climbing.git
cd Evolutionary-Creatures-Mountain-Climbing
```

**2. Install dependencies**
```bash
conda install -c conda-forge pybullet numpy -y
```

⚠️ **macOS users:** Do NOT use `pip install pybullet` — use conda instead.

**3. Run the simulation**

macOS:
```bash
/opt/anaconda3/bin/python3 Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_99.csv"
```

Windows/Linux:
```bash
python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_99.csv"
```

**4. Watch the evolution**

A PyBullet GUI window opens showing the creature attempting to climb the mountain. The simulation runs for 60 seconds. Height is printed live in the terminal.

**Try different generations:**
```bash
python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_50.csv"
python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_14.csv"
```

## 15 Experiments Overview

### Phase B1: Baseline Exploitation (Experiments 1–3)
Establish what the system optimizes by default without task pressure.

- **Exp 1:** Standard baseline (gene count=3) → Static giant strategy
- **Exp 2:** Minimalist genome (gene count=1) → Corner leaner exploitation
- **Exp 3:** High exploration (mutation=0.8) → Chaotic motion, no improvement

**Conclusion:** Reward encourages wall-supported height; exploration cannot fix missing task pressure.

### Phase B2–B3: Reward Shaping (Experiments 4–6)
Eliminate exploits and induce locomotion through fitness function redesign.

- **Exp 4:** Distance bonus + metabolic cost → Timber exploit (fall-forward)
- **Exp 5:** Upright orientation penalty → Low-profile crawling emerges
- **Exp 6:** Gene count increase (3→5) → Centipede breakthrough with peristaltic waves

**Conclusion:** Multi-segment bodies enable plausible locomotion; first approach to slope occurs.

### Phase B4: Search Capacity Test (Experiment 7)
Determine if remaining failure is evolution-limited or physically-constrained.

- **Exp 7:** Large search (population 50→150, generations 100→300) → Refines approach but no sustained climbing

**Conclusion:** Brute search cannot cross performance ceiling; suggests physical limit, not search limit.

### Encoding Redesign & Stability (Experiment 8)
Remove morphology as exploit channel; stabilize simulation for clean baseline.

- **Exp 8:** Fixed morphology encoding → Approach → contact → stall without chaos

**Conclusion:** Clean failure mode enables controlled hypothesis testing.

### Physical Isolation & Validation (Experiments 9–15)
Isolate specific physical hypotheses under fixed morphology and fitness.

- **Exp 9–10:** Mountain friction only (grip hypothesis) → Improved contact, no ascent
- **Exp 11:** Motor force scaling (torque hypothesis) → Increased energy, same failure mode
- **Exp 12–13:** Floor friction anchoring (base-slip hypothesis) → Better grounding, same stall
- **Exp 14–15:** Contact-gated control + terrain comparison → Reflex-like stabilization, still no climbing

**Conclusion:** Physical parameters insufficient. Mechanical interaction geometry (contact, foothold stability) is the bottleneck.

## Documentation

- **[Coursework Report](Documentation/AI-Report.pdf)** - 1,961 word analysis of all 15 experiments with graphs, tables, and detailed methodology
- **[Presentation Slides](Documentation/AI-Slides.pdf)** - Complete presentation with visual explanations of each phase
- **[Demo Video](https://drive.google.com/file/d/1zvkN6TkqLaumu7bBIxfCM1Qd1KlZUIie/view?usp=sharing)** - Evolution demonstration showing creatures from different generations (Google Drive)

## Important Note: Experiments and Code Versions

**The current code in `/Project/` is the final, polished version from Experiment 15 (Fixed Morphology encoding with contact-gated control).**

**Why you can only run the latest version:**
- Each experiment used different simulation code, fitness functions, and morphology constraints
- Results from Experiments 1–14 are **not reproducible** with the current codebase
- Attempting to run old result files with new code would produce different (incorrect) outcomes
- The code has been refactored and optimized since earlier experiments

**To see results from previous experiments (1–14):**
- Review the **Coursework Report** (Documentation/AI-Report.pdf) for detailed graphs, tables, and analysis
- Watch the **Demo Video** (Google Drive link above) showing creatures from multiple experimental phases
- Review the **Presentation Slides** for visual explanations of each phase

The current `/Project/` code is provided for reproducibility and educational understanding of the final evolutionary system.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Physics Engine** | PyBullet |
| **Language** | Python 3.8+ |
| **Genetic Algorithm** | Custom implementation |
| **Morphology Format** | URDF (XML) |
| **Visualization** | PyBullet GUI |
| **Data Format** | CSV, URDF |

## Project Structure

```
Evolutionary-Creatures-Mountain-Climbing/
├── Project/                          # Final polished code
│   ├── creature.py                   # Creature lifecycle, motors, fitness
│   ├── genome.py                     # DNA encoding, mutation, crossover
│   ├── population.py                 # GA framework, selection, breeding
│   ├── simulation.py                 # PyBullet physics, evaluation loop
│   ├── cw-envt.py                    # Environment visualization
│   ├── prepare_shapes.py             # Mountain landscape generation
│   ├── starter.py                    # Experiment initialization
│   ├── offline_from_csv.py           # Offline creature loading
│   ├── realtime_from_csv.py          # Real-time replay (use this!)
│   └── test_*.py                     # Validation scripts
│
├── Documentation/
│   ├── AI-Report.pdf                 # Full coursework report
│   ├── AI-Slides.pdf                 # Presentation
│   └── AI-Demonstration.mp4          # Video demo
│
├── Final Experiment (Fixed Morphology)/
│   └── all_elites/                   # Best creatures from each generation
│       ├── elite_gen_99.csv          # Final generation (recommended)
│       ├── elite_gen_50.csv
│       └── elite_gen_14.csv
│
├── README.md                         # This file
└── LICENSE                           # MIT License
```

## Code Architecture

**genome.py:**
- Fixed morphology constants (link length 0.55, radius 0.18, density 1.0)
- Gene specification mapping DNA to control properties (waveform, amplitude, frequency, phase, force)
- Crossover and mutation operators with clamping
- URDF link and joint generation with analytical joint spacing for end-to-end chaining

**creature.py:**
- Motor class supporting PULSE or SINE waveform generation
- Creature lifecycle: DNA → genome dicts → spine links + passive legs → URDF
- Spine + dual-leg architecture (legs stabilize without evolution)
- Position/orientation tracking, uprightness calculation, contact ratio monitoring
- Fitness: `(z_score × distance_bonus × contact_multiplier × upright_penalty) / num_links`

**population.py:**
- Population initialization with random genomes
- Tournament selection for parent selection
- Crossover (both inter-gene and intra-gene) and point mutation
- Elitism preserving best individuals
- Fitness-based breeding loop

**simulation.py:**
- PyBullet environment: floor, four perimeter walls, central mountain
- Creature spawning at consistent position [7, 7, 2.5]
- Motor control execution with per-frame motor output updates
- Contact detection (floor, walls, mountain) and state tracking
- Fitness evaluation and generation-based logging

## Key Experiments & Findings

### Exploit Classes Identified & Eliminated
1. **Wall/corner support** → Removed by distance bonus to center
2. **Distance-collapse ("timber")** → Removed by uprightness penalty
3. **Morphology bloat** → Removed by fixed morphology encoding

### Physical Bottleneck Validation
- **Friction test:** Increasing mountain friction improves grip, not ascent
- **Force test:** Stronger motors increase energy, not effective traction
- **Anchoring test:** Better floor friction improves grounding, not climbing
- **Control test:** Contact-gated control enables bracing, still no sustained ascent

**Interpretation:** Evolution optimizes within physical constraints but cannot bypass contact mechanics and actuation limits without fundamentally different interaction geometry (e.g., hooks, compliance, adhesion) or altered terrain/physics.

## Methodology Highlights

**Controlled Isolation:** Each experiment changes only one variable, enabling clean causal claims.

**Reproducibility:** Fixed random seeds (RANDOM_STATE=42) across all runs. Clean separation between specification and implementation. Physics parameters explicitly documented.

**Simulation Stability:** Passive legs added for contact footprint without control complexity. Collision filtering removes destabilizing internal collisions. Physics tuning (smaller timestep, higher solver iterations) ensures repeatable results.

**Fitness Design Evolution:** Progressed from naive height maximization → distance bonus → uprightness penalty → contact-gated control, each iteration addressing discovered exploits and moving closer to task-aligned behavior.

## Author

**Dhanarasu Naveen**  
Student ID: 230655533  
Course: CM3020 – Artificial Intelligence  
University of London (via SIM Singapore)

## License

MIT License

## References

- PyBullet Documentation: https://pybullet.org/
- Genetic Algorithms: Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*
- Physics Simulation: Coumans, E. (2021). PyBullet Documentation

---

