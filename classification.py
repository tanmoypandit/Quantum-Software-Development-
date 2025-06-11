#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 20:06:30 2021

@author: jader
"""

import math
import numpy as np

def distance(a, b):
    return math.sqrt((np.real(a) - np.real(b))**2 + (np.imag(a) - np.imag(b))**2)

def classify_v1(point: complex, mean_gnd, mean_exc):
    """Classify the given state as |0> or |1>."""
    return int(distance(point, mean_exc) < distance(point, mean_gnd))


def classify_v2(point: complex, dis_fac, mean_gnd, mean_exc):  # dis_fac stands for distance factor
    #
    x_p = np.real(point) 
    y_p = np.imag(point) 
    x_gnd = np.real(mean_gnd)                 # When dis_fac = 1 we get the distance between the two averages    
    y_gnd = np.imag(mean_gnd) 
    x_exc = np.real(mean_exc) 
    y_exc = np.imag(mean_exc) 
    #
    xm = (x_exc+x_gnd)/2
    ym = (y_exc+y_gnd)/2
    a = (y_exc-y_gnd)/(x_exc-x_gnd)
    b = (y_exc+y_gnd)/2 - ((y_exc-y_gnd)/(x_exc-x_gnd)) * (x_exc+x_gnd)/2
    cte_x = (1/2 * distance(mean_exc, mean_gnd) / np.sin( np.arctan(-a) ) )
    #
    if y_exc > y_gnd: 
        #
        y_exc = (-1/a) * x_p + 1/a * (ym+xm - a * (xm-ym) - b) + dis_fac * cte_x
        y_gnd = (-1/a) * x_p + 1/a * (ym+xm - a * (xm-ym) - b) - dis_fac * cte_x 
        #
        if y_p < y_gnd:
            res = 0    
        elif y_p > y_exc:
            res = 1
        else: 
            res = ValueError
    elif y_exc < y_gnd:          
        y_gnd = (-1/a) * x_p + 1/a * (ym+xm - a * (xm-ym) - b) + dis_fac * cte_x 
        y_exc = (-1/a) * x_p + 1/a * (ym+xm - a * (xm-ym) - b) - dis_fac * cte_x
        if y_p > y_gnd:
            res = 0    
        elif y_p < y_exc:
            res = 1
        else: 
            res = ValueError
    else: 
        res = ValueError
    return res 





def classify_v3(point: complex, dis_fac, mean_gnd, mean_exc):  
    #
    raio = dis_fac * distance(mean_exc, mean_gnd)
    #
    #
    #
    dg = distance(point, mean_gnd)
    de = distance(point, mean_exc)
    #
    #
    if dg < raio and de < raio: 
        res = ValueError
    elif dg < raio and de > raio: 
        res = 0
    elif dg > raio and de < raio: 
        res = 1
    elif dg < de:
        res = 0
    elif dg > de:    
        res = 1
    else: 
        res = print('ERROR')
    return res 