from onboarding import ImageValidator, Settings, FaceAngle

iv = ImageValidator()
output = iv.validateImage("images/kfront-blur.png")

# output = iv.validateImage("images/kgroup.png")
# output = iv.validateImage("images/kgroup.png", FaceAngle.FRONT)
# output = iv.validateImage("images/kright.jpg",  FaceAngle.FRONT)

# output = iv.validateImage("images/kfront.jpg",  FaceAngle.FRONT)
# output = iv.validateImage("images/chris.png", FaceAngle.LEFT, "images/kfront.jpg")
# output = iv.validateImage("images/kleft.jpg",  FaceAngle.LEFT, "images/kfront.jpg")
# output = iv.validateImage("images/kfront-lowerfacing.jpg", FaceAngle.RIGHT, "images/kfront.jpg")
# output = iv.validateImage("images/kright.jpg",  FaceAngle.RIGHT, "images/kfront.jpg")

# output = iv.validateImage("images/kextremeleft.jpg",  FaceAngle.RIGHT, "images/kfront.jpg")
# output = iv.validateImage("images/kfront-upfacing.jpg", FaceAngle.FRONT, "images/kfront.jpg")
# output = iv.validateImage("images/bad-multiple.png", FaceAngle.FRONT, "images/kfront.jpg")

print(output["ValidationErrors"])
print(output)