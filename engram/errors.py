import random
import sys

class EngramError(Exception):
    pass

class ErrorHandler:
    def __init__(self):
        self.error_prefixes = [
            "Unfortunately", "Regrettably", "Distressingly", "Unfortunately for you",
            "Against my better judgment", "With deep sorrow", "I regret to inform",
            "Painfully", "Crushingly", "Saddeningly", "Unfortunately indeed",
            "Most unfortunately", "To my disappointment"
        ]
        
        self.error_explanations = [
            "the interpreter's tea was too cold this morning",
            "a butterfly flapped its wings in Brazil causing turbulence in your code",
            "the ghosts in the machine are闹 (that's Chinese for 'making trouble')",
            "your code invoked the wrath of the semicolon mafia",
            "the invisible pink unicorn is displeased",
            "entropy has increased in your program by 0.0000001 joules",
            "the cookie jar was empty and the interpreter is cranky",
            "your syntax went on vacation to Bermuda and didn't come back",
            "the programming faeries are on strike today",
            "someone spelled 'potato' wrong and now reality is confused",
            "the quantum bits are in a superposition of wrong and more wrong",
            "your code is so confusing even the error messages are confused",
            "the Great Cthulhu hasawakened and your code disturbs his slumber"
        ]
        
        self.error_suggestions = [
            "perhaps try whispering your code more politely?",
            "have you tried sacrificing a semicolon to the code gods?",
            "maybe your variables need a hug? They're feeling undefined.",
            "try adding 'please' before your statement, it sometimes helps",
            "have you considered that your code might just be... too creative?",
            "perhaps the universe isn't ready for your brilliance yet",
            "try turning it off and on again, but also pray to the binary gods",
            "your code has successfully confused 47 error messages and counting",
            "have you tried speaking slower? The interpreter is hard of hearing",
            "maybe try using words the interpreter actually understands"
        ]
        
        self.error_specifics = {
            "parse_print": "The words you used to express output are unknown to the ancient scrolls. Try 'say:', 'announce:', 'communicate:', or one of the {count} other accepted verbs.",
            "parse_set": "The variable assignment syntax has gone on strike. Try 'set X to Y' or 'let X be Y'.",
            "parse_input": "Listening for input requires specifying where to store. Try 'listen into variable_name'.",
            "parse_arithmetic": "The math operators need clearer instructions. Try 'add X to Y', 'subtract X from Y', etc.",
            "parse_if": "The conditional statement has existential doubts. Try 'if X equals Y then'.",
            "parse_condition": "The comparison operator is playing hard to get. Try 'equals', 'greater than', etc.",
            "loop": "The loop construct lost track of repetitions. Try 'loop 5 times ... end'.",
            "variable_not_found": "The variable '{var}' is playing hide and seek. Define it with 'set {var} to value'.",
            "division_by_zero": "You attempted to divide by zero. Congratulations, you've broken mathematics.",
            "invalid_expression": "The expression '{expr}' makes no sense to the interpreter.",
            "unexpected_end": "An 'end' appeared where it wasn't expected.",
            "unclosed_quote": "A quote mark has wandered off. Please pair your quotes.",
            "nested_depth": "Nesting too deep will cause the interpreter to dream of electric sheep.",
            "empty_code": "The code is emptier than a void in a vacuum in space.",
            "file_not_found": "The file '{filename}' seems to have entered witness protection.",
            "indent_error": "Indentation inconsistency detected. Be consistent.",
            "unknown_command": "The command '{cmd}' was not recognized.",
            "type_mismatch": "Cannot perform {operation} between '{left}' ({left_type}) and '{right}' ({right_type}).",
            "negative_loop": "Looping a negative number of times is philosophically problematic.",
            "reserved_word": "The word '{word}' is reserved. Pick a different word.",
            "function_syntax": "Function definitions require 'function name parameters... end'.",
            "return_outside_function": "Cannot return from outside a function.",
            "file_read_error": "Could not read file '{filename}': {details}",
            "unknown_error": "You literally have no idea what you're doing.",
            "function_not_found": "Function '{func}' doesn't exist. Did you even define it?",
            "delete_error": "Cannot '{action}' '{target}'. It doesn't exist.",
            "parameter_error": "Function '{func}' expected {expected} parameters but received {received}.",
            "unknown_command": "What the fuck is this? Fix your shit.",
            "empty_code": "There's literally nothing here. Are you high?",
            "invalid_expression": "That's not valid. Try actually thinking.",
            "division_by_zero": "You can't divide by zero. This is basic math you dumbass.",
            "negative_loop": "Negative loops are mathematically impossible. Think about it.",
            "nested_depth": "Your nesting is too deep. Use your brain.",
            "file_not_found": "File doesn't exist. Try actually existing.",
            "variable_not_found": "Variable '{var}' doesn't exist. Define it first."
        }
        
        self.insults = [
            "You fucking suck.",
            "God you're bad at this.",
            "Did you even read the documentation?",
            "This is embarrassing to watch.",
            "What even is this code?",
            "You need to touch grass.",
            "I've seen better code from a golden retriever.",
            "This is why people hate programmers.",
            "Please stop. Just stop.",
            "Your code is an insult to programming.",
            "I could write this better blindfolded.",
            "This is genuinely sad to look at.",
            "Go outside. Touch some grass.",
            "Your mother was a hamster and your father smelt of elderberries.",
            "Error 418: I'm a teapot and you're a piece of shit."
        ]
    
    def raise_error(self, error_type: str, **kwargs):
        specific = self.error_specifics.get(error_type)
        
        unknown_errors = ["unknown_command", "unknown_error", "invalid_expression", "empty_code"]
        
        truly_unknown = False
        if error_type == "unknown_command":
            cmd = kwargs.get("cmd", "")
            if not cmd:
                truly_unknown = True
            elif "set" in cmd.lower() or "say" in cmd.lower() or "add" in cmd.lower() or "if" in cmd.lower() or "loop" in cmd.lower():
                pass
            else:
                truly_unknown = True
        elif error_type == "empty_code":
            truly_unknown = True
        elif error_type == "invalid_expression":
            expr = kwargs.get("expr", "")
            if not expr:
                truly_unknown = True
        
        if truly_unknown:
            insult = random.choice(self.insults)
            print(f"Error at line unknown. Error type: {error_type}, Fix code please.", file=sys.stderr)
            print(insult, file=sys.stderr)
            raise EngramError(f"Error. {insult}")
        
        if kwargs:
            try:
                specific = specific.format(**kwargs)
            except (KeyError, TypeError):
                specific = "What the fuck is this?"
        
        line_num = kwargs.get('line')
        if line_num is None:
            line_num = 'unknown'
        
        print(f"Error at line {line_num}. Error type: {error_type}, Fix code please.", file=sys.stderr)
        raise EngramError(f"Error: {specific}")