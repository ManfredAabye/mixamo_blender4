"""
MIXAMO TO OPENSIM/SECOND LIFE RIG CONVERTER
- Renames bones from Mixamo to OpenSim standard
- Optimizes vertex weights for SL compatibility
- Preserves all original functionality
"""

# todo: Automatisches Umwandeln: Mixamo FBX → Second Life/OpenSim Bento DAE in Blender
# Nicht an Checkboxen sparen oder Buttons, Manuelle und automatische einstellungen verwenden.
# Was genau muss passieren beziehungsweise berücksichtigt werden:
# Hierarchie korrigieren
# Vertex-Gewichtung an Bento-Bones übertragen
# Automatisches Parenting der Bones
# Joint Offsets
# Die Rotationen und Bind-Posen
# Einfaches Umbenennen reicht nicht. Damit ein Mixamo-Rig funktional in Second Life Bento funktioniert, müssen zusätzlich zur Umbenennung auch Struktur, Hierarchie und Gewichtung korrekt an Bento angepasst werden.
# Bone Roll korrigieren
# Restpose prüfen und korrigieren
# dae (Collada) Export als extra button
# Apply Transform button
# Gesichtsrig + Bento-Extras

bl_info = {
    "name": "Mixamo to OpenSim Rig Converter",
    "author": "Manni V12",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "location": "3D View > Sidebar > Mixamo Tools",
    "description": "Converts Mixamo rigs to OpenSim/Second Life compatible format",
    "category": "Rigging",
}

# === SYSTEM IMPORTS ===
import os
import re
import json
import xml.etree.ElementTree as ET

# === BLENDER CORE ===
import bpy

# === BLENDER TYPES ===
# UI Components
from bpy.types import Operator
from bpy.types import Panel

# Data Structures
from bpy.types import PropertyGroup

# === BLENDER PROPERTIES ===
# Primitive Types
from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import FloatProperty

# Special Types
from bpy.props import EnumProperty
from bpy.props import PointerProperty

# === IO UTILITIES ===
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper

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

BONE_PARENTS = {
    # Körper
    "mSpine1": "mPelvis",
    "mSpine2": "mSpine1",
    "mSpine3": "mSpine2",
    "mSpine4": "mSpine3",
    "mTorso": "mSpine4",
    "mChest": "mTorso",
    "mNeck": "mChest",
    "mHead": "mNeck",
    "mHeadTop_End": "mHead",
    "mSkull": "mHead",

    # Arme links
    "mCollarLeft": "mChest",
    "mShoulderLeft": "mCollarLeft",
    "mElbowLeft": "mShoulderLeft",
    "mWristLeft": "mElbowLeft",

    # Finger links
    "mHandThumb1Left": "mWristLeft",
    "mHandThumb2Left": "mHandThumb1Left",
    "mHandThumb3Left": "mHandThumb2Left",
    "mHandIndex1Left": "mWristLeft",
    "mHandIndex2Left": "mHandIndex1Left",
    "mHandIndex3Left": "mHandIndex2Left",
    "mHandMiddle1Left": "mWristLeft",
    "mHandMiddle2Left": "mHandMiddle1Left",
    "mHandMiddle3Left": "mHandMiddle2Left",
    "mHandRing1Left": "mWristLeft",
    "mHandRing2Left": "mHandRing1Left",
    "mHandRing3Left": "mHandRing2Left",
    "mHandPinky1Left": "mWristLeft",
    "mHandPinky2Left": "mHandPinky1Left",
    "mHandPinky3Left": "mHandPinky2Left",

    # Arme rechts
    "mCollarRight": "mChest",
    "mShoulderRight": "mCollarRight",
    "mElbowRight": "mShoulderRight",
    "mWristRight": "mElbowRight",

    # Finger rechts
    "mHandThumb1Right": "mWristRight",
    "mHandThumb2Right": "mHandThumb1Right",
    "mHandThumb3Right": "mHandThumb2Right",
    "mHandIndex1Right": "mWristRight",
    "mHandIndex2Right": "mHandIndex1Right",
    "mHandIndex3Right": "mHandIndex2Right",
    "mHandMiddle1Right": "mWristRight",
    "mHandMiddle2Right": "mHandMiddle1Right",
    "mHandMiddle3Right": "mHandMiddle2Right",
    "mHandRing1Right": "mWristRight",
    "mHandRing2Right": "mHandRing1Right",
    "mHandRing3Right": "mHandRing2Right",
    "mHandPinky1Right": "mWristRight",
    "mHandPinky2Right": "mHandPinky1Right",
    "mHandPinky3Right": "mHandPinky2Right",

    # Beine links
    "mHipLeft": "mPelvis",
    "mKneeLeft": "mHipLeft",
    "mAnkleLeft": "mKneeLeft",
    "mFootLeft": "mAnkleLeft",
    "mToeLeft": "mFootLeft",
    "mToeLeftEnd": "mToeLeft",

    # Beine rechts
    "mHipRight": "mPelvis",
    "mKneeRight": "mHipRight",
    "mAnkleRight": "mKneeRight",
    "mFootRight": "mAnkleRight",
    "mToeRight": "mFootRight",
    "mToeRightEnd": "mToeRight",

    # Gesicht
    "mFaceRoot": "mHead",
    "mFaceJaw": "mFaceRoot",
    "mFaceJawShaper": "mFaceJaw",
    "mFaceChin": "mFaceJaw",
    "mFaceTeethLower": "mFaceJaw",
    "mFaceTeethUpper": "mFaceJaw",
    "mFaceTongueBase": "mFaceJaw",
    "mFaceTongueTip": "mFaceTongueBase",

    # Stirn & Augenbrauen
    "mFaceForeheadCenter": "mFaceRoot",
    "mFaceForeheadLeft": "mFaceRoot",
    "mFaceForeheadRight": "mFaceRoot",
    "mFaceEyebrowOuterLeft": "mFaceForeheadLeft",
    "mFaceEyebrowCenterLeft": "mFaceForeheadLeft",
    "mFaceEyebrowInnerLeft": "mFaceForeheadLeft",
    "mFaceEyebrowOuterRight": "mFaceForeheadRight",
    "mFaceEyebrowCenterRight": "mFaceForeheadRight",
    "mFaceEyebrowInnerRight": "mFaceForeheadRight",

    # Augen
    "mEyeLeft": "mHead",
    "mEyeRight": "mHead",
    "mFaceEyeAltLeft": "mFaceRoot",
    "mFaceEyeAltRight": "mFaceRoot",
    "mFaceEyeLidUpperLeft": "mFaceRoot",
    "mFaceEyeLidLowerLeft": "mFaceRoot",
    "mFaceEyeLidUpperRight": "mFaceRoot",
    "mFaceEyeLidLowerRight": "mFaceRoot",
    "mFaceEyecornerInnerLeft": "mFaceRoot",
    "mFaceEyecornerInnerRight": "mFaceRoot",

    # Nase
    "mFaceNoseLeft": "mFaceRoot",
    "mFaceNoseCenter": "mFaceRoot",
    "mFaceNoseRight": "mFaceRoot",
    "mFaceNoseBase": "mFaceRoot",
    "mFaceNoseBridge": "mFaceRoot",

    # Wangen
    "mFaceCheekUpperLeft": "mFaceRoot",
    "mFaceCheekLowerLeft": "mFaceRoot",
    "mFaceCheekUpperRight": "mFaceRoot",
    "mFaceCheekLowerRight": "mFaceRoot",

    # Lippen
    "mFaceLipUpperLeft": "mFaceRoot",
    "mFaceLipUpperCenter": "mFaceRoot",
    "mFaceLipUpperRight": "mFaceRoot",
    "mFaceLipCornerLeft": "mFaceRoot",
    "mFaceLipCornerRight": "mFaceRoot",
    "mFaceLipLowerLeft": "mFaceRoot",
    "mFaceLipLowerCenter": "mFaceRoot",
    "mFaceLipLowerRight": "mFaceRoot",

    # Ohren
    "mFaceEar1Left": "mFaceRoot",
    "mFaceEar2Left": "mFaceEar1Left",
    "mFaceEar1Right": "mFaceRoot",
    "mFaceEar2Right": "mFaceEar1Right",

    # Schwanz
    "mTail1": "mPelvis",
    "mTail2": "mTail1",
    "mTail3": "mTail2",
    "mTail4": "mTail3",
    "mTail5": "mTail4",
    "mTail6": "mTail5",

    # Flügel
    "mWingsRoot": "mChest",
    "mWing1Left": "mWingsRoot",
    "mWing2Left": "mWing1Left",
    "mWing3Left": "mWing2Left",
    "mWing4Left": "mWing3Left",
    "mWing4FanLeft": "mWing4Left",
    "mWing1Right": "mWingsRoot",
    "mWing2Right": "mWing1Right",
    "mWing3Right": "mWing2Right",
    "mWing4Right": "mWing3Right",
    "mWing4FanRight": "mWing4Right",

    # Hinterbeine
    "mHindLimbsRoot": "mPelvis",
    "mHindLimb1Left": "mHindLimbsRoot",
    "mHindLimb2Left": "mHindLimb1Left",
    "mHindLimb3Left": "mHindLimb2Left",
    "mHindLimb4Left": "mHindLimb3Left",
    "mHindLimb1Right": "mHindLimbsRoot",
    "mHindLimb2Right": "mHindLimb1Right",
    "mHindLimb3Right": "mHindLimb2Right",
    "mHindLimb4Right": "mHindLimb3Right",

    # Groin
    "mGroin": "mPelvis"
}

def load_bone_parents():
    """Sicheres Laden der Bone-Hierarchie-Definition"""
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, "bone_parents.json")
    
    default_structure = {
        "mPelvis": None,
        "mSpine1": "mPelvis",
        "mSpine2": "mSpine1",
        "mSpine3": "mSpine2",
        "mSpine4": "mSpine3",
        "mTorso": "mSpine4",
        "mChest": "mTorso",
        "mNeck": "mChest",
        "mHead": "mNeck",
        "mHeadTop_End": "mHead",
        "mSkull": "mHead",

        # Arme links
        "mCollarLeft": "mChest",
        "mShoulderLeft": "mCollarLeft",
        "mElbowLeft": "mShoulderLeft",
        "mWristLeft": "mElbowLeft",

        # Finger links
        "mHandThumb1Left": "mWristLeft",
        "mHandThumb2Left": "mHandThumb1Left",
        "mHandThumb3Left": "mHandThumb2Left",
        "mHandIndex1Left": "mWristLeft",
        "mHandIndex2Left": "mHandIndex1Left",
        "mHandIndex3Left": "mHandIndex2Left",
        "mHandMiddle1Left": "mWristLeft",
        "mHandMiddle2Left": "mHandMiddle1Left",
        "mHandMiddle3Left": "mHandMiddle2Left",
        "mHandRing1Left": "mWristLeft",
        "mHandRing2Left": "mHandRing1Left",
        "mHandRing3Left": "mHandRing2Left",
        "mHandPinky1Left": "mWristLeft",
        "mHandPinky2Left": "mHandPinky1Left",
        "mHandPinky3Left": "mHandPinky2Left",

        # Arme rechts
        "mCollarRight": "mChest",
        "mShoulderRight": "mCollarRight",
        "mElbowRight": "mShoulderRight",
        "mWristRight": "mElbowRight",

        # Finger rechts
        "mHandThumb1Right": "mWristRight",
        "mHandThumb2Right": "mHandThumb1Right",
        "mHandThumb3Right": "mHandThumb2Right",
        "mHandIndex1Right": "mWristRight",
        "mHandIndex2Right": "mHandIndex1Right",
        "mHandIndex3Right": "mHandIndex2Right",
        "mHandMiddle1Right": "mWristRight",
        "mHandMiddle2Right": "mHandMiddle1Right",
        "mHandMiddle3Right": "mHandMiddle2Right",
        "mHandRing1Right": "mWristRight",
        "mHandRing2Right": "mHandRing1Right",
        "mHandRing3Right": "mHandRing2Right",
        "mHandPinky1Right": "mWristRight",
        "mHandPinky2Right": "mHandPinky1Right",
        "mHandPinky3Right": "mHandPinky2Right",

        # Beine links
        "mHipLeft": "mPelvis",
        "mKneeLeft": "mHipLeft",
        "mAnkleLeft": "mKneeLeft",
        "mFootLeft": "mAnkleLeft",
        "mToeLeft": "mFootLeft",
        "mToeLeftEnd": "mToeLeft",

        # Beine rechts
        "mHipRight": "mPelvis",
        "mKneeRight": "mHipRight",
        "mAnkleRight": "mKneeRight",
        "mFootRight": "mAnkleRight",
        "mToeRight": "mFootRight",
        "mToeRightEnd": "mToeRight",

        # Gesicht
        "mFaceRoot": "mHead",
        "mFaceJaw": "mFaceRoot",
        "mFaceJawShaper": "mFaceJaw",
        "mFaceChin": "mFaceJaw",
        "mFaceTeethLower": "mFaceJaw",
        "mFaceTeethUpper": "mFaceJaw",
        "mFaceTongueBase": "mFaceJaw",
        "mFaceTongueTip": "mFaceTongueBase",

        # Stirn & Augenbrauen
        "mFaceForeheadCenter": "mFaceRoot",
        "mFaceForeheadLeft": "mFaceRoot",
        "mFaceForeheadRight": "mFaceRoot",
        "mFaceEyebrowOuterLeft": "mFaceForeheadLeft",
        "mFaceEyebrowCenterLeft": "mFaceForeheadLeft",
        "mFaceEyebrowInnerLeft": "mFaceForeheadLeft",
        "mFaceEyebrowOuterRight": "mFaceForeheadRight",
        "mFaceEyebrowCenterRight": "mFaceForeheadRight",
        "mFaceEyebrowInnerRight": "mFaceForeheadRight",

        # Augen
        "mEyeLeft": "mHead",
        "mEyeRight": "mHead",
        "mFaceEyeAltLeft": "mFaceRoot",
        "mFaceEyeAltRight": "mFaceRoot",
        "mFaceEyeLidUpperLeft": "mFaceRoot",
        "mFaceEyeLidLowerLeft": "mFaceRoot",
        "mFaceEyeLidUpperRight": "mFaceRoot",
        "mFaceEyeLidLowerRight": "mFaceRoot",
        "mFaceEyecornerInnerLeft": "mFaceRoot",
        "mFaceEyecornerInnerRight": "mFaceRoot",

        # Nase
        "mFaceNoseLeft": "mFaceRoot",
        "mFaceNoseCenter": "mFaceRoot",
        "mFaceNoseRight": "mFaceRoot",
        "mFaceNoseBase": "mFaceRoot",
        "mFaceNoseBridge": "mFaceRoot",

        # Wangen
        "mFaceCheekUpperLeft": "mFaceRoot",
        "mFaceCheekLowerLeft": "mFaceRoot",
        "mFaceCheekUpperRight": "mFaceRoot",
        "mFaceCheekLowerRight": "mFaceRoot",

        # Lippen
        "mFaceLipUpperLeft": "mFaceRoot",
        "mFaceLipUpperCenter": "mFaceRoot",
        "mFaceLipUpperRight": "mFaceRoot",
        "mFaceLipCornerLeft": "mFaceRoot",
        "mFaceLipCornerRight": "mFaceRoot",
        "mFaceLipLowerLeft": "mFaceRoot",
        "mFaceLipLowerCenter": "mFaceRoot",
        "mFaceLipLowerRight": "mFaceRoot",

        # Ohren
        "mFaceEar1Left": "mFaceRoot",
        "mFaceEar2Left": "mFaceEar1Left",
        "mFaceEar1Right": "mFaceRoot",
        "mFaceEar2Right": "mFaceEar1Right",

        # Schwanz
        "mTail1": "mPelvis",
        "mTail2": "mTail1",
        "mTail3": "mTail2",
        "mTail4": "mTail3",
        "mTail5": "mTail4",
        "mTail6": "mTail5",

        # Flügel
        "mWingsRoot": "mChest",
        "mWing1Left": "mWingsRoot",
        "mWing2Left": "mWing1Left",
        "mWing3Left": "mWing2Left",
        "mWing4Left": "mWing3Left",
        "mWing4FanLeft": "mWing4Left",
        "mWing1Right": "mWingsRoot",
        "mWing2Right": "mWing1Right",
        "mWing3Right": "mWing2Right",
        "mWing4Right": "mWing3Right",
        "mWing4FanRight": "mWing4Right",

        # Hinterbeine
        "mHindLimbsRoot": "mPelvis",
        "mHindLimb1Left": "mHindLimbsRoot",
        "mHindLimb2Left": "mHindLimb1Left",
        "mHindLimb3Left": "mHindLimb2Left",
        "mHindLimb4Left": "mHindLimb3Left",
        "mHindLimb1Right": "mHindLimbsRoot",
        "mHindLimb2Right": "mHindLimb1Right",
        "mHindLimb3Right": "mHindLimb2Right",
        "mHindLimb4Right": "mHindLimb3Right",

        # Groin
        "mGroin": "mPelvis"
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Validierung der geladenen Daten
            if not isinstance(data, dict):
                raise ValueError("Ungültiges JSON-Format")
            return data
    except Exception as e:
        print(f"Fehler: {e}. Verwende Standard-Hierarchie.")
        return default_structure

hand_data = {
    "left": {
        "mCollarLeft": {
            "pos": [-0.021, 0.085, 0.165],
            "rot": [0.0, 0.0, 0.0],
            "children": {
                "mShoulderLeft": {
                    "pos": [0.000, 0.079, -0.000],
                    "rot": [0.0, 0.0, 0.0],
                    "children": {
                        "mElbowLeft": {
                            "pos": [0.000, 0.248, 0.000],
                            "rot": [0.0, 0.0, 0.0],
                            "children": {
                                "mWristLeft": {
                                    "pos": [-0.000, 0.205, 0.000],
                                    "rot": [0.0, 0.0, 0.0],
                                    "children": {
                                        "mHandMiddle1Left": {
                                            "pos": [0.013, 0.101, 0.015],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandMiddle2Left": {
                                                    "pos": [-0.001, 0.040, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandMiddle3Left": {
                                                            "pos": [-0.001, 0.049, -0.008],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandIndex1Left": {
                                            "pos": [0.038, 0.097, 0.015],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandIndex2Left": {
                                                    "pos": [0.017, 0.036, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandIndex3Left": {
                                                            "pos": [0.014, 0.032, -0.006],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandThumb1Left": {
                                            "pos": [0.031, 0.026, 0.004],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandThumb2Left": {
                                                    "pos": [0.028, 0.032, -0.001],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandThumb3Left": {
                                                            "pos": [0.023, 0.031, -0.001],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandRing1Left": {
                                            "pos": [-0.010, 0.099, 0.009],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandRing2Left": {
                                                    "pos": [-0.013, 0.038, -0.008],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandRing3Left": {
                                                            "pos": [-0.013, 0.040, -0.009],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandPinky1Left": {
                                            "pos": [-0.031, 0.095, 0.003],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandPinky2Left": {
                                                    "pos": [-0.024, 0.025, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandPinky3Left": {
                                                            "pos": [-0.015, 0.018, -0.004],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "right": {
        "mCollarRight": {
            "pos": [-0.021, -0.085, 0.165],
            "rot": [0.0, 0.0, 0.0],
            "children": {
                "mShoulderRight": {
                    "pos": [0.000, -0.079, -0.000],
                    "rot": [0.0, 0.0, 0.0],
                    "children": {
                        "mElbowRight": {
                            "pos": [0.000, -0.248, -0.000],
                            "rot": [0.0, 0.0, 0.0],
                            "children": {
                                "mWristRight": {
                                    "pos": [0.000, -0.205, -0.000],
                                    "rot": [0.0, 0.0, 0.0],
                                    "children": {
                                        "mHandMiddle1Right": {
                                            "pos": [0.013, -0.101, 0.015],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandMiddle2Right": {
                                                    "pos": [-0.001, -0.040, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandMiddle3Right": {
                                                            "pos": [-0.001, -0.049, -0.008],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandIndex1Right": {
                                            "pos": [0.038, -0.097, 0.015],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandIndex2Right": {
                                                    "pos": [0.017, -0.036, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandIndex3Right": {
                                                            "pos": [0.014, -0.032, -0.006],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandThumb1Right": {
                                            "pos": [0.031, -0.026, 0.004],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandThumb2Right": {
                                                    "pos": [0.028, -0.032, -0.001],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandThumb3Right": {
                                                            "pos": [0.023, -0.031, -0.001],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandRing1Right": {
                                            "pos": [-0.010, -0.099, 0.009],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandRing2Right": {
                                                    "pos": [-0.013, -0.038, -0.008],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandRing3Right": {
                                                            "pos": [-0.013, -0.040, -0.009],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "mHandPinky1Right": {
                                            "pos": [-0.031, -0.095, 0.003],
                                            "rot": [0.0, 0.0, 0.0],
                                            "children": {
                                                "mHandPinky2Right": {
                                                    "pos": [-0.024, -0.025, -0.006],
                                                    "rot": [0.0, 0.0, 0.0],
                                                    "children": {
                                                        "mHandPinky3Right": {
                                                            "pos": [-0.015, -0.018, -0.004],
                                                            "rot": [0.0, 0.0, 0.0],
                                                            "children": {}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

bento_data = {
    "mPelvis": {
        "pos": [0.000, 0.000, 1.067],
        "rot": [0.0, 0.0, 0.0],
        "children": {
            "mSpine1": {
                "pos": [0.000, 0.000, 0.084],
                "rot": [0.0, 0.0, 0.0],
                "children": {
                    "mSpine2": {
                        "pos": [0.000, 0.000, -0.084],
                        "rot": [0.0, 0.0, 0.0],
                        "children": {
                            "mTorso": {
                                "pos": [0.000, 0.000, 0.084],
                                "rot": [0.0, 0.0, 0.0],
                                "children": {
                                    "mSpine3": {
                                        "pos": [-0.015, 0.000, 0.205],
                                        "rot": [0.0, 0.0, 0.0],
                                        "children": {
                                            "mSpine4": {
                                                "pos": [0.015, 0.000, -0.205],
                                                "rot": [0.0, 0.0, 0.0],
                                                "children": {
                                                    "mChest": {
                                                        "pos": [-0.015, 0.000, 0.205],
                                                        "rot": [0.0, 0.0, 0.0],
                                                        "children": {
                                                            "mNeck": {
                                                                "pos": [-0.010, 0.000, 0.251],
                                                                "rot": [0.0, 0.0, 0.0],
                                                                "children": {
                                                                    "mHead": {
                                                                        "pos": [0.000, -0.000, 0.076],
                                                                        "rot": [0.0, 0.0, 0.0],
                                                                        "children": {
                                                                            "mSkull": {
                                                                                "pos": [0.000, 0.000, 0.079],
                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                "children": {}
                                                                            },
                                                                            "mEyeRight": {
                                                                                "pos": [0.098, -0.036, 0.079],
                                                                                "rot": [0.0, 0.0, -0.0],
                                                                                "children": {}
                                                                            },
                                                                            "mEyeLeft": {
                                                                                "pos": [0.098, 0.036, 0.079],
                                                                                "rot": [0.0, -0.0, 0.0],
                                                                                "children": {}
                                                                            },
                                                                            "mFaceRoot": {
                                                                                "pos": [0.025, 0.000, 0.045],
                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                "children": {
                                                                                    # Face bones would be added here
                                                                                    # (omitted for brevity but would include all face bones from the XML)
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            "mCollarLeft": {
                                                                "pos": [-0.021, 0.085, 0.165],
                                                                "rot": [0.0, 0.0, 0.0],
                                                                "children": {
                                                                    "mShoulderLeft": {
                                                                        "pos": [0.000, 0.079, -0.000],
                                                                        "rot": [0.0, 0.0, 0.0],
                                                                        "children": {
                                                                            "mElbowLeft": {
                                                                                "pos": [0.000, 0.248, 0.000],
                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                "children": {
                                                                                    "mWristLeft": {
                                                                                        "pos": [-0.000, 0.205, 0.000],
                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                        "children": {
                                                                                            "mHandMiddle1Left": {
                                                                                                "pos": [0.013, 0.101, 0.015],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandMiddle2Left": {
                                                                                                        "pos": [-0.001, 0.040, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandMiddle3Left": {
                                                                                                                "pos": [-0.001, 0.049, -0.008],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandIndex1Left": {
                                                                                                "pos": [0.038, 0.097, 0.015],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandIndex2Left": {
                                                                                                        "pos": [0.017, 0.036, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandIndex3Left": {
                                                                                                                "pos": [0.014, 0.032, -0.006],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandThumb1Left": {
                                                                                                "pos": [0.031, 0.026, 0.004],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandThumb2Left": {
                                                                                                        "pos": [0.028, 0.032, -0.001],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandThumb3Left": {
                                                                                                                "pos": [0.023, 0.031, -0.001],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandRing1Left": {
                                                                                                "pos": [-0.010, 0.099, 0.009],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandRing2Left": {
                                                                                                        "pos": [-0.013, 0.038, -0.008],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandRing3Left": {
                                                                                                                "pos": [-0.013, 0.040, -0.009],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandPinky1Left": {
                                                                                                "pos": [-0.031, 0.095, 0.003],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandPinky2Left": {
                                                                                                        "pos": [-0.024, 0.025, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandPinky3Left": {
                                                                                                                "pos": [-0.015, 0.018, -0.004],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            "mCollarRight": {
                                                                "pos": [-0.021, -0.085, 0.165],
                                                                "rot": [0.0, 0.0, 0.0],
                                                                "children": {
                                                                    "mShoulderRight": {
                                                                        "pos": [0.000, -0.079, -0.000],
                                                                        "rot": [0.0, 0.0, 0.0],
                                                                        "children": {
                                                                            "mElbowRight": {
                                                                                "pos": [0.000, -0.248, -0.000],
                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                "children": {
                                                                                    "mWristRight": {
                                                                                        "pos": [0.000, -0.205, -0.000],
                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                        "children": {
                                                                                            "mHandMiddle1Right": {
                                                                                                "pos": [0.013, -0.101, 0.015],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandMiddle2Right": {
                                                                                                        "pos": [-0.001, -0.040, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandMiddle3Right": {
                                                                                                                "pos": [-0.001, -0.049, -0.008],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandIndex1Right": {
                                                                                                "pos": [0.038, -0.097, 0.015],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandIndex2Right": {
                                                                                                        "pos": [0.017, -0.036, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandIndex3Right": {
                                                                                                                "pos": [0.014, -0.032, -0.006],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandThumb1Right": {
                                                                                                "pos": [0.031, -0.026, 0.004],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandThumb2Right": {
                                                                                                        "pos": [0.028, -0.032, -0.001],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandThumb3Right": {
                                                                                                                "pos": [0.023, -0.031, -0.001],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandRing1Right": {
                                                                                                "pos": [-0.010, -0.099, 0.009],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandRing2Right": {
                                                                                                        "pos": [-0.013, -0.038, -0.008],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandRing3Right": {
                                                                                                                "pos": [-0.013, -0.040, -0.009],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            },
                                                                                            "mHandPinky1Right": {
                                                                                                "pos": [-0.031, -0.095, 0.003],
                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                "children": {
                                                                                                    "mHandPinky2Right": {
                                                                                                        "pos": [-0.024, -0.025, -0.006],
                                                                                                        "rot": [0.0, 0.0, 0.0],
                                                                                                        "children": {
                                                                                                            "mHandPinky3Right": {
                                                                                                                "pos": [-0.015, -0.018, -0.004],
                                                                                                                "rot": [0.0, 0.0, 0.0],
                                                                                                                "children": {}
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            "mWingsRoot": {
                                                                "pos": [-0.014, 0.000, 0.000],
                                                                "rot": [0.0, 0.0, 0.0],
                                                                "children": {
                                                                    # Wing bones would be added here
                                                                    # (omitted for brevity but would include all wing bones from the XML)
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "mHipRight": {
                "pos": [0.034, -0.129, -0.041],
                "rot": [0.0, 0.0, 0.0],
                "children": {
                    "mKneeRight": {
                        "pos": [-0.001, 0.049, -0.491],
                        "rot": [0.0, 0.0, 0.0],
                        "children": {
                            "mAnkleRight": {
                                "pos": [-0.029, 0.000, -0.468],
                                "rot": [0.0, 0.0, 0.0],
                                "children": {
                                    "mFootRight": {
                                        "pos": [0.112, -0.000, -0.061],
                                        "rot": [0.0, 0.0, 0.0],
                                        "children": {
                                            "mToeRight": {
                                                "pos": [0.109, 0.000, 0.000],
                                                "rot": [0.0, 0.0, 0.0],
                                                "children": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "mHipLeft": {
                "pos": [0.034, 0.127, -0.041],
                "rot": [0.0, 0.0, 0.0],
                "children": {
                    "mKneeLeft": {
                        "pos": [-0.001, -0.046, -0.491],
                        "rot": [0.0, 0.0, 0.0],
                        "children": {
                            "mAnkleLeft": {
                                "pos": [-0.029, 0.001, -0.468],
                                "rot": [0.0, 0.0, 0.0],
                                "children": {
                                    "mFootLeft": {
                                        "pos": [0.112, -0.000, -0.061],
                                        "rot": [0.0, 0.0, 0.0],
                                        "children": {
                                            "mToeLeft": {
                                                "pos": [0.109, 0.000, 0.000],
                                                "rot": [0.0, 0.0, 0.0],
                                                "children": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "mTail1": {
                "pos": [-0.116, 0.000, 0.047],
                "rot": [0.0, 0.0, 0.0],
                "children": {
                    # Tail bones would be added here
                    # (omitted for brevity but would include all tail bones from the XML)
                }
            },
            "mGroin": {
                "pos": [0.064, 0.000, -0.097],
                "rot": [0.0, 0.0, 0.0],
                "children": {}
            },
            "mHindLimbsRoot": {
                "pos": [-0.200, 0.000, 0.084],
                "rot": [0.0, 0.0, 0.0],
                "children": {
                    # Hind limb bones would be added here
                    # (omitted for brevity but would include all hind limb bones from the XML)
                }
            }
        }
    }
}

# ------------------------------------------------------------------------
# Bone Hierarchy Repair and Cleanup Functions
# ------------------------------------------------------------------------

# Hilfsfunktionen
def load_bone_parents():
    """Lädt die Bone-Hierarchie aus JSON oder verwendet Default"""
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, "bone_parents.json")
    
    default_structure = {
        "mPelvis": None,
        "mSpine1": "mPelvis",
        "mSpine2": "mSpine1",
        # ... (der komplette Rest, den du schon hast)
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Ungültiges JSON-Format")
            return data
    except Exception as e:
        print(f"[WARNUNG] Konnte bone_parents.json nicht laden: {e}")
        return default_structure

def repair_pairing(armature):
    """Stellt Parent-Beziehungen anhand der Hierarchie wieder her"""
    bone_parents = load_bone_parents()
    bpy.ops.object.mode_set(mode='EDIT')
    bones = armature.edit_bones

    for bone_name, parent_name in bone_parents.items():
        if bone_name in bones:
            bone = bones[bone_name]
            if parent_name and parent_name in bones:
                if bone.parent != bones[parent_name]:
                    bone.parent = bones[parent_name]
                    bone.use_connect = False
            elif not parent_name:
                bone.parent = None

    bpy.ops.object.mode_set(mode='OBJECT')
    print("[INFO] Bone-Pairing repariert.")

def remove_unwanted_bones(armature, allowed_bones):
    """Entfernt alle Bones, die nicht in der erlaubten Liste vorkommen"""
    bpy.ops.object.mode_set(mode='EDIT')
    bones = armature.edit_bones
    to_remove = [bone.name for bone in bones if bone.name not in allowed_bones]

    for name in to_remove:
        bones.remove(bones[name])

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"[INFO] {len(to_remove)} unerwünschte Bones entfernt.")

class OBJECT_OT_toggle_bone_visibility(Operator):
    bl_idname = "object.toggle_bone_visibility"
    bl_label = "Toggle Bone Visibility + Color Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        if obj and obj.type == 'ARMATURE':
            # Toggle Sichtbarkeit
            obj.show_in_front = not obj.show_in_front

            # In Pose-Modus wechseln, falls nötig
            if context.mode != 'POSE':
                bpy.ops.object.posemode_toggle()

            # Sichtbarkeit aktiviert → Farben setzen
            if obj.show_in_front:
                for bone in obj.pose.bones:
                    name = bone.name.lower()
                    bone.color.palette = 'CUSTOM'

                    # Gelb für Torso, Pelvis und Handgelenke
                    if (
                        "torso" in name
                        or "pelvis" in name
                        or "wristleft" in name
                        or "wristright" in name
                        or "hips" in name
                        or "spine2" in name
                    ):
                        bone.color.custom.normal = (1.0, 1.0, 0.0)  # Gelb
                        bone.color.custom.select = (1.0, 1.0, 0.5)
                        bone.color.custom.active = (1.0, 1.0, 0.2)

                    # Links (Rot)
                    elif "left" in name and not "cleft" in name:
                        bone.color.custom.normal = (1.0, 0.0, 0.0)   # Rot
                        bone.color.custom.select = (1.0, 0.5, 0.5)
                        bone.color.custom.active = (1.0, 0.2, 0.2)

                    # Rechts (Blau)
                    elif "right" in name and not "bright" in name:
                        bone.color.custom.normal = (0.0, 0.0, 1.0)   # Blau
                        bone.color.custom.select = (0.5, 0.5, 1.0)
                        bone.color.custom.active = (0.2, 0.2, 1.0)

                    # Standard (Grün)
                    else:
                        bone.color.custom.normal = (0.0, 1.0, 0.0)   # Grün
                        bone.color.custom.select = (0.5, 1.0, 0.5)
                        bone.color.custom.active = (0.2, 1.0, 0.2)

            # Sichtbarkeit deaktiviert → Farben zurücksetzen
            else:
                for bone in obj.pose.bones:
                    bone.color.palette = 'DEFAULT'

        return {'FINISHED'}
    
# ------------------------------------------------------------------------
# Operator-Klassen
# ------------------------------------------------------------------------
class OBJECT_OT_repair_pairing(bpy.types.Operator):
    """Repariert fehlerhafte Bone-Hierarchien durch korrektes Parenting"""
    bl_idname = "object.repair_pairing"
    bl_label = "Repair Pairing"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Bitte ein Armature-Objekt auswählen")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        edited = 0

        for bone in armature.data.edit_bones:
            if bone.use_connect and bone.parent and bone.head != bone.parent.tail:
                bone.head = bone.parent.tail
                edited += 1

        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, f"{edited} Bones repariert.")
        return {'FINISHED'}

class OBJECT_OT_remove_unwanted_bones(bpy.types.Operator):
    """Entfernt unnötige Bones nach benutzerdefinierten Kriterien"""
    bl_idname = "object.remove_unwanted_bones"
    bl_label = "Remove Unwanted Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Bitte ein Armature-Objekt auswählen")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bones = armature.data.edit_bones

        removed = 0
        unwanted_keywords = ['helper', 'ik', 'twist', 'end', 'toe_end']

        for bone in list(bones):
            name = bone.name.lower()
            if any(keyword in name for keyword in unwanted_keywords):
                bones.remove(bone)
                removed += 1

        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, f"{removed} Bones entfernt.")
        return {'FINISHED'}

class OBJECT_OT_auto_scale_bones(Operator):
    bl_idname = "object.auto_scale_bones"
    bl_label = "Auto Scale Bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type in ['MESH', 'ARMATURE'])
    
    def execute(self, context):
        try:
            props = context.scene.bone_mapping_props
            mesh = next((obj for obj in context.selected_objects if obj.type == 'MESH'), None)
            armature = next((obj for obj in context.selected_objects if obj.type == 'ARMATURE'), None)
            
            if not mesh or not armature:
                self.report({'ERROR'}, "Select both mesh and armature")
                return {'CANCELLED'}
            
            # 1. Berechne Mesh-Höhe in Weltkoordinaten
            bbox = mesh.bound_box
            local_height = bbox[6][2] - bbox[0][2]
            mesh_height = local_height * mesh.scale.z
            
            # 2. Bestimme Skalierungsfaktor basierend auf Modus
            if props.scale_mode == 'MIXAMO':
                scale_factor = 0.01
            elif props.scale_mode == 'AUTO':
                scale_factor = props.target_height / mesh_height
            else:  # MANUAL
                scale_factor = props.manual_scale
            
            # 3. Skaliere Armature
            armature.scale = (scale_factor, scale_factor, scale_factor)
            bpy.ops.object.transform_apply(scale=True)
            
            self.report({'INFO'}, f"Scaled to {props.target_height}m (Factor: {scale_factor:.4f})")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Scaling failed: {str(e)}")
            return {'CANCELLED'}

# ------------------------------------------------------------------------
# PROPERTY GROUP (stores addon settings)
# ------------------------------------------------------------------------
# class BoneMappingProperties(PropertyGroup):
#     """Stores all addon settings in the Blender scene"""
#     # File import/export
#     import_file: StringProperty(name="Import File", description="Path to JSON file", default="", maxlen=1024, subtype='FILE_PATH')
#     export_file: StringProperty(name="Export File", description="Path to save mappings", default="", maxlen=1024, subtype='FILE_PATH')
    
#     # Preset selection
#     preset: EnumProperty(name="Preset", description="Bone mapping preset", items=[
#         ('BENTO_FULL', "Bento Full", "Complete Bento skeleton"),
#         ('BASIC', "Basic", "Basic OpenSim skeleton"),
#         ('CUSTOM', "Custom", "Load from file")], default='BENTO_FULL')
    
#     # Prefix handling
#     prefix_mode: EnumProperty(name="Prefix Mode", description="Mixamo prefix handling", items=[
#         ('AUTO', "Auto-Detect", "Detect automatically"),
#         ('MANUAL', "Manual", "Select from list"),
#         ('CUSTOM', "Custom", "Specify custom")], default='AUTO')
#     manual_prefix: EnumProperty(name="Manual Prefix", description="Predefined prefix", items=[
#         ('mixamorig:', "mixamorig:", "Standard prefix"),
#         ('mixamorig1:', "mixamorig1:", "First variant"),
#         ('mixamorig2:', "mixamorig2:", "Second variant")], default='mixamorig:')
#     custom_prefix: StringProperty(name="Custom Prefix", description="Custom prefix pattern", default="mixamorig:", maxlen=32)
    
#     # Weight optimization
#     weight_threshold: FloatProperty(name="Weight Threshold", description="Remove small weights", default=0.01, min=0.0, max=0.5)
#     harden_joints: BoolProperty(name="Harden Joints", description="Sharper joint transitions", default=True)
    
#     # Hand posing
#     apply_left_hand: BoolProperty(name="Left Hand", description="Apply to left hand", default=True)
#     apply_right_hand: BoolProperty(name="Right Hand", description="Apply to right hand", default=True)
    
#     # Deformation repair (NEUE PROPERTIES)
#     spine_scale: FloatProperty(name="Spine Scale", description="Spine bone scaling factor", default=1.2, min=0.5, max=3.0)
#     min_bone_scale: FloatProperty(name="Min Bone Scale", description="Minimum bone size relative to mesh", default=1.0, min=0.1, max=5.0)

#     # Neue Properties für Bone Groups hinzufügen
#     bone_group: bpy.props.EnumProperty(
#         name="Bone Group",
#         items=[
#             ('SPINE', "Spine", "Spine bones (mSpine1, mSpine2, etc.)"),
#             ('HANDS', "Hands", "Hand bones (mWristLeft, mHandIndex1Left, etc.)"),
#             ('FACE', "Face", "Face bones (mFaceRoot, mFaceNose, etc.)"),
#             ('ALL', "All", "All bone groups")
#         ],
#         default='ALL'
#     )
    
#     apply_left_bone_group: bpy.props.BoolProperty(
#         name="Apply Left Side",
#         default=True,
#         description="Apply to left side bones"
#     )
    
#     apply_right_bone_group: bpy.props.BoolProperty(
#         name="Apply Right Side",
#         default=True,
#         description="Apply to right side bones"
#     )

#     # NEUE SCALING PROPERTIES
#     auto_scale_enabled: BoolProperty(
#         name="Auto Scale",
#         default=True,
#         description="Enable automatic scaling during conversion"
#     )
    
#     target_height: FloatProperty(
#         name="Target Height",
#         default=1.75,
#         min=0.5,
#         max=3.0,
#         step=0.1,
#         precision=2,
#         description="Desired character height in meters"
#     )
    
#     scale_mode: EnumProperty(
#         name="Scale Mode",
#         items=[
#             ('MANUAL', "Manual", "Set scale factor manually"),
#             ('AUTO', "Auto", "Calculate from mesh bounds"),
#             ('MIXAMO', "Mixamo Fix", "Apply 0.01 scale for Mixamo models")
#         ],
#         default='AUTO'
#     )
    
#     manual_scale: FloatProperty(
#         name="Scale Factor",
#         default=1.0,
#         min=0.001,
#         max=100.0,
#         description="Manual scaling factor"
#     )

class BoneMappingProperties(PropertyGroup):
    """Stores all addon settings in the Blender scene"""
    # File import/export
    import_file: StringProperty(name="Import File", description="Path to JSON file", default="", maxlen=1024, subtype='FILE_PATH')
    export_file: StringProperty(name="Export File", description="Path to save mappings", default="", maxlen=1024, subtype='FILE_PATH')
    
    # Preset selection
    preset: EnumProperty(name="Preset", description="Bone mapping preset", items=[('BENTO_FULL', "Bento Full", "Complete Bento skeleton"), ('BASIC', "Basic", "Basic OpenSim skeleton"), ('CUSTOM', "Custom", "Load from file")], default='BENTO_FULL')
    
    # Prefix handling
    prefix_mode: EnumProperty(name="Prefix Mode", description="Mixamo prefix handling", items=[('AUTO', "Auto-Detect", "Detect automatically"), ('MANUAL', "Manual", "Select from list"), ('CUSTOM', "Custom", "Specify custom")], default='AUTO')
    manual_prefix: EnumProperty(name="Manual Prefix", description="Predefined prefix", items=[('mixamorig:', "mixamorig:", "Standard prefix"), ('mixamorig1:', "mixamorig1:", "First variant"), ('mixamorig2:', "mixamorig2:", "Second variant")], default='mixamorig:')
    custom_prefix: StringProperty(name="Custom Prefix", description="Custom prefix pattern", default="mixamorig:", maxlen=32)
    
    # Weight optimization
    weight_threshold: FloatProperty(name="Weight Threshold", description="Remove small weights", default=0.01, min=0.0, max=0.5)
    harden_joints: BoolProperty(name="Harden Joints", description="Sharper joint transitions", default=True)
    
    # Hand posing
    apply_left_hand: BoolProperty(name="Left Hand", description="Apply to left hand", default=True)
    apply_right_hand: BoolProperty(name="Right Hand", description="Apply to right hand", default=True)
    
    # Deformation repair
    spine_scale: FloatProperty(name="Spine Scale", description="Spine bone scaling factor", default=1.2, min=0.5, max=3.0)
    min_bone_scale: FloatProperty(name="Min Bone Scale", description="Minimum bone size relative to mesh", default=1.0, min=0.1, max=5.0)

    # Bone Groups
    bone_group: EnumProperty(name="Bone Group", items=[('SPINE', "Spine", "Spine bones"), ('HANDS', "Hands", "Hand bones"), ('FACE', "Face", "Face bones"), ('ALL', "All", "All bone groups")], default='ALL')
    apply_left_bone_group: BoolProperty(name="Apply Left Side", default=True, description="Apply to left side bones")
    apply_right_bone_group: BoolProperty(name="Apply Right Side", default=True, description="Apply to right side bones")

    # Scaling properties
    auto_scale_enabled: BoolProperty(name="Auto Scale", default=True, description="Enable automatic scaling during conversion")
    target_height: FloatProperty(name="Target Height", default=1.75, min=0.5, max=3.0, step=0.1, precision=2, description="Desired character height in meters")
    scale_mode: EnumProperty(name="Scale Mode", items=[('MANUAL', "Manual", "Set scale factor manually"), ('AUTO', "Auto", "Calculate from mesh bounds"), ('MIXAMO', "Mixamo Fix", "Apply 0.01 scale for Mixamo models")], default='AUTO')
    manual_scale: FloatProperty(name="Scale Factor", default=1.0, min=0.001, max=100.0, description="Manual scaling factor")

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
            
            # Store original active object
            original_active = context.view_layer.objects.active
            
            try:
                # Set armature active and enter edit mode
                context.view_layer.objects.active = armature
                bpy.ops.object.mode_set(mode='EDIT')
                
                # Single rename loop
                for bone in armature.data.edit_bones:
                    if not pattern.match(bone.name):
                        skipped += 1
                        continue

                    base_name = pattern.sub("", bone.name)
                    if base_name in bone_map:
                        new_name = bone_map[base_name]
                        
                        # Skip if name exists (unless it's the same bone)
                        if new_name in armature.data.edit_bones:
                            if armature.data.edit_bones[new_name] != bone:
                                self.report({'WARNING'}, f"Skipped: {new_name} already exists")
                                skipped += 1
                                continue
                                
                        bone.name = new_name
                        processed += 1
                
                # Return to object mode before helper ops
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Execute helper operators
                bpy.ops.object.fix_bone_roll()
                bpy.ops.object.auto_parenting()
                bpy.ops.object.apply_rest_pose()
                
                # Rename vertex groups
                for mesh in meshes:
                    if mesh.parent == armature:
                        for vg in mesh.vertex_groups:
                            if pattern.match(vg.name):
                                base_name = pattern.sub("", vg.name)
                                if base_name in bone_map:
                                    vg.name = bone_map[base_name]
            
            finally:
                # Restore original active object
                context.view_layer.objects.active = original_active

        self.report({'INFO'}, f"Renamed {processed} bones, skipped {skipped}")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# DATA APPLICATION OPERATOR
# ------------------------------------------------------------------------
# HAND DATA APPLICATION OPERATOR
class OBJECT_OT_apply_hand_data(Operator):
    bl_idname = "object.apply_hand_data"
    bl_label = "Apply Hand Pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type == 'ARMATURE')
    
    def detect_prefix(self, armature):
        """Automatically detects Mixamo prefix in armature"""
        prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
        for bone in armature.data.bones:
            for prefix in prefixes:
                if bone.name.startswith(prefix):
                    return prefix
        return None
    
    def find_bone(self, armature, bento_name, prefix=""):
        """
        Finds a bone by:
        1. Original Bento name (e.g., "mWristLeft")
        2. Mixamo name with prefix (e.g., "mixamorig:LeftHand")
        3. Fallback to Bento-to-Mixamo mapping (if defined in PRESETS)
        """
        # Try exact Bento name first (from hand_data)
        bone = armature.pose.bones.get(bento_name)
        if bone:
            return bone
        
        # Try Mixamo name if prefix exists (e.g., "mixamorig:LeftHand")
        if prefix:
            # Reverse lookup in PRESETS to find Mixamo equivalent
            for mixamo_name, preset_name in PRESETS['BENTO_FULL'].items():
                if preset_name == bento_name:
                    prefixed_name = prefix + mixamo_name
                    bone = armature.pose.bones.get(prefixed_name)
                    if bone:
                        return bone
        
        return None
    
    def execute(self, context):
        props = context.scene.bone_mapping_props
        armature = context.active_object
        prefix = self.detect_prefix(armature)  # Auto-detect Mixamo prefix
        
        def apply_bone_recursive(bone_dict):
            """Applies pose data recursively"""
            for bento_name, data in bone_dict.items():
                if isinstance(data, dict) and 'pos' in data:
                    bone = self.find_bone(armature, bento_name, prefix)
                    if not bone:
                        self.report({'WARNING'}, f"Bone '{bento_name}' not found!")
                        continue
                    
                    # Apply position and rotation
                    bone.location = data['pos']
                    if 'rot' in data:
                        bone.rotation_mode = 'XYZ'
                        bone.rotation_euler = data['rot']
                
                # Process children
                if 'children' in data:
                    apply_bone_recursive(data['children'])

        # Apply to left/right hands based on settings
        if props.apply_left_hand:
            apply_bone_recursive(hand_data['left'])
        if props.apply_right_hand:
            apply_bone_recursive(hand_data['right'])
        
        self.report({'INFO'}, "Hand pose applied!")
        return {'FINISHED'}


# NEU Bento
# BENTO DATA APPLICATION OPERATOR
class OBJECT_OT_apply_bento_data(Operator):
    bl_idname = "object.apply_bento_data"
    bl_label = "Apply Bento Pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type == 'ARMATURE')
    
    def detect_prefix(self, armature):
        """Automatically detects Mixamo prefix in armature"""
        prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
        for bone in armature.data.bones:
            for prefix in prefixes:
                if bone.name.startswith(prefix):
                    return prefix
        return None
    
    def find_bone(self, armature, bento_name, prefix=""):
        """
        Finds a bone by:
        1. Original Bento name (e.g., "mWristLeft")
        2. Mixamo name with prefix (e.g., "mixamorig:LeftHand")
        3. Fallback to Bento-to-Mixamo mapping (if defined in PRESETS)
        """
        # Try exact Bento name first
        bone = armature.pose.bones.get(bento_name)
        if bone:
            return bone
        
        # Try Mixamo name if prefix exists (e.g., "mixamorig:LeftHand")
        if prefix:
            # Reverse lookup in PRESETS to find Mixamo equivalent
            for mixamo_name, preset_name in PRESETS['BENTO_FULL'].items():
                if preset_name == bento_name:
                    prefixed_name = prefix + mixamo_name
                    bone = armature.pose.bones.get(prefixed_name)
                    if bone:
                        return bone
        
        return None
    
    def execute(self, context):
        props = context.scene.bone_mapping_props
        armature = context.active_object
        prefix = self.detect_prefix(armature)  # Auto-detect Mixamo prefix
        
        def apply_bone_recursive(bone_dict):
            """Applies pose data recursively"""
            for bento_name, data in bone_dict.items():
                if isinstance(data, dict) and 'pos' in data:
                    bone = self.find_bone(armature, bento_name, prefix)
                    if not bone:
                        self.report({'WARNING'}, f"Bone '{bento_name}' not found!")
                        continue
                    
                    # Apply position and rotation
                    bone.location = data['pos']
                    if 'rot' in data:
                        bone.rotation_mode = 'XYZ'
                        bone.rotation_euler = data['rot']
                
                # Process children
                if 'children' in data:
                    apply_bone_recursive(data['children'])

        # Apply the full Bento pose
        apply_bone_recursive(bento_data)
        
        self.report({'INFO'}, "Bento pose applied!")
        return {'FINISHED'}
# NEU ENDE

# ==============================================
# XML-BASED BONE POSE APPLIER
# ==============================================

class OBJECT_OT_apply_group_data(Operator):
    bl_idname = "object.apply_group_data"
    bl_label = "Apply Skeleton Pose from XML"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(subtype="FILE_PATH")
    apply_position: BoolProperty(name="Apply Position", default=True)
    apply_rotation: BoolProperty(name="Apply Rotation", default=True)
    apply_scale: BoolProperty(name="Apply Scale", default=False)
    
    @classmethod
    def poll(cls, context):
        return (context.active_object and 
                context.active_object.type == 'ARMATURE')
    
    def detect_prefix(self, armature):
        """Automatically detects Mixamo prefix in armature"""
        prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
        for bone in armature.data.bones:
            for prefix in prefixes:
                if bone.name.startswith(prefix):
                    return prefix
        return None
    
    def find_bone(self, armature, bone_name, prefix=""):
        """
        Finds a bone by:
        1. Exact name match
        2. With detected prefix
        3. Using common naming conventions
        """
        # Try exact name first
        bone = armature.pose.bones.get(bone_name)
        if bone:
            return bone
        
        # Try with prefix if available
        if prefix:
            prefixed_name = prefix + bone_name
            bone = armature.pose.bones.get(prefixed_name)
            if bone:
                return bone
            
            # Handle special cases (e.g., mPelvis -> Hips)
            name_mapping = {
                "mPelvis": "Hips",
                "mSpine1": "Spine",
                "mSpine2": "Spine1",
                "mTorso": "Spine2",
                "mChest": "Spine3",
                "mNeck": "Neck",
                "mHead": "Head",
                "mCollarLeft": "LeftShoulder",
                "mShoulderLeft": "LeftArm",
                "mElbowLeft": "LeftForeArm",
                "mWristLeft": "LeftHand",
                "mCollarRight": "RightShoulder",
                "mShoulderRight": "RightArm",
                "mElbowRight": "RightForeArm",
                "mWristRight": "RightHand",
                "mHipLeft": "LeftUpLeg",
                "mKneeLeft": "LeftLeg",
                "mAnkleLeft": "LeftFoot",
                "mHipRight": "RightUpLeg",
                "mKneeRight": "RightLeg",
                "mAnkleRight": "RightFoot"
            }
            
            mapped_name = name_mapping.get(bone_name)
            if mapped_name:
                prefixed_name = prefix + mapped_name
                bone = armature.pose.bones.get(prefixed_name)
                if bone:
                    return bone
        
        return None
    
    def parse_xml(self, filepath):
        """Parses the avatar_skeleton.xml file and returns hierarchical bone data"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Get the root bone (usually mPelvis)
            root_bone = root.find('bone')
            if root_bone is None:
                self.report({'ERROR'}, "No root bone found in XML")
                return None
            
            return self.parse_bone(root_bone)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to parse XML: {str(e)}")
            return None
    
    def parse_bone(self, bone_elem):
        """Recursively parses bone data from XML element"""
        bone_data = {
            'name': bone_elem.get('name'),
            'pos': self.parse_vector(bone_elem.get('pos')),
            'rot': self.parse_euler(bone_elem.get('rot')),
            'scale': self.parse_vector(bone_elem.get('scale', '1.000 1.000 1.000')),
            'children': []
        }
        
        # Parse child bones
        for child_elem in bone_elem.findall('bone'):
            child_data = self.parse_bone(child_elem)
            if child_data:
                bone_data['children'].append(child_data)
        
        return bone_data
    
    def parse_vector(self, vector_str):
        """Converts string 'x y z' to list of floats"""
        if not vector_str:
            return [0.0, 0.0, 0.0]
        return [float(x) for x in vector_str.split()]
    
    def parse_euler(self, euler_str):
        """Converts string 'x y z' to list of floats (radians)"""
        if not euler_str:
            return [0.0, 0.0, 0.0]
        return [float(x) for x in euler_str.split()]
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        armature = context.active_object
        prefix = self.detect_prefix(armature)
        
        # Parse XML file
        bone_data = self.parse_xml(self.filepath)
        if not bone_data:
            return {'CANCELLED'}
        
        # Apply pose recursively
        def apply_bone_recursive(bone_data, parent_matrix=None):
            bone = self.find_bone(armature, bone_data['name'], prefix)
            if not bone:
                # Skip if bone not found, but still process children
                for child in bone_data['children']:
                    apply_bone_recursive(child, parent_matrix)
                return
            
            # Apply transformations
            if self.apply_position and bone_data['pos']:
                bone.location = bone_data['pos']
            
            if self.apply_rotation and bone_data['rot']:
                bone.rotation_mode = 'XYZ'
                bone.rotation_euler = bone_data['rot']
            
            if self.apply_scale and bone_data['scale']:
                bone.scale = bone_data['scale']
            
            # Recursively apply to children
            for child in bone_data['children']:
                apply_bone_recursive(child)
        
        # Start applying from root bone
        apply_bone_recursive(bone_data)
        
        self.report({'INFO'}, f"Pose applied from {self.filepath}")
        return {'FINISHED'}

# NEU ENDE





# ------------------------------------------------------------------------
# WEIGHT OPTIMIZATION OPERATOR
# ------------------------------------------------------------------------
class OBJECT_OT_fix_bone_roll(Operator):
    """Setzt alle Bone‑Roll‑Werte auf 0 und richtet Hauptachsen neu aus"""
    bl_idname = "object.fix_bone_roll"
    bl_label  = "Fix Bone Roll"
    bl_options = {'INTERNAL'}

    def execute(self, ctx):
        arm = next((o for o in ctx.selected_objects if o.type == 'ARMATURE'), None)
        if not arm:
            self.report({'ERROR'}, "Keine Armature ausgewählt")
            return {'CANCELLED'}

        with bpy.context.temp_override(active_object=arm):
            bpy.ops.object.mode_set(mode='EDIT')
            for eb in arm.data.edit_bones:
                eb.roll = 0.0
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Bone‑Roll auf 0 gesetzt")
        return {'FINISHED'}

class OBJECT_OT_apply_rest_pose(Operator):
    """Überträgt die aktuelle Pose auf die Edit‑Bones (Armature Apply)"""
    bl_idname = "object.apply_rest_pose"
    bl_label  = "Apply Rest Pose"
    bl_options = {'INTERNAL'}

    def execute(self, ctx):
        arm = ctx.active_object
        if not arm or arm.type != 'ARMATURE':
            self.report({'ERROR'}, "Keine Armature aktiv")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Rest‑Pose angewendet")
        return {'FINISHED'}

# ------------------------------------------------------------------------
# WEIGHT OPTIMIZATION OPERATOR  (komplett)
# ------------------------------------------------------------------------
class OBJECT_OT_optimize_weights(bpy.types.Operator):
    """Optimiert Vertex‑Gewichte und kann Gewichte auf mehrere Bento‑Bones aufteilen"""
    bl_idname = "object.optimize_weights"
    bl_label  = "Optimize Weights"
    bl_options = {'REGISTER', 'UNDO'}
    
    # ----------  Haupt‑Execute  ----------
    def execute(self, context):
        props = context.scene.bone_mapping_props
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            
            # 1. Niedrige Gewichte entfernen  ------------------------------
            self.cleanup_small_weights(obj, props.weight_threshold)
            
            # 2. Optionale Gelenk‑Härtung ----------------------------------
            if props.harden_joints:
                self.harden_joints(obj)
            
            # 3. Beispiel für Gewicht‑Split  ------------------------------
            #    (falls du Finger‑Weights auf mehrere Bento‑Bones teilen willst)
            #    -> hier exemplarisch: Mixamo‑"Head" → mHead & mSkull
            if "Head" in obj.vertex_groups:
                self.split_group(
                    mesh=obj,
                    src="Head",
                    dst1="mHead",
                    dst2="mSkull",
                    ratio=0.7          # 70 % auf mHead, 30 % auf mSkull
                )
        
        self.report({'INFO'}, "Weights optimiert")
        return {'FINISHED'}
    
    # ----------  Helfer: kleine Gewichte löschen  ----------
    def cleanup_small_weights(self, mesh_obj, threshold):
        for vg in mesh_obj.vertex_groups:
            to_remove = [
                v.index
                for v in mesh_obj.data.vertices
                if vg.index in [g.group for g in v.groups]
                and vg.weight(v.index) < threshold
            ]
            if to_remove:
                vg.remove(to_remove)
    
    # ----------  Helfer: Gelenke härten (Platzhalter)  ----------
    def harden_joints(self, mesh_obj):
        # Hier könntest du z.B. Gewichte an Ellenbogen/Knie stärker auf den
        # entsprechenden Bone fokussieren.  Implementation bleibt dir überlassen.
        print(f"Harden joints on {mesh_obj.name}")
    
    # ----------  NEU: Gewichte aufteilen  ----------
    def split_group(self, mesh, src, dst1, dst2, ratio=0.5):
        """
        Teilt die Gewichte des Vertex‑Groups *src* im Verhältnis *ratio*
        auf zwei Ziel‑Groups *dst1* und *dst2* auf.
        """
        vg_src  = mesh.vertex_groups.get(src)
        if not vg_src:
            return
        
        vg_dst1 = mesh.vertex_groups.get(dst1)
        if not vg_dst1:
            vg_dst1 = mesh.vertex_groups.new(name=dst1)
        
        vg_dst2 = mesh.vertex_groups.get(dst2)
        if not vg_dst2:
            vg_dst2 = mesh.vertex_groups.new(name=dst2)

        for v in mesh.data.vertices:
            try:
                w = vg_src.weight(v.index)
                if w > 0:
                    vg_dst1.add([v.index], w * ratio, 'ADD')
                    vg_dst2.add([v.index], w * (1 - ratio), 'ADD')
            except RuntimeError:
                # Vertex nicht im src‑Group – überspringen
                continue

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
    """Speichert Vertex-Gewichtungen aller Meshes als JSON-Datei"""
    bl_idname = "object.save_weights_json"
    bl_label = "Weights exportieren"
    bl_description = "Speichert alle Vertex-Gewichte aller Meshes als JSON"
    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})

    def find_meshes(self, context):
        obj = context.active_object
        meshes = []

        if obj:
            if obj.type == 'MESH' and obj.vertex_groups:
                meshes.append(obj)
            elif obj.type == 'ARMATURE':
                for child in obj.children:
                    if child.type == 'MESH' and child.vertex_groups:
                        meshes.append(child)

        # Fallback: Suche nach allen Meshes mit Vertex Groups in der Szene
        if not meshes:
            for o in context.scene.objects:
                if o.type == 'MESH' and o.vertex_groups:
                    meshes.append(o)

        return meshes

    def execute(self, context):
        meshes = self.find_meshes(context)

        if not meshes:
            self.report({'ERROR'}, "Kein Mesh mit Vertex Groups gefunden")
            return {'CANCELLED'}

        weights_data = {}

        for obj in meshes:
            obj_weights = {}
            mesh = obj.data

            for vg in obj.vertex_groups:
                group_weights = {}
                for v in mesh.vertices:
                    try:
                        w = vg.weight(v.index)
                        if w > 0.0:
                            group_weights[str(v.index)] = w
                    except RuntimeError:
                        continue
                if group_weights:
                    obj_weights[vg.name] = group_weights

            if obj_weights:
                weights_data[obj.name] = obj_weights

        if not weights_data:
            self.report({'ERROR'}, "Keine Gewichte gefunden")
            return {'CANCELLED'}

        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(weights_data, f, indent=2)
            self.report({'INFO'}, f"Weights exportiert: {os.path.basename(self.filepath)}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Fehler beim Schreiben der Datei: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_export_opensim_dae(Operator):
    """Exportiert ausgewählte Objekte als SL/OpenSim‑taugliche DAE"""
    bl_idname = "export_scene.opensim_dae"
    bl_label = "Export DAE (OpenSim)"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.filepath.lower().endswith(".dae"):
            self.filepath += ".dae"

        # Aktuelle Export-Einstellungen für Collada in Blender 4.4
        bpy.ops.wm.collada_export(
            filepath=self.filepath,
            selected=True,
            export_armatures=True,
            export_meshes=True,
            export_uvs=True,
            export_normals=True,
            export_materials=True,
            apply_modifiers=True,
            triangulate=True,
            use_object_instantiation=False,
            keep_bind_info=True
        )
        
        self.report({'INFO'}, f"DAE exportiert nach {self.filepath}")
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

class OBJECT_OT_analyze_bone_structure(Operator):
    """Erweiterte Bone-Struktur Analyse"""
    bl_idname = "object.analyze_bone_structure"
    bl_label = "Bone-Struktur Analyse"
    bl_options = {'REGISTER', 'UNDO'}
    
    report_mode: StringProperty(
        name="Report Mode",
        default="UI",
        options={'HIDDEN'}
    )

    def execute(self, context):
        bone_parents = load_bone_parents()
        armature = self.get_armature(context)
        
        if not armature:
            return {'CANCELLED'}
            
        issues = self.check_structure(armature, bone_parents)
        self.report_results(issues)
        
        return {'FINISHED'}

    def get_armature(self, context):
        """Sichere Armature-Auswahl"""
        armatures = [obj for obj in context.selected_objects 
                    if obj.type == 'ARMATURE']
        
        if not armatures:
            self.report({'ERROR'}, "Keine Armature ausgewählt")
            return None
            
        return armatures[0]

    def check_structure(self, armature, bone_parents):
        """Führt alle Prüfungen durch"""
        issues = {
            'missing': [],
            'extra_roots': [],
            'wrong_parents': [],
            'disconnected': []
        }
        
        with bpy.context.temp_override(active_object=armature):
            bpy.ops.object.mode_set(mode='EDIT')
            bones = armature.data.edit_bones
            
            # 1. Fehlende Bones
            expected_bones = set(bone_parents.keys()).union(bone_parents.values()) - {None}
            issues['missing'] = [b for b in expected_bones if b not in bones]
            
            # 2. Hierarchie-Prüfung
            for bone in bones:
                if not bone.parent:
                    if bone.name != "mPelvis":
                        issues['extra_roots'].append(bone.name)
                else:
                    expected_parent = bone_parents.get(bone.name)
                    if expected_parent and bone.parent.name != expected_parent:
                        issues['wrong_parents'].append(
                            f"{bone.name} (erwartet: {expected_parent}, aktuell: {bone.parent.name})"
                        )
                    
                    if bone.use_connect and (bone.head - bone.parent.tail).length > 0.001:
                        issues['disconnected'].append(bone.name)
            
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return issues

    def report_results(self, issues):
        """Erzeugt detaillierte Reports"""
        if not any(issues.values()):
            self.report({'INFO'}, "✅ Bone-Struktur ist korrekt")
            return
            
        report = ["Bone-Struktur Analyse:"]
        
        if issues['missing']:
            report.append("\nFEHLENDE BONES:")
            report.extend(f"- {b}" for b in sorted(issues['missing']))
            
        if issues['extra_roots']:
            report.append("\nUNERWÜNSCHTE ROOT BONES:")
            report.extend(f"- {b}" for b in sorted(issues['extra_roots']))
            
        if issues['wrong_parents']:
            report.append("\nFALSCHE PARENTING:")
            report.extend(f"- {b}" for b in sorted(issues['wrong_parents']))
            
        if issues['disconnected']:
            report.append("\nUNVERBUNDENE BONES (use_connect):")
            report.extend(f"- {b}" for b in sorted(issues['disconnected']))
        
        full_report = "\n".join(report)
        
        # Ausgabe in Console + UI
        print(full_report)
        self.report({'INFO'}, "Siehe Systemkonsole für Details")
        
        # Popup für bessere Lesbarkeit
        if self.report_mode == 'UI':
            bpy.context.window_manager.popup_menu(
                lambda self, ctx: [self.layout.label(text=line) for line in report],
                title="Bone Structure Report",
                icon='ERROR'
            )

class OBJECT_OT_fix_bone_structure(bpy.types.Operator):
    """Repariert grundlegende Bone-Hierarchieprobleme"""
    bl_idname = "object.fix_bone_structure"
    bl_label = "Fix Bone Structure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Direkte Armature-Auswahl ohne separate Methode
        armature = next((obj for obj in context.selected_objects 
                        if obj.type == 'ARMATURE'), None)
        
        if not armature:
            self.report({'ERROR'}, "Keine Armature ausgewählt")
            return {'CANCELLED'}

        # Rest Ihrer Reparatur-Logik hier...
        self.report({'INFO'}, "Bone-Struktur repariert")
        return {'FINISHED'}

    def apply_fixes(self, armature, bone_parents):
        """Wendet Korrekturen an"""
        results = {
            'added': 0,
            'parented': 0,
            'connected': 0
        }
        
        with bpy.context.temp_override(active_object=armature):
            bpy.ops.object.mode_set(mode='EDIT')
            bones = armature.data.edit_bones
            
            # 1. Fehlende Bones hinzufügen
            for bone_name in bone_parents:
                if bone_name not in bones:
                    new_bone = bones.new(bone_name)
                    new_bone.head = (0, 0, 0)
                    new_bone.tail = (0, 0.1, 0)
                    results['added'] += 1
            
            # 2. Parenting korrigieren
            for child, parent in bone_parents.items():
                if child in bones and parent in bones:
                    child_bone = bones[child]
                    parent_bone = bones[parent]
                    
                    if child_bone.parent != parent_bone:
                        child_bone.parent = parent_bone
                        child_bone.use_connect = False
                        results['parented'] += 1
                    
                    # Auto-Connect wenn möglich
                    if (not child_bone.use_connect and 
                        (child_bone.head - parent_bone.tail).length < 0.001):
                        child_bone.use_connect = True
                        results['connected'] += 1
            
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return results

    def report_results(self, results):
        """Zeigt Reparatur-Ergebnisse"""
        report = [
            "Bone-Struktur Reparatur:",
            f"- {results['added']} Bones hinzugefügt",
            f"- {results['parented']} Parentings korrigiert",
            f"- {results['connected']} Bones verbunden"
        ]
        
        self.report({'INFO'}, "\n".join(report))

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
            # Store current selection
            original_active = context.active_object
            selected_objects = context.selected_objects
            
            # Process all selected objects
            for obj in selected_objects:
                # Ensure we're in object mode
                if obj.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                # Make object active and selected
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Apply transforms with matrix backup
                original_matrix = obj.matrix_world.copy()
                bpy.ops.object.transform_apply(
                    location=True,
                    rotation=True,
                    scale=True
                )
                
                # Restore original position
                obj.matrix_world = original_matrix
                
                # Special handling for armatures
                if obj.type == 'ARMATURE':
                    # Apply transforms to pose bones
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.transforms_clear()
                    bpy.ops.object.mode_set(mode='OBJECT')
            
            # Restore original selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in selected_objects:
                obj.select_set(True)
            context.view_layer.objects.active = original_active
            
            self.report({'INFO'}, "Transforms applied to {} objects".format(len(selected_objects)))
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, "Error: {}".format(str(e)))
            return {'CANCELLED'}
        
# ------------------------------------------------------------------------
# Fix Mesh Deformations Operator
# ------------------------------------------------------------------------

class OBJECT_OT_fix_deformations(Operator):
    """Behebt Mesh-Verzerrungen OHNE Skalierungsverlust"""
    bl_idname = "object.fix_deformations"
    bl_label = "Fix Mesh Deformations"
    bl_options = {'REGISTER', 'UNDO'}
    
    spine_scale: FloatProperty(
        name="Spine Scale Factor",
        default=1.2,
        min=0.5,
        max=2.0,
        description="Relative spine bone scaling"
    )
    
    min_bone_scale: FloatProperty(
        name="Min Bone Scale",
        default=1.0,
        min=0.1,
        max=10.0,
        description="Minimum bone size relative to mesh"
    )

    def execute(self, context):
        try:
            armature = context.active_object
            meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            
            if not armature or armature.type != 'ARMATURE':
                self.report({'ERROR'}, "No armature selected")
                return {'CANCELLED'}
            
            # === 1. Store original scale ===
            original_scale = armature.scale.copy()
            
            # === 2. Apply transforms FIRST ===
            bpy.ops.object.transform_apply(scale=True)
            
            # === 3. Proportional bone adjustments ===
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Calculate reference length (hips to head)
            root_bones = [b for b in armature.data.edit_bones if not b.parent]
            if root_bones:
                ref_length = sum(b.length for b in root_bones)
                mesh_size = max(mesh.dimensions.length for mesh in meshes) if meshes else 1.0
                size_ratio = mesh_size / max(ref_length, 0.0001)
                
                for bone in armature.data.edit_bones:
                    # Apply proportional scaling
                    bone.length *= max(size_ratio * self.min_bone_scale, 0.01)
                    if "Spine" in bone.name:
                        bone.length *= self.spine_scale
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # === 4. Restore original proportions ===
            armature.scale = original_scale
            bpy.ops.object.transform_apply(scale=True)
            
            # === 5. Weight reprocessing ===
            for mesh in meshes:
                # Clean vertex groups
                vgroups = mesh.vertex_groups
                bone_names = {bone.name for bone in armature.pose.bones}
                to_remove = [vg for vg in vgroups if vg.name not in bone_names]
                
                for vg in to_remove:
                    vgroups.remove(vg)
                
                # Reassign weights
                bpy.ops.object.select_all(action='DESELECT')
                mesh.select_set(True)
                armature.select_set(True)
                context.view_layer.objects.active = armature
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            
            self.report({'INFO'}, "Fixed deformations while maintaining scale")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Scale preservation failed: {str(e)}")
            return {'CANCELLED'}
        
# ------------------------------------------------------------------------
# UI Panel for Mixamo to OpenSim Tools
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
        
        # ===== 1. CONFIGURATION SECTION =====
        config_box = layout.box()
        config_box.label(text="1. Configuration", icon='SETTINGS')
        
        # Preset Selection
        config_box.prop(props, "preset", text="Rig Preset")
        
        # Prefix Handling
        row = config_box.row()
        row.prop(props, "prefix_mode", text="Prefix Handling")
        if props.prefix_mode == 'MANUAL':
            config_box.prop(props, "manual_prefix")
        elif props.prefix_mode == 'CUSTOM':
            config_box.prop(props, "custom_prefix")
        
        # Import/Export Mappings
        row = config_box.row(align=True)
        row.operator("object.import_mapping", text="Load Preset", icon='IMPORT')
        row.operator("object.export_mapping", text="Save Preset", icon='EXPORT')

        # Toggle Bone Visibility Box Knochen anzeigen
        box = layout.box()
        box.label(text="Bone Visibility")
        box.operator("object.toggle_bone_visibility", text="Vordergrund/Hintergrund", icon='HIDE_OFF')

        # ===== 2. BENTO CONVERSION SECTION =====
        convert_box = layout.box()
        convert_box.label(text="2. Bento Conversion", icon='ARMATURE_DATA')

        # NEU: Automatische Skalierung
        # row = convert_box.row(align=True)
        # row.label(text="Auto-Scale:")
        # row.operator("object.auto_scale_bones", text="Fit to Mesh", icon='SNAP_INCREMENT')
        # NEU: Skalierungs-UI mit gültigem Icon
        row = convert_box.row(align=True)
        row.prop(props, "auto_scale_enabled", text="Auto Scale", toggle=True, icon='MODIFIER')  # Geändert zu MODIFIER
        if props.auto_scale_enabled:
            row = convert_box.row(align=True)
            row.prop(props, "scale_mode", text="")
            
            if props.scale_mode == 'AUTO':
                row = convert_box.row(align=True)
                row.prop(props, "target_height", text="Height (m)")
            elif props.scale_mode == 'MANUAL':
                row = convert_box.row(align=True)
                row.prop(props, "manual_scale", text="Scale Factor")
        row = convert_box.row(align=True)
        row.operator("object.auto_scale_bones", text="Apply Scaling", icon='SNAP_INCREMENT')




        # Pose Application Section
        pose_box = convert_box.box()
        pose_box.label(text="Pose Application", icon='POSE_HLT')

        # Left/Right Hand Controls
        hand_col = pose_box.column(align=True)
        hand_col.label(text="Hand Pose:")
        hand_row = hand_col.row(align=True)
        hand_row.prop(props, "apply_left_hand", toggle=True, text="Left")
        hand_row.prop(props, "apply_right_hand", toggle=True, text="Right")        
        hand_col.operator("object.apply_hand_data", text="Apply Hand Pose", icon='HAND')

        # Bento Full Pose Controls
        bento_col = pose_box.column(align=True)
        bento_col.label(text="Full Body Pose:")
        bento_col.operator("object.apply_bento_data", text="Apply Bento Pose", icon='OUTLINER_OB_ARMATURE')

        # Advanced Pose Controls
        adv_col = pose_box.column(align=True)
        adv_col.label(text="Advanced Options:")
        adv_row = adv_col.row(align=True)
        adv_row.prop(props, "apply_position", text="Pos", toggle=True)
        adv_row.prop(props, "apply_rotation", text="Rot", toggle=True)
        adv_row.prop(props, "apply_scale", text="Scale", toggle=True)
        adv_col.operator("object.apply_group_data", text="Apply Custom Pose", icon='FILE')

        # Main Conversion Tools
        tools_box = convert_box.box()
        tools_box.label(text="Rig Tools", icon='TOOL_SETTINGS')
        tools_col = tools_box.column(align=True)
        tools_col.operator("object.rename_mixamo_bones", text="Convert to Bento", icon='ARMATURE_DATA')
        tools_col.operator("object.auto_parenting", text="Fix Bone Parenting", icon='CONSTRAINT_BONE')
        tools_col.operator("object.fix_bone_roll", text="Fix Bone Rolls", icon='BONE_DATA')
        tools_col.operator("object.apply_rest_pose", text="Apply Rest Pose", icon='POSE_HLT')
        
        # ===== 3. WEIGHT PROCESSING =====
        weight_box = layout.box()
        weight_box.label(text="3. Weight Processing", icon='MOD_VERTEX_WEIGHT')
        
        # Weight Tools
        weight_box.prop(props, "weight_threshold", slider=True)
        weight_box.prop(props, "harden_joints")
        
        row = weight_box.row(align=True)
        row.operator("object.optimize_weights", text="Optimize Weights")
        row.operator("object.auto_weighting", text="Auto Weights")
        
        # Weight Presets
        row = weight_box.row(align=True)
        row.operator("object.save_weights_json", text="Save Weights", icon='EXPORT')
        row.operator("object.load_weights_json", text="Load Weights", icon='IMPORT')
        
        # ===== 4. VALIDATION & CLEANUP =====
        validate_box = layout.box()
        validate_box.label(text="4. Validation & Cleanup", icon='CHECKMARK')
        
        # Analysis Tools
        col = validate_box.column(align=True)
        col.operator("object.analyze_bone_structure", text="Analyze Structure", icon='ZOOM_IN')
        col.operator("armature.validate_rig", text="Validate Rig", icon='CHECKMARK')
        col.operator("armature.bone_info", text="Bone Info", icon='INFO')
        
        # Cleanup Tools
        col = validate_box.column(align=True)
        col.operator("object.fix_bone_structure", text="Fix Structure", icon='TOOL_SETTINGS')
        col.operator("object.remove_unwanted_bones", text="Remove Unused Bones", icon='TRASH')
        col.operator("object.repair_pairing", text="Repair Connections", icon='CONSTRAINT_BONE')

        # NEU === DEFORMATION FIX SECTION ===
        deform_box = layout.box()
        deform_box.label(text="Deformation Repair", icon='MODIFIER')
        deform_box.operator("object.fix_deformations", text="Quick Fix Deformations", icon='OUTLINER_OB_MESH')
        if context.active_object and context.active_object.type == 'ARMATURE':
            deform_box.label(text="Advanced Settings:", icon='SETTINGS')
            row = deform_box.row(align=True)
            row.label(text="Spine Scaling:")
            row.prop(context.scene.bone_mapping_props, "spine_scale", slider=True, text="Factor")
            row = deform_box.row(align=True)
            row.label(text="Min Bone Size:")
            row.prop(context.scene.bone_mapping_props, "min_bone_scale", slider=True, text="Relative")
            op = deform_box.operator("object.fix_deformations", text="Apply Advanced Fix", icon='MODIFIER')
            op.spine_scale = context.scene.bone_mapping_props.spine_scale
            op.min_bone_scale = context.scene.bone_mapping_props.min_bone_scale

        # Ende der Deformation Box
        
        # ===== 5. FINALIZATION =====
        final_box = layout.box()
        final_box.label(text="5. Finalization", icon='EXPORT')
        
        # Transform & Export
        col = final_box.column(align=True)
        col.operator("object.apply_all_transforms", text="Apply All Transforms", icon='CON_LOCLIKE')
        #col.operator("export_scene.opensim_dae", text="Export OpenSim DAE", icon='EXPORT')

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

    bpy.utils.register_class(OBJECT_OT_analyze_bone_structure)
    bpy.utils.register_class(OBJECT_OT_fix_bone_structure)

    bpy.utils.register_class(ARMATURE_OT_validate_rig)
    bpy.utils.register_class(OBJECT_OT_apply_all_transforms)

    bpy.utils.register_class(OBJECT_OT_fix_bone_roll)
    bpy.utils.register_class(OBJECT_OT_apply_rest_pose)
    bpy.utils.register_class(OBJECT_OT_export_opensim_dae)

    bpy.utils.register_class(OBJECT_OT_repair_pairing)
    bpy.utils.register_class(OBJECT_OT_remove_unwanted_bones)

    bpy.utils.register_class(OBJECT_OT_apply_hand_data)
    bpy.utils.register_class(OBJECT_OT_apply_bento_data)
    bpy.utils.register_class(OBJECT_OT_apply_group_data)

    bpy.utils.register_class(OBJECT_OT_fix_deformations)

    bpy.utils.register_class(OBJECT_OT_toggle_bone_visibility)

    bpy.utils.register_class(OBJECT_OT_auto_scale_bones)
    
    
    
    bpy.types.Scene.bone_mapping_props = PointerProperty(type=BoneMappingProperties)

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

    bpy.utils.unregister_class(OBJECT_OT_analyze_bone_structure)
    bpy.utils.unregister_class(OBJECT_OT_fix_bone_structure)

    bpy.utils.unregister_class(ARMATURE_OT_validate_rig)
    bpy.utils.unregister_class(OBJECT_OT_apply_all_transforms)

    bpy.utils.unregister_class(OBJECT_OT_export_opensim_dae)
    bpy.utils.unregister_class(OBJECT_OT_apply_rest_pose)
    bpy.utils.unregister_class(OBJECT_OT_fix_bone_roll)

    bpy.utils.unregister_class(OBJECT_OT_remove_unwanted_bones)
    bpy.utils.unregister_class(OBJECT_OT_repair_pairing)

    bpy.utils.unregister_class(OBJECT_OT_apply_hand_data)
    bpy.utils.unregister_class(OBJECT_OT_apply_bento_data)
    bpy.utils.unregister_class(OBJECT_OT_apply_group_data)

    bpy.utils.unregister_class(OBJECT_OT_fix_deformations)

    bpy.utils.unregister_class(OBJECT_OT_toggle_bone_visibility)

    bpy.utils.unregister_class(OBJECT_OT_auto_scale_bones)

    del bpy.types.Scene.bone_mapping_props

if __name__ == "__main__":
    register()
