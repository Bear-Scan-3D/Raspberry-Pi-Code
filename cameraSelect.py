
def selectCamera():
    currentCamera = 'Nikon'
    if currentCamera == 'Nikon':

    elif currentCamera == 'PiCam':



def Fotoaufnehmen(indx, fotoPfad, scanName): # used for taking a picture with the available camera
    #print('index: ', indx, 'FotoPfad: ', fotoPfad)

    #check whether the current taken picture needs to have one, two or none leading zero
    #(makes sorting the pictures easiert - depends on used software)
    strindx = indx
    if indx <= 9:
        strindx = '00' + str(indx)
    elif indx > 9 <= 99:
        strindx = '0' + str(indx)

    if currentCam() == 'PiCam':
        camera.capture(str(fotoPfad) + '/' + str(scanName) + '_' + str(strindx) + '.jpg')
        #print('Foto ' + str(indx) + ' aufgenommen: ')  # + {timestamp:%Y-%m-%d-%H-%M})
    elif currentCam() == 'Nikon':
        #activate autofocus

        #make sure autofocus works? Is there a method that return a bool if focus is right?

        #fix the camera settings?
        #is there a manual mode? can auto exposure controll be received via python?

        #finally take a picture
        #append a suffix to picture, so it's clear that it was taken by the big camera?


    return

#globale Variable
directionFlip = False

def flipDirection():

    if directionFlip == False:
        directionFlip = True
    else:
        directionFlip = False

    # derzeitige richtung herausfinden?
    # flip boolean?
    if gpio.output(23) == 'True':
        gpio.output(23, False)
    else:
        gpio.output(23, True)



def getStepsforRevolution():#Methode bestimmt die noetigen Schritte für eine Umdrehung
    # (Durch Uebersetztung zwischen zwei verschiednene Pulleys bedingt)
    Schritter = 0

    flipped = False
    while True:
        userInput = raw_input('Schritte + oder -? (+/-)')
        if userInput == '+':
            if
            writeToDisplay(Schritter)
            Stepper = raw_input('Wieviele Schritte?')
            moveStepper(int(Stepper))
            Schritter += int(Stepper)
            #print('Schritter: ', Schritter)
        elif userInput == '-':
            writeToDisplay(Schritter)
            Stepper = raw_input('Wieviele Schritte?')

            moveStepper(int(Stepper))
            Schritter += int(Stepper)
        else:
            print('Schritter beendet.')
            return 0
    return

def writeMeta(pfad, name, setcount):
    #Commentary in xml file?
    #Header?
    metaChoice = raw_input('Wollen sie Metadaten angeben? (y/n)')
    metafile = open('%s/META-%s.txt' % (pfad,name), 'w')
    metafile.write('<name>'+ name + '</name>\n')
    metafile.write('<setcount>'+ str(setcount) + '</setcount>\n')


    metafile.write('<camera>'+ str(currentCamera()) +'</camera>')
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