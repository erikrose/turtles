from nose.tools import eq_
from parsimonious.utils import Token as T

from turtles.lexing import lex

# To turn into tests:
"""
'[deferred thing]
'[8]  --comment
"""
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
