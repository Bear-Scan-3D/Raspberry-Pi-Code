import sys
import RPi.GPIO as gpio #https://pypi.python.org/pypi/RPi.GPIO
import time
import picamera
import os
from datetime import datetime, timedelta

#Variablen ins Programm uebergeben
try: 
    direction = sys.argv[1]
    steps = int(sys.argv[2]) #Microstepping 1/8 ist an
    speed = int(sys.argv[3])
except:
    print ("Keine Perimeter angegeben. Bitte angeben: programmname.py Richtung Schritte Speed\nRichtung= right oder left\nSchritte= z.B. 200\nSpeed in % max 100")
    #direction = raw_input("Richtung: ")#weil man sonst alles mit "..." angeben muss
    direction = "right"
    #raw_input("Press Enter to continue...")#wait for any key
    AnzahlFotos = input("Anzahl der Fotos: ")
    #speed = input("Speed:")
    print("dir= %s AnzahlFotos %s") % (direction, AnzahlFotos)
    

#Kontrollausgabe der Eingegebenen Perimeter
#print("Bewege den Motor %s Schritte nach %s. Speed= %s") % (steps, direction, speed)

#GPIO Vorbereitung
gpio.setmode(gpio.BCM)
#GPIO23 = Dir
#GPIO24 = Step
gpio.setup(23, gpio.OUT) #Dir
gpio.setup(24, gpio.OUT) #Step
gpio.setup(25, gpio.OUT) #enable pin

#Kamera initialisieren
camera = picamera.PiCamera()

#==============================================================
#==============================================================
#Funktionen
def moveStepper(steps):
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
    
def enableMotor(motorZustand):
    if motorZustand:
        gpio.output(25, True)
        print('Motor AN')
    else:
        gpio.output(25, False)
        print('Motor AUS')
    return

def AnzahlFotosToSteps(AnzahlFotos):
    AnzahlSteps = int(1600/AnzahlFotos) #1600 Wegen Microstepping
    print ('AnzahlSteps: ', AnzahlSteps)
    return AnzahlSteps

def Fotoaufnehmen (indx, fotoPfad, scanName):
    print('index: ', indx, 'FotoPfad: ', fotoPfad)
    camera.capture(str(fotoPfad)+ '/'+ str(scanName)+ '_'+ str(indx)+ '.jpg')
    #camera.capture('%s/Scan_{timestamp:%Y-%m-%d-%H-%M}_%s.jpg' % fotoPfad, indx)
    return 
    
    
def makeDirectory(dirPfad, dirName):
    fullDir = dirPfad + dirName
    if not os.path.exists(fullDir):
        os.makedirs(fullDir)
    print('Existiert nun der Pfad: ',str(os.path.exists(fullDir))) 
    return fullDir
    
#==============================================================
#Richtung festlegen GPIO = 23
if str(direction) == 'left':
    gpio.output(23, True)
elif str(direction) == 'right':
    gpio.output(23, False)
	


#Berechnung der Schritte aus Winkel
#Steppermotor hat 1.8 Degree per Step
#Microstepping 1/8 Schritte an 
#Also 200 volle Steps fuer 360 Grad und 1600 Microsteps 
#Beispiel: 18 Grad -> 18/1.8 =10 -> 10*8 = 80
#WinkelSteps = int((grad/1.8)*8)

#WinkelBerechnung aus Intervall
#Wie viele Fotos pro Drehung wollen sie machen (Empfohlen x Fotos)?
#AnzahlSteps = int(1600/AnzahlFotos)

#Geschwindigkeit wird durch eine Wartezeit zwischen den Schritten realisiert
#WaitTime = 0.001
#Speed  0.001 = 100%
#       0.0025= 75%
#       0.002 = 50%

#WaitTime = float(speed)*0.000001
#print (WaitTime)

#main
print ("Starte Hauptprogramm")

AnzahlSteps = 0
AnzahlSteps = AnzahlFotosToSteps(AnzahlFotos)

#directorytest
#dirPfad = raw_input('dirPfad: ')
dirPfad = '/home/pi/RaspiCode/'
dirName = raw_input('Name des Scans: ')
speicherPfad = makeDirectory(dirPfad, dirName)
print('Ganzer Pfad:', speicherPfad)


enableMotor(True)

moveCounter = 0
while moveCounter<AnzahlFotos:
    moveStepper (AnzahlSteps)
    print ("Schritt:", moveCounter)
    moveCounter +=1
    #Fotoaufnehmen (moveCounter)
    camera.led = True
    time.sleep(2) #Wartezeit zwischen den einzelnen Fotos,
    Fotoaufnehmen(moveCounter, speicherPfad, dirName)
    camera.led = False
    
enableMotor(False) #Schaltet den Motor vor Ende des Programms aus



raw_input("Teste Sleep...")#wait for any key

#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()

print ("Bewegung beendet.")