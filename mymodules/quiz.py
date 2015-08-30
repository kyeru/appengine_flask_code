import random
import time

from flask import redirect, request, url_for
from google.appengine.ext import ndb

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *
from mymodules.user import *
from mymodules.namedef import *

#####################################################################
# ndb schema
#####################################################################

class Category(ndb.Model):
    name = ndb.StringProperty()

class QnARecord(ndb.Model):
    quiz_no = ndb.IntegerProperty()
    answer = ndb.IntegerProperty()
    choices = ndb.StringProperty(repeated = True)

class GradeRecord(ndb.Model):
    category = ndb.StringProperty()
    timestamp = ndb.FloatProperty()
    quiz_count = ndb.IntegerProperty()
    correct_count = ndb.IntegerProperty()

#####################################################################
# exception
#####################################################################

class QuizException:
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '[QuizException] ' + self.message

#####################################################################
# class and functions
#####################################################################

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
        record = ndbi.read(QnARecord,
                           ancestor = current_user(),
                           quiz_no = quiz_no)
        if record == None:
            raise QuizException('Record "' + quiz_no + '" not exists.')
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
            ndbi.create(QnARecord,
                        ancestor = current_user(),
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
            ndbi.create(QnARecord,
                        ancestor = current_user(),
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
        ndbi.delete(QnARecord,
                    ancestor = current_user(),
                    quiz_no = quiz_no)

    @staticmethod
    def get_log(qna):
        target, choices = question(qna)
        log = str(target) + ' --> '
        num = 1
        for choice in choices:
            log += str(num) + ') ' + choice + ' '
            num += 1
        return log

def update_grade_record(category, is_correct):
    grade = ndbi.read(GradeRecord,
                      ancestor = current_user(),
                      category = category,
                      timestamp = session['timestamp'])
    if grade == None:
        ndbi.create(GradeRecord,
                    ancestor = current_user(),
                    category = category,
                    timestamp = session['timestamp'],
                    quiz_count = 1,
                    correct_count = 1 if is_correct else 0)
    else:
        grade.quiz_count += 1
        grade.correct_count += 1 if is_correct else 0
        grade.put()

def get_quiz_no():
    return random.randint(1, 65535)

def parse_file(f):
    word_defs = []
    line_num = 0
    for entry in f.read().strip().split('\n'):
        line_num += 1
        word_def = entry.split('\t')
        if len(word_def) < 2:
            raise QuizException(
                'parse_file(): line %d invalid format' % line_num)
        word_defs.append((str(word_def[0]), str(word_def[1])))
    return word_defs

def read_categories(user):
    categories = ndbi.read_entities(Category,
                                    0,
                                    ancestor = user)
    return [category.name for category in categories]

#####################################################################
# page rendering
#####################################################################

def quiz_map():
    common_categories = read_categories(anonymous())
    your_categories = read_categories(current_user())
    return renderer.render_page('quiz_map.html',
                                common_categories = common_categories,
                                user_categories = your_categories)

def common_quiz_map():
    return renderer.render_page('quiz_map.html',
                                categories = read_categories(anonymous()))

def user_defined_quiz_map():
    user_categories = ndbi.read_entities(Category,
                                         0,
                                         ancestor = current_user())
    categories = []
    for category in user_categories:
        categories.append(category.name)
    return renderer.render_page('quiz_map.html',
                                categories = user_categories)

def quiz_input(category):
    try:
        if not 'timestamp' in session:
            session['timestamp'] = time.time()

        quiz_no = request.args.get('no')
        if quiz_no == None:
            return redirect(url_for('quiz_start',
                                     category = category,
                                     no = get_quiz_no()))

        common = category in read_categories(anonymous())
        user = anonymous() if common else current_user()

        content = get_random_items(user, category, 4)
        answer = random.randint(0, len(content) - 1) + 1
        qna = QuestionAnswer(content, answer)
        #quiz_types = [QuizGenerator.get_type1,
        #              QuizGenerator.get_type2]
        #get_type = quiz_types[random.randint(0, 1)]
        #target, choices = get_type(qna, int(quiz_no))
        target, choices = QuizGenerator.get_type1(qna, int(quiz_no))
        numbered_choices = []
        for choice in choices:
            numbered_choices.append({'num': len(numbered_choices) + 1,
                                     'text': choice})
        return renderer.render_page('quiz.html',
                                    target = target,
                                    choices = numbered_choices)
    except Exception as e:
        return renderer.error_page(str(e), 'quiz_start')

def evaluate_result(category):
    try:
        quiz_no = int(request.args.get('no', ''))
        qna = QuizGenerator.load(quiz_no)
        QuizGenerator.delete(quiz_no)

        user_answer = request.form['choice']
        is_correct = qna.evaluate(int(user_answer))
        if get_user_id() != None:
            update_grade_record(category, is_correct)
        next_url = url_for('quiz_start', category = category)
        grade_url = url_for('print_grade', category = category)
        return renderer.render_page('quiz_result.html',
                                    result = is_correct,
                                    answer = qna.answer,
                                    choices = qna.choices,
                                    next_url = next_url,
                                    grade_url = grade_url)
    except Exception as e:
        return renderer.error_page(str(e), 'quiz_start')

#####################################################################
# file upload
#####################################################################

def create_category(user, category):
    if ndbi.read(Category, ancestor = user, name = category) == None:
        ndbi.create(Category, ancestor = user, name = category)

def quiz_file_upload():
    return renderer.render_page('file_upload.html')

def quiz_file_upload_result():
    try:
        namedefs = parse_file(request.files['uploaded'])
        category = request.form['category']
        create_category(current_user(), category)
        initiate_counter(current_user(), category, overwrite = False)
        store_count = 0
        ignore_count = 0
        for (name, definition) in namedefs:
            try:
                add_item(current_user(), category, name, definition)
                store_count += 1
            except NameDefException:
                ignore_count += 1
                continue
        return renderer.render_page('file_upload_result.html',
                                    store_count = store_count,
                                    ignore_count = ignore_count)
    except Exception as e:
        return renderer.error_page('quiz_file_upload_result(): ' + str(e),
                                   'upload_file')

#####################################################################
# grade history
#####################################################################

def check_grade(category):
    if 'timestamp' in session:
        del session['timestamp']
    categories = []
    if category == None:
        categories = ndbi.read_entities(Category, 0)
        categories = [c.name for c in categories]
    else:
        categories.append(category)

    all_histories = []
    for c in categories:
        grade_history = ndbi.read_entities(GradeRecord,
                                           20,
                                           sort = 'timestamp',
                                           ancestor = current_user(),
                                           category = c)
        grade_history.reverse()
        numbered_history = [(i + 1, grade_history[i])
            for i in range(len(grade_history))]
        all_histories.append((c, numbered_history))
    return renderer.render_page('quiz_grade.html',
                                all_histories = all_histories)

#####################################################################
# unit test
#####################################################################

if __name__ == '__main__':
    sample = [('a', 'description of a'),
              ('b', 'description of b'),
              ('c', 'description of c'),
              ('d', 'description of d')]
    qna = QuestionAnswer(sample)
    print 'correct answer: ' + str(qna.answer)
    print qna.evaluate(qna.answer)
    print qna.evaluate(5 - qna.answer)
