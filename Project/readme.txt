GETTING STARTED

Prerequisites:
- Anaconda or Miniconda installed
- Download: https://www.anaconda.com/download

Installation:

1. Clone repository
   git clone https://github.com/naveenlabs/Evolutionary-Creatures-Mountain-Climbing.git
   cd Evolutionary-Creatures-Mountain-Climbing

2. Install dependencies
   conda install -c conda-forge pybullet numpy -y

3. Run simulation
   macOS:
   /opt/anaconda3/bin/python3 Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_99.csv"
   
   Windows/Linux:
   python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_99.csv"

4. View results
   PyBullet GUI opens showing creature attempting to climb the mountain
   Simulation runs for 60 seconds in real time
   Height printed live in terminal

To try different generations:
   python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_50.csv"
   python Project/realtime_from_csv.py "Final Experiment (Fixed Morphology)/all_elites/elite_gen_14.csv"

Note: macOS users must use conda, not pip.
