import urllib2
import re
from xml.etree import ElementTree

def fetch_page(url):
    return urllib2.urlopen(url).read().replace('&nbsp', ' ')

# unused
def find_all_matched(root, tag, attr):
    """ Find all nodes whose tag name and attribute are matched
        the parameter in the (sub)tree starting from root."""
    matched = []
    if root.tag == tag and root.attr == attr:
        matched.append(root)
    for child in root:
        child_matched = find_all_matched(child, tag, attr)
        matched.extend(child_matched)
    return matched

def print_debug(text, line):
    lines = text.splitlines()
    if line < 1 or line > len(text):
        print 'wrong line number'
    else:
        print text.splitlines()[line - 1]

def get_word_definition(word, max_len=100):
    site = 'http://dictionary.reference.com/browse/'
    text = fetch_page(site + word)
    pattern = 'content="' + word + ' definition, ([^;]*)'
    searched = re.compile(pattern, flags=re.IGNORECASE).search(text)
    if searched == None:
        return 'definition not found'
    definition = searched.group(1)
    if len(definition) > max_len:
        return definition[:max_len-3] + '...'
    else:
        return definition[:max_len]
    
if __name__ == '__main__':
    """test"""
    words = ['vindictive', 'corroborate', 'dictionary', 'female']
    for word in words:
        print get_word_definition(word, 100)
