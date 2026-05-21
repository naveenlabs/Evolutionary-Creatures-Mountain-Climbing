"""
genome.py: Handles genetic encoding, mutation, crossover, and conversion 
to URDF (Universal Robot Description Format) link and joint elements.
"""

import numpy as np
import copy
import random


class Genome:
    """
    Static class for genome-level operations including mutation, 
    crossover, and mapping DNA to structural link dictionaries.
    """

    # === PERSONAL WORK START ===
    # Fixed morphology constraints to ensure consistent creature segments
    FIXED_LINK_LENGTH = 0.55     
    FIXED_LINK_RADIUS = 0.18    
    FIXED_LINK_DENSITY = 1.0    
    FIXED_JOINT_LIMIT = 1.57    
    # === PERSONAL WORK END ===

    @staticmethod
    def get_random_gene(length: int) -> np.ndarray:
        """Generates a single gene as a numpy array of random floats."""
        return np.array([np.random.random() for _ in range(length)], dtype=float)

    @staticmethod
    def get_random_genome(gene_length: int, gene_count: int):
        """Creates a list of genes representing a full creature genome."""
        return [Genome.get_random_gene(gene_length) for _ in range(gene_count)]

    @staticmethod
    def get_gene_spec():
        """
        Defines the schema for how DNA values map to physical and control properties.
        Includes scaling factors and fixed values for the morphology.
        """
        # === PERSONAL WORK START ===
        # Mapping updated to use fixed values for morphology and expanded control parameters
        gene_spec = {
            "link-shape": {"scale": 0, "fixed": 1},  
            "link-length": {"scale": 0, "fixed": Genome.FIXED_LINK_LENGTH},
            "link-radius": {"scale": 0, "fixed": Genome.FIXED_LINK_RADIUS},
            "link-recurrence": {"scale": 0, "fixed": 1},
            "link-mass": {"scale": 0, "fixed": Genome.FIXED_LINK_DENSITY},

            "joint-type": {"scale": 0, "fixed": 0},         
            "joint-parent": {"scale": 0, "fixed": 0},       
            "joint-axis-mode": {"scale": 0, "fixed": 0},    

            "joint-origin-rpy-1": {"scale": 0, "fixed": 0},
            "joint-origin-rpy-2": {"scale": 0, "fixed": 0},
            "joint-origin-rpy-3": {"scale": 0, "fixed": 0},

            "joint-origin-xyz-1": {"scale": 0, "fixed": 0},
            "joint-origin-xyz-2": {"scale": 0, "fixed": 0},  
            "joint-origin-xyz-3": {"scale": 0, "fixed": 0},

            "control-waveform": {"scale": 1},
            "control-amp": {"scale": 0.9},                 
            "control-freq": {"scale": 0.8},                 
            "control-phase": {"scale": np.pi * 2},         
            "control-force": {"scale": 25},                  
        }
        # === PERSONAL WORK END ===

        ind = 0
        for key in gene_spec.keys():
            gene_spec[key]["ind"] = ind
            ind += 1
        return gene_spec

    @staticmethod
    def get_gene_dict(gene, spec):
        """Maps a raw gene array to a dictionary using the gene spec."""
        gdict = {}
        for key in spec:
            if "fixed" in spec[key]:
                gdict[key] = spec[key]["fixed"]
                continue

            ind = spec[key]["ind"]
            scale = spec[key]["scale"]
            if ind < len(gene):
                gdict[key] = float(gene[ind]) * scale
            else:
                gdict[key] = 0.0
        return gdict

    @staticmethod
    def get_genome_dicts(genome, spec):
        """Converts an entire genome list into a list of property dictionaries."""
        return [Genome.get_gene_dict(gene, spec) for gene in genome]

    @staticmethod
    def expandLinks(parent_link, uniq_parent_name, flat_links, exp_links):
        """Recursively expands links based on recurrence genes."""
        children = [l for l in flat_links if l.parent_name == parent_link.name]
        for c in children:
            for _ in range(int(c.recur)):
                c_copy = copy.copy(c)
                c_copy.parent_name = uniq_parent_name
                uniq_name = c_copy.name + str(len(exp_links))
                c_copy.name = uniq_name
                exp_links.append(c_copy)
                Genome.expandLinks(c, uniq_name, flat_links, exp_links)

    @staticmethod
    def genome_to_links(gdicts):
        """
        Converts gene dictionaries into a flat list of URDFLink objects.
        Calculates joint offsets to chain segments end-to-end.
        """
        links = []
        link_ind = 0
        prev_len = None

        # === PERSONAL WORK START ===
        # Linear chaining logic for centipede-like morphology
        for gdict in gdicts:
            link_name = str(link_ind)
            parent_name = str(link_ind - 1) if link_ind > 0 else "None"

            curr_len = float(gdict["link-length"])
            curr_rad = float(gdict["link-radius"])

            if prev_len is None:
                joint_y = 0.0
            else:
                # Calculate Y offset to place joint at the tip of the previous segment
                joint_y = (prev_len * 0.5) + (curr_len * 0.5)

            link = URDFLink(
                name=link_name,
                parent_name=parent_name,
                recur=1,
                link_length=curr_len,
                link_radius=curr_rad,
                link_mass=float(gdict["link-mass"]), 
                joint_type=float(gdict["joint-type"]),
                joint_parent=float(gdict["joint-parent"]),
                joint_axis_mode=float(gdict["joint-axis-mode"]),
                joint_origin_rpy_1=float(gdict["joint-origin-rpy-1"]),
                joint_origin_rpy_2=float(gdict["joint-origin-rpy-2"]),
                joint_origin_rpy_3=float(gdict["joint-origin-rpy-3"]),
                joint_origin_xyz_1=0.0,
                joint_origin_xyz_2=joint_y,  
                joint_origin_xyz_3=0.0,
                control_waveform=float(gdict["control-waveform"]),
                control_amp=float(gdict["control-amp"]),
                control_freq=float(gdict["control-freq"]),
                control_phase=float(gdict.get("control-phase", 0.0)),
                control_force=float(gdict.get("control-force", 5.0)),
            )
            links.append(link)

            prev_len = curr_len
            link_ind += 1
        # === PERSONAL WORK END ===

        links[0].parent_name = "None"
        return links

    @staticmethod
    def crossover(dna1, dna2):
        """
        Performs genetic crossover between two parents.
        Can handle both flat numpy arrays and nested lists of genes.
        """
        # === PERSONAL WORK START ===
        if dna1 is None or dna2 is None:
            raise ValueError("crossover received None DNA")

        if isinstance(dna1, np.ndarray) and isinstance(dna2, np.ndarray):
            cut1 = random.randint(0, len(dna1) - 1)
            cut2 = random.randint(0, len(dna2) - 1)
            child = np.concatenate((dna1[:cut1], dna2[cut2:]))
            return child[:len(dna1)]

        n = min(len(dna1), len(dna2))
        if n == 0:
            return []

        gcut = random.randint(1, n - 1) if n > 1 else 1
        child = []

        for i in range(n):
            a = dna1[i]
            b = dna2[i]
            base = a if i < gcut else b
            other = b if i < gcut else a

            # Intra-gene crossover
            if isinstance(base, np.ndarray) and isinstance(other, np.ndarray) and len(base) == len(other) and len(base) > 1:
                icut = random.randint(1, len(base) - 1)
                new_gene = np.concatenate((base[:icut], other[icut:]))
                child.append(new_gene.astype(float))
            else:
                child.append(copy.deepcopy(base))

        # Carry over remaining genes
        if len(dna1) > n:
            child.extend(copy.deepcopy(dna1[n:]))
        elif len(dna2) > n:
            child.extend(copy.deepcopy(dna2[n:]))

        return child
        # === PERSONAL WORK END ===

    @staticmethod
    def point_mutate(genome, rate, amount):
        """Randomly modifies values within genes based on rate and amount."""
        new_genome = copy.deepcopy(genome)
        for gene in new_genome:
            if not isinstance(gene, (np.ndarray, list)):
                continue

            for i in range(len(gene)):
                if random.random() < rate:
                    gene[i] += (random.random() * amount) - (amount / 2)

                # Clamp values between 0.0 and 1.0
                if gene[i] >= 1.0:
                    gene[i] = 0.9999
                if gene[i] < 0.0:
                    gene[i] = 0.0
        return new_genome

    @staticmethod
    def shrink_mutate(genome, rate):
        """Placeholder for shrink mutation; currently preserves genome."""
        return copy.deepcopy(genome)

    @staticmethod
    def grow_mutate(genome, rate):
        """Placeholder for grow mutation; currently preserves genome."""
        return copy.deepcopy(genome)

    @staticmethod
    def to_csv(dna, csv_file):
        """Saves genome DNA to a CSV file."""
        csv_str = ""
        for gene in dna:
            csv_str += ",".join(map(str, gene)) + "\n"
        with open(csv_file, "w") as f:
            f.write(csv_str)

    @staticmethod
    def from_csv(filename):
        """Loads genome DNA from a CSV file."""
        dna = []
        with open(filename) as f:
            lines = f.readlines()
        for line in lines:
            vals = line.strip().split(",")
            gene = [float(v) for v in vals if v != ""]
            if len(gene) > 0:
                dna.append(np.array(gene, dtype=float))
        return dna


class URDFLink:
    """
    Represents a single link and its associated joint in a URDF robot model.
    """
    def __init__(
        self,
        name,
        parent_name,
        recur,
        link_length=0.1,
        link_radius=0.1,
        link_mass=1.0,  
        joint_type=0.1,
        joint_parent=0.1,
        joint_axis_mode=0.1,
        joint_origin_rpy_1=0.0,
        joint_origin_rpy_2=0.0,
        joint_origin_rpy_3=0.0,
        joint_origin_xyz_1=0.0,
        joint_origin_xyz_2=0.0,
        joint_origin_xyz_3=0.0,
        control_waveform=0.1,
        control_amp=0.1,
        control_freq=0.1,
        control_phase=0.0,
        control_force=5.0,
    ):
        self.name = name
        self.parent_name = parent_name
        self.recur = recur
        self.link_length = float(link_length)
        self.link_radius = float(link_radius)
        self.link_mass = float(link_mass) 
        self.joint_type = joint_type
        self.joint_parent = joint_parent
        self.joint_axis_mode = joint_axis_mode
        self.joint_origin_rpy_1 = joint_origin_rpy_1
        self.joint_origin_rpy_2 = joint_origin_rpy_2
        self.joint_origin_rpy_3 = joint_origin_rpy_3
        self.joint_origin_xyz_1 = joint_origin_xyz_1
        self.joint_origin_xyz_2 = joint_origin_xyz_2
        self.joint_origin_xyz_3 = joint_origin_xyz_3
        self.control_waveform = control_waveform
        self.control_amp = control_amp
        self.control_freq = control_freq
        self.control_phase = control_phase
        self.control_force = control_force
        self.sibling_ind = 1

    def to_link_element(self, adom):
        """Generates the <link> XML element including visual, collision, and inertial tags."""
        link_tag = adom.createElement("link")
        link_tag.setAttribute("name", self.name)

        # === PERSONAL WORK START ===
        # Use capsule geometry for better physics stability over cylinders
        for tag_name in ["visual", "collision"]:
            tag = adom.createElement(tag_name)
            geom_tag = adom.createElement("geometry")
            caps_tag = adom.createElement("capsule")
            caps_tag.setAttribute("length", str(self.link_length))
            caps_tag.setAttribute("radius", str(self.link_radius))
            geom_tag.appendChild(caps_tag)
            tag.appendChild(geom_tag)
            link_tag.appendChild(tag)

        inertial_tag = adom.createElement("inertial")
        mass_tag = adom.createElement("mass")
        # Mass calculation based on volume and density
        volume = np.pi * (self.link_radius ** 2) * self.link_length
        mass_val = max(0.001, volume * self.link_mass)  
        mass_tag.setAttribute("value", str(mass_val))
        # === PERSONAL WORK END ===

        inertia_tag = adom.createElement("inertia")
        inertia_tag.setAttribute("ixx", "0.03")
        inertia_tag.setAttribute("iyy", "0.03")
        inertia_tag.setAttribute("izz", "0.03")
        inertia_tag.setAttribute("ixy", "0")
        inertia_tag.setAttribute("ixz", "0")
        inertia_tag.setAttribute("iyx", "0")

        inertial_tag.appendChild(mass_tag)
        inertial_tag.appendChild(inertia_tag)
        link_tag.appendChild(inertial_tag)

        return link_tag

    def to_joint_element(self, adom):
        """Generates the <joint> XML element connecting this link to its parent."""
        joint_tag = adom.createElement("joint")
        joint_tag.setAttribute("name", self.name + "_to_" + self.parent_name)
        joint_tag.setAttribute("type", "revolute")

        parent_tag = adom.createElement("parent")
        parent_tag.setAttribute("link", self.parent_name)

        child_tag = adom.createElement("child")
        child_tag.setAttribute("link", self.name)

        # === PERSONAL WORK START ===
        axis_tag = adom.createElement("axis")
        # Toggle between X and Z axis for joint movement
        if self.joint_axis_mode <= 0.5:
            axis_tag.setAttribute("xyz", "1 0 0")
        else:
            axis_tag.setAttribute("xyz", "0 0 1")

        limit_tag = adom.createElement("limit")
        limit_tag.setAttribute("effort", str(self.control_force))
        limit_tag.setAttribute("upper", str(Genome.FIXED_JOINT_LIMIT))
        limit_tag.setAttribute("lower", str(-Genome.FIXED_JOINT_LIMIT))
        limit_tag.setAttribute("velocity", "1")
        # === PERSONAL WORK END ===

        orig_tag = adom.createElement("origin")
        orig_tag.setAttribute("rpy", "0 0 0")
        orig_tag.setAttribute(
            "xyz",
            f"{self.joint_origin_xyz_1} {self.joint_origin_xyz_2} {self.joint_origin_xyz_3}",
        )

        joint_tag.appendChild(parent_tag)
        joint_tag.appendChild(child_tag)
        joint_tag.appendChild(axis_tag)
        joint_tag.appendChild(limit_tag)
        joint_tag.appendChild(orig_tag)

        return joint_tag