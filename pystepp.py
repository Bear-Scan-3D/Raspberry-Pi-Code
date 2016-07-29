#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import RPi.GPIO as gpio
import time
#import datetime

from Adafruit_LED_Backpack import SevenSegment

import gaugette.rotary_encoder
import gaugette.switch

import picamera
import os


#=======================================================================
#Initialisierungen
#=======================================================================

#GPIO Vorbereitung
gpio.setmode(gpio.BCM)

gpio.setup(23, gpio.OUT) #Dir
gpio.setup(24, gpio.OUT) #Step
gpio.setup(25, gpio.OUT) #enable pin
gpio.setup(4, gpio.OUT)

#Kamera initialisieren
camera = picamera.PiCamera()

#Display initialisieren
display = SevenSegment.SevenSegment()

#encoder Pins
#wiringPI Pins
A_PIN = 2 # = 22
B_PIN = 3 # = 27
SW_PIN = 7 # = 4

encoder = gaugette.rotary_encoder.RotaryEncoder(A_PIN, B_PIN)
switch = gaugette.switch.Switch(SW_PIN)
encoder.steps_per_cycle = 4 # Je nach Hardware unterschiedlich


#Maximale Bilder für 123D Catch?
maxFotos = 72 ##Ist das bei der API auch so? Memento hat kein limit? Trotzdem ein Limit einstellen wegen datenübertragung?
minFotos = 5 ##Empririsch herausfinden??

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
        #ist der Drehteller besonders schwer, dann sollte man besonders langsam drehen
    return

def checkForButton(): #UserInput durch den Button des Rotary Encoders
    print('Bitte Eingabe bestaetigen. (Button druecken)')

    while gpio.input(4) != 0:
        blinkDisplay('medium')

    print('Button Pressed')
    return True

def enableMotor(motorZustand):#schaltet den Easy Driver an und aus
    #Wenn der Easy Driver ständig an ist verbraucht er sehr viel Strom und wird SEHR warm.
    if motorZustand:
        gpio.output(25, True)
    else:
        gpio.output(25, False)
    return

def AnzahlFotosToSteps(AnzahlFotos):#Berechnung der Anzahl der Schritte aus Anzahl der Fotos
    #Steppermotor hat 1.8 Degree per Step
    #Microstepping 1/8 Schritte an (Bessere Kontroller über den Steppermotor)
    #Also 200 volle Steps /1600 Microsteps fuer 360 Grad

    AnzahlSteps = int(2360/AnzahlFotos) #2360 mit getStepsforRevolution herausgefunden
    return AnzahlSteps

def Fotoaufnehmen (indx, fotoPfad, scanName):#nimmt ein Foto mit der PiCam auf
    print('index: ', indx, 'FotoPfad: ', fotoPfad)
    strindx = indx
    if indx <= 9:
        strindx = '00' + str(indx)
    elif indx > 9 <=99:
        strindx = '0' + str(indx)
    camera.capture(str(fotoPfad)+ '/'+ str(scanName)+ '_'+ str(strindx)+ '.jpg')
    print('Foto '+ str(indx)+ ' aufgenommen: ')#+ {timestamp:%Y-%m-%d-%H-%M})
    return

def makeDirectory(dirPfad, dirName):#erstellt ein Verzeichnis mit Name dirName am Pfad dirPfad
    fullDir = dirPfad + dirName
    if not os.path.exists(fullDir): #Verzeichnis existiert noch nicht
        os.makedirs(fullDir)        #Erstellt das Verzeichnis
    else:
        while os.path.exists(fullDir):  #Pfand existiert bereits
            fullDir += '+'              #Hängt ein + an den Pfad an, solange bis der Pfand eindeutig ist
        print 'Verzeichnis existiert bereits. Fotos werden unter: '+ fullDir + ' gespeichert.'
        os.makedirs(fullDir)            #Erstelt das Verzeichnis
    return fullDir

def getStepsforRevolution():#Methode bestimmt die noetigen Schritte für eine Umdrehung
    # (Durch Uebersetztung zwischen zwei verschiednene Pulleys bedingt)
    Schritter = 0

    while raw_input('Schritter starten? (y/n)')=='y':
        Stepper = raw_input('Wieviele Schritte?')
        bauffer = int(Stepper)
        moveStepper(bauffer)
        Schritter +=bauffer
        print('Schritter: ', Schritter)
    return

def setupCamera(lighting):#setzt die Parameter der Cam (lighting = Lichverhältnisse)
    print('Kamera wird vorgewärmt')
    time.sleep(2)
    print('Kamera fertig. Einstellungen werden gespeichert')

    overExposerValue = 5000

    camera.resolution = (2592, 1944)#5Megapixel Aufloesung - volle Aufloesung

    camera.sharpness = 1
    camera.contrast = 0
    camera.brightness = 50
    camera.saturation = 0

    if lighting:#Gute Lichtverhaeltnisse
        camera.iso = 200

        bufferAll = camera.exposure_speed
        print('bufferALLPRE: ', bufferAll)
        bufferAll = int(bufferAll) + overExposerValue
        print('bufferALLAFTER: ', bufferAll)
        camera.shutter_speed = int(bufferAll)


    else:#schlechte lichverhaeltnisse
        camera.iso = 800
        camera.shutter_speed = 2000000 #2Sekunden verschlusszeit

    camera.exposure_mode = 'off'
    whiteBalanceBuffer = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = whiteBalanceBuffer

    return

def setupDisplay(helligkeit, colon): #Bereitet das Display vor. Damit anzeige ordentlich ist.
    display.begin()

    display.set_colon(colon) #True oder False -- setzt den Dezimalpunkt

    if helligkeit >= 0 and helligkeit <= 15: #Range der möglichen Helligkeit
        display.set_brightness(helligkeit)
    else:
        display.set_brightness(15)   #Falls ungültige Eingabe
    return

def writeToDisplay(zahl):#schrieb eine Zahl ins Diaplay --Buchstaben gehen nur A-F Nicht hilfreich
    display.clear()
    zahl = str(zahl) #um sicher zu stellen, dass Zahl ein string ist
    display.print_number_str(zahl)
    display.write_display()
    #time.sleep(0.5)
    return

def setDirection(richtung): #Legt die Drehrichtung des Drehtellers fest. (Ist für diese Anwendung irrelevant)
    if str(richtung) == 'left':
        gpio.output(23, True)
    elif str(richtung) == 'right':
        gpio.output(23, False)
    return

def blinkDisplay(speed): #Lässt das Display ein mal blinken. Vielleicht Hilfreich wenn man auf Eingabe wartet.
    timing = 0
    if speed == 'slow':
        timing = 0.5
    elif speed == 'medium':
        timing = 0.2
    elif speed == 'fast':
        timing = 0.1

    if timing != 0:
        display.set_brightness(1)
        time.sleep(timing)
        display.set_brightness(15)
        time.sleep(timing)
    return

def getAnzahlFoto(): #laesst die Anazhl der Bilder anhand des Encoders und des Displays bestimmen
    #schreibe einen Beispielwert ins Display(10)
    print('in getAnzahlFotos')
    currentFotoAnzahl = 20
    writeToDisplay(currentFotoAnzahl)
    last_state = None

    #RotaryEncoder Bewegung Abfragen

    while True:
        delta = encoder.get_cycles()
        if delta == 0:
            blinkDisplay('slow')

        if delta != 0:
            print "rotate %d" % delta
            currentFotoAnzahl = currentFotoAnzahl - delta

            if currentFotoAnzahl <= minFotos:
                currentFotoAnzahl = minFotos
            elif currentFotoAnzahl >= maxFotos:
                currentFotoAnzahl = maxFotos

            writeToDisplay(currentFotoAnzahl)

        sw_state = switch.get_state()
        if sw_state != last_state:
            print "switch %d" % sw_state
            last_state = sw_state

            if sw_state == 1:
                return currentFotoAnzahl


def writeMeta(pfad, name, setcount):
    metaChoice = raw_input('Wollen sie Metadaten angeben? (y/n)')
    metafile = open('%s/META-%s.txt' % (pfad,name), 'w')
    metafile.write('<name>'+ name + '</name>\n')
    metafile.write('<setcount>'+ str(setcount) + '</setcount>\n')
    #NTP auf dem Raspberry Pi aktiviert?

    timeYear = time.strftime('%Y-%m-%d')
    metafile.write('<date>' + str(timeYear) + '</date>\n')

    timeNow = time.strftime('%H:%M:%S')
    metafile.write('<timecode>' + str(timeNow) + '</timecode>\n')

    timeZone = time.strftime('%Z')
    metafile.write('<timezone>' + str(timeZone) + '</timezone>\n')

    if str(metaChoice) == 'y':
        metaBuffer = raw_input('Beschreibung: ')
        metafile.write('<description>' + str(metaBuffer) + '</description>\n')
        metaBuffer = raw_input('Stichwoerter: (Bsp.: human, russia, awesomeness )')
        metafile.write('<keywords>' + metaBuffer + '</keywords>\n')
        metaBuffer = raw_input('Zustand: ')
        metafile.write('<condition>' + metaBuffer + '</condition>\n')
        metaBuffer = raw_input('Copyright: ')
        metafile.write('<rights>' + metaBuffer + '</rights>\n')
        metaBuffer = raw_input('Weitere Kommentare: ')
        metafile.write('<comment>' + metaBuffer + '</comment>\n')
    else:
        print('Keine Metadaten angebene. Automatische Metadaten wurden erfasst.')

    metafile.close()
    #Inhalt Metadatei
    #<name>Boris</name>
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
        AnzahlFotos = int(sys.argv[1])#Schiebt das 1. Argument des Programmaufrufs in Anzahlfotos
        writeToDisplay(AnzahlFotos) #schreibt das ins Display
except: #oder im Programm abfragen
    AnzahlFotos = getAnzahlFoto()  # Ermittelt Anzahl der gewollten Fotos über Rotary Encoder und Display
    print ('Keine Parameter angegeben. Bitte Anzahl der Fotos angeben')
    #AnzahlFotos = input("Anzahl der Fotos: ")

#========================================================================
#MAIN
#========================================================================
setDirection('right')
setupDisplay(15,False)

#Variablen
#AnzahlSteps = 0
moveCounter = 0
licht = True #True = hell /False = Dunkel Wird durch lichtsensor überprüft?

AnzahlSteps = AnzahlFotosToSteps(AnzahlFotos)

enableMotor(False)

#dirPfad = raw_input('dirPfad: ')
dirPfad = '/home/pi/RaspiCode/Bilder/'
#dirName = raw_input('Name des Scans: ')
dirName = 'DEBUGFOTOS'
speicherPfad = makeDirectory(dirPfad, dirName)
print('Ganzer Pfad: ', speicherPfad)
writeMeta(speicherPfad, dirName, AnzahlFotos)

setupCamera(licht)
enableMotor(True)#Easydriver vor Bewegung anschalten

#getStepsforRevolution() #Nur bei der Verwendung von neuen (anderen) Pulleys nötig

while moveCounter < AnzahlFotos:
    moveStepper (AnzahlSteps)
    print ('Schritt: ', moveCounter)
    moveCounter += 1
    writeToDisplay(AnzahlFotos - moveCounter) #Restliche Anzahl von Fotos ins Display schreiben

    camera.led = True
    #camera.start_preview(alpha=128, fullscreen=True)
    time.sleep(2) #Wartezeit zwischen den einzelnen Fotos
    Fotoaufnehmen(moveCounter, speicherPfad, dirName)
    camera.led = False

enableMotor(False) #Schaltet den Easydriver vor Ende des Programms aus

checkForButton()
#raw_input('Motor Sleep')#wait for any key

#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()
camera.close()
display.clear()

#ENDE