from torchvision import models
import torch.nn as nn


def Multiclass_classifier(n_classes):
    model = models.vgg16(pretrained=True)
    for param in model.parameters():
        param.requires_grad = False
    model.classifier[6] = nn.Sequential(
        nn.Linear(4096, 256),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(256, n_classes),
        nn.LogSoftmax(dim=1))
    return model
