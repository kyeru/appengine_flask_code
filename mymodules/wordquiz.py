import random

class QuizException:
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

class QuizGenerator:
    def __init__(self, entries = []):
        self.entries = entries
        if len(entries) == 0:
            self.answer = 0
        else:
            self.answer = random.randint(0, len(entries) - 1) + 1

    @classmethod
    def load_quiz(seq_num):
        entrie
        return QuizGenerator(entries)
    
    def question(self):
        if len(self.entries) <= 0:
            return '', []
        
        choices = []
        try:
            target, description = self.entries[self.answer - 1]
            for name, description in self.entries:
                choices.append(description)
            return target, choices
        except Exception:
            raise QuizException(str(self.answer) +
                                '/' +
                                str(len(self.entries)))

    def question_string(self):
        target, choices = self.question()
        question = target + ' --> '
        num = 1
        for choice in choices:
            question += str(num) + ') ' + choice + ' '
            num += 1
        question += str(self.answer)
        return question

    def get_answer_num(self):
        return self.answer

    def evaluate(self, answer_num):
        return self.answer == answer_num

# test
if __name__ == '__main__':
    sample = [('a', 'description of a'),
              ('b', 'description of b'),
              ('c', 'description of c'),
              ('d', 'description of d')]
    quiz = QuizGenerator(sample)
    print quiz.question_string()
    print 'correct answer: ' + str(quiz.get_answer_num())
    print quiz.evaluate(quiz.get_answer_num())
    print quiz.evaluate(5 - quiz.get_answer_num())
    print id(quiz)
