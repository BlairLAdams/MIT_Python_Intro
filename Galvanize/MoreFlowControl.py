#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Dec 15 19:44:00 2018
@author: BlairLAdams
"""

hours = 0
while hours < 24:
    minutes = 0              # Reset minutes to 0 before entering the loop!
    while minutes < 60:
        seconds = 0
        while seconds < 60:  # Reset seconds to 0 before entering the loop!
            print(hours, minutes, seconds)  # Display the time
            seconds += 1
        minutes += 1
    hours += 1
print(hours, minutes, seconds)