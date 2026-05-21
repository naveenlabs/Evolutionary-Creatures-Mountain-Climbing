"""
test_ga_no_threads.py: Entry point for the Genetic Algorithm experiment.
This script manages the evolutionary loop, including selection, reproduction,
and extensive logging of results to CSV and local directories.
"""

import unittest
import os
import csv
import copy
import random
from datetime import datetime

import numpy as np

import population
import simulation
import genome
import creature


class TestGA(unittest.TestCase):
    """
    Unit test class used as a wrapper to run the Genetic Algorithm experiment.
    """
    def testCentipedeFixedMorphologyGA(self):
        # === PERSONAL WORK START ===
        # Experiment hyperparameters
        POP_SIZE = 50
        GENE_COUNT = 5            
        GENERATIONS = 100
        SIM_ITERATIONS = 2400

        MUTATION_RATE = 0.2
        MUTATION_AMOUNT = 0.3
        SUCCESS_THRESHOLD = 0.35
        EXP_NAME = "final_2"

        # Directory setup for data persistence
        base_dir = f"experiment_{EXP_NAME}"
        elites_dir = os.path.join(base_dir, "all_elites")
        best_dir = os.path.join(base_dir, "best_overall")
        success_dir = os.path.join(base_dir, "success_creatures")

        for d in [base_dir, elites_dir, best_dir, success_dir]:
            os.makedirs(d, exist_ok=True)

        # Initialize CSV logging file with headers
        csv_path = os.path.join(base_dir, "results.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "pop_size", "gene_count", "mutation_rate",
                "mutation_amount", "sim_steps", "generation",
                "max_fitness", "mean_fitness", "median_fitness", "max_height",
            ])
        # === PERSONAL WORK END ===

        # Initialize Population and Simulation
        pop = population.Population(pop_size=POP_SIZE, gene_count=GENE_COUNT)
        sim = simulation.Simulation(sim_id=0, gui=False)

        overall_best_fitness = -1e9
        overall_best_gen = -1

        # Main Evolutionary Loop
        for gen in range(GENERATIONS):

            # Evaluation Phase
            for cr in pop.creatures:
                sim.run_creature(cr, iterations=SIM_ITERATIONS)

            # === PERSONAL WORK START ===
            # Statistics Collection
            fits = np.array([float(cr.get_distance_travelled()) for cr in pop.creatures], dtype=float)
            heights = np.array([float(cr.max_z) for cr in pop.creatures], dtype=float)

            curr_max_fit = float(np.max(fits)) if len(fits) else 0.0
            curr_mean_fit = float(np.mean(fits)) if len(fits) else 0.0
            curr_median_fit = float(np.median(fits)) if len(fits) else 0.0
            curr_max_h = float(np.max(heights)) if len(heights) else -999.0

            print(
                f"Gen {gen:02d} | "
                f"BestFit: {curr_max_fit:.4f} | "
                f"MeanFit: {curr_mean_fit:.4f} | "
                f"MedianFit: {curr_median_fit:.4f} | "
                f"MaxZ: {curr_max_h:.3f}"
            )

            # Write generation results to CSV
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    POP_SIZE, GENE_COUNT, MUTATION_RATE, MUTATION_AMOUNT,
                    SIM_ITERATIONS, gen, curr_max_fit, curr_mean_fit,
                    curr_median_fit, curr_max_h,
                ])

            # Export "Success" creatures (those exceeding the fitness threshold)
            for i, fit in enumerate(fits):
                if fit >= SUCCESS_THRESHOLD:
                    fit_str = f"{fit:.4f}".replace(".", "_")
                    fname = f"success_gen{gen}_fit{fit_str}.csv"
                    genome.Genome.to_csv(pop.creatures[i].dna, os.path.join(success_dir, fname))

            # Elite Selection and Saving
            elite_idx = int(np.argmax(fits)) if len(fits) else 0
            elite_cr = pop.creatures[elite_idx]
            genome.Genome.to_csv(elite_cr.dna, os.path.join(elites_dir, f"elite_gen_{gen}.csv"))

            # Track and save the best overall champion
            if curr_max_fit > overall_best_fitness:
                overall_best_fitness = curr_max_fit
                overall_best_gen = gen
                genome.Genome.to_csv(elite_cr.dna, os.path.join(best_dir, "champion.csv"))

            # Reproduction Phase
            new_creatures = []

            # 1. Elitism: Carry over the champion to the next generation
            new_el = creature.Creature(gene_count=GENE_COUNT)
            new_el.update_dna(copy.deepcopy(elite_cr.dna))
            new_creatures.append(new_el)

            # 2. Parent Selection Setup
            total_fit = float(np.sum(fits))
            use_random_parents = (not np.isfinite(total_fit)) or (total_fit <= 0.0)

            if not use_random_parents:
                fit_map = population.Population.get_fitness_map(list(fits))
            else:
                fit_map = None

            # 3. Create the rest of the new population
            for _ in range(1, POP_SIZE):
                if use_random_parents:
                    p1 = random.randrange(POP_SIZE)
                    p2 = random.randrange(POP_SIZE)
                else:
                    p1 = population.Population.select_parent(fit_map)
                    p2 = population.Population.select_parent(fit_map)

                # Crossover
                child_dna = genome.Genome.crossover(pop.creatures[p1].dna, pop.creatures[p2].dna)

                # Mutation
                child_dna = genome.Genome.point_mutate(
                    child_dna,
                    rate=MUTATION_RATE,
                    amount=MUTATION_AMOUNT
                )

                # Instantiate new creature
                child = creature.Creature(gene_count=GENE_COUNT)
                child.update_dna(child_dna)
                new_creatures.append(child)

            # Advance to next generation
            pop.creatures = new_creatures
            # === PERSONAL WORK END ===

        # Cleanup
        sim.close()

        # Final assertions for test validity
        self.assertTrue(np.isfinite(overall_best_fitness))
        self.assertGreaterEqual(overall_best_gen, 0)


if __name__ == "__main__":
    unittest.main()