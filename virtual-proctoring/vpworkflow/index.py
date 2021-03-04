import boto3
import json

# aws rekognition list-faces --collection-id "innovate"
# aws rekognition delete-faces --collection-id "innovate" --face-id ""

collectionId = "vp"

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

# Only needed on the first run
# response = rekognition.create_collection(
#     CollectionId=collectionId
# )

# Image
imageNames = [{"Image": "images/kfront.jpg", "Name": "KashifImran"},
              {"Image": "images/kleft.jpg", "Name": "KashifImran"},
              {"Image": "images/kright.jpg", "Name": "KashifImran"}
              ]

for i, imageName in enumerate(imageNames):
    # Read image content
    with open(imageName["Image"], 'rb') as document:
        imageBytes = bytearray(document.read())

    # Call Amazon Rekognition
    response = rekognition.index_faces(
        CollectionId=collectionId,
        Image={
            'Bytes': imageBytes,
        },
        ExternalImageId=imageName["Name"],
        MaxFaces=1,
        QualityFilter='HIGH'
    )

    # print(response)

    with open("output/index-faces-{}.json".format(i), "w") as f:
        f.write(json.dumps(response))