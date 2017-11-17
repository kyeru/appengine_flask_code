from flask import flash, request

from mymodules import ndbi
from mymodules import renderer
from mymodules.item import Item
from mymodules.user import get_user_key


#####################################################################
# class and functions
#####################################################################

def delete_quiz_material(user, category):
	ndbi.delete(Counter,
				ancestor = get_user_key(user),
				name = category)
	ndbi.delete_all(Item,
					ancestor = get_user_key(user),
					category = category)
	flash('Category ' + category + ' of user ' + user + ' deleted')

# def delete_garbage_record(user):
# 	try:
# 		ndbi.delete(QnARecord,
# 					ancestor = get_user_key(user))
# 	except ndbi.NDBIException as e:
# 		return

#####################################################################
# page rendering
#####################################################################

def admin_board():
	return renderer.render_page('admin.html')

def admin_action():
	user_name = request.form['user']
	category = request.form['category']
	try:
		if user_name != '' and category != '':
			delete_quiz_material(user_name, category)
		delete_garbage_record(user_name)
		return renderer.render_page('admin.html')
	except ndbi.NDBIException as e:
		return renderer.error_page(str(e),
								   'admin_start')
