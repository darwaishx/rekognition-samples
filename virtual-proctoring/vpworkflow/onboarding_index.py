from onboarding import ImageIndexer

collectionId = "vp"

# aws rekognition list-faces --collection-id "innovate"
# aws rekognition delete-faces --collection-id "innovate" --face-id ""

# Only needed on the first run to create a collection
# response = rekognition.create_collection(
#     CollectionId=collectionId
# )

# Image
imageNames = [{"Image": "images/kfront.jpg", "Name": "KashifImran"},
              {"Image": "images/kleft.jpg", "Name": "KashifImran"},
              {"Image": "images/kright.jpg", "Name": "KashifImran"}
              ]

imageIndexer = ImageIndexer(collectionId)
imageIndexer.indexImages(imageNames)