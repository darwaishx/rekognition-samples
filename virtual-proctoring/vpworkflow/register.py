import boto3
import json
from enum import Enum
from botocore.exceptions import ClientError

class FaceAngle(Enum):
    FRONT = 1
    LEFT = 2
    RIGHT = 3

class ValidationError(str, Enum):
    NO_FACE_FOUND = 'NO_FACE_FOUND'
    MORE_THAN_ONE_FACE_FOUND = 'MORE_THAN_ONE_FACE_FOUND'
    FACE_DO_NOT_MATCH = 'FACE_DO_NOT_MATCH'
    FACE_POSE_IS_NOT_CORRECT = 'FACE_POSE_IS_NOT_CORRECT'

def writeJsonFile(content, fileName):
    with open("output/" + fileName, "w") as f:
        f.write(json.dumps(content))

def readImage(imageName):
    with open(imageName, 'rb') as document:
        imageBytes = bytearray(document.read())
        return imageBytes

def compareFaces(imageBytes, compareAgainstBytes):
    # Amazon Rekognition client
    rekognition = boto3.client('rekognition')
    response = rekognition.compare_faces(
        SourceImage={
            'Bytes': compareAgainstBytes,
        },
        TargetImage={
            'Bytes': imageBytes,
        },
        # SimilarityThreshold=90,
        QualityFilter='HIGH'
        )
    # print(response)
    return response

def validateFaceAngle(face, faceAngle):
    isValid = False

    if(faceAngle == FaceAngle.FRONT):
        isValid = (face["Pose"]["Yaw"] >= -10 and face["Pose"]["Yaw"] <= 10 and face["Pose"]["Pitch"] >= -20 and face["Pose"]["Pitch"] <= 20)
    elif(faceAngle == FaceAngle.LEFT):
        isValid = (face["Pose"]["Yaw"] >= 20 and face["Pose"]["Yaw"] <= 45 and face["Pose"]["Pitch"] >= -20 and face["Pose"]["Pitch"] <= 20)
    elif(faceAngle == FaceAngle.RIGHT):
        isValid = (face["Pose"]["Yaw"] <= -20 and face["Pose"]["Yaw"] >= -45 and face["Pose"]["Pitch"] >= -20 and face["Pose"]["Pitch"] <= 20)

    return isValid

def validateResponse(response, output, faceAngle, compareAgainstImage):
    # total # of faces meeting the quality bar
    fmc = len(response["FaceMatches"])
    umc = len(response["UnmatchedFaces"])
    faceCount =  + fmc + umc

    if(faceCount == 0):
        output["ValidationErrors"].append(ValidationError.NO_FACE_FOUND)
    elif(faceCount > 1):
        output["ValidationErrors"].append(ValidationError.MORE_THAN_ONE_FACE_FOUND)
    output["TotalFaces"] = faceCount
    if(compareAgainstImage):
        output["FaceMatches"] = fmc
        output["UnmatchedFaces"] = umc

    #Obscured face
    addFacePoseValidationError = False
    for faceMatch in response["FaceMatches"]:
        f = faceMatch["Face"]
        if(compareAgainstImage):
            f["IsMatch"] = True
            f["Similarity"] = faceMatch["Similarity"]
        #Pose
        fv = validateFaceAngle(f, faceAngle)
        if fv:
            f["Pose"]["IsValid"] = True
        else:
            f["Pose"]["IsValid"] = False
            addFacePoseValidationError = True

        output["FaceDetails"].append(f)
    if(addFacePoseValidationError):
        output["ValidationErrors"].append(ValidationError.FACE_POSE_IS_NOT_CORRECT)

    if(umc > 0):
        for umFace in response["UnmatchedFaces"]:
            f = umFace
            if(compareAgainstImage):
                f["IsMatch"] = False

            #Pose
            fv = validateFaceAngle(f, faceAngle)
            if fv:
                f["Pose"]["IsValid"] = True
            else:
                f["Pose"]["IsValid"] = False
                addFacePoseValidationError = True

            output["FaceDetails"].append(f)
        if(compareAgainstImage):
            output["ValidationErrors"].append(ValidationError.FACE_DO_NOT_MATCH)
        if(addFacePoseValidationError):
            output["ValidationErrors"].append(ValidationError.FACE_POSE_IS_NOT_CORRECT)

    if(not output["ValidationErrors"]):
        output["IsValid"] = True

def validateReferenceImage(imageName, faceAngle=FaceAngle.FRONT, compareAgainstImage=None):

    output = {"IsValid": False, "ValidationErrors": [], "TotalFaces": 0, "FaceDetails": []}

    if(compareAgainstImage):
        compareAgainst = compareAgainstImage
    else:
        compareAgainst = imageName
    

    # Read image content
    imageBytes = readImage(imageName)
    compareAgainstBytes = readImage(compareAgainst)

    # Call Amazon Rekognition
    response = None

    try:
        response = compareFaces(imageBytes, compareAgainstBytes)
    except ClientError as e:
        if e.response['Error']['Code'] == "InvalidParameterException":
            # validationErrors.append(ValidationError.NO_FACE_FOUND)
            output["ValidationErrors"].append(ValidationError.NO_FACE_FOUND)
            output["IsValid"] = False

    # print(response)

    if(response):
        validateResponse(response, output, faceAngle, compareAgainstImage)
        
        writeJsonFile(response, "compare-faces.json")
        writeJsonFile(output, "register-output.json")
    else:
        writeJsonFile({}, "compare-faces.json")
        writeJsonFile(output, "register-output.json")

    return output

# output = validateReferenceImage("images/kfront-blur.png", FaceAngle.FRONT)
# output = validateReferenceImage("images/kgroup.png", FaceAngle.FRONT)
# output = validateReferenceImage("images/kright.jpg",  FaceAngle.FRONT)
# output = validateReferenceImage("images/kleft.jpg",  FaceAngle.RIGHT)

# output = validateReferenceImage("images/kfront.jpg",  FaceAngle.FRONT)
# output = validateReferenceImage("images/chris.png", FaceAngle.LEFT, "images/kfront.jpg")
# output = validateReferenceImage("images/kleft.jpg",  FaceAngle.LEFT, "images/kfront.jpg")
# output = validateReferenceImage("images/kfront-lowerfacing.jpg", FaceAngle.RIGHT, "images/kfront.jpg")
# output = validateReferenceImage("images/kright.jpg",  FaceAngle.RIGHT, "images/kfront.jpg")

# output = validateReferenceImage("images/kextremeleft.jpg",  FaceAngle.RIGHT, "images/kfront.jpg")
# output = validateReferenceImage("images/kfront-upfacing.jpg", FaceAngle.FRONT, "images/kfront.jpg")
# output = validateReferenceImage("images/bad-multiple.png", FaceAngle.FRONT, "images/kfront.jpg")

print(output["ValidationErrors"])
print(output)