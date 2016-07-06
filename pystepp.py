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
#camera = picamera.PiCamera()

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
        time.sleep(0.01)#0.001 pretty good
    return
    
def enableMotor(motorZustand):#schaltet den Easy Driver an und aus
    if motorZustand:
        gpio.output(25, True)
    else:
        gpio.output(25, False)
    return

def AnzahlFotosToSteps(AnzahlFotos):#Berechnung der Anzahl der Schritte aus Anzahl der Fotos
#Steppermotor hat 1.8 Degree per Step
#Microstepping 1/8 Schritte an 
#Also 200 volle Steps /1600 Microsteps fuer 360 Grad 
    AnzahlSteps = int(1600/AnzahlFotos) #1600 Wegen Microstepping
    AnzahlSteps = int(1600/AnzahlFotos) #neuer Wert Wegen anderen Pulleys
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
    return fullDir
    
def getStepsforRevolution():
    Schritter = 0
    print('Schritter starten? (y/n)')
    
    while raw_input('Name des Scans: ')=='y':
        Stepper = raw_input('Wieviele Schritte?')
        print('Schritter: ', Schritter)
        bauffer = int(Stepper)
        moveStepper(bauffer)
        Schritter +=(int(stepper))
        print('Weitere Schritte gehen?(y/n)')
        
    return 

def setupCamera(lighting):#setzt die Parameter der Cam
    print('Kamera wird vorgewärmt')
    time.sleep(2)
    print('Kamera fertig. Einstellungen werden gespeichert')
    
    overExposerValue = 1000
    
    camera.resolution = (2592, 1944)#5Megapixel Aufloesung - volle Aufloesung
    
    camera.sharpness = 0
    camera.contrast = 0
    camera.brightness = 50
    camera.saturation = 0
    
    if lighting:#Gute Lichtverhaeltnisse
        camera.iso = 200 
        
        bufferAll = camera.exposure_speed
        bufferAll = int(bufferAll) + overExposerValue
        camera.shutter_speed = int(bufferAll)
        
        
    else:#schlechte lichverhaeltnisse
        camera.iso = 800
        camera.shutter_speed = 2000000 #2Sekunden verschlusszeit
        
    camera.exposure_mode = 'off'
    whiteBalanceBuffer = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = whiteBalanceBuffer
    
    return

#========================================================================
#Parameter vom User erfragen
#========================================================================

try: #Variablen ins Programm uebergeben
    AnzahlFotos = int(sys.argv[1])
except: #oder im Programm abfragen
    print ('Keine Perimeter angegeben. Bitte Anzahl der Fotos angeben')
    AnzahlFotos = input("Anzahl der Fotos: ")
    
#========================================================================
#MAIN
#========================================================================

direction = 'right'

#Richtung festlegen GPIO = 23
if str(direction) == 'left':
    gpio.output(23, True)
elif str(direction) == 'right':
    gpio.output(23, False)

#Variablen
AnzahlSteps = 0
moveCounter = 0
licht = True #True = hell /False = Dunkel Wird durch lichtsensor überprüft

AnzahlSteps = AnzahlFotosToSteps(AnzahlFotos)

enableMotor(False)

#dirPfad = raw_input('dirPfad: ')
dirPfad = '/home/pi/RaspiCode/'
dirName = raw_input('Name des Scans: ')
speicherPfad = makeDirectory(dirPfad, dirName)
print('Ganzer Pfad: ', speicherPfad)

#setupCamera(licht)
enableMotor(True)#Easydriver vor Bewegung anschalten
getStepsforRevolution()
while moveCounter < AnzahlFotos:
    moveStepper (AnzahlSteps)
    print ('Schritt: ', moveCounter)
    moveCounter +=1
    
    #camera.led = True
    #camera.start_preview(alpha=128, fullscreen=True)
    time.sleep(2) #Wartezeit zwischen den einzelnen Fotos
    #Fotoaufnehmen(moveCounter, speicherPfad, dirName)
    #camera.led = False


enableMotor(False) #Schaltet den Easydriver vor Ende des Programms aus

raw_input('Motor Sleep')#wait for any key

#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()
#camera.close()





#ENDE