"""A disembodied piece of code to parse Turtle code

Hey, you've got to start somewhere! :-D

"""
from parsimonious import Grammar


grammar = Grammar(r"""
    list = bracketed_list  # / block
    bracketed_list = "[" _ item* "]" _

    # Parens are just like lists but can be treated differently by a dialect.
    # For example, Rebol's "do" dialect evaluates them immediately rather than
    # lazily.
    paren = "(" _ item* ")" _

    # An item is an element of a list.
    item = path / number / text / word / list / paren

    # Words are barewords, unquoted things, other than literals, that can live
    # in lists. We may renege on some of these chars later, especially ".". We
    # may add Unicode.
    word = spaceless_word _
    spaceless_word = ~r"[-a-z`~!@#$%^&*_+=|\\:;<>,.?][-a-z0-9`~!@#$%^&*_+=|\\:;<>,.?]*"i

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
    return grammar.parse(text)
