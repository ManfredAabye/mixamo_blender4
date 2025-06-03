bl_info = {
    "name": "Mixamo Bone Rename to OpenSim",
    "author": "Manni",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "Object > Rename Bones",
    "description": "Renames Mixamo rig bone and vertex group names to OpenSim compatible names",
    "category": "Rigging",
}

import bpy
from bpy.types import Operator, Panel

# === Bone-Mapping ===
bone_map = {
    "Hips": "mPelvis",
    "Spine": "mSpine1",
    "Spine1": "mSpine2",
    "Spine2": "mSpine3",
    "Neck": "mNeck",
    "Head": "mHead",
    "HeadTop_End": "mHeadTop_End",
    "LeftShoulder": "mCollar",
    "LeftArm": "mShoulder",
    "LeftForeArm": "mElbow",
    "LeftHand": "mWrist",
    "LeftUpLeg": "mHip",
    "LeftLeg": "mKnee",
    "LeftFoot": "mAnkle",
    "LeftToeBase": "mToe",
    "LeftToe_End": "mToe_End",
    "RightShoulder": "mCollar",
    "RightArm": "mShoulder",
    "RightForeArm": "mElbow",
    "RightHand": "mWrist",
    "RightUpLeg": "mHip",
    "RightLeg": "mKnee",
    "RightFoot": "mAnkle",
    "RightToeBase": "mToe",
    "RightToe_End": "mToe_End",
}

class OBJECT_OT_rename_mixamo_bones(Operator):
    """Renames bones and vertex groups from Mixamo to OpenSim naming"""
    bl_idname = "object.rename_mixamo_bones"
    bl_label = "Rename Mixamo Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

        for armature in armatures:
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in armature.data.edit_bones:
                clean = bone.name.replace("mixamorig:", "")
                if clean in bone_map:
                    new_name = bone_map[clean]
                    self.report({'INFO'}, f"Bone: {bone.name} → {new_name}")
                    bone.name = new_name
            bpy.ops.object.mode_set(mode='OBJECT')

        for mesh in meshes:
            for vg in mesh.vertex_groups:
                clean = vg.name.replace("mixamorig:", "")
                if clean in bone_map:
                    new_name = bone_map[clean]
                    self.report({'INFO'}, f"Vertex Group: {vg.name} → {new_name}")
                    vg.name = new_name

        return {'FINISHED'}

class OBJECT_PT_mixamo_bone_panel(Panel):
    bl_label = "Mixamo to OpenSim Tools"
    bl_idname = "OBJECT_PT_mixamo_bone_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mixamo'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.rename_mixamo_bones")

def register():
    bpy.utils.register_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.register_class(OBJECT_PT_mixamo_bone_panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.unregister_class(OBJECT_PT_mixamo_bone_panel)

if __name__ == "__main__":
    register()
