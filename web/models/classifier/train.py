import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import numpy as np
import visdom
import os

from web.models.classifier.dataset import ClassifierDataset
from web.models.classifier.model import Multiclass_classifier

vis = visdom.Visdom()
accuracy_figure = vis.line(
    X=np.array([0]),
    Y=np.array([0]),
    name='Accuracy',
    opts=dict(title="Test Accuracy")
)
device = torch.device(
    "cuda") if torch.cuda.is_available() else torch.device("cpu")
criterion = nn.NLLLoss()
batch_size = 20


def train(dataset_path, class_list, num_epoch=10, test_split=0.2, model_saving_path=None, lr=0.0001):
    model = Multiclass_classifier(n_classes=len(class_list))
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    dataset = ClassifierDataset(dataset_path, class_list)
    dataset_length = len(dataset)
    train_dataset, test_dataset = random_split(
        dataset, (dataset_length * (1 - test_split), dataset_length * test_split))
    trainLoader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True)
    testLoader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    track_acc = []
    for epoch in range(num_epoch):
        running_loss = 0.0
        count = 0
        for images, labels in trainLoader:
            images = images.to(device)

            output = model(images)
            labels = labels.to(device)
            loss = criterion(output, labels)
            loss.backward()
            # print(loss)
            optimizer.step()
            count = count + 1
            running_loss += loss.item()
        print('training done in epoch:', epoch)
        print('testing model')

        acc = []
        for images, labels in testLoader:
            images = images.to(device)
            labels = labels.to(device)
            log_ps = model(images)
            pred = torch.max(log_ps, dim=1)[1]
            acc.extend(list(torch.eq(pred, labels)))
        accuracy = acc.count(1) / len(acc)

        # Plot accuracy in visdom
        vis.line(
            X=np.array([epoch]),
            Y=np.array([accuracy]),
            win=accuracy_figure,
            name='Accuracy',
            update='append'
        )

        track_acc.append(accuracy)
        if max(track_acc) == accuracy and model_saving_path is not None:
            torch.save(model.state_dict(), os.path.join(
                model_saving_path, 'best_removed(%f)' % accuracy))

        print("running_loss:", running_loss)
        print('accuracy', acc.count(1) / len(acc))
