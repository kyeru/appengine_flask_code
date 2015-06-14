import random

from google.appengine.ext import ndb
from mymodules import ndbi
from mymodules.counter import *

quiz_seqno = 'QuizSeqNum'

class Answer(ndb.Model):
    seqno = ndb.IntegerProperty()
    answer = ndb.IntegerProperty()
    #indexes = ndb.IntegerProperty(repeated=True)

class QuizException:
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

class QuestionAnswer:
    def __init__(self, choices, answer):
        self.choices = choices
        self.answer = answer

    def __str__(self):
        return str(self.choices) + ' (' + str(self.answer) + ')'

    def evaluate(self, answer):
        return self.answer == answer

class QuizGenerator:
    @staticmethod
    def load(seqno):
        answer = ndbi.read_entity(Answer, {'seqno': seqno})
        return QuestionAnswer([], answer.answer)

    @staticmethod
    def translate(qna, seqno):
        if len(qna.choices) <= 0:
            return '', []
        try:
            target, description = qna.choices[qna.answer - 1]
            choices = []
            for name, description in qna.choices:
                choices.append(description)
            ndbi.add_entity(Answer,
                            seqno = seqno,
                            answer = qna.answer)
            return target, choices
        except Exception as e:
            raise QuizException(
                'Quiz generation failed: ' + str(qna) + '\n' +
                str(type(e)) + ': ' + str(e))

    @staticmethod
    def cleanup(seqno):
        ndbi.delete_entity(Answer, seqno = seqno)

    @staticmethod
    def get_log(qna):
        target, choices = question(qna)
        log = str(target) + ' --> '
        num = 1
        for choice in choices:
            log += str(num) + ') ' + choice + ' '
            num += 1
        return log

def get_quiz_seqno():
    return increase_counter(quiz_seqno)

# test
if __name__ == '__main__':
    sample = [('a', 'description of a'),
              ('b', 'description of b'),
              ('c', 'description of c'),
              ('d', 'description of d')]
    qna = QuestionAnswer(sample)
    print 'correct answer: ' + str(qna.answer)
    print qna.evaluate(qna.answer)
    print qna.evaluate(5 - qna.answer)
