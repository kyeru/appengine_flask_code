import random
import time
from sys import stderr

from flask import redirect, request, url_for
from google.appengine.ext import ndb

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *
from mymodules.namedef import *
from mymodules.user import *


#
# ndb schema
#


class Category(ndb.Model):
    name = ndb.StringProperty()


class Scores(ndb.Model):
    category = ndb.StringProperty()
    timestamp = ndb.FloatProperty()
    question_count = ndb.IntegerProperty()
    correct_count = ndb.IntegerProperty()


#
# exception
#


class QuizException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '[QuizException] ' + self.message


#
# classes and functions
#


class QuestionMaker:
    def __init__(self, user, category):
        self.choices = content = get_random_items(user, category, 4)
        self.answer = random.randint(0, len(content) - 1) + 1

    def __str__(self):
        return str(self.choices) + ' (' + str(self.answer) + ')'

    def choice_type1(self):
        return self.answer, self.choices


# class QuizGenerator:
#     def __init__(self, qna, quiz_no):
#         self.qna = qna
#         self.quiz_no = quiz_no

#     def choice_type1(self):
#         try:
#             target, description = self.qna.choices[self.qna.answer - 1]
#             choices = []
#             for name, description in self.qna.choices:
#                 choices.append(description)
#             ndbi.create(QnARecord,
#                         ancestor = current_user(),
#                         quiz_no = self.quiz_no,
#                         answer = self.qna.answer,
#                         choices = choices)
#             return target, choices
#         except Exception as e:
#             return QuizException('Quiz type 1 error: ' + str(e))


def read_categories(user):
    categories = ndbi.read_entities(Category,
                                    0,
                                    ancestor = user)
    return [category.name for category in categories]


#
# Quiz
#

max_round = 5

def quiz_list():
    c1 = set(read_categories(current_user()))
    c2 = set(read_categories(anonymous()))
    categories = c1.union(c2)
    return renderer.render_page('quiz_list.html',
                                categories = categories)


def show_question(category):
    try:
        if not 'quiz_id' in session:
            session['quiz_id'] = random.randint(0, 1000000)
            session['begin_time'] = time.time()
            session['round_num'] = 0
            session['correct_count'] = 0
            # session['qa_history'] = []
            # return redirect(url_for('run_quiz', category = category))

        session['round_num'] += 1
        round_num = session['round_num']

        answer, choices = \
            QuestionMaker(current_user(), category).choice_type1()
        numbered_choices = []
        for i in range(len(choices)):
            name, definition = choices[i]
            numbered_choices.append({'num': i + 1, 'text': definition})
        session['choices'] = choices
        session['answer'] = answer
        target, _ = choices[answer - 1]
        
        return renderer.render_page('quiz.html',
                                    target = target,
                                    question_number = round_num,
                                    total_count = max_round,
                                    choices = numbered_choices)
    except Exception as e:
        return renderer.error_page(str(e), 'run_quiz')


def evaluate_result(category):
    try:
        round_num = session['round_num']
        correct_answer = session['answer']
        user_choice = int(request.form['choice'])

        is_correct = (correct_answer == user_choice)
        if is_correct:
            session['correct_count'] = session['correct_count'] + 1
            
        choices = session['choices']
        numbered_choices = []
        for i in range(len(choices)):
            name, definition = choices[i]
            numbered_choices.append({'num': i + 1, 'text': definition})
                
        if round_num < max_round:
            return renderer.render_page(
                'quiz_result.html',
                result = is_correct,
                your_answer = user_choice,
                correct_answer = correct_answer,
                choices = numbered_choices,
                next_url = url_for('run_quiz', category = category))
        else:
            session.pop('quiz_id')
            ndbi.create(Scores,
                        ancestor = current_user(),
                        category = category,
                        timestamp = session['begin_time'],
                        question_count = round_num,
                        correct_count = session['correct_count'])
            return renderer.render_page(
                'quiz_result.html',
                result = is_correct,
                your_answer = user_choice,
                correct_answer = correct_answer,
                choices = numbered_choices,
                final_url = url_for('show_scores', category = category))
    except Exception as e:
        return renderer.error_page(str(e), 'default')


#
# Score
#

def show_scores(category):
    categories = []
    if category == None:
        categories = ndbi.read_entities(Category, 0)
        categories = [c.name for c in categories]
    else:
        categories.append(category)

    all_histories = []
    for c in categories:
        score_history = ndbi.read_entities(
            Scores,
            20,
            sort = 'timestamp',
            ancestor = current_user(),
            category = c)
        score_history.reverse()
        numbered_history = [(i + 1, score_history[i])
            for i in range(len(score_history))]
        all_histories.append((c, numbered_history))
    return renderer.render_page('scores.html',
                                all_histories = all_histories)


#
# unit test
#


if __name__ == '__main__':
    pass
    # sample = [('a', 'description of a'),
    #           ('b', 'description of b'),
    #           ('c', 'description of c'),
    #           ('d', 'description of d')]
    # qna = QuestionAnswer(sample)
    # print 'correct answer: ' + str(qna.answer)
