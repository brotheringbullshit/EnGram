import re
from typing import Any

class Lexer:
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.print_synonyms = [
            "say", "announce", "communicate", "return", "spit", "spit out", "convey",
            "echo", "output", "print", "display", "show", "present", "utter",
            "vocalize", "declare", "proclaim", "broadcast", "transmit", "publish",
            "reveal", "express", "voice", "pronounce", "articulate", "enounce",
            "recite", "narrate", "relay", "impart", "divulge", "expose"
        ]
        
        self.input_synonyms = [
            "listen", "hear", "receive", "capture", "gather", "obtain", "acquire",
            "accept", "collect", "fetch", "read", "scan", "sense", "perceive",
            "ask for input", "ask and wait for input", "have we got a input yet",
            "get input", "obtain input", "request input", "prompt for", "query"
        ]
        
        self.file_synonyms = [
            "write to file", "save to file", "store to file", "dump to file",
            "read from file", "load from file", "get from file", "open file",
            "append to file", "add to file",
            "create file", "make file", "new file",
            "delete file", "remove file", "erase file"
        ]
        
        self.set_synonyms = [
            "set", "let", "make", "assign", "establish", "create", "define",
            "configure", "store", "place", "put", "fix", "bind", "initialize"
        ]
        
        self.add_synonyms = [
            "add", "plus", "append", "increase", "augment", "extend", "supplement"
        ]
        
        self.subtract_synonyms = [
            "subtract", "minus", "remove", "decrease", "reduce", "diminish", "deduct"
        ]
        
        self.multiply_synonyms = [
            "multiply", "times", "scale", "double", "triple", "quadruple", "expand"
        ]
        
        self.divide_synonyms = [
            "divide", "split", "half", "partition", "separate", "distribute", "share"
        ]
        
        self.if_synonyms = [
            "if", "when", "provided", "assuming", "should", "given", "conditional",
            "did we get anything", "is there", "do we have", "check if",
            "in case", "just in case", "conditionally", "assuming that",
            "only if", "but if", "however if", "else if", "otherwise if"
        ]
        
        self.question_if_synonyms = [
            "are we there yet", "did we arrive", "has it happened",
            "is it done", "is it complete", "did it finish",
            "are we done", "is it over", "has it ended"
        ]
        
        self.return_check_synonyms = [
            "did", "does", "has", "have", "will", "would"
        ]
        
        self.else_synonyms = [
            "else", "otherwise", "instead", "alternative"
        ]
        
        self.end_synonyms = [
            "end", "finish", "done", "complete", "terminate", "stop", "cease"
        ]
        
        self.halt_synonyms = [
            "conclude", "wrap up", "expire", "halt", "HLT"
        ]
        
        self.loop_synonyms = [
            "loop", "repeat", "iterate", "cycle", "recur", "while", "during"
        ]
        
        self.break_synonyms = [
            "break", "stop loop", "exit loop", "quit loop", "terminate loop", "end loop"
        ]
        
        self.continue_synonyms = [
            "continue", "skip", "next", "next iteration", "jump"
        ]
        
        self.modulo_synonyms = [
            "modulo", "mod", "remainder", "rem"
        ]
        
        self.import_synonyms = [
            "import", "include", "load", "read", "source", "exec", "run",
            "bring in", "pull in", "fetch", "inject", "embed"
        ]
        
        self.string_synonyms = [
            "length of", "size of", "character count of",
            "character at", "char at", "letter at",
            "split", "divide", "separate",
            "iterate", "for each", "loop through",
            "count", "how many", "number of",
            "get arg at", "argument at", "arg number"
        ]
        
        self.compare_ops = {
            "equals": ("==", 1), "equal": ("==", 1), "is": ("==", 1), "same": ("==", 1),
            "notequals": ("!=", 1), "different": ("!=", 1), "unequal": ("!=", 1), "not": ("!=", 1),
            "greater than": (">", 2), "greater": (">", 1), "above": (">", 1), "more than": (">", 2),
            "less than": ("<", 2), "less": ("<", 1), "below": ("<", 1), "fewer than": ("<", 2),
            "greater or equal": (">=", 3), "atleast": (">=", 1), "more or equal": (">=", 3),
            "less or equal": ("<=", 3), "atmost": ("<=", 1), "fewer or equal": ("<=", 3)
        }
        
        self.stack_synonyms = [
            "push", "pop", "peek", "top", "stack push", "stack pop", "stack peek",
            "is empty", "is stack empty", "stack size", "stack length"
        ]
        
        self.array_synonyms = [
            "create array", "make array", "new array", "array with",
            "push to array", "add to array", "append to array",
            "pop from array", "remove from array",
            "get from array", "array at", "array index",
            "set array at", "array length", "array size"
        ]
        
        self.object_synonyms = [
            "create object", "make object", "new object", "object with",
            "set property", "set attribute", "set field",
            "get property", "get attribute", "get field",
            "object property", "object attribute", "object field",
            "has property", "has attribute", "has field",
            "delete property", "delete attribute", "remove property"
        ]
        
        self.context_modifiers = [
            "with context of", "in the context of", "with context", "in context of"
        ]
        
        self.sense_modifiers = [
            "with sense of", "in the sense of", "with sense", "in sense of",
            "as the keyword", "interpreted as", "meaning of", "treated as"
        ]
        
        self.context_synonyms = [
            "context", "namespace", "scope", "separate", "instance"
        ]
        
        self.function_synonyms = [
            "make a function with the following name", "make a function with the name",
            "define a function with the name", "define a function with the following name",
            "create a function with the name", "create a function with the following name",
            "function", "func", "define", "new function"
        ]
        
        self.enter_synonyms = [
            "go to", "go inside", "enter", "enter function", "invoke", "call",
            "execute", "run", "use function", "apply"
        ]
        
        self.return_synonyms = [
            "leave", "exit", "get out of", "move away from", "depart",
            "yield", "give back", "send back", "return"
        ]
        
        self.delete_synonyms = [
            "abandon", "annihilate", "destroy", "omit", "eradicate",
            "delete", "remove", "clear", "drop", "unset", "undefine"
        ]
    
    def tokenize(self, code: str) -> list:
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        return lines
    
    def extract_string(self, text: str) -> str:
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]
        return text
    
    def parse_print(self, line: str) -> str:
        for synonym in self.print_synonyms:
            pattern = rf'^{synonym}[:\s]+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def parse_set(self, line: str) -> tuple:
        for synonym in self.set_synonyms:
            pattern = rf'^{synonym}\s+(\w+)\s+(?:to|as|=|:)\s*(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return (match.group(1), match.group(2).strip())
        return None
    
    def parse_input(self, line: str) -> tuple:
        # Check "ask for input into x" - must check longer phrases first
        long_patterns = [
            (r'^ask\s+for\s+input\s+into\s+(\w+)$', (None, None)),
            (r'^ask\s+for\s+input\s*:\s*["\']?([^"\']+)["\']?\s+into\s+(\w+)$', (2, 1)),
            (r'^prompt\s+for\s+(\w+)$', (1, None)),
            (r'^prompt\s+for\s+(\w+)\s*:\s*["\']?([^"\']+)["\']?$', (1, 2)),
        ]
        
        for pattern, groups in long_patterns:
            match = __import__('re').match(pattern, line, __import__('re').IGNORECASE)
            if match:
                g = match.groups()
                if groups == (None, None):
                    return (g[0], None)
                else:
                    var_idx, prompt_idx = groups
                    return (g[var_idx - 1], g[prompt_idx - 1])
        
        # Simple: "listen into x", "hear into x", "get input into x"
        simple_syns = ["listen", "hear", "get input", "obtain input", "read"]
        for synonym in simple_syns:
            pattern = rf'^{synonym}\s+into\s+(\w+)$'
            match = __import__('re').match(pattern, line, __import__('re').IGNORECASE)
            if match:
                return (match.group(1), None)
        
        return None
    
    def parse_arithmetic(self, line: str) -> tuple:
        for synonym in self.add_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:to|by)?\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("add", match.group(2).strip(), match.group(1).strip())
        
        for synonym in self.subtract_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:from|by)?\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("sub", match.group(2).strip(), match.group(1).strip())
        
        for synonym in self.multiply_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:by)?\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("mul", match.group(2).strip(), match.group(1).strip())
        
        for synonym in self.divide_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:by|into)?\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("div", match.group(2).strip(), match.group(1).strip())
        
        return None
    
    def parse_context_modifier(self, line: str) -> tuple:
        for modifier in self.context_modifiers:
            pattern = rf'^(.+?)\s+{modifier}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("context", match.group(1).strip(), match.group(2).strip())
        
        for modifier in self.sense_modifiers:
            idx = line.lower().rfind(modifier)
            if idx != -1:
                command_part = line[:idx].strip()
                after_modifier = line[idx + len(modifier):].strip()
                keyword = after_modifier.replace("the keyword", "").replace("the keyword", "").strip().strip('"\'')
                return ("sense", command_part, keyword)
        
        return None
    
    def resolve_keyword(self, keyword: str) -> str:
        keyword = keyword.lower()
        
        if keyword in self.print_synonyms:
            return "print"
        if keyword in self.set_synonyms:
            return "set"
        if keyword in self.input_synonyms:
            return "input"
        if keyword in self.add_synonyms:
            return "add"
        if keyword in self.subtract_synonyms:
            return "sub"
        if keyword in self.multiply_synonyms:
            return "mul"
        if keyword in self.divide_synonyms:
            return "div"
        if keyword in self.if_synonyms:
            return "if"
        if keyword in self.loop_synonyms:
            return "loop"
        
        return keyword
    
    def parse_if(self, line: str) -> str:
        for synonym in self.question_if_synonyms:
            if line.lower().startswith(synonym):
                return "question_true"
        
        for synonym in self.return_check_synonyms:
            pattern = rf'^{synonym}\s+(\w+)\s+return\s+(.+?)(?:\s+then)?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return f"return_check:{match.group(1)}:{match.group(2)}"
            
            pattern = rf'^{synonym}\s+(\w+)\s+(?:return|equal|equals|be)\s+(.+?)(?:\s+then)?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return f"return_check:{match.group(1)}:{match.group(2)}"
        
        for synonym in self.if_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:then|do|perform)?\s*$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def parse_condition(self, condition: str) -> tuple:
        sorted_ops = sorted(self.compare_ops.items(), key=lambda x: x[1][1], reverse=True)
        for word, (op, _) in sorted_ops:
            pattern = rf'(.+?)\s+{word}\s+(.+)'
            match = re.match(pattern, condition, re.IGNORECASE)
            if match:
                return (match.group(1).strip(), op, match.group(2).strip())
        return None
    
    def parse_loop(self, line: str) -> tuple:
        for synonym in self.loop_synonyms:
            pattern = rf'^{synonym}\s+(?:while|until|when)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("while", match.group(1).strip())
            
            pattern = rf'^{synonym}\s+(\w+)\s+times$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("times", match.group(1))
        
        return None
    
    def parse_function_def(self, line: str) -> tuple:
        for synonym in self.function_synonyms:
            pattern = rf'^{synonym}[:\s]+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            pattern = rf'^{synonym}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def parse_function_call(self, line: str) -> tuple:
        for synonym in self.enter_synonyms:
            pattern = rf'^{synonym}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            pattern = rf'^{synonym}\s+(\w+)\s+with\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return (match.group(1).strip(), match.group(2).strip())
        return None
    
    def parse_return(self, line: str) -> str:
        for synonym in self.return_synonyms:
            pattern = rf'^{synonym}\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            pattern = rf'^{synonym}$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return None
        return None
    
    def parse_file_op(self, line: str) -> tuple:
        line_lower = line.lower()
        
        # Write to file
        for syn in ["write to file", "save to file", "store to file", "dump to file"]:
            pattern = rf'^{syn}\s+["\']?(.+?)["\']?\s+(?:with|content|data)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("write", match.group(1).strip(), match.group(2).strip())
        
        # Append to file
        for syn in ["append to file", "add to file"]:
            pattern = rf'^{syn}\s+["\']?(.+?)["\']?\s+(?:with|content|data)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("append", match.group(1).strip(), match.group(2).strip())
        
        # Read from file
        for syn in ["read from file", "load from file", "get from file"]:
            pattern = rf'^{syn}\s+["\']?(.+?)["\']?(?:\s+into\s+(\w+))?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                return ("read", groups[0], groups[1])
        
        # Delete file
        for syn in ["delete file", "remove file", "erase file"]:
            pattern = rf'^{syn}\s+["\']?(.+?)["\']?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("delete", match.group(1).strip())
        
        return None
    
    def parse_stack_op(self, line: str) -> tuple:
        line_lower = line.lower()
        
        # Push to stack
        for syn in ["push", "stack push"]:
            pattern = rf'^{syn}\s+(.+?)\s+(?:to|onto)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("push", match.group(2).strip(), match.group(1).strip())
        
        # Pop from stack
        for syn in ["pop", "stack pop"]:
            pattern = rf'^{syn}\s+(?:from|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("pop", match.group(1).strip())
        
        # Peek stack
        for syn in ["peek", "top", "stack peek"]:
            pattern = rf'^{syn}\s+(?:of|from)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("peek", match.group(1).strip())
        
        # Stack size
        for syn in ["stack size", "stack length"]:
            pattern = rf'^{syn}\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("stack_size", match.group(1).strip())
        
        # Is empty
        for syn in ["is empty", "is stack empty"]:
            pattern = rf'^{syn}\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("is_empty", match.group(1).strip())
        
        return None
    
    def parse_array_op(self, line: str) -> tuple:
        # Create array
        for syn in ["create array", "make array", "new array"]:
            pattern = rf'^{syn}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("create", match.group(1).strip())
            
            pattern = rf'^{syn}\s+(\w+)\s+(?:with|size|length)\s+(\d+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("create_size", match.group(1).strip(), int(match.group(2)))
        
        # Push to array
        for syn in ["push to array", "add to array", "append to array"]:
            pattern = rf'^{syn}\s+(.+?)\s+(?:to|into)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("array_push", match.group(2).strip(), match.group(1).strip())
        
        # Pop from array
        for syn in ["pop from array", "remove from array"]:
            pattern = rf'^{syn}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("array_pop", match.group(1).strip())
        
        # Get from array
        for syn in ["get from array", "array at", "array index"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:at|index|position)\s+(\d+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("array_get", match.group(1).strip(), int(match.group(2)))
        
        # Set array at
        for syn in ["set array at"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:at|index|position)\s+(\d+)\s+(?:to|value)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("array_set", match.group(1).strip(), int(match.group(2)), match.group(3).strip())
        
        # Array length
        for syn in ["array length", "array size"]:
            pattern = rf'^{syn}\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("array_length", match.group(1).strip())
        
        return None
    
    def parse_object_op(self, line: str) -> tuple:
        # Create object
        for syn in ["create object", "make object", "new object"]:
            pattern = rf'^{syn}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("create", match.group(1).strip())
            
            pattern = rf'^{syn}\s+(\w+)\s+with\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("create_with", match.group(1).strip(), match.group(2).strip())
        
        # Set property
        for syn in ["set property", "set attribute", "set field"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:of|)\s+(\w+)\s+(?:to|value|as)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("object_set", match.group(2).strip(), match.group(1).strip(), match.group(3).strip())
        
        # Get property
        for syn in ["get property", "get attribute", "get field"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("object_get", match.group(2).strip(), match.group(1).strip())
        
        # Has property
        for syn in ["has property", "has attribute", "has field"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("object_has", match.group(2).strip(), match.group(1).strip())
        
        # Delete property
        for syn in ["delete property", "delete attribute", "remove property"]:
            pattern = rf'^{syn}\s+(\w+)\s+(?:of|)\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("object_delete", match.group(2).strip(), match.group(1).strip())
        
        return None
    
    def parse_delete(self, line: str) -> tuple:
        for synonym in self.delete_synonyms:
            pattern = rf'^{synonym}\s+(\w+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def parse_break(self, line: str) -> bool:
        for synonym in self.break_synonyms:
            if line.lower().startswith(synonym):
                return True
        return False
    
    def parse_continue(self, line: str) -> bool:
        for synonym in self.continue_synonyms:
            if line.lower().startswith(synonym):
                return True
        return False
    
    def parse_halt(self, line: str) -> bool:
        for synonym in self.halt_synonyms:
            if line.lower().startswith(synonym) or line == "HLT":
                return True
        return False
    
    def parse_modulo(self, line: str) -> tuple:
        for synonym in self.modulo_synonyms:
            pattern = rf'^{synonym}\s+(.+?)\s+(?:of|by)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return (match.group(1).strip(), match.group(2).strip())
            
            pattern = rf'^(\w+)\s+{synonym}\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return (match.group(1).strip(), match.group(2).strip())
        return None
    
    def parse_import(self, line: str) -> str:
        for synonym in self.import_synonyms:
            pattern = rf'^{synonym}\s+["\']?([^"\']+)["\']?\s*$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            pattern = rf'^{synonym}\s+file\s+["\']?([^"\']+)["\']?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def parse_string_op(self, line: str) -> tuple:
        # length of string
        for syn in self.string_synonyms[:3]:
            pattern = rf'^{syn}\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("length", match.group(1).strip())
        
        # character at index
        for syn in self.string_synonyms[3:6]:
            pattern = rf'^{syn}\s+(.+?)\s+(?:position|index|num|number)\s+(\d+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("char_at", match.group(1).strip(), int(match.group(2)))
        
        # split string
        for syn in self.string_synonyms[6:9]:
            pattern = rf'^{syn}\s+(.+?)\s+(?:by|with|using|delimiter)\s+["\']?(.+?)["\']?$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("split", match.group(1).strip(), match.group(2).strip())
        
        # count character in string
        for syn in self.string_synonyms[9:12]:
            pattern = rf'^{syn}\s+(.)\s+(?:in|of)\s+(.+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("count", match.group(1).strip(), match.group(2).strip())
        
        # get argument at index
        for syn in self.string_synonyms[12:15]:
            pattern = rf'^{syn}\s+(\d+)$'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return ("arg_at", int(match.group(1)))
        
        return None
