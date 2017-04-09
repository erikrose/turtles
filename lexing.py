"""A lexer that takes apart Turtles syntax into indents, outdents, and words"""
import re

from parsimonious.utils import Token

from turtles.exceptions import LexError


TOKEN_RE = re.compile(r'(?P<skipped_line>\n[ \t]*(?:#.*|)$)|'
                      # ^ A line that's just whitespace and/or comment
                      r'(?P<newline_and_dent>\n(?P<dent>[ \t]*))|'
                      r'(?P<bracket>\[)|'
                      r'(?P<end_bracket>\])|'
                      r'(?P<paren>\()|'
                      r'(?P<end_paren>\))|'
                      r'(?P<horizontal_whitespace>[ \t]+)|'
                      r'(?P<word>[-a-zA-Z]+)|'
                      r'(?P<unmatched>.)',
                      flags=re.M)
def lex(text):
    """Scan a string, and break it down into an iterable of Tokens.

    At the moment, these are very language-independent: just alphabetic words
    separated by whitespace, along with whitespace-based indents.

    """
    indents = ['']  # The indents we're inside of
    openers = []  # Brackets or parens we're inside of
    for match in TOKEN_RE.finditer(text):
        type = match.lastgroup
        if type == 'newline_and_dent':
            if not openers:  # Ignore newlines inside parenthesize expressions.
                yield Token('newline')
                old_indent = indents[-1]
                new_indent = match.group('dent')
                if new_indent == old_indent:
                    pass
                elif (new_indent.startswith(old_indent) and
                      len(new_indent) > len(old_indent)):
                    yield Token('indent')
                    indents.append(new_indent)
                elif old_indent.startswith(new_indent):
                    # Emit outdents while we can still outdent a level without
                    # going farther left than the new indent:
                    while (indents != [''] and
                           indents[-2].startswith(new_indent)):
                        indents.pop()
                        yield Token('outdent')

                    # See if we need a partial outdent:
                    if (indents != [''] and
                        # We still have to go out farther, but we need to split
                        # an indent to do it.
                        len(indents[-1]) > len(new_indent) and
                        indents[-1].startswith(new_indent)):
                        # Chop the new_indent off the end of the top indent of
                        # the stack:
                        indents[-1] = indents[-1][:-len(new_indent)]
                        yield Token('partial_outdent')
                else:
                    raise LexError("Indentation was not consistent. The whitespace characters that make up each indent must be either an addition to or a truncation of the ones in the indent above. You can't just swap out tabs for spaces between lines.")
        elif type == 'unmatched':
            raise LexError('Unrecognized token')
        elif type in ('bracket', 'paren'):
            openers.append(type)
            yield Token(type)
        elif type in ('end_bracket', 'end_paren'):
            if openers:
                if openers[-1] == type[4:]:
                    openers.pop()
                    yield Token(type)
                else:
                    raise LexError('Found "%s", but, if you were going to close something, a %s was the most recently opened thing.' % (match.group(), openers[-1]))
            else:
                raise LexError('Found "%s", but there was no opener before it.')
        elif type not in ('horizontal_whitespace', 'skipped_line'):  # We aren't interested in emitting these.
            yield Token(type)
    # Close all remaining open indents:
    for _ in xrange(len(indents) - 1):
        yield Token('outdent')


# More next: implement the visitor, function definition, and dispatch.
