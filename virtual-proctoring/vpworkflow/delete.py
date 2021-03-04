import boto3
import json

# aws rekognition list-faces --collection-id "innovate"
# aws rekognition delete-faces --collection-id "innovate" --face-id ""

collectionId = "vp"

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

response = rekognition.list_faces(
    CollectionId=collectionId
)

listOfFaces = []
for face in response["Faces"]:
    listOfFaces.append(face["FaceId"])
print("Face list\n==========")
print(listOfFaces)

if(listOfFaces):
    response = rekognition.delete_faces(
        CollectionId=collectionId,
        FaceIds=listOfFaces
    )

response = rekognition.list_faces(
    CollectionId=collectionId
)

print("Clear faces output\n==========")
print(response)