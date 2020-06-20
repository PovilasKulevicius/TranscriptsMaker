import re
import json
import datetime
import os.path
from pydub import AudioSegment
import Objects as o

pathToBook = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Book/chapter-1.txt"
pathToJsonTranscripts = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Transcripts/02 - John R. R. Tolkien - Hobitas.json"
pathToWav = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Audio/02 - John R. R. Tolkien - Hobitas.wav"
newAudioDestination = "C:/Users/Povilas Kulevicius/Desktop/VoiceRecognitionTools/SequenceMatcher2/Resources/Hobitas/Cut"

cutTranscriptsName = "Hobitas"


def main():
    textFromFile = readFile(pathToBook)
    textFromFileWithRemovedUnnecessaryCharacters = removeUnnecessaryCharacters(textFromFile)
    wordDataFromJson = readGoogleJson(pathToJsonTranscripts)
    textFromFile, wordDataFromJson = allignBookTextWithJson(textFromFileWithRemovedUnnecessaryCharacters, wordDataFromJson)
    tooLongTranscripts = cutWavFilesForTranscripts(wordDataFromJson, textFromFile)
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


def cutWavFilesForTranscripts(wordDataFromJson, text):
    lastFileWasCut = True
    temporaryListOfWordsUsedForMatchingTooLongTranscripts = []
    wordsToMatchInWholeText = ''
    cutStart = datetime.datetime.now()
    fileNameIndex = 0
    tooLongTranscripts = []

    i = 0
    while i < len(wordDataFromJson):

        if lastFileWasCut:
            temporaryListOfWordsUsedForMatchingTooLongTranscripts = []
            cutStart = getTimeSpanFromString(wordDataFromJson[i].startTime)
            wordsToMatchInWholeText = ""
            lastFileWasCut = False
            fileNameIndex += 1

        temporaryListOfWordsUsedForMatchingTooLongTranscripts.append(wordDataFromJson[i])
        wordsToMatchInWholeText += f'{wordDataFromJson[i].word} '
        indexOfMatchedWordsInText = text.find(wordsToMatchInWholeText)
        if indexOfMatchedWordsInText != -1 and len(wordsToMatchInWholeText.split()) >= 4:
            text = cutAudioAndWriteToFile(text, wordsToMatchInWholeText, wordDataFromJson[i], cutStart, fileNameIndex, tooLongTranscripts, temporaryListOfWordsUsedForMatchingTooLongTranscripts)
            lastFileWasCut = True

        if len(wordsToMatchInWholeText.split()) >= 4:
            wordsToMatchInWholeText = wordsToMatchInWholeText.split(' ', 1)[1]

        i += 1

    return tooLongTranscripts


def cutAudioAndWriteToFile(wholeText, textToFind, lastWordData, audioStart, fileNameIndex, tooLongTranscripts, temporaryListOfWordsUsedForMatchingTooLongTranscripts):
    transcript, wholeText = getTranscriptAndRemoveFromWholeText(wholeText, textToFind)
    audioEnd = getTimeSpanFromString(lastWordData.endTime)
    fileWasWriten = trimWavFile(audioStart, audioEnd, f'{cutTranscriptsName} 1_{fileNameIndex}_{transcript}.wav')

    if not fileWasWriten:
        tooLongTranscripts.append(o.TranscriptData(transcript, temporaryListOfWordsUsedForMatchingTooLongTranscripts))

    fileNameIndex += 1
    return wholeText

def getTranscriptAndRemoveFromWholeText(wholeText, textToFind):
    indexOfFoundText = wholeText.find(textToFind) + len(textToFind.strip())
    fileName = wholeText[:indexOfFoundText]

    if len(wholeText.strip()) != len(textToFind.strip()):
        remainingText = wholeText[indexOfFoundText + 1:]
    else:
        remainingText = ""

    return fileName, remainingText


def trimWavFile(audioStart, audioEnd, outputFileName):
    bookAudio = AudioSegment.from_wav(pathToWav)
    audioStartInt = audioStart.second * 1000 + audioStart.microsecond / 1000 - (0) # number in brackets is used for adjusting cut time
    audioEndInt = audioEnd.second * 1000 + audioEnd.microsecond / 1000 + (240)
    bookAudio = bookAudio[audioStartInt:audioEndInt]
    bookAudio.export(f'{newAudioDestination}/{outputFileName}', format="wav")

    if os.path.isfile(f'{newAudioDestination}/{outputFileName}'):
        return True
    else:
        return False


def getTimeSpanFromString(timeString):
    indexOfSCharacter = timeString.find('s')
    timeString = timeString[:indexOfSCharacter]

    if timeString.find('.') == -1:
        timeString = f'{timeString}.0'

    return datetime.datetime.strptime(timeString, '%S.%f').time()


main()





