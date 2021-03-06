import boto3
import json
from threading import Thread

class Settings:

    def __init__(self):
        ''' Constructor. '''
        self.awsRegion = 'us-east-1'
        
        self.runForLabels = True
        self.minimumLabelConfidence = 80

        self.runForFaces = True
        self.faceMatchThreshold = 85
        self.maxFaceMatchResults = 20
        
        self.runForFaceSearch = False
        self.collectionId = "vp"
        self.QualityFilter = "HIGH"

        self.runForCompareFace = True

class LabelsProcessor(Thread):

    def __init__(self, imageBytes, settings, dataObject):
        ''' Constructor. '''
        Thread.__init__(self)
        self.imageBytes = imageBytes
        self.settings = settings
        self.dataObject = dataObject

    def run(self):
        try:
            rekognition = boto3.client('rekognition', region_name=self.settings.awsRegion)
            labels = rekognition.detect_labels(
                 Image={
                    'Bytes': self.imageBytes,
                },
                MinConfidence = self.settings.minimumLabelConfidence
            )

            self.dataObject['Labels'] = labels

        except Exception as e:
            #print("Failed to process labels for {}. Error: {}.".format(self.imageName, e))
            self.dataObject['Labels'] = { 'Error' : "{}".format(e)}

class FaceProcessor(Thread):

    def __init__(self, imageBytes, settings, dataObject):
        ''' Constructor. '''
        Thread.__init__(self)
        self.imageBytes = imageBytes
        self.settings = settings
        self.dataObject = dataObject

    def run(self):
        try:
            rekognition = boto3.client('rekognition', region_name=self.settings.awsRegion)
            faces = rekognition.detect_faces(
                 Image={
                    'Bytes': self.imageBytes,
                },
                Attributes=['ALL']
            )

            self.dataObject['Faces'] = faces
        except Exception as e:
            #print("Failed to process faces for {}. Error: {}.".format(self.imageName, e))
            self.dataObject['Faces'] = { 'Error' : "{}".format(e)}

class FaceSearchProcessor(Thread):

    def __init__(self, imageBytes, settings, dataObject):
        ''' Constructor. '''
        Thread.__init__(self)
        self.imageBytes = imageBytes
        self.settings = settings
        self.dataObject = dataObject
    
    def recognizeFace(self):
        rekognition = boto3.client('rekognition', region_name=self.settings.awsRegion)
        searchFacesResponse = rekognition.search_faces_by_image(
            CollectionId=self.settings.collectionId,
            Image={
                'Bytes': self.imageBytes
                },
            MaxFaces=self.settings.maxFaceMatchResults,
            FaceMatchThreshold=self.settings.faceMatchThreshold,
            QualityFilter=self.settings.QualityFilter
        )

        return searchFacesResponse

    def run(self):
        try:
            searchFacesResponse = self.recognizeFace()

            if(searchFacesResponse):
                self.dataObject['FaceSearch'] = searchFacesResponse
            else:
                self.dataObject['FaceSearch'] = {}
        except Exception as e:
            #print("Failed to process faces search for {}. Error: {}.".format(self.imageName, e))
            self.dataObject['FaceSearch'] = { 'Error' : "{}".format(e)}

class FaceCompareProcessor(Thread):

    def __init__(self, imageBytes, referenceImagesBytes, settings, dataObject):
        ''' Constructor. '''
        Thread.__init__(self)
        self.imageBytes = imageBytes
        self.referenceImagesBytes = referenceImagesBytes
        self.settings = settings
        self.dataObject = dataObject
    
    def recognizeFace(self):
        rekognition = boto3.client('rekognition', region_name=self.settings.awsRegion)
        compareFacesResponse = rekognition.compare_faces(
            SourceImage={
                'Bytes': self.referenceImagesBytes[0],
            },
            TargetImage={
                'Bytes': self.imageBytes,
            },
            # SimilarityThreshold=90,
            QualityFilter=self.settings.QualityFilter
            )

        return compareFacesResponse

    def run(self):
        try:
            compareFacesResponse = self.recognizeFace()

            if(compareFacesResponse):
                self.dataObject['FaceCompare'] = compareFacesResponse
            else:
                self.dataObject['FaceCompare'] = {}
        except Exception as e:
            #print("Failed to process faces compare for {}. Error: {}.".format(self.imageName, e))
            self.dataObject['FaceCompare'] = { 'Error' : "{}".format(e)}

class ImageProcessor:
    def __init__(self, imageName, settings, output, referenceImages):
        ''' Constructor. '''
        self.imageName = imageName
        self.settings = settings
        self.output = output
        self.referenceImages = referenceImages

    def start(self):
        # Read image content
        with open(self.imageName, 'rb') as document:
            imageBytes = bytearray(document.read())

        referenceImagesBytes = []
        if(self.referenceImages):
            for referenceImage in self.referenceImages:
                with open(referenceImage, 'rb') as document:
                    referenceImagesBytes.append(bytearray(document.read()))

        threads = []

        if(self.settings.runForLabels):
            threads.append(LabelsProcessor(imageBytes, self.settings, self.output))
        if(self.settings.runForFaces):
            threads.append(FaceProcessor(imageBytes, self.settings, self.output))
        if self.settings.runForFaceSearch:
            threads.append(FaceSearchProcessor(imageBytes, self.settings, self.output))
        if self.settings.runForCompareFace:
            threads.append(FaceCompareProcessor(imageBytes, referenceImagesBytes, self.settings, self.output))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
