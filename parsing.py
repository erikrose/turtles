"""A disembodied piece of code to parse Turtle code

Hey, you've got to start somewhere! :-D

"""
import re

from parsimonious import Grammar
from parsimonious.utils import Token


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


def parse(text):
    return grammar.parse(list(lex(text)))


TOKEN_RE = re.compile(r'(?P<newline>\n)|'
                      # Can't just make this '^ *', because finditer omits
                      # overlapping matches, making an empty indent still eat a
                      # char:
                      r'(?P<dent>^ +)|'
                      r'(?P<bracket>\[)|'
                      r'(?P<end_bracket>\])|'
                      r'(?P<horizontal_whitespace>[ \t]+)|'
                      r'(?P<word>[-a-zA-Z]+)',
                      flags=re.M)
def lex(text):
    """Scan a string, and break it down into an iterable of Tokens."""
    indent_level = 0
    openers = []  # ['(', '[', '(', '(']
    just_saw_newline = False  # Keep track of whether the previous token was a newline, so we can detect empty indents.
    for match in TOKEN_RE.finditer(text):
        type = match.lastgroup
        if type == 'newline':
            just_saw_newline = True
        else:
            contents = match.group()
            type_is_dent = type == 'dent'
            if (type_is_dent or
                just_saw_newline):  # Newline was followed by a non-indent
                                    # token, so indent is 0.
                dent_length = len(contents) if type_is_dent else 0
                new_level, remainder = divmod(dent_length, 2)
                if remainder:
                    raise LexError('Indentation was not a multiple of 2 spaces.',
                                   match.span())
                dent_type = 'indent' if new_level > indent_level else 'dedent'
                for _ in xrange(abs(new_level - indent_level)):
                    yield Token(dent_type)
                indent_level = new_level

            just_saw_newline = False
            if not type_is_dent:
                yield Token(type)

# TODO: Ignore indents inside parens and brackets.
# Test: A skipped blank or more indented empty line between indented ones shouldn't touch indent level.

# NEXT: Probably implement indentation sensitivity. I want to start coding stuff, and I don't want to look at brackets.
# Or, implement the visitor, function definition, and dispatch.