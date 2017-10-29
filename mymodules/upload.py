from flask import request

from mymodules import ndbi
from mymodules import renderer
from mymodules.counter import *
from mymodules.item import *
from mymodules.quiz import Category
from mymodules.user import *


#
# class and functions
#


def parse_file(f):
    word_defs = []
    line_num = 0
    for entry in f.read().strip().split('\n'):
        line_num += 1
        # word_def = entry.decode('euc-kr').encode('utf8').split('\t')
        word_def = entry.split('\t')
        if len(word_def) != 2:
            raise Exception(
                'parse_file(): line %d invalid format' % line_num)
        word_defs.append((str(word_def[0]), str(word_def[1])))
    return word_defs


def create_category(user, category):
    if ndbi.read(Category, ancestor = user, name = category) == None:
        ndbi.create(Category,
                    ancestor = user,
                    name = category,
                    item_count = 0)


#
# page rendering
#


def quiz_file_upload():
    return renderer.render_page('file_upload.html')


def quiz_file_upload_result():
    try:
        items = parse_file(request.files['uploaded'])
        category = request.form['category']
        create_category(current_user(), category)
        store_count = 0
        ignore_count = 0
        for (name, definition) in items:
            try:
                add_item(current_user(), category, name, definition)
                store_count += 1
            except Exception:
                ignore_count += 1
                continue
        return renderer.render_page('file_upload_result.html',
                                    store_count = store_count,
                                    ignore_count = ignore_count)
    except Exception as e:
        return renderer.error_page('quiz_file_upload_result(): ' + str(e),
                                   'upload_file')
