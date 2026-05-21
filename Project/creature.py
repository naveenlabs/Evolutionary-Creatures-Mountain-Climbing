"""
creature.py: Defines the Creature class and its associated Motor controller.
This module handles the transformation of genetic data into a structural robot
representation (XML) and manages movement and fitness evaluation.
"""

import genome
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np
import pybullet as p


class MotorType(Enum):
    """Enumeration for different types of motor control waveforms."""
    PULSE = 1
    SINE = 2


class Motor:
    """
    Represents a motor controller that generates cyclic output values.
    
    Args:
        control_waveform (float): Logic threshold to determine MotorType.
        control_amp (float): The amplitude of the motor output.
        control_freq (float): The frequency/speed of the phase cycle.
        control_phase (float): The starting offset of the phase.
    """
    def __init__(self, control_waveform, control_amp, control_freq, control_phase):
        self.motor_type = MotorType.PULSE if control_waveform <= 0.5 else MotorType.SINE
        self.amp = float(control_amp)
        self.freq = float(control_freq)
        self.phase = float(control_phase)

    def get_output(self):
        """Calculates and returns the current motor output based on phase."""
        self.phase = (self.phase + self.freq) % (np.pi * 2)

        if self.motor_type == MotorType.PULSE:
            output = 1.0 if self.phase < np.pi else -1.0
        else:
            output = float(np.sin(self.phase))

        return output * self.amp


class Creature:
    """
    Manages the lifecycle, morphology, and fitness of a simulated centipede creature.
    """

    # === PERSONAL WORK START ===
    # Custom constants for leg morphology and positioning
    LEG_LENGTH = 0.30
    LEG_RADIUS = 0.05
    LEG_DROP_FACTOR = 0.90  
    LEG_SIDE_GAP = 0.01  
    # === PERSONAL WORK END ===

    def __init__(self, gene_count):
        """Initializes the creature with random DNA based on the genome spec."""
        self.spec = genome.Genome.get_gene_spec()
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)

        self.flat_links = None
        self.exp_links = None
        self.motors = None

        self.start_position = None
        self.last_position = None
        
        # === PERSONAL WORK START ===
        # Extended tracking variables for advanced fitness calculation
        self.max_z = -9999
        self.last_z = 0
        self.last_orn = None
        self.contact_frames = 0
        self.total_frames = 0
        # === PERSONAL WORK END ===

    # === PERSONAL WORK START ===
    def _build_spine_links(self):
        """Internal helper to convert DNA into the core spine segments."""
        gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
        spine_links = genome.Genome.genome_to_links(gdicts)  
        return spine_links

    def _make_leg_link(self, parent_name: str, side: str, spine_radius: float):
        """
        Creates a URDFLink object configured as a leg attached to the spine.
        
        Args:
            parent_name (str): Name of the spine segment this leg attaches to.
            side (str): "L" for left side, "R" for right side.
            spine_radius (float): Radius of parent spine for collision avoidance.
        """
        assert side in ("L", "R")

        x_sign = 1.0 if side == "L" else -1.0
        x_off = x_sign * (spine_radius + self.LEG_RADIUS + self.LEG_SIDE_GAP)
        z_off = -self.LEG_DROP_FACTOR * (spine_radius + (self.LEG_LENGTH * 0.5))
        leg_name = f"{parent_name}_leg{side}"

        return genome.URDFLink(
            name=leg_name,
            parent_name=parent_name,
            recur=1,
            link_length=self.LEG_LENGTH,
            link_radius=self.LEG_RADIUS,
            link_mass=1.0, 
            joint_type=0.0,
            joint_parent=0.0,
            joint_axis_mode=0.0,
            joint_origin_rpy_1=0.0,
            joint_origin_rpy_2=0.0,
            joint_origin_rpy_3=0.0,
            joint_origin_xyz_1=x_off,
            joint_origin_xyz_2=0.0,
            joint_origin_xyz_3=z_off,
            control_waveform=0.0,
            control_amp=0.0,
            control_freq=0.0,
            control_phase=0.0,
            control_force=20.0,
        )
    # === PERSONAL WORK END ===

    def get_flat_links(self):
        """
        Generates the list of all links (spine + legs).
        Replaces the starter recursive expansion with custom centipede morphology.
        """
        if self.flat_links is not None:
            return self.flat_links

        # === PERSONAL WORK START ===
        spine = self._build_spine_links()
        if not spine:
            self.flat_links = []
            return self.flat_links

        spine_radius = float(spine[0].link_radius)
        exp = []

        # Build the centipede structure: Spine segment followed by two legs
        exp.append(spine[0])
        exp.append(self._make_leg_link(parent_name=spine[0].name, side="L", spine_radius=spine_radius))
        exp.append(self._make_leg_link(parent_name=spine[0].name, side="R", spine_radius=spine_radius))

        for i in range(1, len(spine)):
            seg = spine[i]
            exp.append(seg)
            exp.append(self._make_leg_link(parent_name=seg.name, side="L", spine_radius=spine_radius))
            exp.append(self._make_leg_link(parent_name=seg.name, side="R", spine_radius=spine_radius))

        self.flat_links = exp
        # === PERSONAL WORK END ===
        return self.flat_links

    def get_expanded_links(self):
        """Returns the flat list of links, ensuring they have been generated."""
        if self.exp_links is not None:
            return self.exp_links
        self.exp_links = self.get_flat_links()
        return self.exp_links

    def to_xml(self):
        """Converts the creature's morphology into a URDF XML string."""
        self.get_expanded_links()
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None, "start", None)

        robot_tag = adom.createElement("robot")

        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))

        first = True
        for link in self.exp_links:
            if first:
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))

        robot_tag.setAttribute("name", "centipede_fixed_morphology")
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()

    def get_motors(self):
        """Instantiates and returns the motor controllers for each joint."""
        self.get_expanded_links()

        if self.motors is not None:
            return self.motors

        motors = []
        for i in range(1, len(self.exp_links)):
            l = self.exp_links[i]
            m = Motor(
                l.control_waveform,
                l.control_amp,
                l.control_freq,
                l.control_phase
            )
            motors.append(m)

        self.motors = motors
        return self.motors

    def update_position(self, pos, orn, is_touching):
        """
        Updates the tracking data used for fitness calculation.
        
        Args:
            pos (tuple): (x, y, z) coordinates.
            orn (tuple): Orientation quaternion.
            is_touching (bool): Whether the creature is in contact with the ground.
        """
        # === PERSONAL WORK START ===
        self.total_frames += 1
        if is_touching:
            self.contact_frames += 1

        if self.start_position is None:
            self.start_position = pos

        self.last_position = pos
        self.last_orn = orn
        self.last_z = pos[2]

        if pos[2] > self.max_z:
            self.max_z = pos[2]
        # === PERSONAL WORK END ===

    def get_distance_travelled(self):
        """
        Calculates the fitness score based on height, movement, ground contact, 
        and uprightness.
        """
        # === PERSONAL WORK START ===
        if self.total_frames == 0 or self.start_position is None or self.last_orn is None:
            return 0.0

        z_score = float(self.last_z)

        # Movement distance relative to origin
        start_dist = float(np.sqrt(self.start_position[0] ** 2 + self.start_position[1] ** 2))
        curr_dist = float(np.sqrt(self.last_position[0] ** 2 + self.last_position[1] ** 2))
        distance_moved = start_dist - curr_dist
        distance_bonus = max(0.01, distance_moved)

        # Ground contact stability
        contact_ratio = self.contact_frames / self.total_frames
        contact_multiplier = 1.0 if contact_ratio > 0.8 else contact_ratio

        num_links = len(self.get_expanded_links())
        if num_links < 1:
            num_links = 1

        # Orientation penalty (Uprightness check)
        rot_matrix = p.getMatrixFromQuaternion(self.last_orn)
        local_z = rot_matrix[8]
        uprightness = max(0.0, float(local_z))
        upright_penalty = uprightness ** 4

        # Final Fitness aggregation
        raw_fitness = z_score * distance_bonus * contact_multiplier * upright_penalty
        return max(0.0, raw_fitness / num_links)
        # === PERSONAL WORK END ===

    def update_dna(self, dna):
        """Resets the creature state and updates its genetic data."""
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None

        self.start_position = None
        self.last_position = None
        self.last_orn = None

        # === PERSONAL WORK START ===
        self.max_z = -9999
        self.last_z = 0
        self.contact_frames = 0
        self.total_frames = 0
        # === PERSONAL WORK END ===