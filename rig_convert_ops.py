import bpy

# ---------------------------------------------------------------------------
# Squad Bip01 → UE4 Mannequin
# ---------------------------------------------------------------------------
SQUAD_TO_UE4_BONE_MAP = {
    'Root':             'root',
    'Bip01':            'pelvis',
    # Spine
    'Bip01_Spine':      'spine_01',
    'Bip01_Spine1':     'spine_02',
    'Bip01_Spine2':     'spine_03',
    # Head / neck
    'Bip01_Neck':       'neck_01',
    'Bip01_Head':       'head',
    # Left arm
    'Bip01_L_Clavicle': 'clavicle_l',
    'Bip01_L_UpperArm': 'upperarm_l',
    'Bip01_L_Forearm':  'lowerarm_l',
    'Bip01_L_Hand':     'hand_l',
    # Right arm
    'Bip01_R_Clavicle': 'clavicle_r',
    'Bip01_R_UpperArm': 'upperarm_r',
    'Bip01_R_Forearm':  'lowerarm_r',
    'Bip01_R_Hand':     'hand_r',
    # Left leg
    'Bip01_L_Thigh':    'thigh_l',
    'Bip01_L_Calf':     'calf_l',
    'Bip01_L_Foot':     'foot_l',
    'Bip01_L_Toe0':     'ball_l',
    # Right leg
    'Bip01_R_Thigh':    'thigh_r',
    'Bip01_R_Calf':     'calf_r',
    'Bip01_R_Foot':     'foot_r',
    'Bip01_R_Toe0':     'ball_r',
    # Left thumb
    'Bip01_L_Finger0':  'thumb_01_l',
    'Bip01_L_Finger01': 'thumb_02_l',
    'Bip01_L_Finger02': 'thumb_03_l',
    # Left index
    'Bip01_L_Finger1':  'index_01_l',
    'Bip01_L_Finger11': 'index_02_l',
    'Bip01_L_Finger12': 'index_03_l',
    # Left middle
    'Bip01_L_Finger2':  'middle_01_l',
    'Bip01_L_Finger21': 'middle_02_l',
    'Bip01_L_Finger22': 'middle_03_l',
    # Left ring
    'Bip01_L_Finger3':  'ring_01_l',
    'Bip01_L_Finger31': 'ring_02_l',
    'Bip01_L_Finger32': 'ring_03_l',
    # Left pinky
    'Bip01_L_Finger4':  'pinky_01_l',
    'Bip01_L_Finger41': 'pinky_02_l',
    'Bip01_L_Finger42': 'pinky_03_l',
    # Right thumb
    'Bip01_R_Finger0':  'thumb_01_r',
    'Bip01_R_Finger01': 'thumb_02_r',
    'Bip01_R_Finger02': 'thumb_03_r',
    # Right index
    'Bip01_R_Finger1':  'index_01_r',
    'Bip01_R_Finger11': 'index_02_r',
    'Bip01_R_Finger12': 'index_03_r',
    # Right middle
    'Bip01_R_Finger2':  'middle_01_r',
    'Bip01_R_Finger21': 'middle_02_r',
    'Bip01_R_Finger22': 'middle_03_r',
    # Right ring
    'Bip01_R_Finger3':  'ring_01_r',
    'Bip01_R_Finger31': 'ring_02_r',
    'Bip01_R_Finger32': 'ring_03_r',
    # Right pinky
    'Bip01_R_Finger4':  'pinky_01_r',
    'Bip01_R_Finger41': 'pinky_02_r',
    'Bip01_R_Finger42': 'pinky_03_r',
    # IK / special
    'IK_Feet_Root':      'ik_foot_root',
    'IK_Left_Foot':      'ik_foot_l',
    'IK_Right_Foot':     'ik_foot_r',
    'Bip01_IK_Weapon':   'ik_hand_gun',
    'Bip01_IK_L_Hand':   'ik_hand_l',
    'Bip01_IK_R_Hand':   'ik_hand_r',
    'Bip01_Weapon1':     'weapon_r',
    'Bip01_CameraBone':  'camera',
}

# ---------------------------------------------------------------------------
# UE4 Mannequin → Squad Bip01
# ---------------------------------------------------------------------------
UE4_TO_SQUAD_BONE_MAP = {
    'root':         'Root',
    'pelvis':       'Bip01',
    # Spine
    'spine_01':     'Bip01_Spine',
    'spine_02':     'Bip01_Spine1',
    'spine_03':     'Bip01_Spine2',
    # Head / neck
    'neck_01':      'Bip01_Neck',
    'head':         'Bip01_Head',
    # Left arm
    'clavicle_l':   'Bip01_L_Clavicle',
    'upperarm_l':   'Bip01_L_UpperArm',
    'lowerarm_l':   'Bip01_L_Forearm',
    'hand_l':       'Bip01_L_Hand',
    # Right arm
    'clavicle_r':   'Bip01_R_Clavicle',
    'upperarm_r':   'Bip01_R_UpperArm',
    'lowerarm_r':   'Bip01_R_Forearm',
    'hand_r':       'Bip01_R_Hand',
    # Left leg
    'thigh_l':      'Bip01_L_Thigh',
    'calf_l':       'Bip01_L_Calf',
    'foot_l':       'Bip01_L_Foot',
    'ball_l':       'Bip01_L_Toe0',
    # Right leg
    'thigh_r':      'Bip01_R_Thigh',
    'calf_r':       'Bip01_R_Calf',
    'foot_r':       'Bip01_R_Foot',
    'ball_r':       'Bip01_R_Toe0',
    # Left thumb
    'thumb_01_l':   'Bip01_L_Finger0',
    'thumb_02_l':   'Bip01_L_Finger01',
    'thumb_03_l':   'Bip01_L_Finger02',
    # Left index
    'index_01_l':   'Bip01_L_Finger1',
    'index_02_l':   'Bip01_L_Finger11',
    'index_03_l':   'Bip01_L_Finger12',
    # Left middle
    'middle_01_l':  'Bip01_L_Finger2',
    'middle_02_l':  'Bip01_L_Finger21',
    'middle_03_l':  'Bip01_L_Finger22',
    # Left ring
    'ring_01_l':    'Bip01_L_Finger3',
    'ring_02_l':    'Bip01_L_Finger31',
    'ring_03_l':    'Bip01_L_Finger32',
    # Left pinky
    'pinky_01_l':   'Bip01_L_Finger4',
    'pinky_02_l':   'Bip01_L_Finger41',
    'pinky_03_l':   'Bip01_L_Finger42',
    # Right thumb
    'thumb_01_r':   'Bip01_R_Finger0',
    'thumb_02_r':   'Bip01_R_Finger01',
    'thumb_03_r':   'Bip01_R_Finger02',
    # Right index
    'index_01_r':   'Bip01_R_Finger1',
    'index_02_r':   'Bip01_R_Finger11',
    'index_03_r':   'Bip01_R_Finger12',
    # Right middle
    'middle_01_r':  'Bip01_R_Finger2',
    'middle_02_r':  'Bip01_R_Finger21',
    'middle_03_r':  'Bip01_R_Finger22',
    # Right ring
    'ring_01_r':    'Bip01_R_Finger3',
    'ring_02_r':    'Bip01_R_Finger31',
    'ring_03_r':    'Bip01_R_Finger32',
    # Right pinky
    'pinky_01_r':   'Bip01_R_Finger4',
    'pinky_02_r':   'Bip01_R_Finger41',
    'pinky_03_r':   'Bip01_R_Finger42',
    # IK / special
    'ik_foot_root': 'IK_Feet_Root',
    'ik_foot_l':    'IK_Left_Foot',
    'ik_foot_r':    'IK_Right_Foot',
    'ik_hand_gun':  'Bip01_IK_Weapon',
    'ik_hand_l':    'Bip01_IK_L_Hand',
    'ik_hand_r':    'Bip01_IK_R_Hand',
    'weapon_r':     'Bip01_Weapon1',
    'camera':       'Bip01_CameraBone',
}

# ---------------------------------------------------------------------------
# Squad Bip01 → UE5 Mannequin (Manny / Quinn)
#
# UE5 uses the same bone names as UE4 for every bone Squad has an equivalent
# for.  UE5 adds spine_04, spine_05, neck_02, ik_hand_root, and a set of
# twist/correction bones — none of those have Squad counterparts, so they are
# not present here and will be left unrenamed during a UE5→Squad conversion.
# ---------------------------------------------------------------------------
SQUAD_TO_UE5_BONE_MAP = {
    **SQUAD_TO_UE4_BONE_MAP,
    # UE5 adds ik_hand_root as a parent of the hand IK chain; Squad has no
    # equivalent so this entry only applies when an explicit root bone exists.
    # (No Squad source bone maps here — the key column must be Squad names.)
}

# ---------------------------------------------------------------------------
# UE5 Mannequin → Squad Bip01
#
# Same as UE4→Squad for all shared bones.  UE5-exclusive bones (spine_04,
# spine_05, neck_02, ik_hand_root, twist bones) have no Squad counterpart and
# will remain unchanged after the conversion — delete or repurpose them
# manually if needed.
# ---------------------------------------------------------------------------
UE5_TO_SQUAD_BONE_MAP = {
    **UE4_TO_SQUAD_BONE_MAP,
    # UE5 adds a second neck bone; Squad has only one neck bone so neck_02
    # is intentionally absent — it will be left unrenamed.
    # spine_04 / spine_05 are likewise absent for the same reason.
}


# ---------------------------------------------------------------------------
# Core rename helper
# ---------------------------------------------------------------------------

def apply_bone_rename(armature_obj, bone_map):
    """Rename bones in armature, then update vertex groups and fcurves in all actions."""
    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature_obj.data.edit_bones

    renamed = {}
    for old_name, new_name in bone_map.items():
        if old_name in edit_bones and new_name not in edit_bones:
            edit_bones[old_name].name = new_name
            renamed[old_name] = new_name

    bpy.ops.object.mode_set(mode='OBJECT')

    # Update vertex groups on all meshes deformed by this armature.
    # Blender propagates renames to the currently-assigned action automatically,
    # but not to every action in the file, so we handle both here.
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object == armature_obj:
                for old_name, new_name in renamed.items():
                    if old_name in obj.vertex_groups:
                        obj.vertex_groups[old_name].name = new_name

    # Update fcurve data paths and action groups in every action.
    for action in bpy.data.actions:
        for fcurve in action.fcurves:
            for old_name, new_name in renamed.items():
                old_path = f'pose.bones["{old_name}"]'
                new_path = f'pose.bones["{new_name}"]'
                if old_path in fcurve.data_path:
                    fcurve.data_path = fcurve.data_path.replace(old_path, new_path)
        for group in action.groups:
            if group.name in renamed:
                group.name = renamed[group.name]

    bpy.context.view_layer.objects.active = prev_active
    return len(renamed)


# ---------------------------------------------------------------------------
# Operators — UE4
# ---------------------------------------------------------------------------

class SquadRig_OT_ConvertSquadToUE4(bpy.types.Operator):
    """Rename bones on the active armature from Squad (Bip01) naming to UE4 Mannequin naming.\nAlso updates vertex groups and animation fcurves."""
    bl_idname = "squadrig.convert_squad_to_ue4"
    bl_label = "Squad Rig → UE4 Mannequin"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        count = apply_bone_rename(context.active_object, SQUAD_TO_UE4_BONE_MAP)
        self.report({'INFO'}, f"Renamed {count} bones to UE4 Mannequin naming.")
        return {'FINISHED'}


class SquadRig_OT_ConvertUE4ToSquad(bpy.types.Operator):
    """Rename bones on the active armature from UE4 Mannequin naming to Squad (Bip01) naming.\nAlso updates vertex groups and animation fcurves."""
    bl_idname = "squadrig.convert_ue4_to_squad"
    bl_label = "UE4 Mannequin → Squad Rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        count = apply_bone_rename(context.active_object, UE4_TO_SQUAD_BONE_MAP)
        self.report({'INFO'}, f"Renamed {count} bones to Squad rig naming.")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operators — UE5
# ---------------------------------------------------------------------------

class SquadRig_OT_ConvertSquadToUE5(bpy.types.Operator):
    """Rename bones on the active armature from Squad (Bip01) naming to UE5 Mannequin naming.\nAlso updates vertex groups and animation fcurves.\nNote: UE5-exclusive bones (spine_04/05, neck_02) have no Squad equivalent and will not be created."""
    bl_idname = "squadrig.convert_squad_to_ue5"
    bl_label = "Squad Rig → UE5 Mannequin"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        count = apply_bone_rename(context.active_object, SQUAD_TO_UE5_BONE_MAP)
        self.report({'INFO'}, f"Renamed {count} bones to UE5 Mannequin naming.")
        return {'FINISHED'}


class SquadRig_OT_ConvertUE5ToSquad(bpy.types.Operator):
    """Rename bones on the active armature from UE5 Mannequin naming to Squad (Bip01) naming.\nAlso updates vertex groups and animation fcurves.\nNote: UE5-exclusive bones (spine_04/05, neck_02, twist bones) have no Squad equivalent and will be left unrenamed."""
    bl_idname = "squadrig.convert_ue5_to_squad"
    bl_label = "UE5 Mannequin → Squad Rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        count = apply_bone_rename(context.active_object, UE5_TO_SQUAD_BONE_MAP)
        self.report({'INFO'}, f"Renamed {count} bones to Squad rig naming.")
        return {'FINISHED'}
