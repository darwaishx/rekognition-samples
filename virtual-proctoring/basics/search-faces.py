import boto3
import json

# Image
# imageName = "image1.png"
imageName = "kashif-search.jpeg"

# Read image content
with open(imageName, 'rb') as document:
    imageBytes = bytearray(document.read())

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

# Call Amazon Rekognition
response = rekognition.search_faces_by_image(
    CollectionId='innovate',
    Image={
        'Bytes': imageBytes,
    },
    MaxFaces=5,
    FaceMatchThreshold=95,
    QualityFilter='HIGH'
)

# print(response)

with open("search-faces.json", "w") as f:
    f.write(json.dumps(response))