'''
Created on Sep 5, 2020

@author: shan.jiang
'''
import os,database

roster_path="C:\\Users\\shan.jiang\OneDrive - University of Massachusetts Boston\\Jiang\\Courses\\MIS615\\Codes\\workspace\\EmailExtraction"

source_f=open(roster_path+"\\current_semester.txt", "r")
for line in source_f:
    username=line.split(",")[0].strip()
    stid=line.split(",")[1].strip()
    database.create_login(username,stid)
    database.grant_permission(username)
source_f.close()
