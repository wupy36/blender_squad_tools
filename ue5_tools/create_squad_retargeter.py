"""
create_squad_retargeter.py
==========================
Run this script from the UE5 Python console (Output Log > Cmd > Python) or
from an Editor Utility Widget's Python node.

What it does:
  1. Validates both skeleton assets (checks configured paths, then falls back
     to the current Content Browser selection with a confirmation dialog)
  2. Inspects each skeleton's bone hierarchy and warns about any expected
     bones that are missing
  3. Creates an IK Rig for the UE5 Mannequin skeleton (source)
  4. Creates an IK Rig for the Squad soldier skeleton (target)
  5. Creates an IK Retargeter mapping Manny -> Squad with matching chain names

After running, open RTG_Manny_To_Squad and:
  - Set a matching retarget pose on both sides (Retarget Pose > Edit Retarget Pose)
  - Verify chain mappings in the Chain Mapping panel
  - Use Asset Browser > Export Animations to batch retarget

Tested against UE5.4 - 5.7.
"""

import unreal

# =============================================================================
# CONFIGURATION  —  edit these to match your project layout
# =============================================================================

SQUAD_SKELETON_PATH = "/Game/Art/Soldier2/TEST_US_Soldier_Skeleton_V3"
MANNY_SKELETON_PATH  = "/Game/Assets/Soldiers/-Standard-/Meshes/SK_BS_Mannequin"
OUTPUT_PATH          = "/Game/Art/Retargeting"

# =============================================================================
# EXPECTED BONE HIERARCHIES
# Used to validate that the correct skeleton was found before doing any work.
# Only "landmark" bones are listed — if these exist, the skeleton is likely
# correct.  Chains whose bones are absent are skipped with a warning.
# =============================================================================

SQUAD_RETARGET_ROOT  = "Bip01"
SQUAD_LANDMARK_BONES = [
    "Bip01", "Bip01_Spine", "Bip01_Spine2",
    "Bip01_Neck", "Bip01_Head",
    "Bip01_L_Thigh", "Bip01_L_Calf", "Bip01_L_Foot",
    "Bip01_R_Thigh", "Bip01_R_Calf", "Bip01_R_Foot",
    "Bip01_L_UpperArm", "Bip01_L_Hand",
    "Bip01_R_UpperArm", "Bip01_R_Hand",
]

MANNY_RETARGET_ROOT  = "pelvis"
MANNY_LANDMARK_BONES = [
    "pelvis", "spine_01", "spine_03",
    "neck_01", "head",
    "thigh_l", "calf_l", "foot_l",
    "thigh_r", "calf_r", "foot_r",
    "upperarm_l", "hand_l",
    "upperarm_r", "hand_r",
]

# =============================================================================
# BONE CHAINS
# Chain names are identical in both IK Rigs so set_chain_mapping works 1-to-1.
# Bones missing from a skeleton cause that chain to be skipped with a warning.
# =============================================================================

SQUAD_CHAINS = [
    # (chain_name,      start_bone,          end_bone)
    ("Root",            "Root",              "Root"),
    ("Spine",           "Bip01_Spine",       "Bip01_Spine2"),
    ("Head",            "Bip01_Neck",        "Bip01_Head"),
    ("LeftClavicle",    "Bip01_L_Clavicle",  "Bip01_L_Clavicle"),
    ("LeftArm",         "Bip01_L_UpperArm",  "Bip01_L_Hand"),
    ("RightClavicle",   "Bip01_R_Clavicle",  "Bip01_R_Clavicle"),
    ("RightArm",        "Bip01_R_UpperArm",  "Bip01_R_Hand"),
    ("LeftLeg",         "Bip01_L_Thigh",     "Bip01_L_Foot"),
    ("LeftToe",         "Bip01_L_Toe0",      "Bip01_L_Toe0"),
    ("RightLeg",        "Bip01_R_Thigh",     "Bip01_R_Foot"),
    ("RightToe",        "Bip01_R_Toe0",      "Bip01_R_Toe0"),
    ("LeftThumb",       "Bip01_L_Finger0",   "Bip01_L_Finger02"),
    ("LeftIndex",       "Bip01_L_Finger1",   "Bip01_L_Finger12"),
    ("LeftMiddle",      "Bip01_L_Finger2",   "Bip01_L_Finger22"),
    ("LeftRing",        "Bip01_L_Finger3",   "Bip01_L_Finger32"),
    ("LeftPinky",       "Bip01_L_Finger4",   "Bip01_L_Finger42"),
    ("RightThumb",      "Bip01_R_Finger0",   "Bip01_R_Finger02"),
    ("RightIndex",      "Bip01_R_Finger1",   "Bip01_R_Finger12"),
    ("RightMiddle",     "Bip01_R_Finger2",   "Bip01_R_Finger22"),
    ("RightRing",       "Bip01_R_Finger3",   "Bip01_R_Finger32"),
    ("RightPinky",      "Bip01_R_Finger4",   "Bip01_R_Finger42"),
    ("Weapon",          "Bip01_Weapon1",     "Bip01_Weapon1"),
]

MANNY_CHAINS = [
    ("Root",            "root",        "root"),
    ("Spine",           "spine_01",    "spine_05"),
    ("Head",            "neck_01",     "head"),
    ("LeftClavicle",    "clavicle_l",  "clavicle_l"),
    ("LeftArm",         "upperarm_l",  "hand_l"),
    ("RightClavicle",   "clavicle_r",  "clavicle_r"),
    ("RightArm",        "upperarm_r",  "hand_r"),
    ("LeftLeg",         "thigh_l",     "foot_l"),
    ("LeftToe",         "ball_l",      "ball_l"),
    ("RightLeg",        "thigh_r",     "foot_r"),
    ("RightToe",        "ball_r",      "ball_r"),
    ("LeftThumb",       "thumb_01_l",  "thumb_03_l"),
    ("LeftIndex",       "index_01_l",  "index_03_l"),
    ("LeftMiddle",      "middle_01_l", "middle_03_l"),
    ("LeftRing",        "ring_01_l",   "ring_03_l"),
    ("LeftPinky",       "pinky_01_l",  "pinky_03_l"),
    ("RightThumb",      "thumb_01_r",  "thumb_03_r"),
    ("RightIndex",      "index_01_r",  "index_03_r"),
    ("RightMiddle",     "middle_01_r", "middle_03_r"),
    ("RightRing",       "ring_01_r",   "ring_03_r"),
    ("RightPinky",      "pinky_01_r",  "pinky_03_r"),
    ("Weapon",          "weapon_r",    "weapon_r"),
]

# =============================================================================
# ASSET RESOLUTION & VALIDATION
# =============================================================================

_SKEL_TYPES = (unreal.SkeletalMesh, unreal.Skeleton)


def _asset_package_path(asset):
    """Return the /Game/... package path for a loaded asset (no .ObjectName suffix)."""
    return asset.get_path_name().split(".")[0]


def _dialog(title, message, msg_type=None):
    """Show a modal dialog. msg_type defaults to AppMsgType.OK."""
    if msg_type is None:
        msg_type = unreal.AppMsgType.OK
    return unreal.EditorDialog.show_message(title, message, msg_type)


def resolve_asset(configured_path, label):
    """
    Return a loaded SkeletalMesh or Skeleton for *label* (e.g. "Squad skeleton").

    Resolution order:
      1. Try the configured path — success if asset exists and is the right type.
      2. If that fails, inspect the Content Browser selection:
           - If exactly one valid asset is selected, ask the user whether to use it.
           - If multiple valid assets are selected, show them and ask which to use
             (the user must re-select one and re-run — we pick the first for now).
           - If nothing valid is selected, show an instructional dialog and abort.

    Raises RuntimeError if no valid asset can be resolved.
    """
    # --- Attempt 1: configured path ---
    if unreal.EditorAssetLibrary.does_asset_exist(configured_path):
        asset = unreal.load_asset(configured_path)
        if isinstance(asset, _SKEL_TYPES):
            unreal.log(f"  [{label}] Loaded from config: {configured_path}")
            return asset
        else:
            unreal.log_warning(
                f"  [{label}] Asset at configured path is not a SkeletalMesh/Skeleton "
                f"(got {type(asset).__name__}). Falling back to Content Browser selection."
            )
    else:
        unreal.log_warning(
            f"  [{label}] Configured path not found: {configured_path}\n"
            f"             Falling back to Content Browser selection."
        )

    # --- Attempt 2: Content Browser selection ---
    selected = unreal.EditorUtilityLibrary.get_selected_assets()
    candidates = [a for a in selected if isinstance(a, _SKEL_TYPES)]

    if not candidates:
        _dialog(
            f"Asset Not Found — {label}",
            f"Could not find a SkeletalMesh or Skeleton at:\n"
            f"  {configured_path}\n\n"
            f"Nothing suitable is selected in the Content Browser either.\n\n"
            f"Fix one of the following, then re-run the script:\n"
            f"  • Update {label.upper().replace(' ', '_')}_PATH at the top of the script, OR\n"
            f"  • Select the correct {label} in the Content Browser before running."
        )
        raise RuntimeError(f"No valid asset found for {label}.")

    chosen = candidates[0]
    chosen_path = _asset_package_path(chosen)

    if len(candidates) > 1:
        names = "\n".join(f"  • {_asset_package_path(a)}" for a in candidates)
        _dialog(
            f"Multiple Assets Selected — {label}",
            f"Multiple valid assets are selected. The script will use the first one:\n"
            f"  {chosen_path}\n\n"
            f"All selected:\n{names}\n\n"
            f"If this is wrong, deselect all, select only the correct asset, and re-run."
        )
    else:
        result = _dialog(
            f"Asset Not At Configured Path — {label}",
            f"Could not find:\n  {configured_path}\n\n"
            f"Found selected in Content Browser:\n  {chosen_path}\n\n"
            f"Use this asset as the {label}?",
            unreal.AppMsgType.YES_NO,
        )
        if result != unreal.AppReturnType.YES:
            raise RuntimeError(f"User declined to use selected asset for {label}.")

    unreal.log(f"  [{label}] Using Content Browser selection: {chosen_path}")
    return chosen


def validate_bone_hierarchy(asset, landmark_bones, retarget_root, label):
    """
    Create a temporary IK Rig (not saved), assign the skeleton, then probe
    whether the retarget root and each landmark bone are present by attempting
    to add a single-bone chain for each.

    Returns (ok, missing_bones) where ok=True means the root bone was found.
    Missing landmark bones are reported but don't block execution.
    """
    # Create a throw-away IK Rig purely for probing
    probe_rig = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "_probe_rig_temp", OUTPUT_PATH,
        unreal.IKRigDefinition, unreal.IKRigDefinitionFactory()
    )
    if probe_rig is None:
        unreal.log_warning(f"  [{label}] Could not create probe rig — skipping hierarchy check.")
        return True, []

    ctrl = unreal.IKRigController.get_controller(probe_rig)
    ctrl.set_skeleton(asset)

    # Check retarget root first — this is a hard requirement
    root_ok = ctrl.set_retarget_root(retarget_root)

    # Check each landmark by trying to add a single-bone chain
    missing = []
    for bone in landmark_bones:
        try:
            added = ctrl.add_retarget_chain(f"_probe_{bone}", bone, bone)
            if not added:
                missing.append(bone)
        except Exception:
            missing.append(bone)

    # Clean up the probe asset
    probe_path = f"{OUTPUT_PATH}/_probe_rig_temp"
    unreal.EditorAssetLibrary.delete_asset(probe_path)

    # Report results
    if not root_ok:
        _dialog(
            f"Wrong Skeleton — {label}",
            f"The expected root bone '{retarget_root}' was NOT found in:\n"
            f"  {_asset_package_path(asset)}\n\n"
            f"This is almost certainly the wrong skeleton.\n\n"
            f"Please select the correct {label} in the Content Browser and re-run,\n"
            f"or update the path constant at the top of the script."
        )
        return False, missing

    if missing:
        names = "\n".join(f"  • {b}" for b in missing)
        _dialog(
            f"Missing Bones — {label}",
            f"The following expected bones were NOT found in:\n"
            f"  {_asset_package_path(asset)}\n\n"
            f"{names}\n\n"
            f"Chains that use these bones will be skipped.\n"
            f"The retargeter will still be created — verify the Chain Mapping\n"
            f"panel afterwards and add any missing chains manually."
        )

    found = len(landmark_bones) - len(missing)
    unreal.log(
        f"  [{label}] Hierarchy check: {found}/{len(landmark_bones)} landmark bones found"
        + (f", {len(missing)} missing" if missing else " — OK")
    )
    return True, missing


# =============================================================================
# IK RIG & RETARGETER CREATION
# =============================================================================

def _delete_if_exists(full_asset_path):
    if unreal.EditorAssetLibrary.does_asset_exist(full_asset_path):
        unreal.EditorAssetLibrary.delete_asset(full_asset_path)


def create_ik_rig(asset_name, skel_asset, retarget_root, chains, output_path):
    """Create and save an IK Rig with the given retarget root and bone chains."""
    full_path = f"{output_path}/{asset_name}"
    _delete_if_exists(full_path)

    ik_rig = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, output_path,
        unreal.IKRigDefinition, unreal.IKRigDefinitionFactory()
    )
    if ik_rig is None:
        unreal.log_error(f"Failed to create IK Rig: {full_path}")
        return None

    ctrl = unreal.IKRigController.get_controller(ik_rig)
    ctrl.set_skeleton(skel_asset)
    ctrl.set_retarget_root(retarget_root)

    skipped = []
    for chain_name, start_bone, end_bone in chains:
        try:
            if not ctrl.add_retarget_chain(chain_name, start_bone, end_bone):
                skipped.append(chain_name)
        except Exception as exc:
            skipped.append(chain_name)
            unreal.log_warning(f"    Chain '{chain_name}': {exc}")

    added = len(chains) - len(skipped)
    unreal.log(f"  {full_path}: {added}/{len(chains)} chains added"
               + (f" ({len(skipped)} skipped: {', '.join(skipped)})" if skipped else ""))

    unreal.EditorAssetLibrary.save_asset(full_path)
    return ik_rig


def create_retargeter(asset_name, source_rig, target_rig, chain_names, output_path):
    """Create and save an IK Retargeter wiring source_rig -> target_rig."""
    full_path = f"{output_path}/{asset_name}"
    _delete_if_exists(full_path)

    retargeter = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, output_path,
        unreal.IKRetargeter, unreal.IKRetargeterFactory()
    )
    if retargeter is None:
        unreal.log_error(f"Failed to create IK Retargeter: {full_path}")
        return None

    ctrl = unreal.IKRetargetController.get_controller(retargeter)

    # COMPATIBILITY: UE5.4+ uses set_source/set_target; older builds use set_ik_rig + enum
    try:
        ctrl.set_source_ik_rig(source_rig)
        ctrl.set_target_ik_rig(target_rig)
    except AttributeError:
        ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
        ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)

    unmapped = []
    for name in chain_names:
        try:
            ctrl.set_chain_mapping(name, name)
        except Exception:
            unmapped.append(name)

    mapped = len(chain_names) - len(unmapped)
    unreal.log(f"  {full_path}: {mapped}/{len(chain_names)} chains mapped"
               + (f" ({len(unmapped)} unmapped)" if unmapped else ""))
    if unmapped:
        unreal.log_warning("  Unmapped chains (add manually in the Chain Mapping panel): "
                           + ", ".join(unmapped))

    unreal.EditorAssetLibrary.save_asset(full_path)
    return retargeter


# =============================================================================
# MAIN
# =============================================================================

def main():
    unreal.log("=" * 60)
    unreal.log("  Squad <-> UE5 Manny IK Retargeter Setup")
    unreal.log("=" * 60)

    unreal.EditorAssetLibrary.make_directory(OUTPUT_PATH)

    # ------------------------------------------------------------------
    # Step 1 — Resolve assets (check paths, fall back to CB selection)
    # ------------------------------------------------------------------
    unreal.log("\n[1/5] Resolving skeleton assets...")
    try:
        manny_asset = resolve_asset(MANNY_SKELETON_PATH,  "UE5 Mannequin skeleton")
        squad_asset = resolve_asset(SQUAD_SKELETON_PATH,  "Squad soldier skeleton")
    except RuntimeError as e:
        unreal.log_error(f"Aborted: {e}")
        return

    # ------------------------------------------------------------------
    # Step 2 — Validate bone hierarchies
    # ------------------------------------------------------------------
    unreal.log("\n[2/5] Validating bone hierarchies...")

    manny_ok, _ = validate_bone_hierarchy(
        manny_asset, MANNY_LANDMARK_BONES, MANNY_RETARGET_ROOT, "UE5 Mannequin"
    )
    squad_ok, _ = validate_bone_hierarchy(
        squad_asset, SQUAD_LANDMARK_BONES, SQUAD_RETARGET_ROOT, "Squad skeleton"
    )

    if not manny_ok or not squad_ok:
        unreal.log_error("Aborted — one or both skeletons failed hierarchy validation.")
        return

    # ------------------------------------------------------------------
    # Step 3 & 4 — Build IK Rigs
    # ------------------------------------------------------------------
    with unreal.ScopedEditorTransaction("Create Squad IK Rigs and Retargeter"):

        unreal.log("\n[3/5] Creating Manny IK Rig...")
        manny_rig = create_ik_rig(
            "IK_Manny_ForSquad", manny_asset,
            MANNY_RETARGET_ROOT, MANNY_CHAINS, OUTPUT_PATH
        )

        unreal.log("\n[4/5] Creating Squad IK Rig...")
        squad_rig = create_ik_rig(
            "IK_Squad_Soldier", squad_asset,
            SQUAD_RETARGET_ROOT, SQUAD_CHAINS, OUTPUT_PATH
        )

        if not manny_rig or not squad_rig:
            unreal.log_error("Aborted — IK Rig creation failed.")
            return

        # --------------------------------------------------------------
        # Step 5 — Build retargeter
        # --------------------------------------------------------------
        unreal.log("\n[5/5] Creating IK Retargeter...")
        chain_names = [name for name, _, _ in MANNY_CHAINS]
        retargeter = create_retargeter(
            "RTG_Manny_To_Squad",
            manny_rig, squad_rig,
            chain_names, OUTPUT_PATH
        )

    if retargeter:
        unreal.log("\n" + "=" * 60)
        unreal.log("  Done!")
        unreal.log(f"  Assets saved to: {OUTPUT_PATH}")
        unreal.log("=" * 60)
        unreal.log("  Next steps:")
        unreal.log("  1. Open RTG_Manny_To_Squad")
        unreal.log("  2. Retarget Pose > Edit Retarget Pose on BOTH sides")
        unreal.log("     and match them to the same reference pose (T-pose)")
        unreal.log("  3. Check Chain Mapping panel for any gaps")
        unreal.log("  4. Asset Browser > Export Animations to batch retarget")
        unreal.log("=" * 60)
    else:
        unreal.log_error("Failed to create retargeter — see warnings above.")


main()
