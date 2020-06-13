import re
import json
import datetime
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

    i = 0
    while i < len(wordDataFromJson):

        if lastFileWasCut:
            temporaryWordsForLongTranscripts = []
            cutStart = getTimeSpanFromString(wordDataFromJson[i].startTime)
            wordsToMatchInWholeText = ""
            lastFileWasCut = False




def getTimeSpanFromString(startTimeString):
    indexOfSCharacter = startTimeString.find('s')
    startTimeString = startTimeString[:indexOfSCharacter]
    return datetime.datetime.strptime(startTimeString, '%S.%f').time()


main()





