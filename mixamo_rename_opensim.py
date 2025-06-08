"""
MIXAMO TO OPENSIM/SECOND LIFE RIG CONVERTER
- Renames bones from Mixamo to OpenSim standard
- Optimizes vertex weights for SL compatibility
- Preserves all original functionality
"""

bl_info = {
    "name": "Mixamo to OpenSim Rig Converter",
    "author": "Manni V7",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "3D View > Sidebar > Mixamo Tools",
    "description": "Converts Mixamo rigs to OpenSim/Second Life compatible format",
    "category": "Rigging",
}

import bpy
import re
import json
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import (StringProperty, 
                      BoolProperty, 
                      FloatProperty,
                      EnumProperty,
                      PointerProperty)
from bpy_extras.io_utils import ImportHelper, ExportHelper

# ------------------------------------------------------------------------
# PRESET MAPPINGS
# ------------------------------------------------------------------------
PRESETS = {
    'BENTO_FULL': {
        # Core bones (required for basic functionality)
        "Hips": "mPelvis",               # Root bone for SL avatars
        "Spine": "mSpine1",               # Lower spine
        "Spine1": "mSpine2",              # Middle spine
        "Spine2": "mTorso",               # Upper chest
        "Neck": "mNeck",                  # Neck base
        "Head": "mHead",                  # Head bone
        "HeadTop_End": "mHeadTop_End",    # Head endpoint
        
        # Left arm bones
        "LeftShoulder": "mCollarLeft",    # Shoulder/collar area
        "LeftArm": "mShoulderLeft",       # Upper arm
        "LeftForeArm": "mElbowLeft",      # Elbow area
        "LeftHand": "mWristLeft",         # Wrist area
        
        # Right arm bones (mirror of left)
        "RightShoulder": "mCollarRight",
        "RightArm": "mShoulderRight",
        "RightForeArm": "mElbowRight",
        "RightHand": "mWristRight",
        
        # Left leg bones
        "LeftUpLeg": "mHipLeft",          # Hip/upper leg
        "LeftLeg": "mKneeLeft",           # Knee area
        "LeftFoot": "mAnkleLeft",         # Ankle area
        "LeftToeBase": "mToeLeft",        # Toe base
        "LeftToe_End": "mToeLeftEnd",     # Toe tip
        
        # Right leg bones (mirror of left)
        "RightUpLeg": "mHipRight",
        "RightLeg": "mKneeRight",
        "RightFoot": "mAnkleRight",
        "RightToeBase": "mToeRight",
        "RightToe_End": "mToeRightEnd",
        
        # Left hand bones (Bento)
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
        
        # Right hand bones (Bento, mirror of left)
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

        # Face Bones (complete set)
        "FaceForeheadLeft": "mFaceForeheadLeft",
        "FaceForeheadCenter": "mFaceForeheadCenter",
        "FaceForeheadRight": "mFaceForeheadRight",
        "FaceEyebrowOuterLeft": "mFaceEyebrowOuterLeft",
        "FaceEyebrowCenterLeft": "mFaceEyebrowCenterLeft",
        "FaceEyebrowInnerLeft": "mFaceEyebrowInnerLeft",
        "FaceEyebrowOuterRight": "mFaceEyebrowOuterRight",
        "FaceEyebrowCenterRight": "mFaceEyebrowCenterRight",
        "FaceEyebrowInnerRight": "mFaceEyebrowInnerRight",
        "FaceEyeLidUpperLeft": "mFaceEyeLidUpperLeft",
        "FaceEyeLidLowerLeft": "mFaceEyeLidLowerLeft",
        "FaceEyeLidUpperRight": "mFaceEyeLidUpperRight",
        "FaceEyeLidLowerRight": "mFaceEyeLidLowerRight",
        "FaceEyeAltLeft": "mFaceEyeAltLeft",
        "FaceEyeAltRight": "mFaceEyeAltRight",
        "FaceEyecornerInnerLeft": "mFaceEyecornerInnerLeft",
        "FaceEyecornerInnerRight": "mFaceEyecornerInnerRight",
        "FaceEar1Left": "mFaceEar1Left",
        "FaceEar2Left": "mFaceEar2Left",
        "FaceEar1Right": "mFaceEar1Right",
        "FaceEar2Right": "mFaceEar2Right",
        "FaceNoseLeft": "mFaceNoseLeft",
        "FaceNoseCenter": "mFaceNoseCenter",
        "FaceNoseRight": "mFaceNoseRight",
        "FaceNoseBase": "mFaceNoseBase",
        "FaceNoseBridge": "mFaceNoseBridge",
        "FaceCheekUpperLeft": "mFaceCheekUpperLeft",
        "FaceCheekLowerLeft": "mFaceCheekLowerLeft",
        "FaceCheekUpperRight": "mFaceCheekUpperRight",
        "FaceCheekLowerRight": "mFaceCheekLowerRight",
        "FaceJaw": "mFaceJaw",
        "FaceLipUpperLeft": "mFaceLipUpperLeft",
        "FaceLipUpperCenter": "mFaceLipUpperCenter",
        "FaceLipUpperRight": "mFaceLipUpperRight",
        "FaceLipCornerLeft": "mFaceLipCornerLeft",
        "FaceLipCornerRight": "mFaceLipCornerRight",
        "FaceTongueBase": "mFaceTongueBase",
        "FaceTongueTip": "mFaceTongueTip",
        "FaceLipLowerLeft": "mFaceLipLowerLeft",
        "FaceLipLowerCenter": "mFaceLipLowerCenter",
        "FaceLipLowerRight": "mFaceLipLowerRight",
        "FaceTeethLower": "mFaceTeethLower",
        "FaceTeethUpper": "mFaceTeethUpper",
        "FaceChin": "mFaceChin",

        # List of wing bones
        "WingsRoot": "mWingsRoot",
        "Wing1Left": "mWing1Left",
        "Wing2Left": "mWing2Left",
        "Wing3Left": "mWing3Left",
        "Wing4Left": "mWing4Left",
        "Wing1Right": "mWing1Right",
        "Wing2Right": "mWing2Right",
        "Wing3Right": "mWing3Right",
        "Wing4Right": "mWing4Right",
        "Wing4FanRight": "mWing4FanRight",
        "Wing4FanLeft": "mWing4FanLeft",

        # List of tail bones
        "Tail1": "mTail1",
        "Tail2": "mTail2",
        "Tail3": "mTail3",
        "Tail4": "mTail4",
        "Tail5": "mTail5",
        "Tail6": "mTail6",

        # List of other joints
        "Groin": "mGroin"
    },
    'BASIC': {
        # Minimal bone set for basic SL avatars
        "Hips": "mPelvis",
        "Spine": "mSpine1",
        "Spine1": "mSpine2",
        "Spine2": "mTorso",
        "Neck": "mNeck",
        "Head": "mHead",
        "HeadTop_End": "mHeadTop_End"
    },
    'FACE_ONLY': {
        # Face bones only
        "FaceForeheadLeft": "mFaceForeheadLeft",
        "FaceForeheadCenter": "mFaceForeheadCenter",
        "FaceForeheadRight": "mFaceForeheadRight",
        "FaceEyebrowOuterLeft": "mFaceEyebrowOuterLeft",
        "FaceEyebrowCenterLeft": "mFaceEyebrowCenterLeft",
        "FaceEyebrowInnerLeft": "mFaceEyebrowInnerLeft",
        "FaceEyebrowOuterRight": "mFaceEyebrowOuterRight",
        "FaceEyebrowCenterRight": "mFaceEyebrowCenterRight",
        "FaceEyebrowInnerRight": "mFaceEyebrowInnerRight",
        "FaceEyeLidUpperLeft": "mFaceEyeLidUpperLeft",
        "FaceEyeLidLowerLeft": "mFaceEyeLidLowerLeft",
        "FaceEyeLidUpperRight": "mFaceEyeLidUpperRight",
        "FaceEyeLidLowerRight": "mFaceEyeLidLowerRight",
        "FaceEyeAltLeft": "mFaceEyeAltLeft",
        "FaceEyeAltRight": "mFaceEyeAltRight",
        "FaceEyecornerInnerLeft": "mFaceEyecornerInnerLeft",
        "FaceEyecornerInnerRight": "mFaceEyecornerInnerRight",
        "FaceEar1Left": "mFaceEar1Left",
        "FaceEar2Left": "mFaceEar2Left",
        "FaceEar1Right": "mFaceEar1Right",
        "FaceEar2Right": "mFaceEar2Right",
        "FaceNoseLeft": "mFaceNoseLeft",
        "FaceNoseCenter": "mFaceNoseCenter",
        "FaceNoseRight": "mFaceNoseRight",
        "FaceNoseBase": "mFaceNoseBase",
        "FaceNoseBridge": "mFaceNoseBridge",
        "FaceCheekUpperLeft": "mFaceCheekUpperLeft",
        "FaceCheekLowerLeft": "mFaceCheekLowerLeft",
        "FaceCheekUpperRight": "mFaceCheekUpperRight",
        "FaceCheekLowerRight": "mFaceCheekLowerRight",
        "FaceJaw": "mFaceJaw",
        "FaceLipUpperLeft": "mFaceLipUpperLeft",
        "FaceLipUpperCenter": "mFaceLipUpperCenter",
        "FaceLipUpperRight": "mFaceLipUpperRight",
        "FaceLipCornerLeft": "mFaceLipCornerLeft",
        "FaceLipCornerRight": "mFaceLipCornerRight",
        "FaceTongueBase": "mFaceTongueBase",
        "FaceTongueTip": "mFaceTongueTip",
        "FaceLipLowerLeft": "mFaceLipLowerLeft",
        "FaceLipLowerCenter": "mFaceLipLowerCenter",
        "FaceLipLowerRight": "mFaceLipLowerRight",
        "FaceTeethLower": "mFaceTeethLower",
        "FaceTeethUpper": "mFaceTeethUpper",
        "FaceChin": "mFaceChin"
    }
}

# ------------------------------------------------------------------------
# PROPERTY GROUP (stores addon settings)
# ------------------------------------------------------------------------
class BoneMappingProperties(PropertyGroup):
    """
    Stores all addon settings in the Blender scene
    Access via: context.scene.bone_mapping_props
    """
    
    # File import/export properties
    import_file: StringProperty(
        name="Import File",
        description="Path to JSON file containing custom bone mappings",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    export_file: StringProperty(
        name="Export File",
        description="Path to save current bone mappings as JSON",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    # Preset selection
    preset: EnumProperty(
        name="Preset",
        description="Select bone mapping preset",
        items=[
            ('BENTO_FULL', "Bento Full", "Complete Bento skeleton with hands"),
            ('BASIC', "Basic", "Basic OpenSim skeleton without hands"),
            ('CUSTOM', "Custom", "Load custom mapping from file")
        ],
        default='BENTO_FULL'
    )
    
    # Prefix handling options
    prefix_mode: EnumProperty(
        name="Prefix Mode",
        description="How to handle Mixamo bone prefixes",
        items=[
            ('AUTO', "Auto-Detect", "Automatically detect Mixamo prefix"),
            ('MANUAL', "Manual Select", "Select from common prefixes"),
            ('CUSTOM', "Custom", "Specify custom prefix pattern")
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
        description="Enter custom prefix (e.g. 'myRig_:')",
        default="mixamorig:",
        maxlen=32
    )
    
    # Weight optimization settings
    weight_threshold: FloatProperty(
        name="Weight Threshold",
        description="Remove vertex weights below this value",
        default=0.01,
        min=0.0,
        max=0.5
    )
    
    harden_joints: BoolProperty(
        name="Harden Joints",
        description="Create sharper transitions at elbows and knees",
        default=True
    )

# ------------------------------------------------------------------------
# IMPORT/EXPORT OPERATORS
# ------------------------------------------------------------------------
class OBJECT_OT_import_mapping(Operator, ImportHelper):
    """Imports bone mapping from JSON file"""
    bl_idname = "object.import_mapping"
    bl_label = "Import Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    # execute was? execute1
    def execute(self, context):
        scene = context.scene
        props = scene.bone_mapping_props
        
        try:
            with open(self.filepath, 'r') as f:
                mappings = json.load(f)
                scene['custom_bone_map'] = mappings
                props.preset = 'CUSTOM'
                self.report({'INFO'}, f"Imported mapping for {len(mappings)} bones")
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
        
        return {'FINISHED'}

# class OBJECT_OT_export_mapping(Operator, ExportHelper):
#     """Export current bone mapping to JSON file"""
#     bl_idname = "object.export_mapping"
#     bl_label = "Export Bone Mapping"
#     bl_options = {'REGISTER', 'UNDO'}
    
#     filename_ext = ".json"
#     filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
#     def execute(self, context):
#         try:
#             bone_map = self.get_current_bone_mapping(context)
#             with open(self.filepath, 'w') as f:
#                 json.dump(bone_map, f, indent=2)
#             self.report({'INFO'}, f"Exported {len(bone_map)} bones")
#         except Exception as e:
#             self.report({'ERROR'}, f"Export failed: {str(e)}")
#         return {'FINISHED'}
    
#     def get_current_bone_mapping(self, context):
#         """Generates bone mapping from selected armature's actual bones"""
#         bone_map = {}
#         props = context.scene.bone_mapping_props
        
#         # Get first selected armature
#         armature = next((obj for obj in context.selected_objects if obj.type == 'ARMATURE'), None)
        
#         if not armature:
#             self.report({'WARNING'}, "No armature selected")
#             return bone_map
            
#         # Store current mode
#         current_mode = armature.mode
#         bpy.context.view_layer.objects.active = armature
        
#         try:
#             # Get bones from pose mode (works in all modes)
#             bone_map = {bone.name: bone.name for bone in armature.pose.bones}
            
#             # Apply current mappings
#             if props.preset == 'CUSTOM':
#                 custom_map = context.scene.get('custom_bone_map', {})
#                 bone_map.update({k:v for k,v in custom_map.items() if k in bone_map})
#             else:
#                 preset_map = PRESETS.get(props.preset, {})
#                 bone_map.update({k:v for k,v in preset_map.items() if k in bone_map})
                
#         finally:
#             # Restore original mode
#             bpy.ops.object.mode_set(mode=current_mode)
        
#         return bone_map

class OBJECT_OT_export_mapping(Operator, ExportHelper):
    """Export current bone mapping to JSON file"""
    bl_idname = "object.export_mapping"
    bl_label = "Export Bone Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})
    
    def execute(self, context):
        bone_map = self.get_current_bone_mapping(context)
        
        if not bone_map:
            self.report({'ERROR'}, "No bones to export")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(bone_map, f, indent=2, ensure_ascii=False)
            self.report({'INFO'}, f"Successfully exported {len(bone_map)} bones")
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
    def get_current_bone_mapping(self, context):
        """Generates complete bone mapping including custom renames"""
        props = context.scene.bone_mapping_props
        bone_map = {}
        
        # Get the active armature
        armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        if not armatures:
            return {}
            
        armature = armatures[0]
        
        # Get all bones (works in any mode)
        bone_map = {bone.name: bone.name for bone in armature.pose.bones}
        
        # Apply current mappings
        if props.preset == 'CUSTOM':
            custom_map = context.scene.get('custom_bone_map', {})
            bone_map.update({k: v for k, v in custom_map.items() if k in bone_map})
        else:
            preset_map = PRESETS.get(props.preset, {})
            bone_map.update({k: v for k, v in preset_map.items() if k in bone_map})
        
        return bone_map
    
# ------------------------------------------------------------------------
# MAIN RENAMING OPERATOR
# ------------------------------------------------------------------------
class OBJECT_OT_rename_mixamo_bones(Operator):
    """Main operator that performs the bone renaming"""
    bl_idname = "object.rename_mixamo_bones"
    bl_label = "Convert Mixamo Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def detect_prefix(self, armature):
        """Automatically detects Mixamo prefix in armature"""
        prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
        for bone in armature.data.bones:
            for prefix in prefixes:
                if bone.name.startswith(prefix):
                    return prefix
        return None

    def get_prefix(self, context, armature):
        """Gets prefix based on user settings"""
        props = context.scene.bone_mapping_props
        if props.prefix_mode == 'AUTO':
            return self.detect_prefix(armature)
        elif props.prefix_mode == 'MANUAL':
            return props.manual_prefix
        return props.custom_prefix

    # execute was? execute3
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

            # Rename bones in Edit Mode
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            
            for bone in armature.data.edit_bones:
                if not pattern.match(bone.name):
                    skipped += 1
                    continue
                    
                base_name = pattern.sub("", bone.name)
                
                if base_name in bone_map:
                    new_name = bone_map[base_name]
                    
                    # Skip if name already exists (unless it's the same bone)
                    if new_name in armature.data.edit_bones:
                        if armature.data.edit_bones[new_name] != bone:
                            self.report({'WARNING'}, f"Skipped: {new_name} already exists")
                            skipped += 1
                            continue
                            
                    bone.name = new_name
                    processed += 1
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Rename vertex groups in child meshes
            for mesh in meshes:
                if mesh.parent == armature:
                    for vg in mesh.vertex_groups:
                        if pattern.match(vg.name):
                            base_name = pattern.sub("", vg.name)
                            if base_name in bone_map:
                                vg.name = bone_map[base_name]

        self.report({'INFO'}, f"Renamed {processed} bones, skipped {skipped}")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# WEIGHT OPTIMIZATION OPERATOR
# ------------------------------------------------------------------------
class OBJECT_OT_optimize_weights(Operator):
    """Optimizes vertex weights for Second Life compatibility"""
    bl_idname = "object.optimize_weights"
    bl_label = "Optimize Weights"
    bl_options = {'REGISTER', 'UNDO'}

    # execute was? execute3
    # def execute(self, context):
    #     props = context.scene.bone_mapping_props
        
    #     for obj in context.selected_objects:
    #         if obj.type != 'MESH':
    #             continue
                
    #         # Clean up low influence weights
    #         for vg in obj.vertex_groups:
    #             # Get all vertices with weights below threshold
    #             to_remove = [
    #                 v.index for v in obj.data.vertices 
    #                 if vg.weight(v.index) < props.weight_threshold
    #             ]
                
    #             # Remove the low weights
    #             if to_remove:
    #                 vg.remove(to_remove)
            
    #         # Harden joints if enabled
    #         if props.harden_joints:
    #             self.harden_joints(obj)
                
    #     return {'FINISHED'}
    
    def execute(self, context):
        props = context.scene.bone_mapping_props
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
                
            for vg in obj.vertex_groups:
                to_remove = []
                for v in obj.data.vertices:
                    try:
                        # Check if vertex has weight in this group
                        if vg.weight(v.index) < props.weight_threshold:
                            to_remove.append(v.index)
                    except RuntimeError:
                        # Vertex not in group, skip it
                        continue
                
                # Remove vertices below threshold in batch
                if to_remove:
                    vg.remove(to_remove)
                    
            # Harden joints if enabled
            if props.harden_joints:
                self.harden_joints(obj)
        
        return {'FINISHED'}

    def harden_joints(self, mesh_obj):
        """Creates sharper transitions at key joints"""
        # This is a placeholder - actual implementation would require
        # modifying the weight paint data directly
        print(f"Weight optimization would be applied to {mesh_obj.name}")

# ------------------------------------------------------------------------
# UI PANEL
# ------------------------------------------------------------------------
class OBJECT_PT_mixamo_bone_panel(Panel):
    """Creates the UI panel in the 3D view sidebar"""
    bl_label = "Mixamo to OpenSim"
    bl_idname = "OBJECT_PT_mixamo_bone_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mixamo Tools'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.bone_mapping_props
        
        # Bone Mapping Section
        box = layout.box()
        box.label(text="Bone Mapping")
        box.prop(props, "preset", text="Preset")
        
        # Prefix Options
        box.prop(props, "prefix_mode", text="Prefix Handling")
        if props.prefix_mode == 'MANUAL':
            box.prop(props, "manual_prefix")
        elif props.prefix_mode == 'CUSTOM':
            box.prop(props, "custom_prefix")
        
        # Import/Export Buttons
        row = box.row()
        row.operator("object.import_mapping", text="Import", icon='IMPORT')
        row.operator("object.export_mapping", text="Export", icon='EXPORT')
        
        # Main Conversion Button
        box.operator("object.rename_mixamo_bones", text="Convert Rig", icon='ARMATURE_DATA')
        
        # Weight Optimization Section
        box = layout.box()
        box.label(text="Weight Optimization")
        box.prop(props, "weight_threshold")
        box.prop(props, "harden_joints")
        box.operator("object.optimize_weights", text="Optimize Weights", icon='MOD_VERTEX_WEIGHT')

# ------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------
def register():
    bpy.utils.register_class(BoneMappingProperties)
    bpy.utils.register_class(OBJECT_OT_import_mapping)
    bpy.utils.register_class(OBJECT_OT_export_mapping)
    bpy.utils.register_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.register_class(OBJECT_OT_optimize_weights)
    bpy.utils.register_class(OBJECT_PT_mixamo_bone_panel)
    
    bpy.types.Scene.bone_mapping_props = PointerProperty(
        type=BoneMappingProperties)

def unregister():
    bpy.utils.unregister_class(BoneMappingProperties)
    bpy.utils.unregister_class(OBJECT_OT_import_mapping)
    bpy.utils.unregister_class(OBJECT_OT_export_mapping)
    bpy.utils.unregister_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.unregister_class(OBJECT_OT_optimize_weights)
    bpy.utils.unregister_class(OBJECT_PT_mixamo_bone_panel)
    
    del bpy.types.Scene.bone_mapping_props

if __name__ == "__main__":
    register()