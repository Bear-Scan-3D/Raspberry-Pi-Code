#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as gpio
import time
import picamera
import os
from datetime import datetime, timedelta

#=======================================================================
#Initialisierungen
#=======================================================================

#GPIO Vorbereitung
gpio.setmode(gpio.BCM)

gpio.setup(23, gpio.OUT) #Dir
gpio.setup(24, gpio.OUT) #Step
gpio.setup(25, gpio.OUT) #enable pin

#Kamera initialisieren
camera = picamera.PiCamera()

#========================================================================
#Funktionen
#========================================================================

def moveStepper(steps):#bewegt den Motor x(steps) Schritte
    #Schrittzaehler initialisieren
    StepCounter = 0
    while StepCounter<steps:
        #einmaliger Wechsel zwischen an und aus = Easydriver macht einen (Mirco-)Step
        gpio.output(24, True)
        gpio.output(24, False)
        StepCounter += 1
        
        #wartezeit Bestimmt die Geschwindigkeit des Steppermotors
        time.sleep(0.0005)#0.001 pretty good
    return
    
def enableMotor(motorZustand):#schaltet den Easy Driver an und aus
    if motorZustand:
        gpio.output(25, True)
        print('Motor AN')
    else:
        gpio.output(25, False)
        print('Motor AUS')
    return

def AnzahlFotosToSteps(AnzahlFotos):#Berechnung der Anzahl der Schritte aus Anzahl der Fotos
#Steppermotor hat 1.8 Degree per Step
#Microstepping 1/8 Schritte an 
#Also 200 volle Steps /1600 Microsteps fuer 360 Grad 
    AnzahlSteps = int(1600/AnzahlFotos) #1600 Wegen Microstepping
    print ('AnzahlSteps: ', AnzahlSteps)
    return AnzahlSteps

def Fotoaufnehmen (indx, fotoPfad, scanName):#nimmt ein Foto mit der PiCam auf
    print('index: ', indx, 'FotoPfad: ', fotoPfad)
    camera.capture(str(fotoPfad)+ '/'+ str(scanName)+ '_'+ str(indx)+ '.jpg')
    print('Foto '+ str(indx)+ 'aufgenommen: ')#+ {timestamp:%Y-%m-%d-%H-%M})
    return 
    
def makeDirectory(dirPfad, dirName):#macht ein verzeichnis
    fullDir = dirPfad + dirName
    if not os.path.exists(fullDir):
        os.makedirs(fullDir)
    print('Existiert nun der Pfad: ',str(os.path.exists(fullDir))) 
    return fullDir

def setupCamera():#setzt die Parameter der Cam
    camera.resolution = (2592, 1944)#5Megapixel Aufloesung - volle Aufloesung
    print('ISO-PRE: ', camera.iso)
    camera.iso = 100 
    print('ISO-AFTER: ', camera.iso)
    bufferAll = camera.exposure_speed
    print('Shutter-PRE: ', bufferAll)
    camera.shutter_speed = int(bufferAll)
    print('Shutter-AFTER: ', bufferAll)
    
    
    
    #ISO etwas höher stellen als Auto damit overexposed und bessere scans?
    #if lighting:
    #    print('gute Lichtverhältnisse')
    #else:
    #    print('schlechte Lichtverhältnisse')
    #    camera.iso = 800
    #camera.start_preview()
    return
#========================================================================
#Parameter vom User erfragen
#========================================================================

try: #Variablen ins Programm uebergeben
    AnzahlFotos = int(sys.argv[1])
    direction = 'right'
    #speed = int(sys.argv[2])
except: #oder im Programm abfragen
    print ('Keine Perimeter angegeben. Bitte Anzahl der Fotos angeben')
    #direction = raw_input("Richtung: ")#weil man sonst alles mit " " angeben muss
    direction = 'right'
    #raw_input("Press Enter to continue...")#wait for any key
    AnzahlFotos = input("Anzahl der Fotos: ")
    #speed = input("Speed:")
    print("dir= %s AnzahlFotos %s") % (direction, AnzahlFotos)
    
#========================================================================
#MAIN
#========================================================================

#Richtung festlegen GPIO = 23
if str(direction) == 'left':
    gpio.output(23, True)
elif str(direction) == 'right':
    gpio.output(23, False)

#Variablen
AnzahlSteps = 0
moveCounter = 0

AnzahlSteps = AnzahlFotosToSteps(AnzahlFotos)

#dirPfad = raw_input('dirPfad: ')
dirPfad = '/home/pi/RaspiCode/'
dirName = raw_input('Name des Scans: ')
speicherPfad = makeDirectory(dirPfad, dirName)
print('Ganzer Pfad:', speicherPfad)

enableMotor(True)#Easydriver vor Bewegung anschalten

while moveCounter < AnzahlFotos:
    moveStepper (AnzahlSteps)
    print ("Schritt:", moveCounter)
    moveCounter +=1
    #Fotoaufnehmen (moveCounter)
    camera.led = True
    camera.start_preview(alpha=128, fullscreen=True)
    time.sleep(2) #Wartezeit zwischen den einzelnen Fotos
    setupCamera()
    Fotoaufnehmen(moveCounter, speicherPfad, dirName)
    camera.led = False
    #camera.stop_preview()
    
enableMotor(False) #Schaltet den Easydriver vor Ende des Programms aus

raw_input("Teste Sleep...")#wait for any key

#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()
camera.close()


print ("Programm beendet.")






#ENDE