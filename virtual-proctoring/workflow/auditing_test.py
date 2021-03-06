from auditing import ImageProcessor, Settings
import json

# Image
imageName = "images/ksearch.jpg"

referenceImages = ["images/kfront.jpg"]

settings = Settings()
output = {}

ip = ImageProcessor(imageName, settings, output, referenceImages)
ip.start()

with open("output/audit.json", "w") as f:
    f.write(json.dumps(output))

