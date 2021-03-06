import boto3
import json
from enum import Enum
from botocore.exceptions import ClientError

class Settings:
    def __init__(self):
        self.frontFaceMinYaw = -10
        self.frontFaceMaxYaw = 10
        self.leftFaceMinYaw = 20
        self.leftFaceMaxYaw = 45
        self.rightFaceMinYaw = -45
        self.rightFaceMaxYaw = -20
        self.MinPitch = -20
        self.MaxPitch = 20
        self.QualityFilter = "HIGH"

class FaceAngle(Enum):
    FRONT = 1
    LEFT = 2
    RIGHT = 3

class ValidationError(str, Enum):
    NO_FACE_FOUND = 'NO_FACE_FOUND'
    MORE_THAN_ONE_FACE_FOUND = 'MORE_THAN_ONE_FACE_FOUND'
    FACE_DO_NOT_MATCH = 'FACE_DO_NOT_MATCH'
    FACE_POSE_IS_NOT_CORRECT = 'FACE_POSE_IS_NOT_CORRECT'

class ImageValidator:

    def __init__(self, settings=None):
        ''' Constructor. '''
        if(settings):
            self.settings = settings
        else:
            self.settings = Settings()
    
    def writeJsonFile(self, content, fileName):
        with open("output/" + fileName, "w") as f:
            f.write(json.dumps(content))

    def readImage(self, imageName):
        with open(imageName, 'rb') as document:
            imageBytes = bytearray(document.read())
            return imageBytes

    def compareFaces(self, imageBytes, compareAgainstBytes):
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
            QualityFilter=self.settings.QualityFilter
            )
        # print(response)
        return response

    def validateFaceAngle(self, face, faceAngle):
        isValid = False

        if(faceAngle == FaceAngle.FRONT):
            isValid = (face["Pose"]["Yaw"] >= self.settings.frontFaceMinYaw
                        and face["Pose"]["Yaw"] <= self.settings.frontFaceMaxYaw
                        and face["Pose"]["Pitch"] >= self.settings.MinPitch
                        and face["Pose"]["Pitch"] <= self.settings.MaxPitch)
        elif(faceAngle == FaceAngle.LEFT):
            isValid = (face["Pose"]["Yaw"] >= self.settings.leftFaceMinYaw
                        and face["Pose"]["Yaw"] <= self.settings.leftFaceMaxYaw
                        and face["Pose"]["Pitch"] >= self.settings.MinPitch
                        and face["Pose"]["Pitch"] <= self.settings.MaxPitch)
        elif(faceAngle == FaceAngle.RIGHT):
            isValid = (face["Pose"]["Yaw"] >= self.settings.rightFaceMinYaw
                        and face["Pose"]["Yaw"] <= self.settings.rightFaceMaxYaw
                        and face["Pose"]["Pitch"] >= self.settings.MinPitch
                        and face["Pose"]["Pitch"] <= self.settings.MaxPitch)

        return isValid

    def validateResponse(self, response, output, faceAngle, compareAgainstImage):
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
            if(faceAngle):
                fv = self.validateFaceAngle(f, faceAngle)
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
                if(faceAngle):
                    fv = self.validateFaceAngle(f, faceAngle)
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

    def processImage(self, imageBytes, compareAgainstBytes, output):
    
        response = None

        try:
            response = self.compareFaces(imageBytes, compareAgainstBytes)
        except ClientError as e:
            if e.response['Error']['Code'] == "InvalidParameterException":
                output["ValidationErrors"].append(ValidationError.NO_FACE_FOUND)
                output["IsValid"] = False
        
        return response

    def validateImage(self, imageName, faceAngle=None, compareAgainstImage=None):

        output = {
            "IsValid": False,
            "ValidationErrors": [],
            "TotalFaces": 0,
            "FaceDetails": []
            }

        #Self compare if not comparing against another image
        if(compareAgainstImage):
            compareAgainst = compareAgainstImage
        else:
            compareAgainst = imageName
        
        # Read image content
        imageBytes = self.readImage(imageName)
        if(compareAgainstImage):
            compareAgainstBytes = self.readImage(compareAgainst)
        else:
            compareAgainstBytes = imageBytes

        # Call Amazon Rekognition
        response = self.processImage(imageBytes, compareAgainstBytes, output)

        if(response):
            self.validateResponse(response, output, faceAngle, compareAgainstImage)
            
            self.writeJsonFile(response, "compare-faces.json")
            self.writeJsonFile(output, "register-output.json")
        else:
            self.writeJsonFile({}, "compare-faces.json")
            self.writeJsonFile(output, "register-output.json")

        return output

class ImageIndexer:
    def __init__(self, collectionId, settings=None):
        ''' Constructor. '''
        if(settings):
            self.settings = settings
        else:
            self.settings = Settings()

        self.collectionId = collectionId

    def indexImages(self, imageNames):
        for i, imageName in enumerate(imageNames):
            # Read image content
            with open(imageName["Image"], 'rb') as document:
                imageBytes = bytearray(document.read())

            # Call Amazon Rekognition
            rekognition = boto3.client('rekognition')
            response = rekognition.index_faces(
                CollectionId=self.collectionId,
                Image={
                    'Bytes': imageBytes,
                },
                ExternalImageId=imageName["Name"],
                MaxFaces=1,
                QualityFilter=self.settings.QualityFilter
            )

            # print(response)

            with open("output/index-faces-{}.json".format(i), "w") as f:
                f.write(json.dumps(response))