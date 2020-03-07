# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 18:27:48 2019

@author: Luz
"""

import numpy as np
import matplotlib.pyplot as plt


Inv=30000
flujo_E=np.random.normal(8000,500,(1000,1))
flujo_E
tasa_D=0.08
VPN=np.pv(tasa_D, range(1, 6), 0, -flujo_E).sum(axis=1, keepdims=True) - Inv
plt.hist(VPN, bins=20)
RN=(VPN < 0).mean()
RN
