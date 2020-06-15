import re
import json
import datetime
import scipy.io.wavfile
import numpy
import os.path
import Objects as o

pathToBook = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Book/chapter-1.txt"
pathToJsonTranscripts = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Transcripts/02 - John R. R. Tolkien - Hobitas.json"
pathToWav = ""

cutTranscriptsName = ""


def main():
    textFromFile = readFile(pathToBook)
    textFromFileWithRemovedUnnecessaryCharacters = removeUnnecessaryCharacters(textFromFile)
    wordDataFromJson = readGoogleJson(pathToJsonTranscripts)
    textFromFile, wordDataFromJson = allignBookTextWithJson(textFromFileWithRemovedUnnecessaryCharacters, wordDataFromJson)
    cutWavFilesForTranscripts(wordDataFromJson, pathToWav, textFromFile, cutTranscriptsName)
    print()


def readFile(filePath):
    return open(filePath, mode="r", encoding="utf-8").read()


def removeUnnecessaryCharacters(text):
    text = text.replace("\n", ' ')
    text = re.sub('\s+', ' ', text).strip()
    return re.sub(r'([^\s\w]|_)+', '', text).lower()


def readGoogleJson(jsonPath):
    jsonContentsText = readFile(jsonPath)
    jsonContent = json.loads(jsonContentsText)
    results = jsonContent['results']

    words = []

    for result in results:
        firstAlternative = result['alternatives'][0]['words']
        for alternativeWordInformation in firstAlternative:
            words.append(o.WordData(alternativeWordInformation['word'], alternativeWordInformation['startTime'], alternativeWordInformation['endTime']))

    return words


def allignBookTextWithJson(text, wordDataFromJson):
    wordCountToMatch = 3
    wordsToMatch = ""

    i = 0
    while i < len(wordDataFromJson):
        wordsToMatch += wordDataFromJson[i].word
        if len(wordsToMatch.split()) >= wordCountToMatch:
            indexOfFoundWords = text.find(wordsToMatch)
            if indexOfFoundWords != -1:
                text = text[indexOfFoundWords:]
                break
            else:
                indexOfFoundSpace = wordsToMatch.find(" ")
                wordsToMatch = wordsToMatch[indexOfFoundSpace+1:]
                wordDataFromJson = wordDataFromJson[1:]
                i -= 1

        wordsToMatch += " "
        i += 1
    return text, wordDataFromJson


def cutWavFilesForTranscripts(wordDataFromJson, pathToWavFile, text, fileName):
    lastFileWasCut = True
    temporaryListOfWordsUsedForMatching = []
    wordsToMatchInWholeText = ""
    cutStart = datetime.datetime.now()
    fileNameIndex = 0

    i = 0
    while i < len(wordDataFromJson):

        if lastFileWasCut:
            temporaryListOfWordsUsedForMatching = []
            cutStart = getTimeSpanFromString(wordDataFromJson[i].startTime)
            wordsToMatchInWholeText = ""
            lastFileWasCut = False
            fileNameIndex += 1

        temporaryListOfWordsUsedForMatching.append(wordDataFromJson[i])
        wordsToMatchInWholeText = wordDataFromJson[i] + ' '
        indexOfMatchedWordsInText = text.find(wordsToMatchInWholeText)
        if indexOfMatchedWordsInText != -1 & wordsToMatchInWholeText.split() >= 4:
            cutAudioAndWriteToFile(text, wordsToMatchInWholeText, wordDataFromJson[i], cutStart, fileNameIndex)



def cutAudioAndWriteToFile(wholeText, textToFind, lastWordData, audioStart, fileNameIndex):
    transcript, remainingText = getTranscriptAndRemoveFromWholeText(wholeText, textToFind)
    audioEnd = getTimeSpanFromString(lastWordData.endTime)
    fileWasWriten = trimWavFile(audioStart, audioEnd, pathToWav, f'{cutTranscriptsName} 1_{fileNameIndex}_{transcript}.wav')

    if not fileWasWriten:
        

def getTranscriptAndRemoveFromWholeText(wholeText, textToFind):
    indexOfFoundText = wholeText.find(textToFind) + len(textToFind.strip())
    fileName = wholeText[:indexOfFoundText]

    if len(wholeText.strip()) != len(textToFind.strip()):
        remainingText = wholeText[:indexOfFoundText + 1]
    else:
        remainingText = ""

    return fileName, remainingText


def trimWavFile(audioStart, audioEnd, fileName, outputFileName):
    fs1, y1 = scipy.io.wavfile.read(fileName)
    l1 = numpy.array([[audioStart, audioEnd]])
    l1 = numpy.ceil(l1 * fs1)  # get integer indices into the wav file - careful of end of array reading with a check for greater than y1.shape
    newWavFileAsList = []
    for elem in l1:
        startRead = elem[0]
        endRead = elem[1]
        if startRead >= y1.shape[0]:
            startRead = y1.shape[0] - 1
        if endRead >= y1.shape[0]:
            endRead = y1.shape[0] - 1
        newWavFileAsList.extend(y1[startRead:endRead])

    newWavFile = numpy.array(newWavFileAsList)

    scipy.io.wavfile.write(outputFileName, fs1, newWavFile)

    if os.path.isfile(fileName):
        return True
    else:
        return False


def getTimeSpanFromString(timeString):
    indexOfSCharacter = timeString.find('s')
    timeString = timeString[:indexOfSCharacter]
    return datetime.datetime.strptime(timeString, '%S.%f').time()


main()





