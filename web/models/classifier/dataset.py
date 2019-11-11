from web.image_path.utils import absoluteFilePaths
from torchvision import transforms
from torch.utils.data import Dataset
from PIL import Image


class ClassifierDataset(Dataset):
    def __init__(self, image_folder, class_list):

        self.image_path_list = absoluteFilePaths(image_folder)
        self.label_list = []
        self.transform = transforms.Compose([
            transforms.ToTensor(),
        ])
        for p in self.image_path_list:
            for class_name in class_list:
                if class_name in p:
                    ind = class_list.index(class_name)
                    self.label_list.append(ind)

    def __len__(self):
        return len(self.image_path_list)

    def __getitem__(self, idx):
        image = Image.open(self.image_path_list[idx])
        image = self.transform(image)
        label = self.label_list[idx]
        return image,label
