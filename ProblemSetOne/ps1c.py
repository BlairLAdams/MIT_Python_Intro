#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 19:55:31 2018
@author: BlairLAdams
"""

print("\033[1;31;40m >>>")
annual_salary = float(input("\033[1;34;40m Enter your starting salary: "))
portion_saved = float(input("\033[1;34;40m Enter the percent of your salary to save, as a decimal: "))

months_per_year = 12
semi_annual_count = months_per_year / 2
monthly_savings = (int(annual_salary) * float(portion_saved))/months_per_year
investment_return_rate = 0.04
total_cost = 1000000
down_payment = total_cost * 0.25
semi_annual_raise = 0.07
current_savings = 0
count = 0

while current_savings <= (down_payment):    
#   print(current_savings, "\t", count)
    current_savings += monthly_savings
    current_savings += current_savings * (investment_return_rate/months_per_year)
    count += 1
    if(count % semi_annual_count == 0):
        monthly_savings += monthly_savings * semi_annual_raise
#       print("Raise!")

print("\033[1;34;40m Number of Months: ", count, "\n")
print("\033[1;31;40m >>>\n")