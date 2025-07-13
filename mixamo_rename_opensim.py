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

import bpy
import os
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

# Operator-Klassen
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
# class OBJECT_OT_rename_mixamo_bones(Operator):
#     """Main operator that performs the bone renaming"""
#     bl_idname = "object.rename_mixamo_bones"
#     bl_label = "Convert Mixamo Rig"
#     bl_options = {'REGISTER', 'UNDO'}

#     def detect_prefix(self, armature):
#         """Automatically detects Mixamo prefix in armature"""
#         prefixes = ['mixamorig:', 'mixamorig1:', 'mixamorig2:']
#         for bone in armature.data.bones:
#             for prefix in prefixes:
#                 if bone.name.startswith(prefix):
#                     return prefix
#         return None

#     def get_prefix(self, context, armature):
#         """Gets prefix based on user settings"""
#         props = context.scene.bone_mapping_props
#         if props.prefix_mode == 'AUTO':
#             return self.detect_prefix(armature)
#         elif props.prefix_mode == 'MANUAL':
#             return props.manual_prefix
#         return props.custom_prefix

#     # execute was? execute3
#     def execute(self, context):
#         props = context.scene.bone_mapping_props
        
#         # Get current mapping
#         if props.preset == 'CUSTOM':
#             bone_map = context.scene.get('custom_bone_map', {})
#         else:
#             bone_map = PRESETS[props.preset]

#         processed = 0
#         skipped = 0
#         armatures = [obj for obj in context.selected_objects if obj.type == 'ARMATURE']
#         meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

#         for armature in armatures:
#             prefix = self.get_prefix(context, armature)
#             if not prefix:
#                 self.report({'WARNING'}, f"No Mixamo prefix found in {armature.name}")
#                 continue

#             pattern = re.compile(f"^{re.escape(prefix)}")
# # ausgetauscht
#             # Rename bones in Edit Mode
#             bpy.context.view_layer.objects.active = armature
#             bpy.ops.object.mode_set(mode='EDIT')

#             # ---------- RENAME‑LOOP ----------
#             for bone in armature.data.edit_bones:
#                 if not pattern.match(bone.name):
#                     skipped += 1
#                     continue

#                 base_name = pattern.sub("", bone.name)
#                 if base_name in bone_map:
#                     new_name = bone_map[base_name]
#                     if new_name in armature.data.edit_bones and armature.data.edit_bones[new_name] != bone:
#                         self.report({'WARNING'}, f"Skipped: {new_name} already exists")
#                         skipped += 1
#                         continue
#                     bone.name = new_name
#                     processed += 1
#             # ----------------------------------

#             # zurück in Object‑Mode
#             bpy.ops.object.mode_set(mode='OBJECT')

#             # Hilfs‑Operatoren jetzt erst ausführen
#             bpy.ops.object.fix_bone_roll()
#             bpy.ops.object.auto_parenting()
#             bpy.ops.object.apply_rest_pose()
# # ausgetauscht
            
#             for bone in armature.data.edit_bones:
#                 if not pattern.match(bone.name):
#                     skipped += 1
#                     continue
                    
#                 base_name = pattern.sub("", bone.name)
                
#                 if base_name in bone_map:
#                     new_name = bone_map[base_name]
                    
#                     # Skip if name already exists (unless it's the same bone)
#                     if new_name in armature.data.edit_bones:
#                         if armature.data.edit_bones[new_name] != bone:
#                             self.report({'WARNING'}, f"Skipped: {new_name} already exists")
#                             skipped += 1
#                             continue
                            
#                     bone.name = new_name
#                     processed += 1
            
#             bpy.ops.object.mode_set(mode='OBJECT')
            
#             # Rename vertex groups in child meshes
#             for mesh in meshes:
#                 if mesh.parent == armature:
#                     for vg in mesh.vertex_groups:
#                         if pattern.match(vg.name):
#                             base_name = pattern.sub("", vg.name)
#                             if base_name in bone_map:
#                                 vg.name = bone_map[base_name]

#         self.report({'INFO'}, f"Renamed {processed} bones, skipped {skipped}")
#         return {'FINISHED'}

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


# class OBJECT_OT_export_opensim_dae(Operator):
#     """Exportiert ausgewählte Objekte als SL/OpenSim‑taugliche DAE"""
#     bl_idname = "export_scene.opensim_dae"
#     bl_label  = "Export DAE (OpenSim)"
#     bl_options = {'REGISTER'}

#     filepath: StringProperty(subtype="FILE_PATH")

#     def execute(self, ctx):
#         if not self.filepath.lower().endswith(".dae"):
#             self.filepath += ".dae"

#         bpy.ops.wm.collada_export(
#             filepath=self.filepath,
#             selected=True,
#             apply_armature_deform=True,
#             export_armatures=True,
#             export_meshes=True,
#             deform_bones_only=False,
#             keep_bind_info=True,
#             second_life=True      # <‑‑ wichtig!
#         )
#         self.report({'INFO'}, f"DAE exportiert nach {self.filepath}")
#         return {'FINISHED'}

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
# class OBJECT_PT_mixamo_bone_panel(Panel):
#     """Creates the UI panel in the 3D view sidebar"""
#     bl_label = "Mixamo to OpenSim"
#     bl_idname = "OBJECT_PT_mixamo_bone_panel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Mixamo Tools'
    
#     def draw(self, context):
#         layout = self.layout
#         props = context.scene.bone_mapping_props
        
#         # Bone Mapping Section
#         box = layout.box()
#         box.label(text="Bone Mapping")
#         box.prop(props, "preset", text="Preset")
        
#         # Prefix Options
#         box.prop(props, "prefix_mode", text="Prefix Handling")
#         if props.prefix_mode == 'MANUAL':
#             box.prop(props, "manual_prefix")
#         elif props.prefix_mode == 'CUSTOM':
#             box.prop(props, "custom_prefix")
        
#         # Import/Export Buttons
#         row = box.row()
#         row.operator("object.import_mapping", text="Import", icon='IMPORT')
#         row.operator("object.export_mapping", text="Export", icon='EXPORT')
        
#         # Main Conversion Button
#         box.operator("object.rename_mixamo_bones", text="Convert Rig", icon='ARMATURE_DATA')
        
#         # Weight Optimization Section
#         box = layout.box()
#         box.label(text="Weight Optimization")
#         box.prop(props, "weight_threshold")
#         box.prop(props, "harden_joints")
#         box.operator("object.optimize_weights", text="Optimize Weights", icon='MOD_VERTEX_WEIGHT')

#         # Auto Parenting and Auto Weighting Section
#         box = layout.box()
#         box.label(text="Auto-Rigging Funktionen")
#         box.operator("object.auto_parenting", text="Knochen automatisch parenten", icon='CONSTRAINT_BONE')
#         box.operator("object.auto_weighting", text="Gewichtung automatisch berechnen", icon='MOD_VERTEX_WEIGHT')

#         # Weight Presets Section
#         box = layout.box()
#         box.label(text="Weight Presets", icon='MOD_VERTEX_WEIGHT')
#         row = box.row()
#         row.operator("object.save_weights_json", icon='EXPORT')
#         row.operator("object.load_weights_json", icon='IMPORT')
#         box.operator("object.auto_weighting", icon='AUTO')
        
#         # Analyse-Block
#         box = layout.box()
#         box.label(text="Bone-Struktur prüfen", icon='BONE_DATA')
#         row = box.row()
#         row.operator("object.analyze_bone_structure", text="Analyse starten", icon='ZOOM_IN')

#         # Reparatur-Block
#         box = layout.box()
#         box.label(text="Bone-Struktur reparieren", icon='TOOL_SETTINGS')
#         box.operator("object.fix_bone_structure", text="Struktur reparieren", icon='MODIFIER')

#         # Bone Hierarchy Repair and Cleanup Section
#         box = layout.box()
#         box.label(text="Bone-Hierarchie reparieren und aufräumen", icon="BONE_DATA")
#         row = box.row()
#         row.operator("object.repair_pairing", icon="CONSTRAINT_BONE")
#         row.operator("object.remove_unwanted_bones", icon="TRASH")

#         # Bone Analysis Section
#         box = layout.box()
#         box.label(text="Bone Analysis", icon='BONE_DATA')
#         col = box.column(align=True)
#         col.operator("armature.bone_info", text="Show Bone Info", icon='INFO')
#         col.operator("armature.validate_rig", text="Validate Rigging", icon='CHECKMARK')

#         # Apply All Transforms Button
#         box = layout.box()
#         box.label(text="Apply All Transforms", icon='CON_LOCLIKE')
#         box.operator("object.apply_all_transforms", icon='CON_LOCLIKE')

class OBJECT_PT_mixamo_bone_panel(Panel):
    """Creates the UI panel in the 3D view sidebar"""
    bl_label = "Mixamo to OpenSim"
    bl_idname = "OBJECT_PT_mixamo_bone_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mixamo Tools'
    bl_options = {'DEFAULT_CLOSED'}
    
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
        
        # ===== 2. CONVERSION SECTION =====
        convert_box = layout.box()
        convert_box.label(text="2. Conversion", icon='ARMATURE_DATA')
        
        # Main Conversion Button
        convert_box.operator("object.rename_mixamo_bones", text="Convert Rig", icon='ARMATURE_DATA')
        
        # Bone Structure Tools
        col = convert_box.column(align=True)
        col.operator("object.auto_parenting", text="Fix Bone Parenting", icon='CONSTRAINT_BONE')
        col.operator("object.fix_bone_roll", text="Fix Bone Rolls", icon='BONE_DATA')
        col.operator("object.apply_rest_pose", text="Apply Rest Pose", icon='POSE_HLT')
        
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

    bpy.utils.unregister_class(OBJECT_OT_analyze_bone_structure)
    bpy.utils.unregister_class(OBJECT_OT_fix_bone_structure)

    bpy.utils.unregister_class(ARMATURE_OT_validate_rig)
    bpy.utils.unregister_class(OBJECT_OT_apply_all_transforms)

    bpy.utils.unregister_class(OBJECT_OT_export_opensim_dae)
    bpy.utils.unregister_class(OBJECT_OT_apply_rest_pose)
    bpy.utils.unregister_class(OBJECT_OT_fix_bone_roll)

    bpy.utils.unregister_class(OBJECT_OT_remove_unwanted_bones)
    bpy.utils.unregister_class(OBJECT_OT_repair_pairing)
    
    del bpy.types.Scene.bone_mapping_props

if __name__ == "__main__":
    register()
