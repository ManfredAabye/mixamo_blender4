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
    # Core Body
    "mChest": "mTorso",
    "mHead": "mNeck",
    "mHeadTop_End": "mHead",
    "mNeck": "mChest",
    "mSpine1": "mPelvis",
    "mSpine2": "mSpine1",
    "mSpine3": "mSpine2",
    "mSpine4": "mSpine3",
    "mTorso": "mSpine4",

    # Arms Left
    "mCollarLeft": "mChest",
    "mElbowLeft": "mShoulderLeft",
    "mShoulderLeft": "mCollarLeft",
    "mWristLeft": "mElbowLeft",

    # Fingers Left
    "mHandIndex1Left": "mWristLeft",
    "mHandIndex2Left": "mHandIndex1Left",
    "mHandIndex3Left": "mHandIndex2Left",
    "mHandMiddle1Left": "mWristLeft",
    "mHandMiddle2Left": "mHandMiddle1Left",
    "mHandMiddle3Left": "mHandMiddle2Left",
    "mHandPinky1Left": "mWristLeft",
    "mHandPinky2Left": "mHandPinky1Left",
    "mHandPinky3Left": "mHandPinky2Left",
    "mHandRing1Left": "mWristLeft",
    "mHandRing2Left": "mHandRing1Left",
    "mHandRing3Left": "mHandRing2Left",
    "mHandThumb1Left": "mWristLeft",
    "mHandThumb2Left": "mHandThumb1Left",
    "mHandThumb3Left": "mHandThumb2Left",

    # Arms Right
    "mCollarRight": "mChest",
    "mElbowRight": "mShoulderRight",
    "mShoulderRight": "mCollarRight",
    "mWristRight": "mElbowRight",

    # Fingers Right
    "mHandIndex1Right": "mWristRight",
    "mHandIndex2Right": "mHandIndex1Right",
    "mHandIndex3Right": "mHandIndex2Right",
    "mHandMiddle1Right": "mWristRight",
    "mHandMiddle2Right": "mHandMiddle1Right",
    "mHandMiddle3Right": "mHandMiddle2Right",
    "mHandPinky1Right": "mWristRight",
    "mHandPinky2Right": "mHandPinky1Right",
    "mHandPinky3Right": "mHandPinky2Right",
    "mHandRing1Right": "mWristRight",
    "mHandRing2Right": "mHandRing1Right",
    "mHandRing3Right": "mHandRing2Right",
    "mHandThumb1Right": "mWristRight",
    "mHandThumb2Right": "mHandThumb1Right",
    "mHandThumb3Right": "mHandThumb2Right",

    # Legs Left
    "mAnkleLeft": "mKneeLeft",
    "mFootLeft": "mAnkleLeft",
    "mHipLeft": "mPelvis",
    "mKneeLeft": "mHipLeft",
    "mToeLeft": "mFootLeft",
    "mToeLeftEnd": "mToeLeft",

    # Legs Right
    "mAnkleRight": "mKneeRight",
    "mFootRight": "mAnkleRight",
    "mHipRight": "mPelvis",
    "mKneeRight": "mHipRight",
    "mToeRight": "mFootRight",
    "mToeRightEnd": "mToeRight",

    # Face
    "mFaceCheekLowerLeft": "mFaceRoot",
    "mFaceCheekLowerRight": "mFaceRoot",
    "mFaceCheekUpperLeft": "mFaceRoot",
    "mFaceCheekUpperRight": "mFaceRoot",
    "mFaceChin": "mFaceJaw",
    "mFaceEar1Left": "mFaceRoot",
    "mFaceEar1Right": "mFaceRoot",
    "mFaceEar2Left": "mFaceEar1Left",
    "mFaceEar2Right": "mFaceEar1Right",
    "mFaceEyeAltLeft": "mFaceRoot",
    "mFaceEyeAltRight": "mFaceRoot",
    "mFaceEyeLidLowerLeft": "mFaceRoot",
    "mFaceEyeLidLowerRight": "mFaceRoot",
    "mFaceEyeLidUpperLeft": "mFaceRoot",
    "mFaceEyeLidUpperRight": "mFaceRoot",
    "mFaceEyebrowCenterLeft": "mFaceForeheadLeft",
    "mFaceEyebrowCenterRight": "mFaceForeheadRight",
    "mFaceEyebrowInnerLeft": "mFaceForeheadLeft",
    "mFaceEyebrowInnerRight": "mFaceForeheadRight",
    "mFaceEyebrowOuterLeft": "mFaceForeheadLeft",
    "mFaceEyebrowOuterRight": "mFaceForeheadRight",
    "mFaceEyecornerInnerLeft": "mFaceRoot",
    "mFaceEyecornerInnerRight": "mFaceRoot",
    "mFaceForeheadCenter": "mFaceRoot",
    "mFaceForeheadLeft": "mFaceRoot",
    "mFaceForeheadRight": "mFaceRoot",
    "mFaceJaw": "mFaceRoot",
    "mFaceLipCornerLeft": "mFaceRoot",
    "mFaceLipCornerRight": "mFaceRoot",
    "mFaceLipLowerCenter": "mFaceRoot",
    "mFaceLipLowerLeft": "mFaceRoot",
    "mFaceLipLowerRight": "mFaceRoot",
    "mFaceLipUpperCenter": "mFaceRoot",
    "mFaceLipUpperLeft": "mFaceRoot",
    "mFaceLipUpperRight": "mFaceRoot",
    "mFaceNoseBase": "mFaceRoot",
    "mFaceNoseBridge": "mFaceRoot",
    "mFaceNoseCenter": "mFaceRoot",
    "mFaceNoseLeft": "mFaceRoot",
    "mFaceNoseRight": "mFaceRoot",
    "mFaceRoot": "mHead",
    "mFaceTeethLower": "mFaceJaw",
    "mFaceTeethUpper": "mFaceJaw",
    "mFaceTongueBase": "mFaceJaw",
    "mFaceTongueTip": "mFaceTongueBase",

    # Wings
    "mWing1Left": "mWingsRoot",
    "mWing1Right": "mWingsRoot",
    "mWing2Left": "mWing1Left",
    "mWing2Right": "mWing1Right",
    "mWing3Left": "mWing2Left",
    "mWing3Right": "mWing2Right",
    "mWing4FanLeft": "mWing4Left",
    "mWing4FanRight": "mWing4Right",
    "mWing4Left": "mWing3Left",
    "mWing4Right": "mWing3Right",
    "mWingsRoot": "mChest",

    # Tail
    "mTail1": "mPelvis",
    "mTail2": "mTail1",
    "mTail3": "mTail2",
    "mTail4": "mTail3",
    "mTail5": "mTail4",
    "mTail6": "mTail5",

    # Other
    "mGroin": "mPelvis",
}

# ------------------------------------------------------------------------
# CONTROL RIG DEFINITIONS 
# ------------------------------------------------------------------------

# control rig
c_prefix = "Ctrl_"
master_rig_names = {"master":"Master"}
spine_rig_names = {"pelvis":"Hips", "spine1":"Spine", "spine2":"Spine1", "spine3":"Spine2", "hips_free":"Hips_Free", "hips_free_helper":"Hips_Free_Helper"}
head_rig_names = {"neck":"Neck", "head":"Head"}
leg_rig_names = {"thigh_ik":"UpLeg_IK", "thigh_fk":"UpLeg_FK", "calf_ik":"Leg_IK", "calf_fk":"Leg_FK", "foot_fk":"Foot_FK", "foot_ik":"Foot_IK", "foot_snap":"Foot_Snap", "foot_ik_target":"Foot_IK_target", "foot_01":"Foot_01", "foot_01_pole":"Foot_01_Pole", "heel_out":"FootHeelOut", "heel_in":"FootHeelIn", "heel_mid":"FootHeelMid", "toes_end":"ToeEnd", "toes_end_01":"ToeEnd_01", "toes_ik":"Toe_IK", "toes_track":"ToeTrack", "toes_01_ik":"Toe01_IK", "toes_02":"Toe02", "toes_fk":"Toe_FK", "foot_roll_cursor":"FootRoll_Cursor", "pole_ik":"LegPole_IK"}
arm_rig_names = {"shoulder":"Shoulder", "arm_ik":"Arm_IK", "arm_fk":"Arm_FK", "forearm_ik":"ForeArm_IK", "forearm_fk":"ForeArm_FK", "pole_ik":"ArmPole_IK", "hand_ik":"Hand_IK", "hand_fk":"Hand_FK"}

# mixamo bone names
spine_names = {"pelvis":"Hips", "spine1":"Spine", "spine2":"Spine1", "spine3":"Spine2"}
head_names = {"neck":"Neck", "head":"Head", "head_end":"HeadTop_End"}
leg_names = {"thigh":"UpLeg", "calf":"Leg", "foot":"Foot", "toes":"ToeBase", "toes_end":"Toe_End"}
arm_names = {"shoulder":"Shoulder", "arm":"Arm", "forearm":"ForeArm", "hand":"Hand"}
fingers_type = ["Thumb", "Index", "Middle", "Ring", "Pinky"]