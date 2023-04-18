import os, sys, signal
import time as tm
#import serial
from datetime import date, datetime, timedelta, time
from turtle import distance
import RPi.GPIO as GPIO
from threading import Thread
from queue import Queue
from collections import deque 
import mysql.connector
import requests
import json
from fetch_device_data import get_device_data
from send_milldata import send_milldata

# import numpy as np
# from tfMiniPlus import read_data
#ser = serial.Serial("/dev/ttyS0", 115200)

# Replace this with the actual device_id you want to use
DEVICE_ID = "1"

#Database Configuration
mydb = mysql.connector.connect(
    host="localhost",
    user="coder",
    password="w24",
    database="avinashi"
)
curA = mydb.cursor(dictionary=True)#buffered=True
sql = "INSERT INTO production(katta, filltime, datetime, average) VALUES(%s, %s, %s, %s)"

# GPIO Basic setting 
GPIO.setmode(GPIO.BCM) # use GPIO numbering
GPIO.setwarnings(False)

#---------------------------------------- GPIO INPUT PINS ----------------------------------------------
# PIN Setting for Katta Button
button = 5
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button,GPIO.IN) # Is this line Required ? Check while testing

# PIN Setting for Overload
# overload = 45
# GPIO.setup(overload, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(overload,GPIO.IN)

# Galla Vibrator PIN Setting
galla_Vibrator_ON = 26
galla_Vibrator_OFF = 19
GPIO.setup(galla_Vibrator_ON,GPIO.OUT)# Hopper Vibrator Pin ON
GPIO.output(galla_Vibrator_ON,GPIO.HIGH)
GPIO.setup(galla_Vibrator_OFF,GPIO.OUT)# Hopper Vibrator Pin OFF
GPIO.output(galla_Vibrator_OFF,GPIO.HIGH)

# Hopper Vibrator PIN Setting
hopper_Vibrator_ON = 6
hopper_Vibrator_OFF = 13
GPIO.setup(hopper_Vibrator_ON,GPIO.OUT)# Hopper Vibrator Pin ON
GPIO.output(hopper_Vibrator_ON,GPIO.HIGH)
GPIO.setup(hopper_Vibrator_OFF,GPIO.OUT)# Hopper Vibrator Pin OFF
GPIO.output(hopper_Vibrator_OFF,GPIO.HIGH)


#--------------------------------------- Code to Get Counted Bag Number ---------------------------------------
counted_bag = 0   

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time




# Code
dt_in_db = '''SELECT datetime FROM production ORDER BY id DESC LIMIT 1'''
curA.execute(dt_in_db)
result = curA.fetchall()
for lstitem in result:
    for i in lstitem.items():
        rcvDate = (i[1]).date()
        print(f"Received Date from DB: {rcvDate} \n")
        
        rcvTime = (i[1]).time()
        print(f"Received Time from DB: {rcvTime}\n")
        

        Current_Date = datetime.today().date()
        Previous_Date = (datetime.today() - timedelta(days=1)).date()
        Before_Previous_Date = (datetime.today() - timedelta(days=2)).date()
        NextDay_Date = (datetime.today() + timedelta(days=1)).date()
        print(f"Current_Date is : {Current_Date} \n")
        #print(f"Previous_Date is : {Previous_Date} \n")
        #print(f"NextDay_Date is : {NextDay_Date} \n")
        
        # Check Last DB timestamp Date entry with current/today's Date
        if rcvDate == Current_Date:
            thisDay, pastDay, beforePastDay = True, False, False
            print("Last DB entry Date is Today's Date")
        elif rcvDate == Previous_Date:
            thisDay, pastDay, beforePastDay = False, True, False
            print("Last DB entry Date is Yesterday's Date")
        else:
            if rcvDate < Previous_Date or rcvDate == Before_Previous_Date:
                thisDay, pastDay, beforePastDay = False, False, True
                print("Last DB entry Date is Before Yesterday")

# Check Last DB timestamp TIME (SHIFT) entry with current/today's SHIFT TIME
morningShiftDB = is_time_between(time(7,00), time(19,00), rcvTime)
if morningShiftDB == True:
    print(f"Morning Shift (DB) = {morningShiftDB}")
# Test case when range crosses midnight
eveningShiftDB = is_time_between(time(19,00), time(7,00), rcvTime)
if eveningShiftDB == True:
    print(f"Evening Shift (DB) = {eveningShiftDB}")


# Check Today's Current SHIFT TIME 
morningShift_Today = is_time_between(time(7,00), time(19,00), datetime.now().time())
if morningShift_Today == True:
    print("Currently Shift is Morning Shift.")
# Test case when range crosses midnight
eveningShift_Today = is_time_between(time(19,00), time(7,00), datetime.now().time())
if eveningShift_Today == True:
    print("Currently Shift is Evening Shift.")



if (morningShiftDB or eveningShiftDB)==True:
    bag = '''SELECT katta FROM production ORDER BY id DESC LIMIT 1'''
    # bag = '''SELECT MAX(katta) FROM kattaTable'''
    curA.execute(bag)
    bagDB = curA.fetchall()
    #print(bagDB)
    for dictkatta in bagDB:
        for knum in dictkatta.values():
            #print(knum)
            counted_bag_DB = knum
            
if thisDay == True:
    if morningShiftDB == True:
        if morningShift_Today == True:
            counted_bag = counted_bag_DB 
        if eveningShift_Today == True:
            counted_bag = 0          
    if eveningShiftDB == True:
        if eveningShift_Today == True:
            counted_bag = counted_bag_DB        

if pastDay == True:
    if morningShiftDB == True:
        counted_bag = 0
    if eveningShiftDB == True:
        if eveningShift_Today == True:
            counted_bag = counted_bag_DB
        if morningShift_Today == True:
            counted_bag = 0

if beforePastDay == True:
    counted_bag = 0

print(f"Counted Bag Database= {counted_bag_DB} \n")
print(f"Counted Bag = {counted_bag}")

# For Display
list_5K = []
list_10K = []
list_15K = []
list_20K = []
# Variables to pass value from Katta Counter function to feeding function 'feedAlgo'
que_out1 = Queue()
#que_out2 = deque()
# que_5K= Queue()
# --------------------------------------- Katta Counter Function ----- START---------------------------------------
def katta_counter():
    global counted_bag
    
    # machineOnTime=tm.time()
    mShiftStart, eShiftStart = False, False

    if counted_bag ==0:
        startTime=tm.time()
        firstTime=tm.time()
        # startTimerFile = open("startTime.txt","w")
        # startTimerFile.write(str(startTime))
        # startTimerFile.close()
        newCount = -1
    else:

        newCount = 0
        startTime = False
        # otherTime = 1
    while True:
        #print("Entered in while loop")
        if (time(7,00,59) > datetime.now().time() >= time(7,00,00)) and mShiftStart == False:
            counted_bag = 0
            eShiftStart = False
            mShiftStart = True
            startTime = tm.time()
            newCount = -1
            # mShiftDay = datetime.now().date()
            # startTimerFile = open("startTime.txt","w")
            # startTimerFile.write(str(startTime))
            # startTimerFile.close()

        if (time(19,00,59) > datetime.now().time() >= time(19,00,00)) and eShiftStart == False:
            counted_bag = 0
            eShiftStart = True
            mShiftStart = False
            startTime = tm.time()
            newCount = -1
            # eShiftDay = datetime.now().date()

        if GPIO.input(button)==0:
            #print(f'Katta laga hua hai')
            tm.sleep(9)
        elif GPIO.input(button)==1:
            t3= tm.time()
            #print(f"Katta Out")
            tm.sleep(9)
            if GPIO.input(button)==0:
                if (tm.time()-t3)>=9.0:
                    counted_bag += 1
                    endTime=tm.time()
                    #print(f"EndTme is {endTime}")

                    if newCount == 0:
                        #print(f"New Count before increment {newCount}")
                        newCount = 1
                        #print(f"New Count when it's One ({newCount})")
                        #firstTime = endTime - 120
                        otherTime = True
                    else:
                        if newCount >= 1:
                            newCount +=1
                        #print(f"New Count after increment {newCount}")

                    kattadbtime = datetime.now()
                    if startTime:
                        firstTime=endTime-120 #use t3 instead of 120 seconds
                        fillTime=round((endTime-firstTime),2)
                        otherTime=endTime
                        average=round(((counted_bag/(endTime-firstTime))*3600),2)
                        list_5K.append(fillTime)
                        list_10K.append(fillTime)
                        list_15K.append(fillTime)
                        list_20K.append(fillTime)
                        print(f" Am3 {counted_bag} F_T {fillTime} Time {kattadbtime.strftime('%H:%M:%S')} Avg = {average}\n  L5 = {average}  L10 = {average}  L15 = {average}  L20 = {average}\n")
                        #print(f" Katta No. {counted_bag} Filling_Time {fillTime} DateTime {kattadbtime} Average = {average}")
# Comment Below 3 line if Don't want to save to Database
                        val = (counted_bag, fillTime, kattadbtime, average)
                        curA.execute(sql, val)
                        mydb.commit()
                        startTime=0
                        que_out1.put(counted_bag)
                        #que_out2.append(average)

                    elif otherTime:
                        if newCount==1:
                            firstTime=endTime-120 #use t3 instead of 120 seconds
                            fillTime=round((endTime-firstTime),2)
                            list_5K.append(fillTime)
                            list_10K.append(fillTime)
                            list_15K.append(fillTime)
                            list_20K.append(fillTime)
                            

                        else:
                            fillTime=round((endTime-otherTime),2)
                            if len(list_5K)<5:
                                list_5K.append(fillTime)
                            if len(list_5K)==5:
                                list_5K.pop(0)
                                list_5K.append(fillTime)
                            l5 = round(((len(list_5K)/(sum(list_5K)))*3600),2) # Average of Last 5 Katta

                            # Last 10 Katta List
                            if len(list_10K)<10:
                                list_10K.append(fillTime)
                            if len(list_10K)==10:
                                list_10K.pop(0)
                                list_10K.append(fillTime)
                            l10 = round(((len(list_10K)/(sum(list_10K)))*3600),2) # Average of Last 10 Katta

                            # Last 15 Katta List
                            if len(list_15K)<15:
                                list_15K.append(fillTime)
                            if len(list_15K)==15:
                                list_15K.pop(0)
                                list_15K.append(fillTime)
                            l15 = round(((len(list_15K)/(sum(list_15K)))*3600),2) # Average of Last 15 Katta

                            # Last 20 Katta List
                            if len(list_20K)<20:
                                list_20K.append(fillTime)
                            if len(list_20K)==20:
                                list_20K.pop(0)
                                list_20K.append(fillTime)
                            l20 = round(((len(list_20K)/(sum(list_20K)))*3600),2) # Average of Last 20 Katta


                        otherTime=endTime
                        if newCount>=1:
                            average=round(((newCount/(endTime-firstTime))*3600),2)
                            if newCount==1:
                                l5, l10, l15, l20 = average, average, average, average
                                # print(f" Katta No. {counted_bag} Filling_Time {fillTime} DateTime {kattadbtime} Average = {average}")
                            print(f" Am2 {counted_bag} F_T {fillTime} Time {kattadbtime.strftime('%H:%M:%S')} Avg = {average}\n  L5 = {l5}  L10 = {l10}  L15 = {l15}  L20 = {l20}\n")
                            #elif newCount>1:
                                #average=round(((newCount/(endTime-firstTime))*3600),2)
                                #print(f" Am3 {counted_bag} F_T {fillTime} Time {kattadbtime.strftime('%H:%M:%S')} Avg = {average}\n  L5 = {l5}  L10 = {l10}  L15 = {l15}  L20 = {l20}\n")
                        else:
                            average=round(((counted_bag/(endTime-firstTime))*3600),2)
                            # print(f" Katta No. {counted_bag} Filling_Time {fillTime} DateTime {kattadbtime} Average = {average}")
                            print(f" Am2 {counted_bag} F_T {fillTime} Time {kattadbtime.strftime('%H:%M:%S')} Avg = {average}\n  L5 = {l5}  L10 = {l10}  L15 = {l15}  L20 = {l20}\n")
# Comment Below 3 line if Don't want to save to Database
                        # val = (counted_bag, fillTime, kattadbtime, average)
                        # curA.execute(sql, val)
                        # mydb.commit()
                        
                        device_data = get_device_data(DEVICE_ID)
                        katta_time = kattadbtime.isoformat()
                        katta_weight = 50  # Replace this with the actual value
                        circle = device_data.get('circle')
                        feed_time = device_data.get('feed_time')
                        circle_hold = device_data.get('circle_hold')
                        # galla_clear_time = device_data.get('galla_clear_time')
                        actual_hold = device_data.get('actual_hold')
                        feedstatus = GPIO.input(hopper_Vibrator_ON)
                        if feedstatus:
                            feed_status = True
                        else:
                            feed_status - False
                        # if GPIO.input(overload)==1:
                        #     overload_status = False
                        # else:
                        #     overload_status = True
                        overload_status = False
                        response = send_milldata(katta_time, katta_weight, circle, feed_time, circle_hold, actual_hold, feed_status, overload_status)
                        print(f"Sent data to device {DEVICE_ID}: {response.status_code}")
                        
                        que_out1.put(counted_bag)
                        #que_out2.append(average)
                        #que_5K.put(3600/(sum(list_of_n_Katta)/len(list_of_n_Katta)))
                    else:
                        print(f'Katta Laga Hua HAI')
            else:
                continue
        else:
            pass
# --------------------------------------- Katta Counter Function ----- END---------------------------------------


# --------------------------------------- Feeding Function ----- START---------------------------------------
# Auto timer function to control Vibrator & Conveyar
def feeding(que1):
    print(" Feeding Function Actived.\n Waiting for 1st Katta...")
    katta_number = que1.get()
    print(" 1st Katta Received.\nFeeding Process Started.\n10 Second Wait...")
    try:
        # counter
        device_data = get_device_data(DEVICE_ID)

        initial_hold = device_data.get('initial_hold')
        # tm.sleep(initial_hold)
        print(f"Initial Hold {initial_hold} seconds")
        #if intkatta_numer) >= 1:
        while True:
            device_data = get_device_data(DEVICE_ID)

            # if GPIO.input(overload)==1:
            print("System START")
            # GPIO.output(galla_Vibrator_ON,GPIO.LOW)
            print("Galla Vibrator \t ON")
            tm.sleep(4)
            # GPIO.output(galla_Vibrator_ON,GPIO.HIGH)
            tm.sleep(4)
            circle = device_data.get('circle')
            feed_time = device_data.get('feed_time')
            circle_hold = device_data.get('circle_hold')
            galla_clear_time = device_data.get('galla_clear_time')
            actual_hold = device_data.get('actual_hold')
            # overload_hold = device_data.get('overload_hold')
            for i in range(circle):
                # if GPIO.input(overload) == 1:
                # GPIO.output(hopper_Vibrator_ON,GPIO.LOW)
                print(f"Mall ON Round no {i+1}")
                tm.sleep(2)
                # GPIO.output(hopper_Vibrator_ON,GPIO.HIGH)
                tm.sleep(feed_time)
                # GPIO.output(hopper_Vibrator_OFF,GPIO.LOW)
                print("Mall OFF")
                tm.sleep(2)
                # tm.sleep(30)
                # GPIO.output(hopper_Vibrator_OFF,GPIO.HIGH)
                tm.sleep(1)
                tm.sleep(circle_hold)
                # else:
                #     pass
            tm.sleep(galla_clear_time)
            # GPIO.output(galla_Vibrator_OFF,GPIO.LOW)
            tm.sleep(1)
        
            print("Galla Vibrator \t OFF")
            tm.sleep(2)
            # GPIO.output(galla_Vibrator_OFF,GPIO.HIGH)
            tm.sleep(2)
            print(f"All off. Actual Hold time sleep {actual_hold} seconds.r")
            tm.sleep(actual_hold)

                # else:
                #     counter_overload += 1
                #     time.sleep(2)
                #     if counter_overload>=5:
                #         print('OverLoaded So Mall off for 1200 Seconds')
                #         time.sleep(1800)
                #         counter_overload = 0
    except KeyboardInterrupt:
        print("\nStopping the script.")

# --------------------------------------- Feeding Function ----- END---------------------------------------

def exit_test():
    if sys.argv== signal.SIGINT:
        GPIO.cleanup()
        os.kill()
        raise KeyboardInterrupt


if __name__ == '__main__':
    try:
        if que_out1:
            a=que_out1
        Thread(target = katta_counter).start()
        Thread(target = feeding, args=(a,), daemon =True).start()
        # Thread(target = feeding).start()
        Thread(target = exit_test).start()
    except KeyboardInterrupt:
        GPIO.cleanup()
