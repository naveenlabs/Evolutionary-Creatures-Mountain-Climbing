"""
realtime_from_csv.py: A visualizer script that loads a creature's DNA from 
a CSV file and renders its movement in a high-fidelity PyBullet GUI environment.
"""

import os
import sys
import time

import pybullet as p
import pybullet_data

import genome
import creature

# === PERSONAL WORK START ===
def apply_friction_to_body(body_id, lateral, spinning=0.0, rolling=0.0):
    """
    Applies custom friction coefficients to a body and all its constituent links.
    """
    try:
        p.changeDynamics(
            body_id,
            -1,
            lateralFriction=float(lateral),
            spinningFriction=float(spinning),
            rollingFriction=float(rolling),
        )

        num_joints = p.getNumJoints(body_id)
        for link_idx in range(num_joints):
            p.changeDynamics(
                body_id,
                link_idx,
                lateralFriction=float(lateral),
                spinningFriction=float(spinning),
                rollingFriction=float(rolling),
            )
    except Exception:
        pass


def build_world():
    """
    Constructs the 3D environment, matching the simulation arena exactly.
    Includes the floor, perimeter walls, and the central obstacle mountain.
    """
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -10)

    p.setPhysicsEngineParameter(
        fixedTimeStep=1.0 / 240.0,
        numSolverIterations=120,
        numSubSteps=1
    )

    arena_size = 25
    wall_height = 1.0
    wall_thickness = 0.5

    # Create the floor body
    floor_col = p.createCollisionShape(
        p.GEOM_BOX,
        halfExtents=[arena_size / 2, arena_size / 2, wall_thickness]
    )
    floor_vis = p.createVisualShape(
        p.GEOM_BOX,
        halfExtents=[arena_size / 2, arena_size / 2, wall_thickness],
        rgbaColor=[1, 1, 0, 1]
    )
    floor_id = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=floor_col,
        baseVisualShapeIndex=floor_vis,
        basePosition=[0, 0, -wall_thickness]
    )

    apply_friction_to_body(floor_id, lateral=0.5, spinning=0.05, rolling=0.0)

    # Perimeter Wall Generation
    wall_col = p.createCollisionShape(
        p.GEOM_BOX,
        halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2]
    )
    wall_vis = p.createVisualShape(
        p.GEOM_BOX,
        halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2],
        rgbaColor=[0.7, 0.7, 0.7, 1]
    )
    p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col, baseVisualShapeIndex=wall_vis, basePosition=[0, arena_size / 2, wall_height / 2])
    p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col, baseVisualShapeIndex=wall_vis, basePosition=[0, -arena_size / 2, wall_height / 2])

    wall_col_side = p.createCollisionShape(
        p.GEOM_BOX,
        halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2]
    )
    wall_vis_side = p.createVisualShape(
        p.GEOM_BOX,
        halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2],
        rgbaColor=[0.7, 0.7, 0.7, 1]
    )
    p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col_side, baseVisualShapeIndex=wall_vis_side, basePosition=[arena_size / 2, 0, wall_height / 2])
    p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_col_side, baseVisualShapeIndex=wall_vis_side, basePosition=[-arena_size / 2, 0, wall_height / 2])

    # Mountain (Obstacle) Generation
    if os.path.exists("shapes"):
        p.setAdditionalSearchPath("shapes")

    mountain_id = p.loadURDF("mountain.urdf", [0, 0, -1], useFixedBase=1)
    apply_friction_to_body(mountain_id, lateral=1.8, spinning=0.05, rolling=0.0)

    return floor_id, mountain_id


def apply_self_collision_filters(body_id):
    """
    Prevents adjacent links from colliding with each other to improve sim stability.
    """
    num_joints = p.getNumJoints(body_id)
    for jid in range(num_joints):
        info = p.getJointInfo(body_id, jid)
        parent_link = info[16]
        child_link = jid
        p.setCollisionFilterPair(body_id, body_id, parent_link if parent_link != -1 else -1, child_link, 0)
# === PERSONAL WORK END ===


def load_creature_from_csv(csv_file):
    """
    Reads DNA from CSV, builds the creature model, and generates a URDF for visualization.
    """
    dna = genome.Genome.from_csv(csv_file)
    gene_count = len(dna)

    cr = creature.Creature(gene_count=gene_count)
    cr.update_dna(dna)

    urdf_path = "viz_creature.urdf"
    with open(urdf_path, "w") as f:
        f.write(cr.to_xml())

    body_id = p.loadURDF(urdf_path)

    # === PERSONAL WORK START ===
    # Set specialized starting orientation and damping for visual tests
    start_orn = p.getQuaternionFromEuler([0, 0, -3.927])
    p.resetBasePositionAndOrientation(body_id, [5, 5, 2.5], start_orn)

    p.changeDynamics(body_id, -1, linearDamping=0.04, angularDamping=0.04)
    apply_self_collision_filters(body_id)
    # === PERSONAL WORK END ===

    return cr, body_id


def main(csv_file):
    """
    Main loop for GUI playback. Handles motor updates and camera initialization.
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(csv_file)

    p.connect(p.GUI)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

    # Set up the initial camera view
    p.resetDebugVisualizerCamera(
        cameraDistance=10,
        cameraYaw=45,
        cameraPitch=-30,
        cameraTargetPosition=[0, 0, 2]
    )

    build_world()
    cr, body_id = load_creature_from_csv(csv_file)

    motors = cr.get_motors()
    exp_links = cr.get_expanded_links()

    step = 0
    wait_time = 1.0 / 240.0
    total_time = 60.0
    elapsed = 0.0

    while elapsed < total_time:
        p.stepSimulation()
        step += 1

        if step % 24 == 0:
            usable = min(
                p.getNumJoints(body_id),
                len(motors),
                len(exp_links) - 1
            )

            for jid in range(usable):
                vel = motors[jid].get_output()
                # === PERSONAL WORK START ===
                # Apply the specific force evolved in the DNA/Link structure
                force = float(exp_links[jid + 1].control_force) 
                # === PERSONAL WORK END ===

                p.setJointMotorControl2(
                    bodyUniqueId=body_id,
                    jointIndex=jid,
                    controlMode=p.VELOCITY_CONTROL,
                    targetVelocity=vel,
                    force=force
                )

            pos, _ = p.getBasePositionAndOrientation(body_id)
            print(f"Height: {pos[2]:.3f}", end="\r")

        time.sleep(wait_time)
        elapsed += wait_time

    print("\nDone.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python realtime_from_csv.py path/to/creature.csv")
        sys.exit(1)

    main(sys.argv[1])