from nose.tools import eq_, assert_raises
from parsimonious import ParseError
from parsimonious.nodes import Node, RegexNode

from turtles.parsing import parse, grammar

# To turn into tests:
"""
'[deferred: thing]
'[8]  --comment
"""
# Bracketed constructs should ultimately lose their brackets:
# show: "hey"
# frob: thing with: thong
# 1 + 2

# Quoted bracketed constructs should get just brackets:
# '["this" "thing"] --> ["this" "thing"]
# '[[] []] --> [[] []]
# '[key: value key2: value2 orphan] --> [key: value key2: value2 orphan]
# '[8] --> [8]  --comment
# Solved: How do we distinguish between something we're supposed to run and a plain old list? A quote? A different kind of bracket? The lack of brackets? A dialect specifier? A form, like (quote (some list)). We can abbreviate it, like '(some list).

def test_int():
    s = '8'
    eq_(grammar['item'].parse(s), Node('item', s, 0, 1, children=[Node('number', s, 0, 1, children=[Node('int', s, 0, 1, children=[RegexNode('spaceless_int', s, 0, 1), RegexNode('_', s, 1, 1)])])]))


def test_no_brackets_in_words():
    """Don't let barewords suck up end brackets."""
    assert_raises(ParseError, grammar['word'].parse, ']')


def test_smoke():
    """Smoke-test all the constructs."""
    parse('[8]')
    parse('[show: "hey"]')
    parse('[frob: thing with: thong]')
    parse('["this" "thing"]')
    parse('[[] []]')
    parse('[key: value key2: value2 orphan]')
    parse('[1 + (2 + 3)]')
    parse('[funcs: [term/on-red 8 "foo"]]')


def test_comments():
    # TODO: Replace this uncompared calls to parse() with something better once
    # we get visitation going. The tree structure is too brittle until then to
    # test against.
    parse("""[8 -- comment
             "teen"]""")
    parse('["hey -- dude"]')
