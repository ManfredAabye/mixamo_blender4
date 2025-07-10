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
# Auto Parenting and Auto Weighting Section
# ------------------------------------------------------------------------
class OBJECT_OT_auto_parenting(bpy.types.Operator):
    """Automatisches Bone Parenting basierend auf Preset-Mapping"""
    bl_idname = "object.auto_parenting"
    bl_label = "Auto Bone Parenting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.bone_mapping_props
        preset_name = props.preset
        preset_map = PRESETS.get(preset_name, {})

        # Armature finden
        armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
        if not armatures:
            self.report({'ERROR'}, "Kein Armature ausgewählt")
            return {'CANCELLED'}

        armature = armatures[0]
        bpy.context.view_layer.objects.active = armature

        # In Edit Mode wechseln
        bpy.ops.object.mode_set(mode='EDIT')
        bones = armature.data.edit_bones

        count = 0
        for src_name, target_name in preset_map.items():
            src_bone = bones.get(src_name)
            target_bone = bones.get(target_name)
            if src_bone and target_bone and src_bone != target_bone:
                src_bone.parent = target_bone
                src_bone.use_connect = False
                count += 1

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, f"{count} Bones automatisch verbunden")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# Weight Preset Save/Load Section
# ------------------------------------------------------------------------
class OBJECT_OT_save_weights_json(bpy.types.Operator, ExportHelper):
    """Speichert Vertex-Gewichtungen in JSON-Datei"""
    bl_idname = "object.save_weights_json"
    bl_label = "Weights exportieren"
    bl_description = "Speichert alle Vertex-Gewichte als JSON"
    filename_ext = ".json"
    
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Kein Mesh-Objekt ausgewählt")
            return {'CANCELLED'}
            
        weights = {}
        mesh = obj.data
        
        for vg in obj.vertex_groups:
            weights[vg.name] = {}
            for v in mesh.vertices:
                try:
                    w = vg.weight(v.index)
                    if w > 0.0:  # Nur relevante Weights speichern
                        weights[vg.name][str(v.index)] = w
                except:
                    continue
        
        with open(self.filepath, 'w') as f:
            json.dump(weights, f, indent=2)
            
        self.report({'INFO'}, f"Weights exportiert: {os.path.basename(self.filepath)}")
        return {'FINISHED'}


class OBJECT_OT_load_weights_json(bpy.types.Operator, ImportHelper):
    """Lädt Vertex-Gewichtungen aus JSON-Datei"""
    bl_idname = "object.load_weights_json"
    bl_label = "Weights importieren"
    bl_description = "Lädt Vertex-Gewichte aus JSON"
    filename_ext = ".json"
    
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Kein Mesh-Objekt ausgewählt")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'r') as f:
                weights = json.load(f)
                
            # Vorhandene Groups löschen
            for vg in obj.vertex_groups:
                obj.vertex_groups.remove(vg)
                
            # Neue Groups erstellen
            for vg_name in weights:
                vg = obj.vertex_groups.new(name=vg_name)
                for v_idx, weight in weights[vg_name].items():
                    vg.add([int(v_idx)], weight, 'REPLACE')
                    
        except Exception as e:
            self.report({'ERROR'}, f"Import fehlgeschlagen: {str(e)}")
            return {'CANCELLED'}
            
        self.report({'INFO'}, f"Weights importiert: {os.path.basename(self.filepath)}")
        return {'FINISHED'}


class OBJECT_OT_auto_weighting(bpy.types.Operator):
    """Automatische Gewichtszuweisung via Armature"""
    bl_idname = "object.auto_weighting"
    bl_label = "Auto-Gewichtung"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Kein Mesh-Objekt ausgewählt")
            return {'CANCELLED'}
            
        armature = next((o for o in context.selected_objects if o.type == 'ARMATURE'), None)
        if not armature:
            self.report({'ERROR'}, "Keine Armature ausgewählt")
            return {'CANCELLED'}
            
        try:
            # Backup der aktuellen Selektion
            prev_active = context.view_layer.objects.active
            prev_selected = context.selected_objects
            
            # Parenting durchführen
            context.view_layer.objects.active = obj
            obj.select_set(True)
            armature.select_set(True)
            
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            
            # Originale Selektion wiederherstellen
            context.view_layer.objects.active = prev_active
            for o in prev_selected:
                o.select_set(True)
                
        except Exception as e:
            self.report({'ERROR'}, f"Fehler: {str(e)}")
            return {'CANCELLED'}
            
        self.report({'INFO'}, "Automatische Gewichtung erfolgreich")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# Bone Info Report Operator
# ------------------------------------------------------------------------
class OBJECT_OT_bone_info(Operator):
    """Zeigt detaillierte Knochen-Informationen und prüft auf Auffälligkeiten"""
    bl_idname = "armature.bone_info"
    bl_label = "Bone Info Report"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type == 'ARMATURE' and
                context.mode == 'POSE')

    def execute(self, context):
        bone = context.active_pose_bone
        if not bone:
            self.report({'ERROR'}, "Kein Knochen ausgewählt!")
            return {'CANCELLED'}

        # Basis-Informationen sammeln
        info = [
            f"Name: {bone.name}",
            f"Parent: {bone.parent.name if bone.parent else 'None'}",
            f"Length: {bone.length:.4f}",
            f"Volume: {bone.bone.head_radius * bone.bone.tail_radius * bone.length:.4f}",
            f"Connected: {bone.bone.use_connect}"
        ]

        # Gewichtungsanalyse (nur wenn Mesh ausgewählt)
        weight_stats = self.get_weight_stats(context, bone.name)
        if weight_stats:
            info.extend([
                "",
                "Weight Statistics:",
                f"Vertices: {weight_stats['vertex_count']}",
                f"Avg Weight: {weight_stats['avg_weight']:.2f}",
                f"Max Weight: {weight_stats['max_weight']:.2f}",
                f"Zero Weights: {weight_stats['zero_count']}",
            ])

        # Validierung
        warnings = self.validate_bone(bone, weight_stats)
        if warnings:
            info.extend(["", "WARNINGS:"] + warnings)

        # Popup anzeigen
        context.window_manager.popup_menu(
            lambda self, ctx: [self.layout.label(text=line) for line in info if line],
            title="Bone Info",
            icon='BONE_DATA'
        )

        return {'FINISHED'}

    def get_weight_stats(self, context, bone_name):
        """Analysiert die Vertex-Gewichte für diesen Knochen"""
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return None

        vertex_group = obj.vertex_groups.get(bone_name)
        if not vertex_group:
            return None

        mesh = obj.data
        total = 0
        count = 0
        max_weight = 0
        zero_count = 0

        for v in mesh.vertices:
            try:
                weight = vertex_group.weight(v.index)
                if weight > 0:
                    total += weight
                    count += 1
                    max_weight = max(max_weight, weight)
                else:
                    zero_count += 1
            except:
                zero_count += 1

        return {
            'vertex_count': count,
            'avg_weight': total / count if count else 0,
            'max_weight': max_weight,
            'zero_count': zero_count
        }

    def validate_bone(self, bone, weight_stats):
        """Führt Validierungsprüfungen durch"""
        warnings = []
        
        # Knochenlänge prüfen
        if bone.length < 0.001:
            warnings.append(f"- Extrem kurze Länge ({bone.length:.4f})")
        
        # Gewichtungsprüfung
        if weight_stats:
            if weight_stats['avg_weight'] < 0.1:
                warnings.append("- Geringer durchschnittlicher Einfluss (Avg Weight < 0.1)")
            if weight_stats['max_weight'] < 0.5:
                warnings.append("- Keine starken Vertex-Bindungen (Max Weight < 0.5)")
        
        return warnings

# ------------------------------------------------------------------------
# Validate Rig Operator
# ------------------------------------------------------------------------
class ARMATURE_OT_validate_rig(Operator):
    """Überprüft das gesamte Rig auf häufige Probleme"""
    bl_idname = "armature.validate_rig"
    bl_label = "Validate Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.active_object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Keine Armature ausgewählt")
            return {'CANCELLED'}

        issues = []
        bone_count = 0
        weight_issues = 0
        scale_issues = 0

        # 1. Knochen-Hierarchie prüfen
        for bone in armature.pose.bones:
            bone_count += 1
            
            # A. Nicht-uniforme Skalierung
            if abs(bone.scale.x - bone.scale.y) > 0.001 or abs(bone.scale.y - bone.scale.z) > 0.001:
                issues.append(f"⚠️ Nicht-uniforme Skalierung: {bone.name}")
                scale_issues += 1

            # B. Extrem kurze Knochen
            if bone.length < 0.001:
                issues.append(f"⚠️ Extrem kurzer Knochen: {bone.name} (Länge: {bone.length:.4f})")

            # C. Gewichtungsprobleme (nur wenn Mesh ausgewählt)
            if context.selected_objects and context.selected_objects[0].type == 'MESH':
                mesh = context.selected_objects[0]
                vg = mesh.vertex_groups.get(bone.name)
                if vg:
                    weights = [vg.weight(v.index) for v in mesh.data.vertices if vg.weight(v.index) > 0]
                    if weights:
                        avg = sum(weights) / len(weights)
                        if avg < 0.2:
                            issues.append(f"⚠️ Geringer Einfluss: {bone.name} (Avg: {avg:.2f})")
                            weight_issues += 1

        # 2. Root-Bone check
        root_bones = [b for b in armature.pose.bones if not b.parent]
        if len(root_bones) != 1:
            issues.append("⚠️ Mehrere Root-Bones vorhanden")

        # 3. Ergebnis anzeigen
        if not issues:
            self.report({'INFO'}, f"✅ Rig ist sauber ({bone_count} Knochen geprüft)")
        else:
            issues.insert(0, f"Rig-Analyse ({bone_count} Knochen):")
            issues.append(f"\n{len(issues)-1} Probleme gefunden:")
            issues.append(f"- {weight_issues} Gewichtungsprobleme")
            issues.append(f"- {scale_issues} Skalierungsprobleme")
            
            # Multiline-Report
            text = "\n".join(issues)
            self.report({'WARNING'}, text)
            
            # Ausführliches Popup
            context.window_manager.popup_menu(
                lambda self, ctx: [self.layout.label(text=line) for line in issues if line],
                title="Rig Validation Report", 
                icon='ERROR'
            )

        return {'FINISHED'}

# ------------------------------------------------------------------------
# Apply All Transforms Operator
# ------------------------------------------------------------------------
class OBJECT_OT_apply_all_transforms(Operator):
    """Wendet alle Transformationen (Location, Rotation, Scale) auf das ausgewählte Objekt an"""
    bl_idname = "object.apply_all_transforms"
    bl_label = "Apply All Transforms"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        try:
            # Sicherstellen dass wir im Object Mode sind
            if context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Alle Transformationen anwenden
            bpy.ops.object.transform_apply(
                location=True,
                rotation=True,
                scale=True
            )
            
            self.report({'INFO'}, "Alle Transformationen wurden angewendet")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Fehler: {str(e)}")
            return {'CANCELLED'}

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

        # Auto Parenting and Auto Weighting Section
        box = layout.box()
        box.label(text="Auto-Rigging Funktionen")
        box.operator("object.auto_parenting", text="Knochen automatisch parenten", icon='CONSTRAINT_BONE')
        box.operator("object.auto_weighting", text="Gewichtung automatisch berechnen", icon='MOD_VERTEX_WEIGHT')

        # Weight Presets Section
        box = layout.box()
        box.label(text="Weight Presets", icon='MOD_VERTEX_WEIGHT')
        row = box.row()
        row.operator("object.save_weights_json", icon='EXPORT')
        row.operator("object.load_weights_json", icon='IMPORT')
        box.operator("object.auto_weighting", icon='AUTO')

        # Bone Analysis Section (NEU)
        box = layout.box()
        box.label(text="Bone Analysis", icon='BONE_DATA')
        col = box.column(align=True)
        col.operator("armature.bone_info", text="Show Bone Info", icon='INFO')
        col.operator("armature.validate_rig", text="Validate Rigging", icon='CHECKMARK')

        # Apply All Transforms Button
        box = layout.box()
        box.label(text="Apply All Transforms", icon='CON_LOCLIKE')
        box.operator("object.apply_all_transforms", icon='CON_LOCLIKE')

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
    bpy.utils.register_class(OBJECT_OT_auto_parenting)
    bpy.utils.register_class(OBJECT_OT_save_weights_json)
    bpy.utils.register_class(OBJECT_OT_load_weights_json)
    bpy.utils.register_class(OBJECT_OT_auto_weighting)
    bpy.utils.register_class(OBJECT_OT_bone_info)
    bpy.utils.register_class(ARMATURE_OT_validate_rig)
    bpy.utils.register_class(OBJECT_OT_apply_all_transforms)
    
    bpy.types.Scene.bone_mapping_props = PointerProperty(
        type=BoneMappingProperties)

def unregister():
    bpy.utils.unregister_class(BoneMappingProperties)
    bpy.utils.unregister_class(OBJECT_OT_import_mapping)
    bpy.utils.unregister_class(OBJECT_OT_export_mapping)
    bpy.utils.unregister_class(OBJECT_OT_rename_mixamo_bones)
    bpy.utils.unregister_class(OBJECT_OT_optimize_weights)
    bpy.utils.unregister_class(OBJECT_PT_mixamo_bone_panel)
    bpy.utils.unregister_class(OBJECT_OT_auto_parenting)
    bpy.utils.unregister_class(OBJECT_OT_auto_weighting)
    bpy.utils.unregister_class(OBJECT_OT_load_weights_json)
    bpy.utils.unregister_class(OBJECT_OT_save_weights_json)
    bpy.utils.unregister_class(OBJECT_OT_bone_info)
    bpy.utils.unregister_class(ARMATURE_OT_validate_rig)
    bpy.utils.unregister_class(OBJECT_OT_apply_all_transforms)
    
    del bpy.types.Scene.bone_mapping_props

if __name__ == "__main__":
    register()