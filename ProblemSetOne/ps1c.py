#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 19:55:31 2018
@author: BlairLAdams
"""

print("\033[1;31;40m >>>")
annual_salary = float(input("\033[1;34;40m Enter your starting salary: "))
portion_saved = float(input("\033[1;34;40m Enter the percent of your salary to save, as a decimal: "))


monthly_savings = (int(annual_salary) * float(portion_saved))/12
total_cost = 1000000
portion_down_payment = int(total_cost) * 0.25
semi_annual_raise = 0.07
current_savings = 0
count = 0

while current_savings <= (portion_down_payment):    
    print(current_savings, "\t", count)
    current_savings += monthly_savings
    current_savings += current_savings * (0.04/12)
    count += 1
    if(count % 6 == 0):
        monthly_savings += monthly_savings * semi_annual_raise
        print("Raise!")

print("\033[1;34;40mNumber of Months: ", count, "\n")
print("\033[1;31;40m >>>\n")