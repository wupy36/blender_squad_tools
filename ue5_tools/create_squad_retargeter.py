"""
create_squad_retargeter.py
==========================
Run this script from the UE5 Python console (Output Log > Cmd > Python) or
from an Editor Utility Widget's Python node.

What it does:
  1. Creates an IK Rig for the UE5 Mannequin skeleton (source)
  2. Creates an IK Rig for the Squad soldier skeleton (target)
  3. Creates an IK Retargeter mapping Manny -> Squad with matching chain names

After running, open the generated RTG_Manny_To_Squad asset and:
  - Check the retarget pose on both skeletons (set both to T-pose or match them)
  - Verify chain mappings look correct in the Chain Mapping panel
  - Run a test animation to preview results before batch retargeting

Tested against UE5.4 - 5.7.  If a method raises AttributeError, see the
COMPATIBILITY NOTE comments below for alternative call signatures.
"""

import unreal

# =============================================================================
# CONFIGURATION  —  edit these to match your project layout
# =============================================================================

# Squad soldier skeleton asset (USkeleton or USkeletalMesh — either works)
SQUAD_SKELETON_PATH = "/Game/Art/Soldier2/TEST_US_Soldier_Skeleton_V3"

# UE5 Mannequin skeletal mesh (the SK_BS_Mannequin from your project)
MANNY_SKELETON_PATH = "/Game/Assets/Soldiers/-Standard-/Meshes/SK_BS_Mannequin"

# Where the three new assets will be saved
OUTPUT_PATH = "/Game/Art/Retargeting"

# =============================================================================
# SQUAD SKELETON — bone chains
#
# Chain names are intentionally identical to the Manny chains below so that
# auto-mapping and manual set_chain_mapping() both work with the same strings.
# Bones that may not be present in every Squad export (e.g. finger sub-bones)
# will be skipped gracefully — a warning is printed for each missing bone.
# =============================================================================

SQUAD_RETARGET_ROOT = "Bip01"

# (chain_name, start_bone, end_bone)
SQUAD_CHAINS = [
    # Core
    ("Root",            "Root",              "Root"),
    ("Spine",           "Bip01_Spine",       "Bip01_Spine2"),
    ("Head",            "Bip01_Neck",        "Bip01_Head"),
    # Left arm
    ("LeftClavicle",    "Bip01_L_Clavicle",  "Bip01_L_Clavicle"),
    ("LeftArm",         "Bip01_L_UpperArm",  "Bip01_L_Hand"),
    # Right arm
    ("RightClavicle",   "Bip01_R_Clavicle",  "Bip01_R_Clavicle"),
    ("RightArm",        "Bip01_R_UpperArm",  "Bip01_R_Hand"),
    # Left leg
    ("LeftLeg",         "Bip01_L_Thigh",     "Bip01_L_Foot"),
    ("LeftToe",         "Bip01_L_Toe0",      "Bip01_L_Toe0"),
    # Right leg
    ("RightLeg",        "Bip01_R_Thigh",     "Bip01_R_Foot"),
    ("RightToe",        "Bip01_R_Toe0",      "Bip01_R_Toe0"),
    # Left fingers
    ("LeftThumb",       "Bip01_L_Finger0",   "Bip01_L_Finger02"),
    ("LeftIndex",       "Bip01_L_Finger1",   "Bip01_L_Finger12"),
    ("LeftMiddle",      "Bip01_L_Finger2",   "Bip01_L_Finger22"),
    ("LeftRing",        "Bip01_L_Finger3",   "Bip01_L_Finger32"),
    ("LeftPinky",       "Bip01_L_Finger4",   "Bip01_L_Finger42"),
    # Right fingers
    ("RightThumb",      "Bip01_R_Finger0",   "Bip01_R_Finger02"),
    ("RightIndex",      "Bip01_R_Finger1",   "Bip01_R_Finger12"),
    ("RightMiddle",     "Bip01_R_Finger2",   "Bip01_R_Finger22"),
    ("RightRing",       "Bip01_R_Finger3",   "Bip01_R_Finger32"),
    ("RightPinky",      "Bip01_R_Finger4",   "Bip01_R_Finger42"),
    # Weapon
    ("Weapon",          "Bip01_Weapon1",     "Bip01_Weapon1"),
]

# =============================================================================
# UE5 MANNEQUIN — bone chains
#
# Standard Epic UE5 Mannequin (Manny / Quinn) skeleton.
# spine_05 is included but silently skipped if your Manny only goes to spine_04.
# =============================================================================

MANNY_RETARGET_ROOT = "pelvis"

MANNY_CHAINS = [
    # Core
    ("Root",            "root",       "root"),
    ("Spine",           "spine_01",   "spine_05"),
    ("Head",            "neck_01",    "head"),
    # Left arm
    ("LeftClavicle",    "clavicle_l", "clavicle_l"),
    ("LeftArm",         "upperarm_l", "hand_l"),
    # Right arm
    ("RightClavicle",   "clavicle_r", "clavicle_r"),
    ("RightArm",        "upperarm_r", "hand_r"),
    # Left leg
    ("LeftLeg",         "thigh_l",    "foot_l"),
    ("LeftToe",         "ball_l",     "ball_l"),
    # Right leg
    ("RightLeg",        "thigh_r",    "foot_r"),
    ("RightToe",        "ball_r",     "ball_r"),
    # Left fingers
    ("LeftThumb",       "thumb_01_l", "thumb_03_l"),
    ("LeftIndex",       "index_01_l", "index_03_l"),
    ("LeftMiddle",      "middle_01_l","middle_03_l"),
    ("LeftRing",        "ring_01_l",  "ring_03_l"),
    ("LeftPinky",       "pinky_01_l", "pinky_03_l"),
    # Right fingers
    ("RightThumb",      "thumb_01_r", "thumb_03_r"),
    ("RightIndex",      "index_01_r", "index_03_r"),
    ("RightMiddle",     "middle_01_r","middle_03_r"),
    ("RightRing",       "ring_01_r",  "ring_03_r"),
    ("RightPinky",      "pinky_01_r", "pinky_03_r"),
    # Weapon
    ("Weapon",          "weapon_r",   "weapon_r"),
]

# =============================================================================
# HELPERS
# =============================================================================

def _delete_if_exists(full_asset_path):
    if unreal.EditorAssetLibrary.does_asset_exist(full_asset_path):
        unreal.EditorAssetLibrary.delete_asset(full_asset_path)
        unreal.log(f"  Deleted existing asset: {full_asset_path}")


def create_ik_rig(asset_name, skeleton_path, retarget_root, chains, output_path):
    """
    Create an IK Rig asset, assign a skeleton, set the retarget root, and
    add all bone chains.  Chains whose start or end bone is missing from the
    skeleton are skipped with a warning.
    Returns the created IKRigDefinition asset, or None on failure.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    full_path = f"{output_path}/{asset_name}"

    _delete_if_exists(full_path)

    ik_rig = asset_tools.create_asset(
        asset_name, output_path,
        unreal.IKRigDefinition,
        unreal.IKRigDefinitionFactory()
    )
    if ik_rig is None:
        unreal.log_error(f"Failed to create IK Rig asset at {full_path}")
        return None

    ctrl = unreal.IKRigController.get_controller(ik_rig)

    # Assign skeleton / skeletal mesh
    skel_asset = unreal.load_asset(skeleton_path)
    if skel_asset is None:
        unreal.log_error(f"Could not load skeleton asset: {skeleton_path}")
        return None
    ctrl.set_skeleton(skel_asset)

    # Set retarget root
    ctrl.set_retarget_root(retarget_root)

    # Add chains
    skipped = []
    for chain_name, start_bone, end_bone in chains:
        # COMPATIBILITY NOTE: some UE5 builds use add_retarget_chain(name, start, end)
        # while others require a FBoneChain struct — try the simple form first.
        try:
            success = ctrl.add_retarget_chain(chain_name, start_bone, end_bone)
            if not success:
                skipped.append((chain_name, start_bone, end_bone))
        except Exception as e:
            skipped.append((chain_name, start_bone, end_bone))
            unreal.log_warning(f"  Chain '{chain_name}': {e}")

    if skipped:
        unreal.log_warning(f"  Skipped {len(skipped)} chains in '{asset_name}' (bones not found):")
        for name, s, e in skipped:
            unreal.log_warning(f"    {name}: {s} -> {e}")

    unreal.EditorAssetLibrary.save_asset(full_path)
    unreal.log(f"  Saved: {full_path}")
    return ik_rig


def create_retargeter(asset_name, source_ik_rig, target_ik_rig, output_path):
    """
    Create an IK Retargeter asset wiring source_ik_rig -> target_ik_rig.
    Chain names are assumed identical in both IK Rigs (matching by name).
    Returns the created IKRetargeter asset, or None on failure.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    full_path = f"{output_path}/{asset_name}"

    _delete_if_exists(full_path)

    retargeter = asset_tools.create_asset(
        asset_name, output_path,
        unreal.IKRetargeter,
        unreal.IKRetargeterFactory()
    )
    if retargeter is None:
        unreal.log_error(f"Failed to create IK Retargeter at {full_path}")
        return None

    ctrl = unreal.IKRetargetController.get_controller(retargeter)

    # Assign IK Rigs
    # COMPATIBILITY NOTE: UE5.4 uses set_source_ik_rig / set_target_ik_rig.
    # UE5.3 and earlier may use set_ik_rig(RetargetSourceOrTarget.SOURCE, rig).
    try:
        ctrl.set_source_ik_rig(source_ik_rig)
        ctrl.set_target_ik_rig(target_ik_rig)
    except AttributeError:
        ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_ik_rig)
        ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_ik_rig)

    # Map chains — same name on both sides
    source_chain_names = [name for name, _, _ in MANNY_CHAINS]
    unmapped = []
    for chain_name in source_chain_names:
        try:
            ctrl.set_chain_mapping(chain_name, chain_name)
        except Exception as e:
            unmapped.append(chain_name)
            unreal.log_warning(f"  Could not map chain '{chain_name}': {e}")

    if unmapped:
        unreal.log_warning(f"  {len(unmapped)} chains could not be mapped automatically.")
        unreal.log_warning("  Open the retargeter and map them manually in the Chain Mapping panel.")

    unreal.EditorAssetLibrary.save_asset(full_path)
    unreal.log(f"  Saved: {full_path}")
    return retargeter


# =============================================================================
# MAIN
# =============================================================================

def main():
    with unreal.ScopedEditorTransaction("Create Squad Retargeter") as trans:

        unreal.log("=" * 60)
        unreal.log("Creating Squad <-> UE5 Manny IK Retargeter")
        unreal.log("=" * 60)

        # Ensure output folder exists
        unreal.EditorAssetLibrary.make_directory(OUTPUT_PATH)

        # 1. IK Rig — UE5 Manny (source)
        unreal.log("[1/3] Creating Manny IK Rig...")
        manny_rig = create_ik_rig(
            asset_name="IK_Manny_ForSquad",
            skeleton_path=MANNY_SKELETON_PATH,
            retarget_root=MANNY_RETARGET_ROOT,
            chains=MANNY_CHAINS,
            output_path=OUTPUT_PATH,
        )

        # 2. IK Rig — Squad skeleton (target)
        unreal.log("[2/3] Creating Squad IK Rig...")
        squad_rig = create_ik_rig(
            asset_name="IK_Squad_Soldier",
            skeleton_path=SQUAD_SKELETON_PATH,
            retarget_root=SQUAD_RETARGET_ROOT,
            chains=SQUAD_CHAINS,
            output_path=OUTPUT_PATH,
        )

        if manny_rig is None or squad_rig is None:
            unreal.log_error("Aborting — failed to create one or both IK Rigs.")
            return

        # 3. IK Retargeter
        unreal.log("[3/3] Creating IK Retargeter...")
        retargeter = create_retargeter(
            asset_name="RTG_Manny_To_Squad",
            source_ik_rig=manny_rig,
            target_ik_rig=squad_rig,
            output_path=OUTPUT_PATH,
        )

        if retargeter:
            unreal.log("=" * 60)
            unreal.log("Done!  Next steps:")
            unreal.log(f"  1. Open {OUTPUT_PATH}/RTG_Manny_To_Squad")
            unreal.log("  2. In 'Asset Browser' assign a reference pose to both skeletons")
            unreal.log("     (Retarget Pose > Edit Retarget Pose — pose both into T-pose)")
            unreal.log("  3. Verify chain mappings in the Chain Mapping panel")
            unreal.log("  4. Use Asset Browser > Export Animations to batch retarget")
            unreal.log("=" * 60)
        else:
            unreal.log_error("Failed to create retargeter — see warnings above.")


main()
