import numpy as np
import torch
import torchvision

model = torchvision.models.mobilenet_v3_large(pretrained=True)
model.eval()

def detection(image, threshold=4):
    transforms = torchvision.transforms.Compose([
        torchvision.transforms.ToPILImage(),                                         
        torchvision.transforms.Resize((280, 280)),
        torchvision.transforms.ToTensor()
    ])

    transformed_image = transforms(image)
    transformed_image = transformed_image.reshape(1, 3, 280, 280)

    result = model(transformed_image)
    results = result[0].detach().numpy()

    """
        0. 504: 'coffee mug',
        1. 587: 'hammer',
        2. 673: 'mouse, computer mouse',
        3. 761: 'remote control, remote',
        4. 898: 'water bottle',
        5. 999: 'toilet tissue, toilet paper, bathroom tissue'
    """
    interesting_idxs = [504, 587, 673, 761, 898, 999]
    scores = results[interesting_idxs]

    max_idx = np.argmax(scores)

    if scores[max_idx] > threshold:
        return max_idx
    else:
        return None