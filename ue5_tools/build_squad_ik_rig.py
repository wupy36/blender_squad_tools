"""
build_squad_ik_rig.py
=====================
Auto-discovers every bone present in a skeleton and builds a complete IK Rig
asset with retarget chains derived from what actually exists.

Supports both skeleton types:
  • Squad (Bip01-based)  — detected when "Bip01" is present
  • UE5 Mannequin        — detected when "pelvis" is present

Set SKELETON_TYPE = "auto" to let the script decide, or force it to
"squad" or "manny" if auto-detection picks the wrong one.

Run from the UE5 Output Log:
    py "C:/path/to/build_squad_ik_rig.py"
or paste directly into the Python console.

DRY_RUN = True  →  shows discovered chains without writing any assets.
"""

import unreal

# =============================================================================
# CONFIGURATION
# =============================================================================

# Path to the skeleton you want to build an IK Rig for.
SKELETON_PATH = "/Game/Art/Soldier2/TEST_US_Soldier_Skeleton_V3"

# Output folder for the IK Rig asset.
OUTPUT_PATH   = "/Game/Art/Retargeting"

# Asset name that will be created (overwritten if it already exists).
# Leave as "" to auto-name: "IK_Squad_Soldier" or "IK_Manny_ForSquad".
IK_RIG_NAME   = ""

# "auto" | "squad" | "manny"
SKELETON_TYPE = "auto"

# Set True to preview discovered chains without writing any assets.
DRY_RUN       = False

# Print per-bone probe results (True = verbose, False = summary only).
VERBOSE_PROBE = True

# =============================================================================
# CANDIDATE BONE LISTS
# Every bone name that could appear in each skeleton type.
# The script probes each one; chains are built only from confirmed bones.
# =============================================================================

SQUAD_CANDIDATES = [
    # root
    "Root", "Bip01",
    # spine
    "Bip01_Spine", "Bip01_Spine1", "Bip01_Spine2", "Bip01_Spine3",
    # neck / head
    "Bip01_Neck", "Bip01_Neck1", "Bip01_Head",
    # left arm
    "Bip01_L_Clavicle", "Bip01_L_UpperArm", "Bip01_L_Forearm", "Bip01_L_Hand",
    # right arm
    "Bip01_R_Clavicle", "Bip01_R_UpperArm", "Bip01_R_Forearm", "Bip01_R_Hand",
    # left leg
    "Bip01_L_Thigh", "Bip01_L_Calf", "Bip01_L_Foot", "Bip01_L_Toe0",
    # right leg
    "Bip01_R_Thigh", "Bip01_R_Calf", "Bip01_R_Foot", "Bip01_R_Toe0",
    # left fingers  (0=thumb, 1=index, 2=middle, 3=ring, 4=pinky)
    "Bip01_L_Finger0",  "Bip01_L_Finger01",  "Bip01_L_Finger02",
    "Bip01_L_Finger1",  "Bip01_L_Finger11",  "Bip01_L_Finger12",
    "Bip01_L_Finger2",  "Bip01_L_Finger21",  "Bip01_L_Finger22",
    "Bip01_L_Finger3",  "Bip01_L_Finger31",  "Bip01_L_Finger32",
    "Bip01_L_Finger4",  "Bip01_L_Finger41",  "Bip01_L_Finger42",
    # right fingers
    "Bip01_R_Finger0",  "Bip01_R_Finger01",  "Bip01_R_Finger02",
    "Bip01_R_Finger1",  "Bip01_R_Finger11",  "Bip01_R_Finger12",
    "Bip01_R_Finger2",  "Bip01_R_Finger21",  "Bip01_R_Finger22",
    "Bip01_R_Finger3",  "Bip01_R_Finger31",  "Bip01_R_Finger32",
    "Bip01_R_Finger4",  "Bip01_R_Finger41",  "Bip01_R_Finger42",
    # IK / special
    "IK_Feet_Root", "IK_Left_Foot", "IK_Right_Foot",
    "Bip01_IK_L_Hand", "Bip01_IK_R_Hand",
    "Bip01_IK_Weapon", "Bip01_Weapon1", "Bip01_CameraBone",
]

MANNY_CANDIDATES = [
    # root
    "root", "pelvis",
    # spine  (UE5 Manny has up to spine_05; UE4 stops at spine_03)
    "spine_01", "spine_02", "spine_03", "spine_04", "spine_05",
    # neck / head
    "neck_01", "neck_02", "head",
    # left arm
    "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
    # right arm
    "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
    # left leg
    "thigh_l", "calf_l", "foot_l", "ball_l",
    # right leg
    "thigh_r", "calf_r", "foot_r", "ball_r",
    # left fingers
    "thumb_01_l",  "thumb_02_l",  "thumb_03_l",
    "index_01_l",  "index_02_l",  "index_03_l",
    "middle_01_l", "middle_02_l", "middle_03_l",
    "ring_01_l",   "ring_02_l",   "ring_03_l",
    "pinky_01_l",  "pinky_02_l",  "pinky_03_l",
    # right fingers
    "thumb_01_r",  "thumb_02_r",  "thumb_03_r",
    "index_01_r",  "index_02_r",  "index_03_r",
    "middle_01_r", "middle_02_r", "middle_03_r",
    "ring_01_r",   "ring_02_r",   "ring_03_r",
    "pinky_01_r",  "pinky_02_r",  "pinky_03_r",
    # IK / weapon / special
    "ik_foot_root", "ik_foot_l", "ik_foot_r",
    "ik_hand_gun", "ik_hand_root", "ik_hand_l", "ik_hand_r",
    "weapon_r",
]

# =============================================================================
# DEBUG LOGGING
# =============================================================================

_W = 64

def dbg_section(title):
    unreal.log("")
    unreal.log("=" * _W)
    unreal.log(f"  {title}")
    unreal.log("=" * _W)

def dbg(msg=""):      unreal.log(f"  {msg}")
def dbg_ok(msg):      unreal.log(f"  [ OK ]  {msg}")
def dbg_skip(msg):    unreal.log(f"  [SKIP]  {msg}")
def dbg_warn(msg):    unreal.log_warning(f"  [WARN]  {msg}")
def dbg_err(msg):     unreal.log_error(f"  [ERR ]  {msg}")

def dbg_probe(bone, found):
    if not VERBOSE_PROBE:
        return
    tag = "FOUND  " if found else "absent "
    unreal.log(f"  [BONE]  {tag}  {bone}")

# =============================================================================
# PHASE 1 — ASSET RESOLUTION
# =============================================================================

def resolve_skeleton():
    dbg_section("Phase 1 — Resolve Skeleton Asset")
    _types = (unreal.SkeletalMesh, unreal.Skeleton)

    if unreal.EditorAssetLibrary.does_asset_exist(SKELETON_PATH):
        asset = unreal.load_asset(SKELETON_PATH)
        if isinstance(asset, _types):
            dbg_ok(f"Loaded from config:\n          {SKELETON_PATH}")
            dbg(f"Type : {type(asset).__name__}")
            return asset
        dbg_warn(f"Config path is {type(asset).__name__}, not a skeleton.")
    else:
        dbg_warn(f"Config path not found:\n          {SKELETON_PATH}")

    dbg("Checking Content Browser selection...")
    candidates = [a for a in unreal.EditorUtilityLibrary.get_selected_assets()
                  if isinstance(a, _types)]

    if not candidates:
        dbg_err("No SkeletalMesh/Skeleton selected in the Content Browser.")
        unreal.EditorDialog.show_message(
            "Skeleton Not Found",
            f"Could not load a skeleton from:\n  {SKELETON_PATH}\n\n"
            "Nothing suitable is selected in the Content Browser either.\n\n"
            "Fix one of the following and re-run:\n"
            "  • Update SKELETON_PATH at the top of the script\n"
            "  • Select the skeleton in the Content Browser",
            unreal.AppMsgType.OK,
        )
        return None

    chosen      = candidates[0]
    chosen_path = chosen.get_path_name().split(".")[0]

    if len(candidates) > 1:
        names = "\n".join(f"  • {a.get_path_name().split('.')[0]}" for a in candidates)
        dbg_warn(f"Multiple skeletons selected — using the first.\nAll selected:\n{names}")

    answer = unreal.EditorDialog.show_message(
        "Use Selected Skeleton?",
        f"Config path was not found.\n\nFound selected in Content Browser:\n  {chosen_path}\n\n"
        "Use this skeleton?",
        unreal.AppMsgType.YES_NO,
    )
    if answer != unreal.AppReturnType.YES:
        dbg("User declined — aborting.")
        return None

    dbg_ok(f"Using Content Browser selection:\n          {chosen_path}")
    return chosen

# =============================================================================
# PHASE 2 — SKELETON TYPE DETECTION
# =============================================================================

def detect_type(skel_asset):
    """
    If SKELETON_TYPE == "auto", probe a small set of signature bones to decide
    Squad vs Manny.  Returns ("squad", root_bone) or ("manny", root_bone).
    """
    dbg_section("Phase 2 — Skeleton Type Detection")

    if SKELETON_TYPE in ("squad", "manny"):
        root = "Bip01" if SKELETON_TYPE == "squad" else "pelvis"
        dbg(f"Type forced by config: {SKELETON_TYPE.upper()}  (root={root})")
        return SKELETON_TYPE, root

    # Auto-detect: create a tiny probe rig
    probe_path = f"{OUTPUT_PATH}/_type_probe_TEMP"
    _delete_if_exists(probe_path)
    probe = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "_type_probe_TEMP", OUTPUT_PATH,
        unreal.IKRigDefinition, unreal.IKRigDefinitionFactory(),
    )
    ctrl = unreal.IKRigController.get_controller(probe)
    ctrl.set_skeleton(skel_asset)

    has_bip01  = ctrl.add_retarget_chain("_p_Bip01",  "Bip01",  "Bip01")
    has_pelvis = ctrl.add_retarget_chain("_p_pelvis", "pelvis", "pelvis")

    _delete_if_exists(probe_path)

    dbg(f"Probe result — Bip01 present: {has_bip01}   pelvis present: {has_pelvis}")

    if has_bip01 and not has_pelvis:
        dbg_ok("Detected: Squad (Bip01) skeleton")
        return "squad", "Bip01"
    if has_pelvis and not has_bip01:
        dbg_ok("Detected: UE5 Mannequin skeleton")
        return "manny", "pelvis"
    if has_bip01 and has_pelvis:
        dbg_warn("Both 'Bip01' and 'pelvis' found — defaulting to Squad. "
                 "Set SKELETON_TYPE='manny' to override.")
        return "squad", "Bip01"

    dbg_warn("Neither 'Bip01' nor 'pelvis' found — cannot auto-detect skeleton type.")
    unreal.EditorDialog.show_message(
        "Cannot Detect Skeleton Type",
        "Neither 'Bip01' nor 'pelvis' was found in the skeleton.\n\n"
        "Set SKELETON_TYPE = 'squad' or 'manny' at the top of the script\n"
        "and update the SKELETON_PATH to point to the correct asset.",
        unreal.AppMsgType.OK,
    )
    return None, None

# =============================================================================
# PHASE 3 — BONE DISCOVERY
# =============================================================================

_PROBE_PATH = f"{OUTPUT_PATH}/_bone_probe_TEMP"


def _delete_if_exists(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)


def discover_bones(skel_asset, candidates):
    dbg_section("Phase 3 — Bone Discovery")
    dbg(f"Probing {len(candidates)} candidate bones...")
    dbg()

    _delete_if_exists(_PROBE_PATH)
    probe = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "_bone_probe_TEMP", OUTPUT_PATH,
        unreal.IKRigDefinition, unreal.IKRigDefinitionFactory(),
    )
    if probe is None:
        dbg_err("Could not create probe IK Rig.")
        return set()

    ctrl  = unreal.IKRigController.get_controller(probe)
    ctrl.set_skeleton(skel_asset)

    found   = set()
    missing = []

    for bone in candidates:
        try:
            ok = ctrl.add_retarget_chain(f"_p_{bone}", bone, bone)
            if ok:
                found.add(bone)
                dbg_probe(bone, True)
            else:
                missing.append(bone)
                dbg_probe(bone, False)
        except Exception as exc:
            missing.append(bone)
            if VERBOSE_PROBE:
                unreal.log(f"  [BONE]  error    {bone}  ({exc})")

    _delete_if_exists(_PROBE_PATH)

    dbg()
    dbg(f"Found {len(found)} / {len(candidates)} probed — {len(missing)} absent")

    if missing and not VERBOSE_PROBE:
        dbg("Absent bones:")
        rows = [missing[i:i+3] for i in range(0, len(missing), 3)]
        for row in rows:
            dbg("  " + "   ".join(f"{b:<30}" for b in row))

    return found

# =============================================================================
# PHASE 4 — CHAIN BUILDING
# =============================================================================

def _longest(seq, existing):
    hit = [b for b in seq if b in existing]
    return (hit[0], hit[-1]) if hit else (None, None)


def build_squad_chains(existing):
    dbg_section("Phase 4 — Squad Chain Building")
    chains = []

    def add(name, start, end, note=""):
        chains.append((name, start, end))
        dbg_ok(f"{name:<22}  {start}  ->  {end}" + (f"  [{note}]" if note else ""))

    def skip(name, why):
        dbg_skip(f"{name:<22}  {why}")

    # Root
    if "Root" in existing:
        add("Root", "Root", "Root")
    else:
        skip("Root", "Root not found")

    # Spine
    s, e = _longest(["Bip01_Spine", "Bip01_Spine1", "Bip01_Spine2", "Bip01_Spine3"], existing)
    if s: add("Spine", s, e)
    else: skip("Spine", "no Bip01_Spine* bones")

    # Head
    necks    = [b for b in ["Bip01_Neck", "Bip01_Neck1"] if b in existing]
    has_head = "Bip01_Head" in existing
    if necks and has_head:
        add("Head", necks[0], "Bip01_Head")
    elif has_head:
        add("Head", "Bip01_Head", "Bip01_Head", "no neck bone")
    else:
        skip("Head", "no neck or head bone")

    # Arms
    for side, label in (("L", "Left"), ("R", "Right")):
        clav, upper = f"Bip01_{side}_Clavicle", f"Bip01_{side}_UpperArm"
        lower, hand = f"Bip01_{side}_Forearm",  f"Bip01_{side}_Hand"
        if clav  in existing: add(f"{label}Clavicle", clav, clav)
        else:                  skip(f"{label}Clavicle", f"{clav} not found")
        if upper not in existing:
            skip(f"{label}Arm", f"{upper} not found"); continue
        end = upper
        if lower in existing: end = lower
        if hand  in existing: end = hand
        add(f"{label}Arm", upper, end)

    # Legs
    for side, label in (("L", "Left"), ("R", "Right")):
        thigh = f"Bip01_{side}_Thigh"
        calf  = f"Bip01_{side}_Calf"
        foot  = f"Bip01_{side}_Foot"
        toe   = f"Bip01_{side}_Toe0"
        if thigh in existing:
            end = thigh
            if calf in existing: end = calf
            if foot in existing: end = foot
            add(f"{label}Leg", thigh, end)
        else:
            skip(f"{label}Leg", f"{thigh} not found")
        if toe in existing: add(f"{label}Toe", toe, toe)
        else:               skip(f"{label}Toe", f"{toe} not found")

    # Fingers
    finger_map = {0: "Thumb", 1: "Index", 2: "Middle", 3: "Ring", 4: "Pinky"}
    for side, label in (("L", "Left"), ("R", "Right")):
        for num, fname in finger_map.items():
            root = f"Bip01_{side}_Finger{num}"
            mid  = f"Bip01_{side}_Finger{num}1"
            tip  = f"Bip01_{side}_Finger{num}2"
            name = f"{label}{fname}"
            if root not in existing:
                skip(name, f"{root} not found"); continue
            end = root
            if mid in existing: end = mid
            if tip in existing: end = tip
            add(name, root, end)

    # Special
    for bone, chain_name in [
        ("Bip01_Weapon1",    "Weapon"),
        ("Bip01_CameraBone", "Camera"),
        ("IK_Feet_Root",     "IKFeetRoot"),
        ("IK_Left_Foot",     "IKLeftFoot"),
        ("IK_Right_Foot",    "IKRightFoot"),
    ]:
        if bone in existing: add(chain_name, bone, bone)

    dbg()
    dbg(f"Total chains built: {len(chains)}")
    return chains


def build_manny_chains(existing):
    dbg_section("Phase 4 — UE5 Mannequin Chain Building")
    chains = []

    def add(name, start, end, note=""):
        chains.append((name, start, end))
        dbg_ok(f"{name:<22}  {start}  ->  {end}" + (f"  [{note}]" if note else ""))

    def skip(name, why):
        dbg_skip(f"{name:<22}  {why}")

    # Root
    if "root" in existing:  add("Root", "root", "root")
    else:                   skip("Root", "'root' not found")

    # Spine — take the longest run from spine_01 upward
    s, e = _longest(["spine_01","spine_02","spine_03","spine_04","spine_05"], existing)
    if s: add("Spine", s, e)
    else: skip("Spine", "no spine_* bones found")

    # Head
    necks    = [b for b in ["neck_01", "neck_02"] if b in existing]
    has_head = "head" in existing
    if necks and has_head:
        add("Head", necks[0], "head")
    elif has_head:
        add("Head", "head", "head", "no neck bone")
    else:
        skip("Head", "no neck_01 or head bone")

    # Arms
    for side, label in (("l", "Left"), ("r", "Right")):
        clav  = f"clavicle_{side}"
        upper = f"upperarm_{side}"
        lower = f"lowerarm_{side}"
        hand  = f"hand_{side}"
        if clav  in existing: add(f"{label}Clavicle", clav, clav)
        else:                  skip(f"{label}Clavicle", f"{clav} not found")
        if upper not in existing:
            skip(f"{label}Arm", f"{upper} not found"); continue
        end = upper
        if lower in existing: end = lower
        if hand  in existing: end = hand
        add(f"{label}Arm", upper, end)

    # Legs
    for side, label in (("l", "Left"), ("r", "Right")):
        thigh = f"thigh_{side}"
        calf  = f"calf_{side}"
        foot  = f"foot_{side}"
        ball  = f"ball_{side}"
        if thigh in existing:
            end = thigh
            if calf in existing: end = calf
            if foot in existing: end = foot
            add(f"{label}Leg", thigh, end)
        else:
            skip(f"{label}Leg", f"{thigh} not found")
        if ball in existing: add(f"{label}Toe", ball, ball)
        else:                skip(f"{label}Toe", f"{ball} not found")

    # Fingers
    finger_map = [
        ("thumb",  "Thumb"),
        ("index",  "Index"),
        ("middle", "Middle"),
        ("ring",   "Ring"),
        ("pinky",  "Pinky"),
    ]
    for side, label in (("l", "Left"), ("r", "Right")):
        for prefix, fname in finger_map:
            b1 = f"{prefix}_01_{side}"
            b2 = f"{prefix}_02_{side}"
            b3 = f"{prefix}_03_{side}"
            name = f"{label}{fname}"
            if b1 not in existing:
                skip(name, f"{b1} not found"); continue
            end = b1
            if b2 in existing: end = b2
            if b3 in existing: end = b3
            add(name, b1, end)

    # IK / weapon
    for bone, chain_name in [
        ("weapon_r",    "Weapon"),
        ("ik_foot_root","IKFeetRoot"),
        ("ik_foot_l",   "IKLeftFoot"),
        ("ik_foot_r",   "IKRightFoot"),
        ("ik_hand_gun", "IKHandGun"),
        ("ik_hand_l",   "IKHandLeft"),
        ("ik_hand_r",   "IKHandRight"),
    ]:
        if bone in existing: add(chain_name, bone, bone)

    dbg()
    dbg(f"Total chains built: {len(chains)}")
    return chains

# =============================================================================
# PHASE 5 — IK RIG CREATION
# =============================================================================

def create_ik_rig(skel_asset, retarget_root, chains, asset_name):
    dbg_section("Phase 5 — IK Rig Asset Creation")

    full_path = f"{OUTPUT_PATH}/{asset_name}"

    if DRY_RUN:
        dbg(f"DRY RUN — would create : {full_path}")
        dbg(f"          retarget root : {retarget_root}")
        dbg(f"          chains        : {len(chains)}")
        return None

    _delete_if_exists(full_path)

    ik_rig = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, OUTPUT_PATH,
        unreal.IKRigDefinition, unreal.IKRigDefinitionFactory(),
    )
    if ik_rig is None:
        dbg_err(f"create_asset() returned None — check output path permissions: {full_path}")
        return None

    ctrl = unreal.IKRigController.get_controller(ik_rig)
    ctrl.set_skeleton(skel_asset)
    dbg_ok(f"Skeleton assigned : {skel_asset.get_path_name().split('.')[0]}")

    if ctrl.set_retarget_root(retarget_root):
        dbg_ok(f"Retarget root set : {retarget_root}")
    else:
        dbg_err(f"set_retarget_root('{retarget_root}') failed — bone not found.")

    dbg()
    dbg("Adding chains...")
    added, skipped = [], []

    for chain_name, start, end in chains:
        try:
            ok = ctrl.add_retarget_chain(chain_name, start, end)
            if ok:
                added.append(chain_name)
                dbg(f"  [+] {chain_name:<22}  {start}  ->  {end}")
            else:
                skipped.append((chain_name, start, end))
                dbg_warn(f"  [-] {chain_name:<22}  {start}  ->  {end}  (returned False)")
        except Exception as exc:
            skipped.append((chain_name, start, end))
            dbg_warn(f"  [!] {chain_name:<22}  exception: {exc}")

    dbg()
    dbg(f"Result: {len(added)} added  |  {len(skipped)} skipped")
    if skipped:
        dbg_warn("Skipped chains:")
        for n, s, e in skipped:
            dbg_warn(f"    {n}: {s} -> {e}")

    unreal.EditorAssetLibrary.save_asset(full_path)
    dbg_ok(f"Saved: {full_path}")
    return ik_rig

# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    unreal.log("")
    unreal.log("*" * _W)
    unreal.log("*  IK Rig Auto-Builder  (Squad + UE5 Manny)")
    unreal.log(f"*  DRY_RUN={DRY_RUN}  SKELETON_TYPE={SKELETON_TYPE!r}  VERBOSE_PROBE={VERBOSE_PROBE}")
    unreal.log("*" * _W)

    unreal.EditorAssetLibrary.make_directory(OUTPUT_PATH)

    # 1 — resolve asset
    skel_asset = resolve_skeleton()
    if skel_asset is None:
        return

    # 2 — detect type
    skel_type, retarget_root = detect_type(skel_asset)
    if skel_type is None:
        return

    # determine asset name
    if IK_RIG_NAME:
        asset_name = IK_RIG_NAME
    elif skel_type == "squad":
        asset_name = "IK_Squad_Soldier"
    else:
        asset_name = "IK_Manny_ForSquad"

    # 3 — discover bones
    candidates     = SQUAD_CANDIDATES if skel_type == "squad" else MANNY_CANDIDATES
    existing_bones = discover_bones(skel_asset, candidates)

    if not existing_bones:
        dbg_err("No bones found — cannot continue.")
        return

    if retarget_root not in existing_bones:
        unreal.EditorDialog.show_message(
            "Retarget Root Missing",
            f"The retarget root bone '{retarget_root}' was not found.\n\n"
            f"Bones discovered (first 20):\n"
            + "\n".join(f"  {b}" for b in sorted(existing_bones)[:20]),
            unreal.AppMsgType.OK,
        )
        return

    # 4 — build chains
    chains = (build_squad_chains if skel_type == "squad" else build_manny_chains)(existing_bones)
    if not chains:
        dbg_err("No chains built — review discovery output.")
        return

    # 5 — create IK Rig
    with unreal.ScopedEditorTransaction(f"Build {skel_type.upper()} IK Rig"):
        ik_rig = create_ik_rig(skel_asset, retarget_root, chains, asset_name)

    # final summary
    dbg_section("Done")
    dbg(f"Skeleton type  : {skel_type.upper()}")
    dbg(f"Retarget root  : {retarget_root}")
    dbg(f"Bones found    : {len(existing_bones)} / {len(candidates)} probed")
    dbg(f"Chains created : {len(chains)}")
    dbg(f"IK Rig asset   : {OUTPUT_PATH}/{asset_name}")
    if DRY_RUN:
        dbg()
        dbg("DRY RUN — no assets written. Set DRY_RUN = False and re-run.")
    elif ik_rig:
        dbg()
        dbg_ok("Complete. Run create_squad_retargeter.py next to build")
        dbg("         the paired Manny IK Rig and the IK Retargeter.")
    else:
        dbg_err("IK Rig was NOT created — see errors above.")
    unreal.log("")


main()
