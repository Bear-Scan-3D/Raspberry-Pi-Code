#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as gpio
import time
import datetime
from Adafruit_7Segment import SevenSegment
from Rotary import KY040
import picamera
import os

#from datetime import datetime, timedelta

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

#Display initialisieren
#segment = SevenSegment(address=0x70)

#Encoder initialisieren
CLOCKPIN = 5 #stimmt wahrscheinlich nicht? Habe ich noch genug GPIO pins übrig?
DATAPIN = 6
SWITCHPIN = 13

encoder = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

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
        time.sleep(0.01)#je langsamer desto bessere kontrolle
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
    #AnzahlSteps = int(1600/AnzahlFotos) #1600 Wegen Microstepping
    AnzahlSteps = int(2360/AnzahlFotos) #mit getStepsforRevolution herausgefunden
    return AnzahlSteps

def Fotoaufnehmen (indx, fotoPfad, scanName):#nimmt ein Foto mit der PiCam auf
    print('index: ', indx, 'FotoPfad: ', fotoPfad)
    camera.capture(str(fotoPfad)+ '/'+ str(scanName)+ '_'+ str(indx)+ '.jpg')
    print('Foto '+ str(indx)+ 'aufgenommen: ')#+ {timestamp:%Y-%m-%d-%H-%M})
    return 
    
def makeDirectory(dirPfad, dirName):#erstellt ein verzeichnis
    fullDir = dirPfad + dirName
    if not os.path.exists(fullDir):
        os.makedirs(fullDir) 
    return fullDir
    
def getStepsforRevolution():#Methode bestimmt die noetigen Schritte für eine Umdrehung (Durch Uebersetztung zwischen zwei verschiednene Pulleys bedingt)
    Schritter = 0
   
    while raw_input('Schritter starten? (y/n)')=='y':
        Stepper = raw_input('Wieviele Schritte?')
        bauffer = int(Stepper)
        moveStepper(bauffer)
        Schritter +=bauffer
        print('Schritter: ', Schritter)
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

def setupDisplay(helligkeit, blinking):
    if helligkeit >= 0 and helligkeit <= 15:
        segment.setBrightness(helligkeit)
    else:
        segment.setBrightness(15)
    if blinking >= 0 and blinking <= 3:
        segment.setBlinkRate(blinking)
        #0 = No Blinking
        #1 = Blink at 2Hz
        #2 = Blink at 1Hz
        #3 = Blink at 1/2 Hz
    else:
        segment.setBlinkRate(0)
    return

def setDirection(richtung):
    if str(richtung) == 'left':
        gpio.output(23, True)
    elif str(richtung) == 'right':
        gpio.output(23, False)
    return

def blinkDisplay(state):

    if state:
        setupDisplay(15,)
    else:
        gpio.output(25, False)


    return

def getAnzahlFoto(): #laesst die Anazhl der Bilder anhand des Encoders und des Displays bestimmen
    #schreibe einen Beispielwert ins Display(10)
    segment.writeDigit(3, 1, dot=False)
    segment.writeDigit(4, 0, dot=False)
    
    #

    return

def writeMeta(pfad, name):
    metafile = open('META-%s.txt', 'w') % (name)
    metafile.write('Metadata\n', name)
    metafile.close()

    #Inhalt Metadatei
    #<name>Boris</name>
    #<setnumber>1</setnumber>
    #<date>1999-11-15</date>            DIN ISO 8601 als JJJJ-MM-TT
    #<timecode>11:25:33</timecode>
    #<setcount>10</setcount>
    #<description>Scan von Boris Borwisky</description>
    #<keywords>human, russia, awesomness</keywords>
    #<condition>mint - unbroken</condition>
    #<rights>CC BY-NC 4.0</rights>
    #<comment>schlechte Lichtbedingungen</comment>
    return
#========================================================================
#Parameter vom User erfragen
#========================================================================

try: #Variablen ins Programm uebergeben
    if sys.argv[1] is None:
        getAnzahlFoto()
    else:
        AnzahlFotos = int(sys.argv[1])
except: #oder im Programm abfragen
    print ('Keine Parameter angegeben. Bitte Anzahl der Fotos angeben')
    #AnzahlFotos = input("Anzahl der Fotos: ")
    
#========================================================================
#MAIN
#========================================================================

setDirection('right')
setupDisplay(15,0)

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
writeMeta(speicherPfad, dirName)

#setupCamera(licht)
enableMotor(True)#Easydriver vor Bewegung anschalten
#getStepsforRevolution()
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