#!/Users/BlairLAdams/anaconda3/bin/python
# -*- coding: utf-8 -*-

"""
Created on Wed Dec 16 9:09:00 2018
@author: BlairLAdams
"""

s = input('Please enter a string: ')

i = 0
for i in range(0, len(s),2):
    print(s[i].upper())
i += 2