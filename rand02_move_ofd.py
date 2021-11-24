# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:39:04 2021

@author: vlab_eye
"""

import sys, os
import numpy as np
from matplotlib import pyplot as plt
import shutil


path_dir = r'H:\C1'
path_dir = r'H:\D1'
path_dir = r'H:\OS3'

for session in os.listdir(path_dir):
    print(session)
    
    path_ofd = os.path.join(path_dir, session, 'ofd')
    if os.path.isdir(path_ofd):
        if len(os.listdir(path_ofd))>0:
            fname_ofd = os.listdir(path_ofd)[0]
            print(fname_ofd)
            src = os.path.join(path_ofd, fname_ofd)
            dst = os.path.join(path_dir, session, fname_ofd)
            shutil.move(src, dst)
        else:
            print("pass")