import boto3

collectionId = "vp"

rekognition = boto3.client('rekognition')

# Only needed on the first run to create a collection
response = rekognition.create_collection(
    CollectionId=collectionId
)

print(response)
