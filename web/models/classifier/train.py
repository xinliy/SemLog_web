import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
import numpy as np
import visdom
import os
from random import randrange

from web.models.classifier.dataset import ClassifierDataset
from web.models.classifier.model import Multiclass_classifier

vis = visdom.Visdom()


def create_vis_figures():
    accuracy_figure = vis.line(
        X=np.array([0]),
        Y=np.array([0]),
        name='Accuracy',
        opts=dict(title="Test Accuracy",
                  xlabel='Epoch',
                  ylabel='Accuracy')
    )
    train_loss_figure=vis.line(
        X=np.array([0]),
        Y=np.array([0]),
        name='Loss',
        opts=dict(title="Train Loss",
                  xlabels='Epoch',
                  ylabel='CrossEntropyLoss')
    )
    return accuracy_figure,train_loss_figure
device = torch.device(
    "cuda") if torch.cuda.is_available() else torch.device("cpu")
criterion = nn.NLLLoss()
batch_size = 5


def train(dataset_path, class_list, num_epoch=10, test_split=0.2, model_saving_path=None, lr=0.00001):

    accuracy_figure,train_loss_figure=create_vis_figures()
    model = Multiclass_classifier(n_classes=len(class_list))
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    dataset = ClassifierDataset(dataset_path, class_list)
    dataset_length = len(dataset)
    train_length=int(dataset_length*(1-test_split))
    test_length=dataset_length-train_length
    train_dataset, test_dataset = random_split(
        dataset, (train_length,test_length))
    trainLoader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True)
    testLoader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    track_acc = []
    for epoch in range(num_epoch):
        running_loss = 0.0
        count = 0
        model.train()
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
        for n,(images, labels) in enumerate(testLoader):
            images = images.to(device)
            labels = labels.to(device)
            log_ps = model(images)
            pred = torch.max(log_ps, dim=1)[1]
            acc.extend(list(torch.eq(pred, labels)))
            if n==1:
                show_predictions_on_images(images,pred,labels)

        # Plot accuracy in visdom
        accuracy = acc.count(1) / len(acc)
        vis.line(
            X=np.array([epoch]),
            Y=np.array([accuracy]),
            win=accuracy_figure,
            name='Accuracy',
            update='append'
        )
        vis.line(
            X=np.array([epoch]),
            Y=np.array([running_loss]),
            win=train_loss_figure,
            name='Loss',
            update='append'
        )

        # Sample random images to test the model
        # random_ind=randrange(test_length)
        # sample_images,sample_labels=dataset[random_ind]
        # model.eval()
        # pred_labels=model(sample_images)
        # pred_list=','.join(class_list[i] for i in sample_pred.tolist())
        # label_list=','.join(class_list[i] for i in sample_labels.tolist())
        # vis.images(sample_images,opts={"title":"Predict:"+pred_list+os.linesep
        #                               +"True:"+label_list})



        # Save best model
        track_acc.append(accuracy)
        if max(track_acc) == accuracy and model_saving_path is not None:
            torch.save(model.state_dict(), os.path.join(
                model_saving_path, 'best_removed(%f)' % accuracy))

        print("running_loss:", running_loss)
        print('accuracy', acc.count(1) / len(acc))

def show_predictions_on_images(images,pred,labels):
    pred_list=','.join(str(i) for i in pred.tolist())
    label_list=','.join(str(i) for i in labels.tolist())
    vis.images(images,opts={"title":"Predict:"+pred_list+os.linesep
                                  +"True:"+label_list})
