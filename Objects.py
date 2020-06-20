class WordData:
  def __init__(self, word, startTime, endTime):
    self.word = word
    self.startTime = startTime
    self.endTime = endTime


class TranscriptData:
  def __init__(self, transcript, wordsData):
    self.transcript = transcript
    self.wordsData = wordsData