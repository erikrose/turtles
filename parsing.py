"""A disembodied piece of code to parse Turtle code

Hey, you've got to start somewhere! :-D

"""
from parsimonious import Grammar


grammar = Grammar(r"""
    list = bracketed_list  # / block
    bracketed_list = "[" _ item* "]" _
    block = ~r"\n" dent

    # Parens are just like lists but can be treated differently by a dialect.
    # For example, the "do" dialect evaluates them immediately rather than
    # lazily.
    paren = "(" _ item* ")" _

    # An item is an element of a list.
    item = path / number / word / text / list / paren

    # Words are barewords, unquoted things, other than literals, that can live
    # in lists. We may renege on some of these chars later, especially ".". We
    # may add Unicode.
    word = spaceless_word _
    spaceless_word = ~r"[a-z`~!@#$%^&*-_+=|\\:;\"'<>,.?][a-z0-9`~!@#$%^&*-_+=|\\:;\"'<>,.?]*"i

    # Strings are multiline atm. This may change if we find a reason.
    text = spaceless_text _
    spaceless_text = (~'"[^"\\\\]*(?:\\\\.[^"\\\\]*)*"'is /
                      ~"'[^'\\\\]*(?:\\\\.[^'\\\\]*)*'"is)

    number = int / decimal
    int = spaceless_int _
    spaceless_int = ~r"[0-9]+"
    decimal = ~r"[0-9]*\.?[0-9]+" _

    path = path_item ("/" path_item)+
    path_item = spaceless_word / spaceless_text / spaceless_int

    _ = ~r"[ \t]*"

    """)


def parse(text):
    return grammar.parse(text)


dent_re = re.compile(r'[ \t]*(?=\S)')
class IndentTracker(object):
    def __init__(self):
        self.dents = []  # a stack of ints, each being the number of whitespace chars indenting the line at that indentation level
        self.pos = 0
        self.level = 0  # number of whitespace chars the line beginning at ``self.pos`` is indented. This is used to yield matches on successive dedent() calls iff a line dedents more than one notch.

    @expression
    def dedent(self, text, pos):
        match = dent_re.match(text, pos)  # Optimization: move this to a Regex expr that's a member of this so it can be cached. Make this a Compound subclass.
        if match:
            level = len(match.group(0))
            
            if level < self.dents
# Maybe it'd be simpler and faster just to have a pre-phase that .splitlines() the whole source and stores a map of which lines dent, which way, and how much. Then the custom rule can just do a lookup on that, plus it can be cacheable.

grammar = Grammar(r"""
    block = indent clause (clause / block)* dedent
    clause = samedent somestuff
    """,
    dedent = 
    

# If we're going to have stateful custom rules, those are context-sensitive and cannot be cached. Neither can anything that depends on them be cached, so we have to percolate the _is_cacheable = False up during compilation.