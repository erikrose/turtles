from nose.tools import eq_

from turtles.parsing import parse


def test_lexer_single_line():
    """Make sure lexing a single line works."""
    eq_(parse('[8]'),
        [])
#    eq_(parse('[funcs: [term/on-red 8 "foo"]'),
#        [])

# TODO:
# * Inferred brackets around file
# * Indentation
# * Nested blocks