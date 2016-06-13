import sys
import RPi.GPIO as gpio #https://pypi.python.org/pypi/RPi.GPIO
import time

#Variablen ins Programm uebergeben
try: 
    direction = sys.argv[1]
    steps = int(sys.argv[2]) #Microstepping 1/8 ist an
    speed = int(sys.argv[3])
except:
    print ("Keine Perimeter angegeben. Bitte angeben: programmname.py Richtung Schritte Speed\nRichtung= right oder left\nSchritte= z.B. 200\nSpeed in % max 100")
    direction = input("Richtung: ")
    AnzahlFotos = input("Anzahl der Fotos: ")
    speed = input("Speed:")
    
    

#Kontrollausgabe der Eingegebenen Perimeter
#print("Bewege den Motor %s Schritte nach %s. Speed= %s") % (steps, direction, speed)

#GPIO Vorbereitung
gpio.setmode(gpio.BCM)
#GPIO23 = Dir
#GPIO24 = Step
gpio.setup(23, gpio.OUT)
gpio.setup(24, gpio.OUT)

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
        time.sleep(0.001)
    return

def AnzahlFotosToSteps(AnzahlFotos):
    AnzahlSteps = 0
    AnzahlSteps = int(1600/AnzahlFotos) #1600 Wegen Microstepping
    return AnzahlSteps

#==============================================================
#Richtung festlegen GPIO = 23
if direction == 'left':
    gpio.output(23, True)
elif direction == 'right':
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

moveCounter = 0
while moveCounter<AnzahlFotos:
    moveStepper (AnzahlSteps)
    print ("Schritt:", moveCounter)
    moveCounter +=1
    time.sleep(1000) #Wartezeit zwischen den einzelnen Fotos
    

    


#GPIO freigeben, damit andere Programme damit arbeiten koennen
gpio.cleanup()

print ("Bewegung beendet.")