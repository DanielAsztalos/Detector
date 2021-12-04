import numpy as np
import torch
import torchvision

model = torchvision.models.mobilenet_v3_small(pretrained=True)
model.eval()

def detection(image):
    transforms = torchvision.transforms.Compose([
        torchvision.transforms.ToPILImage(),                                         
        torchvision.transforms.Resize((280, 280)),
        torchvision.transforms.ToTensor()
    ])

    transformed_image = transforms(image)
    transformed_image = transformed_image.reshape(1, 3, 280, 280)

    result = model(transformed_image)

    interesting_idxs = [504, 587, 673, 761, 898, 999]
    scores = result[0].detach().numpy()[interesting_idxs]

    max_idx = np.argmax(scores)
    if scores[max_idx] > 4:
        return max_idx
    else:
        return None