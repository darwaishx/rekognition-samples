import boto3
import json

# Image
imageName = "images/ksearch.jpg"

# Read image content
with open(imageName, 'rb') as document:
    imageBytes = bytearray(document.read())

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

# Call Amazon Rekognition
response = rekognition.search_faces_by_image(
    CollectionId='vp',
    Image={
        'Bytes': imageBytes,
    },
    MaxFaces=10,
    FaceMatchThreshold=95,
    QualityFilter='HIGH'
)

# print(response)

with open("output/search-faces.json", "w") as f:
    f.write(json.dumps(response))