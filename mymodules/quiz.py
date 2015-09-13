import random
import time

from flask import redirect, request, url_for
from google.appengine.ext import ndb

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *
from mymodules.namedef import *
from mymodules.user import *

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

class QuizException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '[QuizException] ' + self.message

#####################################################################
# class and functions
#####################################################################

class QuestionAnswer:
    # def __init__(self, choices, answer):
    #     self.choices = choices
    #     self.answer = answer

    def __init__(self, user, category):
        self.choices = content = get_random_items(user, category, 4)
        self.answer = random.randint(0, len(content) - 1) + 1

    def __str__(self):
        return str(self.choices) + ' (' + str(self.answer) + ')'

class QuizGenerator:
    def __init__(self, qna, quiz_no):
        self.qna = qna
        self.quiz_no = quiz_no

    def choice_type1(self):
        try:
            target, description = self.qna.choices[self.qna.answer - 1]
            choices = []
            for name, description in self.qna.choices:
                choices.append(description)
            ndbi.create(QnARecord,
                        ancestor = current_user(),
                        quiz_no = self.quiz_no,
                        answer = self.qna.answer,
                        choices = choices)
            return target, choices
        except Exception as e:
            return QuizException('Quiz type 1 error: ' + str(e))

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

def generate_quiz_no():
    return random.randint(1, 65535)

def read_categories(user):
    categories = ndbi.read_entities(Category,
                                    0,
                                    ancestor = user)
    return [category.name for category in categories]

def pop_record(quiz_no):
    record = ndbi.read(QnARecord,
                       ancestor = current_user(),
                       quiz_no = quiz_no)
    if record == None:
        raise QuizException('Record "' + quiz_no + '" not exists.')
    ndbi.delete(QnARecord,
                ancestor = current_user(),
                quiz_no = quiz_no)
    return record.choices, record.answer

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
        if not 'quiz_no' in session:
            session['timestamp'] = time.time()
            session['quiz_no'] = 0
            return redirect(url_for('quiz_start',
                                     category = category,
                                     no = session['quiz_no']))
        else:
            session['quiz_no'] = session['quiz_no'] + 1

        quiz_no = session['quiz_no']
        common = category in read_categories(anonymous())
        user = anonymous() if common else current_user()
        qna = QuestionAnswer(user, category)

        # content = get_random_items(user, category, 4)
        # answer = random.randint(0, len(content) - 1) + 1
        # qna = QuestionAnswer(content, answer)
        quiz_gen = QuizGenerator(qna, quiz_no)
        target, choices = quiz_gen.choice_type1()
        numbered_choices = []
        for choice in choices:
            numbered_choices.append({'num': len(numbered_choices) + 1,
                                     'text': choice})
        return renderer.render_page('quiz.html',
                                    target = target,
                                    choices = numbered_choices)
    except Exception as e:
        return renderer.error_page(str(e), 'quiz_start')

max_round = 5

def evaluate_result(category):
    try:
        quiz_no = session['quiz_no']
        choices, correct_answer = pop_record(quiz_no)

        user_answer = int(request.form['choice'])
        is_correct = (correct_answer == user_answer)
        if get_user_id() != None:
            update_grade_record(category, is_correct)
        next_url = url_for('quiz_start', category = category)
        grade_url = url_for('print_grade', category = category)
        numbered_choices = []
        for c in choices:
            numbered_choices.append({'num': len(numbered_choices) + 1,
                                     'text': c})
        if quiz_no < max_round:
            return renderer.render_page('quiz_result.html',
                                        result = is_correct,
                                        your_answer = user_answer,
                                        correct_answer = correct_answer,
                                        choices = numbered_choices,
                                        next_url = next_url)
        else:
            session.pop('quiz_no')
            return renderer.render_page('quiz_result.html',
                                        result = is_correct,
                                        your_answer = user_answer,
                                        correct_answer = correct_answer,
                                        choices = numbered_choices,
                                        grade_url = grade_url)
    except Exception as e:
        return renderer.error_page(str(e), 'quiz_start')

def check_grade(category):
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
    pass
    # sample = [('a', 'description of a'),
    #           ('b', 'description of b'),
    #           ('c', 'description of c'),
    #           ('d', 'description of d')]
    # qna = QuestionAnswer(sample)
    # print 'correct answer: ' + str(qna.answer)
