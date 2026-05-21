# Evolutionary Creatures Mountain Climbing

[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![PyBullet](https://img.shields.io/badge/pybullet-physics-orange)]()
[![Status](https://img.shields.io/badge/status-complete-success)]()

> Genetic algorithm evolution of creatures climbing mountains in PyBullet physics simulator. Explores fitness shaping, morphology encoding, and physical constraints through 15 controlled experiments. CM3020 Artificial Intelligence coursework.

**Module:** CM3020 Artificial Intelligence  
**Assessment:** Midterm Coursework (Part A: Essay + Part B: Implementation)  
**Date:** January 2026

## Overview

This project evolves simulated creatures to climb a steep central mountain using a genetic algorithm. The focus extends beyond whether climbing occurs to understand why evolution fails, what exploits emerge, and how behavior changes as reward shaping, encoding schemes, and simulation constraints are systematically tightened.

The codebase implements a full evolutionary system with creature morphology encoding, motor control, physics simulation, and comprehensive fitness metrics. Fifteen experiments progress from baseline exploitation detection through reward shaping refinement to physical isolation testing.

## Key Results

| Aspect | Finding | Details |
|--------|---------|---------|
| **Baseline Behavior** | Wall/corner exploitation | Static giants lean on walls for stable height |
| **After Reward Shaping** | Centipede locomotion emerges | Multi-segment peristaltic movement toward slope |
| **Search Capacity** | Physical bottleneck, not search limit | Population/generation scaling doesn't enable climbing |
| **Physical Isolation** | Contact geometry is limiting factor | Friction, force, anchoring improvements insufficient |
| **Final State** | Approach → contact → stall | Creatures reach slope but cannot generate sustained ascent |

## Documentation

- **[Coursework Report](Documentation/AI-Report.pdf)** - 1,961 word analysis of 15 experiments with graphs and tables
- **[Presentation Slides](Documentation/AI-Slides.pdf)** - Full coursework presentation
- **[Demo Video](https://drive.google.com/file/d/1zvkN6TkqLaumu7bBIxfCM1Qd1KlZUIie/view?usp=sharing)** - Evolution demonstration (Google Drive)

## Project Structure

```
Evolutionary-Creatures-Mountain-Climbing/
├── Project/                          # Core implementation
│   ├── creature.py                   # Creature lifecycle, motors, fitness
│   ├── genome.py                     # DNA encoding, mutation, crossover
│   ├── population.py                 # GA framework, selection, breeding
│   ├── simulation.py                 # PyBullet physics, evaluation loop
│   ├── cw-envt.py                    # Environment visualization
│   ├── prepare_shapes.py             # Mountain landscape generation
│   ├── starter.py                    # Experiment initialization
│   ├── offline_from_csv.py           # Offline creature loading
│   ├── realtime_from_csv.py          # Real-time replay
│   └── test_*.py                     # Validation scripts
│
├── Documentation/
│   ├── AI-Report.pdf                 # Full coursework report
│   ├── AI-Slides.pdf                 # Presentation
│   └── AI-Demonstration.mp4          # Video demo
│
├── README.md                         # This file
└── LICENSE                           # MIT License
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

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Physics Engine** | PyBullet |
| **Language** | Python 3.8+ |
| **Genetic Algorithm** | Custom implementation |
| **Morphology Format** | URDF (XML) |
| **Data Format** | CSV, URDF, OBJ |
| **Visualization** | PyBullet GUI |

## Code Architecture

**genome.py:**
- Fixed morphology constants (link length, radius, density, joint limits)
- Gene specification mapping DNA to physical/control properties
- Crossover and mutation operators
- URDF link and joint generation with analytical joint spacing

**creature.py:**
- Motor class: PULSE or SINE waveform generation
- Creature lifecycle: DNA → morphology → URDF
- Spine + passive legs architecture (stabilizing without evolution)
- Position/orientation tracking, uprightness calculation
- Fitness aggregation: `z_score × distance_bonus × contact_multiplier × upright_penalty / num_links`

**population.py:**
- Population initialization and elitism
- Parent selection (tournament/proportional)
- Genetic operators: crossover, mutation, selection
- Fitness-based breeding loop

**simulation.py:**
- PyBullet environment setup (floor, walls, mountain terrain)
- Creature spawning and motor control execution
- Per-frame contact detection and state tracking
- Fitness evaluation and logging

## Key Experiments & Findings

### Exploit Classes Identified & Eliminated
1. **Wall/corner support** → Removed by distance bonus to center
2. **Distance-collapse ("timber")** → Removed by uprightness penalty
3. **Morphology bloat** → Removed by fixed morphology encoding

### Physical Bottleneck Validation
- Increasing mountain friction: Improves grip, not ascent
- Increasing motor force: Increases energy, not effective traction
- Increasing floor friction: Improves anchoring, not climbing
- Contact-gated control: Enables bracing, still no sustained ascent

**Interpretation:** Evolution optimizes within physical constraints but cannot bypass contact mechanics and actuation limits without fundamentally different interaction geometry (e.g., hooks, compliance, adhesion) or altered terrain/physics.

## Methodology Highlights

**Controlled Isolation:** Each experiment changes only one variable, enabling clean causal claims.

**Reproducibility:** Fixed random seeds across runs. Separate specification files for schema, queries, and physics tuning. All 398 matches included with no sampling.

**Simulation Stability:** Passive legs added for contact footprint without control complexity. Collision filtering removes destabilizing internal collisions. Physics tuning (smaller timestep, higher solver iterations) ensures repeatable results.

**Fitness Design Evolution:** Progressed from naive height maximization → distance bonus → uprightness penalty → contact-gated control, each iteration addressing discovered exploits.

## Running the Code

### Prerequisites
- Python 3.8+
- PyBullet
- NumPy

### Quick Start
```bash
cd Project
python simulation.py
```

Visualizes evolution in real-time. Logs fitness/height per generation. Saves best creature genomes to CSV.

### Offline Replay
```bash
python offline_from_csv.py genome.csv
```

Renders a previously evolved creature in the environment without re-evaluating.

## Extensions Completed

- **Encoding scheme experiments:** Fixed morphology vs evolvable morphology
- **Stability engineering:** Collision filtering, passive leg scaffolding
- **Terrain variation:** Gaussian pyramid vs irregular mountain terrain
- **Contact-gated control:** Reflex-based actuation conditioned on per-link contact state

## Author

**Dhanarasu Naveen**  
Student ID: 230655533  
Course: CM3020 – Artificial Intelligence  
University of London (via SIM Singapore)

## License

MIT License

## References

- PyBullet Documentation: https://pybullet.org/
- Genetic Algorithms: Standard GA references
- Physics Simulation: PyBullet physics engine documentation

---

