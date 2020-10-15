#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright (c) 2020 ContinualAI                                               #
# Copyrights licensed under the MIT License.                                   #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 10-10-2020                                                             #
# Author: Vincenzo Lomonaco                                                    #
# E-mail: contact@continualai.org                                              #
# Website: www.continualai.org                                                 #
################################################################################

""" Tiny-Imagenet Pytorch Dataset """

import os
from torch.utils.data import Dataset
from torchvision.transforms import ToTensor
from PIL import Image
import pickle as pkl
from os.path import expanduser
from avalanche.benchmarks.datasets.core50 import CORE50_DATA


def pil_loader(path):
    # open path as file to avoid ResourceWarning
    # (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        img = Image.open(f)
        return img.convert('RGB')


class CORe50(Dataset):
    """ CORe50 Pytorch Dataset """

    def __init__(self, root=expanduser("~")+"/.avalanche/data/", train=True,
                 transform=ToTensor(), target_transform=None,
                 loader=pil_loader, download=True):

        self.train = train  # training set or test set
        self.transform = transform
        self.target_transform = target_transform
        self.root = root
        self.loader = loader

        # any scenario and run is good here since we want just to load the
        # train images and targets with no particular order
        scen = 'ni'
        run = 0
        nbatch = 8

        if download:
            self.core_data = CORE50_DATA(data_folder=root)

        print("Loading paths...")
        with open(os.path.join(root, 'paths.pkl'), 'rb') as f:
            self.paths = pkl.load(f)

        print("Loading labels...")
        with open(os.path.join(root, 'labels.pkl'), 'rb') as f:
            self.all_targets = pkl.load(f)
            self.targets = []
            for i in range(nbatch):
                self.targets += self.all_targets[scen][run][i]

        print("Loading LUP...")
        with open(os.path.join(root, 'LUP.pkl'), 'rb') as f:
            self.LUP = pkl.load(f)

        self.idx_list = []
        if train:
            for i in range(nbatch + 1):
                self.idx_list += self.LUP[scen][run][i]
        else:
            self.idx_list = self.LUP[scen][run][-1]

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target
                class.
        """

        target = self.targets[index]
        img = self.loader(
            os.path.join(
                self.root, "core50_128x128", self.paths[self.idx_list[index]]
            )
        )
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.targets)


if __name__ == "__main__":

    # this litte example script can be used to visualize the first image
    # leaded from the dataset.
    from torch.utils.data import DataLoader
    import matplotlib.pyplot as plt
    from torchvision import transforms
    import torch

    train_data = CORe50()
    dataloader = DataLoader(train_data, batch_size=1)

    for batch_data in dataloader:
        x, y = batch_data
        plt.imshow(
            transforms.ToPILImage()(torch.squeeze(x))
        )
        plt.show()
        print(x.size())
        print(len(y))
        break
