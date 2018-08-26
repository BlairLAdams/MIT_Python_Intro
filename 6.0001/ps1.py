#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 19:55:31 2018

@author: BlairLAdams
"""

# import math

print("\033[1;31;47m \n >>>")
annual_salary = float(input("\033[1;34;47m Enter your starting salary: "))
portion_saved = float(input("\033[1;34;47m Enter the percent of your salary to save, as a decimal: "))
total_cost = float(input("\033[1;34;47m Enter the cost of your dream home: ​"))
semi_annual_raise = float(input("\033[1;34;47m Enter the semi­annual raise, as a decimal:​ "))
print("\033[1;31;47m >>>")


current_savings = (annual_salary * portion_saved)/12
count = 0

while current_savings <= (total_cost *.25):    
#    print(current_savings)
    current_savings += (current_savings * 0.04)
    count += 1
    if(count % 6 == 0):
        current_savings += current_savings * semi_annual_raise
#        print("raised")

print("Number of Months: ", count)