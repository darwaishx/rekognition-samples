import boto3
import json

# aws rekognition list-faces --collection-id "innovate"
# aws rekognition delete-faces --collection-id "innovate" --face-id ""

# Image
imageName = "kashif-index.jpeg"

# Read image content
with open(imageName, 'rb') as document:
    imageBytes = bytearray(document.read())

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

# Call Amazon Rekognition
response = rekognition.index_faces(
    CollectionId='innovate',
    Image={
        'Bytes': imageBytes,
    },
    ExternalImageId='KashifImran',
    MaxFaces=1,
    QualityFilter='HIGH'
)

# print(response)

with open("index-faces.json", "w") as f:
    f.write(json.dumps(response))