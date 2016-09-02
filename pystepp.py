#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys #to ba able to create files etc
import RPi.GPIO as gpio
import time

from Adafruit_LED_Backpack import SevenSegment #library for the small Display

#library for using the rotary encoder (also with the button of same)
import gaugette.rotary_encoder
import gaugette.switch

import picamera #for use with the RaspiCam
#import piggyphoto
import os


#=======================================================================
#Init
#=======================================================================

#setting up all the GPIO Pins so that they can be manipulated later
gpio.setmode(gpio.BCM)

#GPIO for control of steppermotor
gpio.setup(23, gpio.OUT) #Dir
gpio.setup(24, gpio.OUT) #Step
gpio.setup(25, gpio.OUT) #enable pin

#GPIO for using the switch of the rotary encoder seperately
gpio.setup(4, gpio.IN, pull_up_down = gpio.PUD_DOWN)

#make instance of display
display = SevenSegment.SevenSegment()

#GPIO for usage with the rotary encoder (NOT BCM but wiringPI pin layout)
A_PIN = 2 # = 22 (BCM)
B_PIN = 3 # = 27
SW_PIN = 7 # = 4

#Make instance of the rotary encoder/switch
encoder = gaugette.rotary_encoder.RotaryEncoder(A_PIN, B_PIN)
switch = gaugette.switch.Switch(SW_PIN)
encoder.steps_per_cycle = 4 #adjust the triggering amount of steps for the rotarty encoder (completely depens on hardware)


#setting up a range for the amount of pictures for each scan
maxFotos = 150 #The more the better? Whats the limit? When doesn't it matter anymore?
minFotos = 5 #Probably should be at least arround 10 for good results

usedCamera = '' #can also be Nikon or RaspiCam

#========================================================================
#Methods
#========================================================================

def moveStepper(steps):#moves the motor a certain amount ('steps')
    stepCounter = 0
    maxSpeed = 0.00005
    jerkSpeed = 0.01
    acceleration = 0.99
    brakeThreshold = 100
    currentSpeed = jerkSpeed

    while stepCounter < steps:
        #switching between the two states of this GPIO Pins results in a 'pulse' for the steppermotordriver
        #Every 'pulse' the stepperdriver makes one microstep
        gpio.output(24, True)
        time.sleep(0.000002)
        gpio.output(24, False)
        stepCounter += 1
        print('currentSpeedvorSleep: ',currentSpeed)
        time.sleep(currentSpeed)#the speed of the steppermotor is controlled by a waiting time between ever microstep

        deltaSteps = steps - stepCounter #calculates the steps that are left
        print('Deltasteps: ', deltaSteps)

        if currentSpeed > maxSpeed and stepCounter < brakeThreshold:
            currentSpeed *= acceleration
        elif currentSpeed < jerkSpeed and deltaSteps < brakeThreshold:
            currentSpeed /= acceleration

    return

def checkForButton(): #waits for user to press the button of the rotary encoder
    print('Please press the button of the knob.')

    while gpio.input(4) != 0:
        blinkDisplay('medium')

    return True

def enableMotor(motorZustand): #toogle the sleep mode of the steppermotordriver
    #If the driver is always on it uses a lot of energy which is displaced as a lot of heat

    if motorZustand:
        gpio.output(25, True)
    else:
        gpio.output(25, False)
    return

def AnzahlFotosToSteps(AnzahlFotos): #calculates the amount of stepps for the given amount of pictures
    #stepperdriver is configured for 1/8 step microstepping
    #steppermotor needs 200 full steps(or 1600 microsteps) for a full 360 degree revolution
    #!IMPORTANT!
    #only works if the turntable and the steppermotor is coupled with a 1:1 gearing ration
    #for every other ration please use getStepsforRevolution() method

    AnzahlSteps = int(2400/AnzahlFotos)
    return AnzahlSteps


def Fotoaufnehmen (indx, fotoPfad, scanName): # used for taking a picture with the available camera

    #print('index: ', indx, 'FotoPfad: ', fotoPfad)

    #check whether the current taken picture needs to have one, two or none leading zero (always have 3 digits)
    #(makes sorting the pictures easiert - depends on used software)
    strindx = indx
    if indx <= 9:
        strindx = '00' + str(indx)
    elif indx > 9 <=99:
        strindx = '0' + str(indx)

    if usedCamera == 'RaspiCam':
        camera.led = True
        camera.capture(str(fotoPfad) + '/' + str(scanName) + '_PiCam_' + str(strindx) + '.jpg')
        print('Foto ' + str(indx) + ' aufgenommen: ')
        time.sleep(2)
        camera.led = False
    elif usedCamera == 'Nikon':
        print('Nikon')
        cam.capture_image(str(fotoPfad) + '/' + str(scanName) + '_PiCam_' + str(strindx) + '.jpg')
        time.sleep(2)
    return

def makeDirectory(dirPfad, dirName):#makes a directory with the name: 'dirName' and the path: 'dirPfad'

    fullDir = dirPfad + dirName #stitch path and name together to get full path

    #checks whether the directory already exists
    if not os.path.exists(fullDir): #if it doesn't
        os.makedirs(fullDir)        #creates the directory
    else: #if it does
        while os.path.exists(fullDir):  #repeat as long there is an directory with exactly this path/name
            fullDir += '+'              #appends a '+' to the path/name
        #print 'Verzeichnis existiert bereits. Fotos werden unter: '+ fullDir + ' gespeichert.'
        os.makedirs(fullDir)            #creates the directory
    return fullDir

def getStepsforRevolution():#method for determine the steps for each revolution empirically
    #!IMPORTANT!
    #Use only if the gearing ratio between steppermotor and turntable IS NOT 1:1 (else use 1600)
    #If gearing ratio is known one can use this method to check if it's correct
    #The value doesn't have to be super accurate

    Schritter = 0
    while raw_input('Schritter starten? (y/n)')=='y':
        Stepper = raw_input('Wieviele Schritte?')
        bauffer = int(Stepper)
        moveStepper(bauffer)
        Schritter +=bauffer
        print('Schritter: ', Schritter)
    return

def getOverexposerValue():
    #determine the right value of the exposure with the rotary encoder and the big display
    value = 5000
    return value

def setupCamera(chosenCam, status): #used to set up various parameters of the camera

    if chosenCam == 'RaspiCam' and status == 1:
        usedCamera = 'RaspiCam'
        # make instance of camera
        camera = picamera.PiCamera()

        camera.resolution = (2592, 1944) #max resolution of the RaspiCam
        camera.sharpness = 1
        camera.contrast = 0
        camera.brightness = 50
        camera.saturation = 0
        camera.iso = 100
        camera.exposure_mode = 'off' #=======================Right Value? What are the possibilities?
        whiteBalanceBuffer = camera.awb_gains
        print('gains: '+str(whiteBalanceBuffer))
        print('mmode: ' + str(camera.awb_mode))
        camera.awb_mode = 'off'
        camera.awb_gains = whiteBalanceBuffer
        camera.start_preview(alpha=128, fullscreen=True)

        #overExposerValue = getOverexposerValue()

        #bufferAll = camera.exposure_speed
        #print('bufferALLPRE: ', bufferAll)
        #bufferAll = int(bufferAll) + overExposerValue
        #print('bufferALLAFTER: ', bufferAll)
        #camera.shutter_speed = int(bufferAll)


    if chosenCam == 'Nikon' and status == 1:
        usedCamera = 'Nikon'
        cam = piggyphoto.camera()

        print('Nikon')

    if status == 0:
        if chosenCam == 'RaspiCam':
            camera.close()
        elif chosenCam == 'Nikon':
            #donothing
            time.sleep(0.00001)
    return

def setupDisplay(helligkeit, colon): #sets up the display
    display.begin()

    display.set_colon(colon) #True oder False

    """if helligkeit >= 0 and helligkeit <= 15: #Range of possible brightness of display
        display.set_brightness(helligkeit)
    else:
        display.set_brightness(15)   #if value is wrong
    """
    try: #Range is between 0 and 15
        display.set_brightness(helligkeit)
    except:
        display.set_brightness(15)
    return

def writeToDisplay(zahl): #writes a number (or string) to the display ABCDEF or 0-9 -- max 4 digits

    display.clear() # clears the buffer of the display
    zahl = str(zahl) # make sure the number is a string
    display.print_number_str(zahl)
    display.write_display() #writes the buffer to the display
    return

def setDirection(richtung): #sets the direction of the steppermotor (not important for a 3D scan)
    if str(richtung) == 'left':
        gpio.output(23, True)
    elif str(richtung) == 'right':
        gpio.output(23, False)
    return

def blinkDisplay(speed): #makes the display blink once. Maybe usefull while waiting for user input
    timing = 0
    #speed determines the frequency of the blinking
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

def getAnzahlFoto(): #uses the small display and the rotary encoder to let the user input a value for the number of pictures

    currentFotoAnzahl = 20
    writeToDisplay(currentFotoAnzahl) # writes a starting point into the display
    last_state = None #needed for correct reading of button press

    #RotaryEncoder get the movement

    while True:
        delta = encoder.get_cycles()

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
#MAIN
#========================================================================
setDirection('right')
setupDisplay(15,False)

#Variablen
#AnzahlSteps = 0
moveCounter = 0
licht = True #True = hell /False = Dunkel Wird durch lichtsensor überprüft?

#========================================================================
#Parameter vom User erfragen
#========================================================================

try: #Variablen ins Programm uebergeben
    AnzahlFotos = int(sys.argv[1])#Schiebt das 1. Argument des Programmaufrufs in Anzahlfotos
    writeToDisplay(AnzahlFotos) #schreibt das ins Display
except: #oder im Programm abfragen
    AnzahlFotos = getAnzahlFoto()  # Ermittelt Anzahl der gewollten Fotos über Rotary Encoder und Display
    #print ('Keine Parameter angegeben. Bitte Anzahl der Fotos angeben')
    #AnzahlFotos = input("Anzahl der Fotos: ")


AnzahlSteps = AnzahlFotosToSteps(AnzahlFotos)

enableMotor(False)

#dirPfad = raw_input('dirPfad: ')
dirPfad = '/home/pi/RaspiCode/Bilder/'
#dirName = raw_input('Name des Scans: ')
dirName = 'DEBUGFOTOS'
speicherPfad = makeDirectory(dirPfad, dirName)
writeMeta(speicherPfad, dirName, AnzahlFotos)


#setupCamera('Nikon', 1)
enableMotor(True)#Easydriver vor Bewegung anschalten

#getStepsforRevolution() #Nur bei der Verwendung von neuen (anderen) Pulleys nötig

while moveCounter < AnzahlFotos:
    moveStepper (AnzahlSteps)
    moveCounter += 1
    writeToDisplay(AnzahlFotos - moveCounter) #Restliche Anzahl von Fotos ins Display schreiben

    #Fotoaufnehmen(moveCounter, speicherPfad, dirName)

enableMotor(False) #Schaltet den Easydriver vor Ende des Programms aus
#setupCamera('Nikon', 0)

#checkForButton()

#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()
display.clear()

#ENDE