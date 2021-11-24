# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:08:42 2021

@author: vlab_eye
"""

import sys, os
import numpy as np
from matplotlib import pyplot as plt


path_top = 'H:\\'

list_lv1 =[
 'C1',
 'D1'
 'Fig1',
 'Fig3',
 'Fig4',
 'FigS6',
 'OS3',
]

#%%

path_top = 'H:\\FigS6'
list_lv1 = os.listdir(path_top)

for folder in list_lv1:
    print(folder)
    print(os.listdir(os.path.join(path_top, folder)))