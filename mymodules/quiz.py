import random

from flask import request
from google.appengine.ext import ndb
from mymodules import ndbi
from mymodules.counter import *
from mymodules.fileparser import parse_file
from mymodules.rendercommon import *
from mymodules.worddef import *

seq_counter = 'QuizSeqNum'

# ndb schema
class QnARecord(ndb.Model):
    quiz_no = ndb.IntegerProperty()
    answer = ndb.IntegerProperty()
    choices = ndb.StringProperty(repeated = True)

# exception
class QuizException:
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return 'quiz: ' + self.message

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
    def load(quiz_no):
        record = ndbi.read_entity(QnARecord, {'quiz_no': quiz_no})
        return QuestionAnswer(record.choices, record.answer)

    @staticmethod
    def get_type1(qna, quiz_no):
        if len(qna.choices) <= 0:
            return '', []
        try:
            target, description = qna.choices[qna.answer - 1]
            choices = []
            for name, description in qna.choices:
                choices.append(description)
            ndbi.add_entity(QnARecord,
                            quiz_no = quiz_no,
                            answer = qna.answer,
                            choices = choices)
            return target, choices
        except Exception as e:
            raise QuizException(
                'Quiz type 1 error: ' + str(qna) + '\n' +
                str(type(e)) + ': ' + str(e))

    @staticmethod
    def get_type2(qna, quiz_no):
        if len(qna.choices) <= 0:
            return '', []
        try:
            name, target = qna.choices[qna.answer - 1]
            choices = []
            for name, description in qna.choices:
                choices.append(name)
            ndbi.add_entity(QnARecord,
                            quiz_no = quiz_no,
                            answer = qna.answer,
                            choices = choices)
            return target, choices
        except Exception as e:
            raise QuizException(
                'Quiz type 2 error: ' + str(qna) + '\n' +
                str(type(e)) + ': ' + str(e))

    @staticmethod
    def delete(quiz_no):
        ndbi.delete_entity(QnARecord, quiz_no = quiz_no)

    @staticmethod
    def get_log(qna):
        target, choices = question(qna)
        log = str(target) + ' --> '
        num = 1
        for choice in choices:
            log += str(num) + ') ' + choice + ' '
            num += 1
        return log

def get_quiz_no():
    return random.randint(1, 65535)
    # return increase_counter(seq_counter)

# page rendering
def quiz_input(user = None):
    try:
        quiz_no = request.args.get('no')
        if quiz_no == None:
            return redirect(url_for('quiz_and_result',
                                    no = get_quiz_no(),
                                    user = user))
        content = get_random_words(4)
        answer = random.randint(0, len(content) - 1) + 1
        qna = QuestionAnswer(content, answer)
        quiz_types = [QuizGenerator.get_type1,
                      QuizGenerator.get_type2]
        get_type = quiz_types[random.randint(0, 1)]
        #target, choices = get_type(qna, int(quiz_no))
        target, choices = QuizGenerator.get_type1(qna, int(quiz_no))
        numbered_choices = []
        for choice in choices:
            numbered_choices.append({'num': len(numbered_choices) + 1,
                                     'text': choice})
        return render_template('quiz.html',
                               style_url = style_url(),
                               user = user,
                               target = target,
                               choices = numbered_choices)
    except Exception as e:
        return error_page(str(e), 'quiz_and_result', user = user)

def quiz_result(user = None):
    try:
        quiz_no = int(request.args.get('no', ''))
        user_answer = request.form['choice']
        qna = QuizGenerator.load(quiz_no)
        QuizGenerator.delete(quiz_no)
        return render_template('quiz_result.html',
                               style_url = style_url(),
                               user = user,
                               result = qna.evaluate(int(user_answer)),
                               answer = qna.answer,
                               choices = qna.choices,
                               next_url = url_for('quiz_and_result',
                                                  user = user))
    except Exception as e:
        return error_page(str(e), 'quiz_and_result', user = user)

def quiz_file_upload():
    return render_template('file_upload.html',
                           style_url = style_url())

def quiz_file_upload_result():
    try:
        worddefs = parse_file(request.files['uploaded'])
        store_count = 0
        ignore_count = 0
        for (word, definition) in worddefs:
            try:
                add_worddef(word, definition)
                store_count += 1
            except WordDefException:
                ignore_count += 1
                continue
        return render_template('file_upload_result.html',
                               style_url = style_url(),
                               store_count = store_count,
                               ignore_count = ignore_count)
    except Exception as e:
        return error_page('quiz_file_upload_result(): ' + str(e),
                          'upload_file')
        
# unit test
if __name__ == '__main__':
    sample = [('a', 'description of a'),
              ('b', 'description of b'),
              ('c', 'description of c'),
              ('d', 'description of d')]
    qna = QuestionAnswer(sample)
    print 'correct answer: ' + str(qna.answer)
    print qna.evaluate(qna.answer)
    print qna.evaluate(5 - qna.answer)
