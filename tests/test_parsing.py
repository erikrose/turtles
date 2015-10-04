from nose import SkipTest
from nose.tools import eq_, assert_raises
from parsimonious import ParseError
from parsimonious.nodes import Node, RegexNode
from parsimonious.utils import Token as T

from turtles.parsing import lex, parse, grammar

# To turn into tests:
"""
'[deferred thing]
'[8]  --comment
"""
# Bracketed constructs should ultimately lose their brackets:
# show "hey"
# frob thing with thong
# 1 + 2

# Quoted bracketed constructs should get just brackets:
# '["this" "thing"] --> ["this" "thing"]
# '[[] []] --> [[] []]
# '[key: value key2: value2 orphan] --> [key: value key2: value2 orphan]
# '[8] --> [8]  --comment
# Solved: How do we distinguish between something we're supposed to run and a plain old list? A quote? A different kind of bracket? The lack of brackets? A dialect specifier? A form, like (quote (some list)). We can abbreviate it, like '(some list).

def test_int():
    raise SkipTest
    s = '8'
    eq_(grammar['item'].parse(s), Node('item', s, 0, 1, children=[Node('number', s, 0, 1, children=[Node('int', s, 0, 1, children=[RegexNode('spaceless_int', s, 0, 1), RegexNode('_', s, 1, 1)])])]))


def test_no_brackets_in_words():
    """Don't let barewords suck up end brackets."""
    raise SkipTest
    assert_raises(ParseError, grammar['word'].parse, ']')


def test_smoke():
    """Smoke-test all the constructs."""
    raise SkipTest
    parse('[8]')
    parse('[show "hey"]')
    parse('[frob thing with thong]')
    parse('["this" "thing"]')
    parse('[[] []]')
    parse('[key: value key2: value2 orphan]')
    parse('[1 + (2 + 3)]')
    parse('[funcs: [term/on-red 8 "foo"]]')


def test_comments():
    raise SkipTest
    # TODO: Replace this uncompared calls to parse() with something better once
    # we get visitation going. The tree structure is too brittle until then to
    # test against.
    parse("""[8 -- comment
             "teen"]""")
    parse('["hey -- dude"]')


def test_lex():
    eq_(list(lex('[  ]')), [T('bracket'),
                            T('end_bracket')])
    eq_(list(lex(
"""foo
    bar""")), [T('word'), T('newline'), T('indent'), T('word'), T('outdent')])
    eq_(list(lex(
"""foo
  bar
baz""")), [T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('outdent'), T('word')])
    eq_(list(lex(
"""
if smoo
    love
  else
    if things
        buck
  elves
    nope
""")), [T('newline'), T('word'), T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('partial_outdent'), T('word'), T('newline'), T('indent'), T('word'), T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('outdent'), T('outdent'), T('word'), T('newline'), T('indent'), T('word'), T('outdent'), T('outdent')])
    # Try mixing tabs and spaces:
    eq_(list(lex("""
hi
    smoo
    \t\tbar
    \thi""")), [T('newline'), T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('partial_outdent'), T('word'), T('outdent'), T('outdent')])


def test_ignore_empty_line_dents():
    """Empty lines or ones consisting wholly of spaces shouldn't affect the
    indentation."""
    eq_(list(lex("""foo\n        \n  bar\nbaz""")),
        [T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('outdent'), T('word')])
    eq_(list(lex(
"""foo
  bar
  baz""")),
        [T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('word'), T('outdent')])
    eq_(list(lex(
"""foo
  bar

  baz""")),
        [T('word'), T('newline'), T('indent'), T('word'), T('newline'), T('word'), T('outdent')])


def test_ignore_newlines_inside_brackets():
    """Like in Python, newlines and dents shouldn't mean anything inside
    parenthesized or bracketed expressions."""
    eq_(list(lex(
"""reem [
    stir
] turv""")), [T('word'), T('bracket'), T('word'), T('end_bracket'), T('word')])
    eq_(list(lex(
"""reem (
    stir
) turv""")), [T('word'), T('paren'), T('word'), T('end_paren'), T('word')])
