bl_info = {
    "name": "Mixamo Bone Rename to OpenSim",
    "author": "Manni V3b",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "Object > Rename Bones",
    "description": "Renames Mixamo rig bone and vertex group names to OpenSim compatible names",
    "category": "Rigging",
}

import bpy
import re
import json
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import (StringProperty, 
                      BoolProperty, 
                      EnumProperty,
                      PointerProperty)
from bpy_extras.io_utils import ImportHelper, ExportHelper

# Default mapping presets
PRESETS = {
    'BENTO_FULL': {
        # Core skeleton
        "Hips": "mPelvis",
        "Spine": "mSpine1",
        "Spine1": "mSpine2",
        "Spine2": "mTorso",
        "Neck": "mNeck",
        "Head": "mHead",
        "HeadTop_End": "mHeadTop_End",
        
        # Arms
        "LeftShoulder": "mCollarLeft",
        "LeftArm": "mShoulderLeft",
        "LeftForeArm": "mElbowLeft",
        "LeftHand": "mWristLeft",
        
        "RightShoulder": "mCollarRight",
        "RightArm": "mShoulderRight",
        "RightForeArm": "mElbowRight",
        "RightHand": "mWristRight",
        
        # Legs
        "LeftUpLeg": "mHipLeft",
        "LeftLeg": "mKneeLeft",
        "LeftFoot": "mAnkleLeft",
        "LeftToeBase": "mToeLeft",
        "LeftToe_End": "mToeLeftEnd",
        
        "RightUpLeg": "mHipRight",
        "RightLeg": "mKneeRight",
        "RightFoot": "mAnkleRight",
        "RightToeBase": "mToeRight",
        "RightToe_End": "mToeRightEnd",
        
        # Hands (Bento)
        "LeftHandThumb1": "mHandThumb1Left",
        "LeftHandThumb2": "mHandThumb2Left",
        "LeftHandThumb3": "mHandThumb3Left",
        "LeftHandIndex1": "mHandIndex1Left",
        "LeftHandIndex2": "mHandIndex2Left",
        "LeftHandIndex3": "mHandIndex3Left",
        "LeftHandMiddle1": "mHandMiddle1Left",
        "LeftHandMiddle2": "mHandMiddle2Left",
        "LeftHandMiddle3": "mHandMiddle3Left",
        "LeftHandRing1": "mHandRing1Left",
        "LeftHandRing2": "mHandRing2Left",
        "LeftHandRing3": "mHandRing3Left",
        "LeftHandPinky1": "mHandPinky1Left",
        "LeftHandPinky2": "mHandPinky2Left",
        "LeftHandPinky3": "mHandPinky3Left",
        
        "RightHandThumb1": "mHandThumb1Right",
        "RightHandThumb2": "mHandThumb2Right",
        "RightHandThumb3": "mHandThumb3Right",
        "RightHandIndex1": "mHandIndex1Right",
        "RightHandIndex2": "mHandIndex2Right",
        "RightHandIndex3": "mHandIndex3Right",
        "RightHandMiddle1": "mHandMiddle1Right",
        "RightHandMiddle2": "mHandMiddle2Right",
        "RightHandMiddle3": "mHandMiddle3Right",
        "RightHandRing1": "mHandRing1Right",
        "RightHandRing2": "mHandRing2Right",
        "RightHandRing3": "mHandRing3Right",
        "RightHandPinky1": "mHandPinky1Right",
        "RightHandPinky2": "mHandPinky2Right",
        "RightHandPinky3": "mHandPinky3Right",
    },
    'BASIC': {
        # Core skeleton
        "Hips": "mPelvis",
        "Spine": "mSpine1",
        "Spine1": "mSpine2",
        "Spine2": "mTorso",
        "Neck": "mNeck",
        "Head": "mHead",
        "HeadTop_End": "mHeadTop_End",
    },
    'HANDS_ONLY': {
        # Hand bones only
        "LeftHandThumb1": "mHandThumb1Left",
        "LeftHandThumb2": "mHandThumb2Left",
        "LeftHandThumb3": "mHandThumb3Left",
        "LeftHandIndex1": "mHandIndex1Left",
        "LeftHandIndex2": "mHandIndex2Left",
        "LeftHandIndex3": "mHandIndex3Left",
        "LeftHandMiddle1": "mHandMiddle1Left",
        "LeftHandMiddle2": "mHandMiddle2Left",
        "LeftHandMiddle3": "mHandMiddle3Left",
        "LeftHandRing1": "mHandRing1Left",
        "LeftHandRing2": "mHandRing2Left",
        "LeftHandRing3": "mHandRing3Left",
        "LeftHandPinky1": "mHandPinky1Left",
        "LeftHandPinky2": "mHandPinky2Left",
        "LeftHandPinky3": "mHandPinky3Left",
        
        "RightHandThumb1": "mHandThumb1Right",
        "RightHandThumb2": "mHandThumb2Right",
        "RightHandThumb3": "mHandThumb3Right",
        "RightHandIndex1": "mHandIndex1Right",
        "RightHandIndex2": "mHandIndex2Right",
        "RightHandIndex3": "mHandIndex3Right",
        "RightHandMiddle1": "mHandMiddle1Right",
        "RightHandMiddle2": "mHandMiddle2Right",
        "RightHandMiddle3": "mHandMiddle3Right",
        "RightHandRing1": "mHandRing1Right",
        "RightHandRing2": "mHandRing2Right",
        "RightHandRing3": "mHandRing3Right",
        "RightHandPinky1": "mHandPinky1Right",
        "RightHandPinky2": "mHandPinky2Right",
        "RightHandPinky3": "mHandPinky3Right",
    }
}

class BoneMappingProperties(PropertyGroup):
    import_file: StringProperty(
        name="Import File",
        description="JSON file with bone mappings",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    export_file: StringProperty(
        name="Export File",
        description="JSON file to save bone mappings",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    preset: EnumProperty(
        name="Preset",
        items=[
            ('BENTO_FULL', "Bento Full", "Complete Bento skeleton"),
            ('BASIC', "Basic", "Basic OpenSim skeleton"),
            ('HANDS_ONLY', "Hands Only", "Only hand bones"),
            ('CUSTOM', "Custom", "Custom mapping")
        ],
        default='BENTO_FULL'
    )
    
    prefix_mode: EnumProperty(
        name="Prefix Mode",
        description="How to handle Mixamo bone prefixes",
        items=[
            ('AUTO', "Auto-Detect", "Automatically find the correct prefix"),
            ('MANUAL', "Manual Select", "Choose from common prefixes"),
            ('CUSTOM', "Custom", "Enter a custom prefix pattern")
        ],
        default='AUTO'
    )
    
    manual_prefix: EnumProperty(
        name="Manual Prefix",
        description="Select a predefined Mixamo prefix",
        items=[
            ('mixamorig:', "mixamorig:", "Standard prefix (most common)"),
            ('mixamorig1:', "mixamorig1:", "First numbered variant"),
            ('mixamorig2:', "mixamorig2:", "Second numbered variant")
        ],
        default='mixamorig:'
    )
    
    custom_prefix: StringProperty(
        name="Custom Prefix",
        description="Enter your custom Mixamo prefix (e.g. 'myPrefix_:')",
        default="mixamorig:",
        maxlen=32
    )

class OBJECT_OT_import_mapping(Operator, ImportHelper):
    """Import bone mapping from JSON file"""
    bl_idname = "object.import_mapping"
    bl_label = "Import Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        scene = context.scene
        props = scene.bone_mapping_props
        
        try:
            with open(self.filepath, 'r') as f:
                mappings = json.load(f)
                scene['custom_bone_map'] = mappings
                props.preset = 'CUSTOM'
                self.report({'INFO'}, f"Mapping imported: {len(mappings)} bones")
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
        
        return {'FINISHED'}

class OBJECT_OT_export_mapping(Operator, ExportHelper):
    """Export current bone mapping to JSON file"""
    bl_idname = "object.export_mapping"
    bl_label = "Export Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".json"
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        scene = context.scene
        props = scene.bone_mapping_props
        
        current_map = self.get_current_mapping(context)
        
        try:
            with open(self.filepath, 'w') as f:
                json.dump(current_map, f, indent=2)
            self.report({'INFO'}, f"Mapping exported: {len(current_map)} bones")
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
        
        return {'FINISHED'}
    
    def get_current_mapping(self, context):
        if context.scene.bone_mapping_props.preset == 'CUSTOM':
            return context.scene.get('custom_bone_map', {})
        return PRESETS[context.scene.bone_mapping_props.preset]

class OBJECT_OT_rename_mixamo_bones(Operator):
    """Apply current bone mapping to selected armatures"""
    bl_idname = "object.rename_mixamo_bones"
    bl_label = "Rename Mixamo Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def detect_prefix(self, armature):
        """Automatic prefix detection"""
        prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
        for bone in armature.data.bones:
            for prefix in prefixes:
                if bone.name.startswith(prefix):
                    return prefix
        return None

    def get_prefix(self, context, armature):
        props = context.scene.bone_mapping_props
        if props.prefix_mode == 'AUTO':
            return self.detect_prefix(armature)
        elif props.prefix_mode == 'MANUAL':
            return props.manual_prefix
        return props.custom_prefix

    def execute(self, context):
        props = context.scene.bone_mapping_props
        
        # Get current mapping
        if props.preset == 'CUSTOM':
            bone_map = context.scene.get('custom_bone_map', {})
        else:
            bone_map = PRESETS[props.preset]

        processed = 0
        skipped = 0
        armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        for armature in armatures:
            prefix = self.get_prefix(context, armature)
            if not prefix:
                self.report({'WARNING'}, f"No Mixamo prefix found in {armature.name}")
                continue

            pattern = re.compile(f"^{re.escape(prefix)}")

            # Bone renaming
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            
            for bone in armature.data.edit_bones:
                if not pattern.match(bone.name):
                    skipped += 1
                    continue
                    
                base_name = pattern.sub("", bone.name)
                
                if base_name in bone_map:
                    new_name = bone_map[base_name]
                    
                    if new_name in armature.data.edit_bones:
                        if armature.data.edit_bones[new_name] != bone:
                            self.report({'WARNING'}, f"Skipped: {new_name} already exists")
                            skipped += 1
                            continue
                            
                    bone.name = new_name
                    processed += 1
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Vertex groups
            for mesh in meshes:
                if mesh.parent == armature:
                    for vg in mesh.vertex_groups:
                        if pattern.match(vg.name):
                            base_name = pattern.sub("", vg.name)
                            if base_name in bone_map:
                                vg.name = bone_map[base_name]

        self.report({'INFO'}, f"Renamed {processed} bones, skipped {skipped}")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.bone_mapping_props
        layout = self.layout
        
        layout.prop(props, "preset")
        
        layout.separator()
        layout.label(text="Prefix Options:")
        layout.prop(props, "prefix_mode", expand=True)
        
        if props.prefix_mode == 'MANUAL':
            layout.prop(props, "manual_prefix")
        elif props.prefix_mode == 'CUSTOM':
            layout.prop(props, "custom_prefix")

class OBJECT_PT_mixamo_bone_panel(Panel):
    bl_label = "Mixamo to OpenSim Tools"
    bl_idname = "OBJECT_PT_mixamo_bone_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mixamo'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.bone_mapping_props
        
        # Preset selection
        layout.prop(props, "preset", text="Preset")
        
        # Mapping operations
        row = layout.row()
        row.operator("object.import_mapping", text="Import")
        row.operator("object.export_mapping", text="Export")
        
        # Rename button
        layout.operator("object.rename_mixamo_bones", text="Rename Bones")

def register():
    bpy.utils.register_class(BoneMappingProperties)
    bpy.utils.register_class(OBJECT_OT_import_mapping)
    bpy.utils.register_class(OBJECT_OT_export_mapping)
    bpy.utils.register_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.register_class(OBJECT_PT_mixamo_bone_panel)
    
    bpy.types.Scene.bone_mapping_props = PointerProperty(
        type=BoneMappingProperties)

def unregister():
    bpy.utils.unregister_class(BoneMappingProperties)
    bpy.utils.unregister_class(OBJECT_OT_import_mapping)
    bpy.utils.unregister_class(OBJECT_OT_export_mapping)
    bpy.utils.unregister_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.unregister_class(OBJECT_PT_mixamo_bone_panel)
    
    del bpy.types.Scene.bone_mapping_props

if __name__ == "__main__":
    register()