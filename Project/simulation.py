"""
simulation.py: Manages the PyBullet physics environment, arena construction, 
and the execution of creature movement trials with advanced contact logic.
"""

import os
import time
import pybullet as p
import pybullet_data
from multiprocessing import Pool


class Simulation:
    """
    Handles the physics setup and execution for a single creature evaluation.
    
    Args:
        sim_id (int): Unique identifier for the simulation instance.
        gui (bool): Whether to run PyBullet with a visual window.
    """
    def __init__(
        self,
        sim_id=0,
        gui=False,

        # === PERSONAL WORK START ===
        # Custom friction parameters for different terrain types
        mountain_lateral_friction=1.8,
        mountain_spinning_friction=0.05,
        mountain_rolling_friction=0.0,
        floor_lateral_friction=0.5,
        floor_spinning_friction=0.05,
        floor_rolling_friction=0.0,

        # Gating logic parameters for stabilizing movement
        enable_contact_gating=True,
        gate_contact_links=True,
        anchor_base_when_touching=True,
        anchor_front_joints=2,
        anchor_force_multiplier=2.5,
        # === PERSONAL WORK END ===
    ):
        self.sim_id = int(sim_id)
        self.gui = bool(gui)

        self.mountain_lateral_friction = float(mountain_lateral_friction)
        self.mountain_spinning_friction = float(mountain_spinning_friction)
        self.mountain_rolling_friction = float(mountain_rolling_friction)

        self.floor_lateral_friction = float(floor_lateral_friction)
        self.floor_spinning_friction = float(floor_spinning_friction)
        self.floor_rolling_friction = float(floor_rolling_friction)

        # === PERSONAL WORK START ===
        self.enable_contact_gating = bool(enable_contact_gating)
        self.gate_contact_links = bool(gate_contact_links)
        self.anchor_base_when_touching = bool(anchor_base_when_touching)
        self.anchor_front_joints = max(0, int(anchor_front_joints))
        self.anchor_force_multiplier = float(anchor_force_multiplier)
        # === PERSONAL WORK END ===

        self.physicsClientId = p.connect(p.GUI if self.gui else p.DIRECT)

    def close(self):
        """Safely disconnects from the physics engine."""
        try:
            p.disconnect(physicsClientId=self.physicsClientId)
        except Exception:
            pass

    def __del__(self):
        self.close()

    # === PERSONAL WORK START ===
    def _apply_friction_to_body(self, body_id, lateral, spinning=0.0, rolling=0.0):
        """Recursively applies friction settings to a body and all its links."""
        pid = self.physicsClientId
        try:
            p.changeDynamics(
                body_id,
                -1,
                lateralFriction=float(lateral),
                spinningFriction=float(spinning),
                rollingFriction=float(rolling),
                physicsClientId=pid,
            )

            num_joints = p.getNumJoints(body_id, physicsClientId=pid)
            for link_idx in range(num_joints):
                p.changeDynamics(
                    body_id,
                    link_idx,
                    lateralFriction=float(lateral),
                    spinningFriction=float(spinning),
                    rollingFriction=float(rolling),
                    physicsClientId=pid,
                )
        except Exception:
            pass

    def _get_contact_links(self, body_a, body_b):
        """Returns a set of link indices of body_a currently touching body_b."""
        pid = self.physicsClientId
        links = set()
        try:
            cps = p.getContactPoints(bodyA=body_a, bodyB=body_b, physicsClientId=pid)
            for c in cps:
                links.add(int(c[3]))
        except Exception:
            pass
        return links
    # === PERSONAL WORK END ===

    def _setup_world(self):
        """
        Creates the simulation environment, including gravity, floor, 
        perimeter walls, and the gaussian pyramid (mountain) obstacle.
        """
        pid = self.physicsClientId

        p.resetSimulation(physicsClientId=pid)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=pid)

        # === PERSONAL WORK START ===
        # Path handling for custom URDF shapes
        try:
            p.setAdditionalSearchPath(os.getcwd(), physicsClientId=pid)
        except Exception:
            pass
        if os.path.exists("shapes"):
            try:
                p.setAdditionalSearchPath(os.path.abspath("shapes"), physicsClientId=pid)
            except Exception:
                pass

        p.setGravity(0, 0, -10, physicsClientId=pid)
        p.setPhysicsEngineParameter(
            enableFileCaching=0,
            fixedTimeStep=1.0 / 240.0,
            numSolverIterations=120,
            numSubSteps=1,
            physicsClientId=pid,
        )

        # Arena construction (Floor + 4 Walls)
        arena_size = 25
        wall_height = 1.0
        wall_thickness = 0.5

        floor_col = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=[arena_size / 2, arena_size / 2, wall_thickness],
            physicsClientId=pid,
        )
        floor_vis = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[arena_size / 2, arena_size / 2, wall_thickness],
            rgbaColor=[1, 1, 0, 1],
            physicsClientId=pid,
        )
        floor_id = p.createMultiBody(
            baseMass=0,
            baseCollisionShapeIndex=floor_col,
            baseVisualShapeIndex=floor_vis,
            basePosition=[0, 0, -wall_thickness],
            physicsClientId=pid,
        )

        self._apply_friction_to_body(
            floor_id,
            lateral=self.floor_lateral_friction,
            spinning=self.floor_spinning_friction,
            rolling=self.floor_rolling_friction,
        )

        # Create arena boundary walls
        wall_col = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2],
            physicsClientId=pid,
        )
        wall_vis = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2],
            rgbaColor=[0.7, 0.7, 0.7, 1],
            physicsClientId=pid,
        )
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col, baseVisualShapeIndex=wall_vis, basePosition=[0, arena_size / 2, wall_height / 2], physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col, baseVisualShapeIndex=wall_vis, basePosition=[0, -arena_size / 2, wall_height / 2], physicsClientId=pid)

        wall_col_side = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2],
            physicsClientId=pid,
        )
        wall_vis_side = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2],
            rgbaColor=[0.7, 0.7, 0.7, 1],
            physicsClientId=pid,
        )
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col_side, baseVisualShapeIndex=wall_vis_side, basePosition=[arena_size / 2, 0, wall_height / 2], physicsClientId=pid)
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col_side, baseVisualShapeIndex=wall_vis_side, basePosition=[-arena_size / 2, 0, wall_height / 2], physicsClientId=pid)

        # Mountain URDF loading logic
        mountain_urdf_candidates = [
            "mountain.urdf",
            os.path.join("shapes", "mountain.urdf"),
            os.path.abspath(os.path.join("shapes", "mountain.urdf")),
        ]

        mountain_id = None
        last_err = None
        for path in mountain_urdf_candidates:
            try:
                mountain_id = p.loadURDF(path, [0, 0, -1], useFixedBase=1, physicsClientId=pid)
                break
            except Exception as e:
                last_err = e
                mountain_id = None

        if mountain_id is None:
            raise FileNotFoundError(f"Could not load gaussian_pyramid.urdf. Last error: {last_err}")

        self._apply_friction_to_body(
            mountain_id,
            lateral=self.mountain_lateral_friction,
            spinning=self.mountain_spinning_friction,
            rolling=self.mountain_rolling_friction,
        )
        # === PERSONAL WORK END ===

        return floor_id, mountain_id

    def _load_creature(self, cr):
        """Generates a temporary URDF file for the creature and loads it into the world."""
        pid = self.physicsClientId

        # === PERSONAL WORK START ===
        # Unique file naming to prevent collisions in multiprocessing
        xml_file = f"temp_{self.sim_id}_{os.getpid()}_{time.time_ns()}.urdf"
        with open(xml_file, "w") as f:
            f.write(cr.to_xml())

        try:
            cid = p.loadURDF(xml_file, physicsClientId=pid)
        finally:
            try:
                os.remove(xml_file)
            except Exception:
                pass

        # Position creature at a specific start location and orientation
        start_orn = p.getQuaternionFromEuler([0, 0, -3.927])
        p.resetBasePositionAndOrientation(
            cid, [5, 5, 2.5], start_orn, physicsClientId=pid
        )

        p.changeDynamics(
            cid,
            -1,
            linearDamping=0.04,
            angularDamping=0.04,
            physicsClientId=pid,
        )
        # === PERSONAL WORK END ===

        return cid

    def _apply_self_collision_filters(self, cid):
        """Disables collisions between immediate parent/child link pairs."""
        # === PERSONAL WORK START ===
        pid = self.physicsClientId
        num_joints = p.getNumJoints(cid, physicsClientId=pid)

        for jid in range(num_joints):
            info = p.getJointInfo(cid, jid, physicsClientId=pid)
            parent_link = int(info[16])  
            child_link = int(jid)       
            try:
                p.setCollisionFilterPair(
                    cid,
                    cid,
                    parent_link if parent_link != -1 else -1,
                    child_link,
                    enableCollision=0,
                    physicsClientId=pid,
                )
            except Exception:
                pass
        # === PERSONAL WORK END ===

    def update_motors(self, cid, cr, contact_links=None, base_touching=False):
        """
        Processes motor outputs. Implements contact gating which anchors 
        specific joints in POSITION_CONTROL when touching terrain.
        """
        pid = self.physicsClientId

        try:
            num_joints = p.getNumJoints(cid, physicsClientId=pid)
            exp_links = cr.get_expanded_links()
            motors = cr.get_motors()

            usable = min(num_joints, len(motors), len(exp_links) - 1)
            if usable <= 0:
                return

            contact_links = contact_links or set()

            # === PERSONAL WORK START ===
            # Advanced anchor logic for stabilizing the creature
            hold_joints = set()

            if self.enable_contact_gating and self.gate_contact_links:
                for jid in range(usable):
                    if jid in contact_links:
                        hold_joints.add(jid)

            if self.enable_contact_gating and self.anchor_base_when_touching and base_touching:
                for jid in range(min(self.anchor_front_joints, usable)):
                    hold_joints.add(jid)

            for jid in range(usable):
                force = float(exp_links[jid + 1].control_force)
                if jid in hold_joints:
                    # Anchor joint at current position to create 'grip'
                    js = p.getJointState(cid, jid, physicsClientId=pid)
                    cur_pos = float(js[0])
                    p.setJointMotorControl2(
                        bodyIndex=cid,
                        jointIndex=jid,
                        controlMode=p.POSITION_CONTROL,
                        targetPosition=cur_pos,
                        force=force * self.anchor_force_multiplier,
                        physicsClientId=pid,
                    )
                else:
                    # Standard cyclic velocity control
                    out = float(motors[jid].get_output())
                    amp = float(getattr(motors[jid], "amp", 1.0))
                    target_vel = out * amp

                    p.setJointMotorControl2(
                        bodyIndex=cid,
                        jointIndex=jid,
                        controlMode=p.VELOCITY_CONTROL,
                        targetVelocity=target_vel,
                        force=force,
                        physicsClientId=pid,
                    )
            # === PERSONAL WORK END ===

        except Exception:
            pass

    def run_creature(self, cr, iterations=2400):
        """Executes the simulation loop for a set number of iterations."""
        pid = self.physicsClientId
        floor_id, mountain_id = self._setup_world()
        cid = self._load_creature(cr)
        self._apply_self_collision_filters(cid)

        try:
            self.update_motors(cid, cr, contact_links=set(), base_touching=False)
        except Exception:
            pass

        for step in range(int(iterations)):
            p.stepSimulation(physicsClientId=pid)

            # === PERSONAL WORK START ===
            # Dynamic contact detection every frame
            touch_mount_links = self._get_contact_links(cid, mountain_id)
            touch_floor_links = self._get_contact_links(cid, floor_id)
            is_touching = (len(touch_mount_links) > 0) or (len(touch_floor_links) > 0)

            # Check if the root/base link is touching terrain
            base_touching = (-1 in touch_mount_links) or (-1 in touch_floor_links)

            if step % 24 == 0:
                self.update_motors(
                    cid,
                    cr,
                    contact_links=touch_mount_links,
                    base_touching=base_touching,
                )
            # === PERSONAL WORK END ===

            try:
                pos, orn = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
                cr.update_position(pos, orn, is_touching)
            except p.error:
                break

            if self.gui:
                time.sleep(1.0 / 240.0)


class ThreadedSim:
    """Handles parallel evaluation of multiple creatures using a process pool."""
    def __init__(self, pool_size=2):
        self.pool_size = int(pool_size)

    @staticmethod
    def _worker_run(sim_id, cr, iterations):
        """Stand-alone worker function to run a single creature trial."""
        sim = Simulation(sim_id=sim_id, gui=False)
        try:
            sim.run_creature(cr, iterations)
            return cr
        finally:
            sim.close()

    def eval_population(self, pop, iterations):
        """Dispatches population to workers and updates results."""
        args = [(i, cr, iterations) for i, cr in enumerate(pop.creatures)]
        with Pool(self.pool_size) as pool:
            pop.creatures = pool.starmap(ThreadedSim._worker_run, args)