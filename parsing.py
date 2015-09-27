"""A disembodied piece of code to parse Turtle code

Hey, you've got to start somewhere! :-D

"""
import re

from parsimonious import Grammar
from parsimonious.utils import Token

from turtles.exceptions import LexError


grammar = Grammar(r"""
    list = bracketed_list  # / block
    bracketed_list = "[" _ item* "]" _

    # Parens are just like lists but can be treated differently by a dialect.
    # For example, Rebol's "do" dialect evaluates them immediately rather than
    # lazily.
    paren = "(" _ item* ")" _

    # An item is an element of a list.
    item = path / number / text / colon_word / word / list / paren

    # Words are barewords, unquoted things, other than literals, that can live
    # in lists. We may renege on some of these chars later, especially ".". We
    # may add Unicode.
    word = spaceless_word _
    colon_word = spaceless_word ":" _
    spaceless_word = ~r"[-a-z`~!@#$%^&*_+=|\\;<>,.?][-a-z0-9`~!@#$%^&*_+=|\\;<>,.?]*"i

    # Strings are multiline atm. This may change if we find a reason.
    text = spaceless_text _
    spaceless_text = (~'"[^"\\\\]*(?:\\\\.[^"\\\\]*)*"'is /
                      ~"'[^'\\\\]*(?:\\\\.[^'\\\\]*)*'"is)

    number = int / decimal
    int = spaceless_int _
    spaceless_int = ~r"[0-9]+"
    decimal = ~r"[0-9]*\.?[0-9]+" _

    path = path_item ("/" path_item)+ _
    path_item = spaceless_word / spaceless_text / spaceless_int

    _ = meaninglessness*
    meaninglessness = whitespace / comment
    whitespace = ~r"\s+"  # TODO: Exclude vertical whitespace when we make it significant.
    comment = ~r"--[^\r\n]*"

    """)

# TokenGrammar:
r"""
file = (newline / statement)*
statement = brace / block
brace = "{" simple_statement ...whatever
block = statement_unindented / statement_indented
statement_indented = indent statement dedent

file = line*
statement = word
suite = 
line = "word" / block
block = "newline" "indent" stuff "dedent"

suite = simple / compound
simple = 
compound = "indent" suite "dedent"

suite = "indent" expression "dedent"
expression = 
"""


def parse(text):
    return grammar.parse(list(lex(text)))


TOKEN_RE = re.compile(r'(?P<skipped_line>\n[ \t]*(?:#.*|)$)|'
                      # ^ A line that's just whitespace and/or comment
                      r'(?P<newline_and_dent>\n(?P<dent>[ \t]*))|'
                      r'(?P<bracket>\[)|'
                      r'(?P<end_bracket>\])|'
                      r'(?P<horizontal_whitespace>[ \t]+)|'
                      r'(?P<word>[-a-zA-Z]+)|'
                      r'(?P<unmatched>.)',
                      flags=re.M)
def lex(text):
    """Scan a string, and break it down into an iterable of Tokens."""
    indents = ['']  # The indents we're inside of
    for match in TOKEN_RE.finditer(text):
        type = match.lastgroup
        if type == 'newline_and_dent':
            yield Token('newline')
            old_indent = indents[-1]
            new_indent = match.group('dent')
            if new_indent == old_indent:
                pass
            elif new_indent.startswith(old_indent) and len(new_indent) > len(old_indent):
                yield Token('indent')
                indents.append(new_indent)
            elif old_indent.startswith(new_indent):
                # Emit outdents while we can still outdent a level without
                # going farther left than the new indent:
                while indents != [''] and indents[-2].startswith(new_indent):
                    indents.pop()
                    yield Token('outdent')

                # See if we need a partial outdent:
                if indents != [''] and len(indents[-1]) > len(new_indent) and indents[-1].startswith(new_indent):  # We still have to go out farther, but we need to split an indent to do it.
                    # Chop the new_indent off the end of the top indent of the
                    # stack:
                    indents[-1] = indents[-1][:-len(new_indent)]
                    yield Token('partial_outdent')
            else:
                raise LexError("Indentation was not consistent. The whitespace characters that make up each indent must be either an addition to or a truncation of the ones in the indent above. You can't just swap out tabs for spaces between lines.")
        elif type == 'unmatched':
            raise LexError('Unrecognized token')
        elif type not in ('horizontal_whitespace', 'skipped_line'):  # We aren't interested in emitting these.
            yield Token(type)
    # Close all remaining open indents:
    for _ in xrange(len(indents) - 1):
        yield Token('outdent')


# TODO: Ignore indents inside parens and brackets. Keep track of the stack of them, and ignore dents inside any openers at all.
# NEXT: A skipped blank or more indented empty line between indented ones shouldn't touch indent level.
# More next: implement the visitor, function definition, and dispatch.
