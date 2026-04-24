import sys
import os

__all__ = ['EngramInterpreter', 'EngramError', 'YEPLBE']
YEPLBE = "Your Esoteric Programming Language Bores Me"

from .errors import EngramError, ErrorHandler
from .lexer import Lexer
from .types import EngramType, EngramInteger, EngramFloat, EngramString, EngramBoolean, EngramList, EngramObject, create_engram_value


class EngramInterpreter:
    def __init__(self):
        self.variables = {}
        self.output = []
        self.contexts = {}
        self.current_context = "default"
        self.functions = {}
        self.current_function = None
        self.return_value = None
        self.error_handler = ErrorHandler()
        self.lexer = Lexer(self.error_handler)
    
    def raise_error(self, error_type: str, **kwargs):
        self.error_handler.raise_error(error_type, **kwargs)
    
    def get_variable(self, name: str):
        ctx = self.current_context
        if ctx not in self.contexts:
            return None
        full_name = f"{ctx}.{name}"
        return self.contexts[ctx].get(name) or self.contexts[ctx].get(full_name)
    
    def set_variable(self, name: str, value):
        ctx = self.current_context
        if ctx not in self.contexts:
            self.contexts[ctx] = {}
        self.contexts[ctx][name] = value
        self.variables[name] = value
    
    def resolve_context_keyword(self, keyword: str) -> str:
        keyword = keyword.lower().strip().strip('"\'')
        return self.lexer.resolve_keyword(keyword)
    
    def evaluate_expression(self, expr: str):
        expr = expr.strip()
        
        if expr.startswith('"') and expr.endswith('"'):
            return EngramString(expr[1:-1])
        if expr.startswith("'") and expr.endswith("'"):
            return EngramString(expr[1:-1])
        
        if expr.lower() == "true":
            return EngramBoolean(True)
        if expr.lower() == "false":
            return EngramBoolean(False)
        
        if expr.isdigit():
            return EngramInteger(expr)
        
        try:
            return EngramFloat(expr)
        except ValueError:
            pass
        
        if expr in self.variables:
            return self.variables[expr]
        
        for op, word in [("plus", " + "), ("minus", " - "), ("times", " * "), ("divided by", " / ")]:
            pattern = rf'^(.+?)\s+{op}\s+(.+)$'
            match = __import__('re').match(pattern, expr, __import__('re').IGNORECASE)
            if match:
                left = self.evaluate_expression(match.group(1))
                right = self.evaluate_expression(match.group(2))
                return left + right
        
        return EngramString(expr)
    
    def get_input(self, var_name: str, prompt: str = ""):
        if prompt:
            user_input = input(prompt)
        else:
            user_input = input()
        
        try:
            self.variables[var_name] = EngramInteger(int(user_input))
        except ValueError:
            try:
                self.variables[var_name] = EngramFloat(float(user_input))
            except ValueError:
                if user_input.lower() == "true":
                    self.variables[var_name] = EngramBoolean(True)
                elif user_input.lower() == "false":
                    self.variables[var_name] = EngramBoolean(False)
                else:
                    self.variables[var_name] = EngramString(user_input)
    
    def execute_print(self, line: str):
        value = self.lexer.parse_print(line)
        if value is not None:
            result = self.evaluate_expression(value)
            self.output.append(str(result))
            return True
        return False
    
    def execute_set(self, line: str):
        result = self.lexer.parse_set(line)
        if result:
            var_name, expr = result
            value = self.evaluate_expression(expr)
            self.variables[var_name] = value
            return True
        return False
    
    def execute_input(self, line: str):
        result = self.lexer.parse_input(line)
        if result:
            var_name, prompt = result
            if var_name:
                self.get_input(var_name, prompt)
            elif prompt:
                user_input = input(prompt)
                self.output.append(user_input)
            return True
        return False
    
    def execute_string_op(self, line: str) -> bool:
        result = self.lexer.parse_string_op(line)
        if result:
            if result[0] == "length":
                var = self.evaluate_expression(result[1])
                if hasattr(var, 'length'):
                    self.output.append(str(var.length()))
                else:
                    self.output.append(str(len(str(var.value))))
                return True
            
            elif result[0] == "char_at":
                var = self.evaluate_expression(result[1])
                index = result[2]
                if hasattr(var, 'char_at'):
                    self.output.append(var.char_at(index))
                else:
                    s = str(var.value)
                    if 0 <= index < len(s):
                        self.output.append(s[index])
                return True
            
            elif result[0] == "split":
                var = self.evaluate_expression(result[1])
                delimiter = result[2]
                if hasattr(var, 'split'):
                    parts = var.split(delimiter)
                    for part in parts:
                        self.output.append(str(part.value))
                else:
                    s = str(var.value)
                    parts = s.split(delimiter)
                    for p in parts:
                        self.output.append(p)
                return True
            
            elif result[0] == "count":
                char = result[1]
                var = self.evaluate_expression(result[2])
                s = str(var.value) if hasattr(var, 'value') else str(var)
                count = s.count(char)
                self.output.append(str(count))
                return True
            
            elif result[0] == "arg_at":
                idx = result[1]
                import sys
                if idx < len(sys.argv):
                    self.output.append(sys.argv[idx])
                else:
                    self.output.append("")
                return True
        
        return False
    
    def execute_stack_op(self, line: str) -> bool:
        result = self.lexer.parse_stack_op(line)
        if result:
            if result[0] == "push":
                stack_name, value = result[1], result[2]
                stack_key = "_stack_" + stack_name
                if stack_key not in self.variables:
                    self.variables[stack_key] = []
                stack = self.variables[stack_key]
                val = self.evaluate_expression(value)
                stack.append(val)
                return True
            
            elif result[0] == "pop":
                stack_name = result[1]
                stack_key = "_stack_" + stack_name
                stack = self.variables.get(stack_key, [])
                if stack:
                    self.variables[stack_name] = stack.pop()
                return True
            
            elif result[0] == "peek":
                stack_name = result[1]
                stack_key = "_stack_" + stack_name
                stack = self.variables.get(stack_key, [])
                if stack:
                    self.output.append(str(stack[-1]))
                return True
            
            elif result[0] == "stack_size":
                stack_name = result[1]
                stack_key = "_stack_" + stack_name
                stack = self.variables.get(stack_key, [])
                self.output.append(str(len(stack)))
                return True
            
            elif result[0] == "is_empty":
                stack_name = result[1]
                stack_key = "_stack_" + stack_name
                stack = self.variables.get(stack_key, [])
                self.output.append(str(len(stack) == 0).lower())
                return True
        
        return False
    
    def execute_array_op(self, line: str) -> bool:
        result = self.lexer.parse_array_op(line)
        if result:
            if result[0] == "create":
                arr_name = result[1]
                self.variables[arr_name] = []
                return True
            
            elif result[0] == "create_size":
                arr_name, size = result[1], result[2]
                self.variables[arr_name] = [None] * size
                return True
            
            elif result[0] == "array_push":
                arr_name, value = result[1], result[2]
                if arr_name in self.variables and isinstance(self.variables[arr_name], list):
                    val = self.evaluate_expression(value)
                    self.variables[arr_name].append(val)
                else:
                    self.raise_error("invalid_expression", expr=f"{arr_name} is not an array")
                return True
            
            elif result[0] == "array_pop":
                arr_name = result[1]
                if arr_name in self.variables and isinstance(self.variables[arr_name], list) and self.variables[arr_name]:
                    self.variables[arr_name].pop()
                return True
            
            elif result[0] == "array_get":
                arr_name, index = result[1], result[2]
                if arr_name in self.variables and isinstance(self.variables[arr_name], list):
                    arr = self.variables[arr_name]
                    if 0 <= index < len(arr):
                        self.output.append(str(arr[index]))
                return True
            
            elif result[0] == "array_set":
                arr_name, index, value = result[1], result[2], result[3]
                if arr_name in self.variables and isinstance(self.variables[arr_name], list):
                    arr = self.variables[arr_name]
                    if 0 <= index < len(arr):
                        arr[index] = self.evaluate_expression(value)
                return True
            
            elif result[0] == "array_length":
                arr_name = result[1]
                if arr_name in self.variables and isinstance(self.variables[arr_name], list):
                    self.output.append(str(len(self.variables[arr_name])))
                return True
        
        return False
    
    def execute_object_op(self, line: str) -> bool:
        result = self.lexer.parse_object_op(line)
        if result:
            if result[0] == "create":
                obj_name = result[1]
                self.variables[obj_name] = {}
                return True
            
            elif result[0] == "create_with":
                obj_name, props = result[1], result[2]
                obj = {}
                for part in props.split(","):
                    if " as " in part.lower():
                        k, v = part.split(" as ", 1)
                        obj[k.strip()] = self.evaluate_expression(v.strip())
                    elif " to " in part.lower():
                        k, v = part.split(" to ", 1)
                        obj[k.strip()] = self.evaluate_expression(v.strip())
                self.variables[obj_name] = obj
                return True
            
            elif result[0] == "object_set":
                obj_name, prop, value = result[1], result[2], result[3]
                if obj_name in self.variables and isinstance(self.variables[obj_name], dict):
                    self.variables[obj_name][prop] = self.evaluate_expression(value)
                return True
            
            elif result[0] == "object_get":
                obj_name, prop = result[1], result[2]
                if obj_name in self.variables and isinstance(self.variables[obj_name], dict):
                    if prop in self.variables[obj_name]:
                        val = self.variables[obj_name][prop]
                        self.output.append(str(val.value) if hasattr(val, 'value') else str(val))
                return True
            
            elif result[0] == "object_has":
                obj_name, prop = result[1], result[2]
                if obj_name in self.variables and isinstance(self.variables[obj_name], dict):
                    self.output.append(str(prop in self.variables[obj_name]).lower())
                return True
            
            elif result[0] == "object_delete":
                obj_name, prop = result[1], result[2]
                if obj_name in self.variables and isinstance(self.variables[obj_name], dict):
                    self.variables[obj_name].pop(prop, None)
                return True
        
        return False
    
    def execute_file_op(self, line: str) -> bool:
        result = self.lexer.parse_file_op(line)
        if result:
            import os
            if result[0] == "write":
                filename, content = result[1], result[2]
                content_val = self.evaluate_expression(content)
                try:
                    # Resolve filename from variable if needed
                    actual_filename = filename
                    if filename in self.variables:
                        val = self.variables[filename]
                        actual_filename = val.value if hasattr(val, 'value') else str(val)
                    
                    with open(actual_filename, 'w') as f:
                        f.write(str(content_val.value) if hasattr(content_val, 'value') else str(content_val))
                except Exception:
                    pass
                return True
            
            elif result[0] == "append":
                filename, content = result[1], result[2]
                content_val = self.evaluate_expression(content)
                try:
                    # Resolve filename from variable if needed
                    actual_filename = filename
                    if filename in self.variables:
                        val = self.variables[filename]
                        actual_filename = val.value if hasattr(val, 'value') else str(val)
                    
                    with open(actual_filename, 'a') as f:
                        f.write(str(content_val.value) if hasattr(content_val, 'value') else str(content_val))
                except Exception:
                    pass
                return True
            
            elif result[0] == "delete":
                filename = result[1]
                try:
                    # Resolve filename from variable if needed
                    actual_filename = filename
                    if filename in self.variables:
                        val = self.variables[filename]
                        actual_filename = val.value if hasattr(val, 'value') else str(val)
                    
                    os.remove(actual_filename)
                except Exception:
                    pass
                return True
            
            elif result[0] == "read":
                filename = result[1]
                var_name = result[2]
                try:
                    # Resolve filename from variable if needed
                    actual_filename = filename
                    if filename in self.variables:
                        val = self.variables[filename]
                        actual_filename = val.value if hasattr(val, 'value') else str(val)
                    
                    with open(actual_filename, 'r') as f:
                        content = f.read()
                    if var_name:
                        self.variables[var_name] = EngramString(content)
                    else:
                        self.output.append(content)
                except Exception:
                    pass
                return True
            
            elif result[0] == "delete":
                filename = result[1]
                try:
                    os.remove(filename)
                except Exception:
                    pass
                return True
        
        return False
    
    def execute_arithmetic(self, line: str):
        result = self.lexer.parse_arithmetic(line)
        if result:
            op, var_expr, expr = result
            
            value = self.evaluate_expression(expr)
            
            if var_expr.isalpha():
                target_var = var_expr
                if target_var not in self.variables:
                    if op in ("sub", "div"):
                        self.variables[target_var] = EngramInteger(0) if op == "sub" else EngramInteger(1)
                    else:
                        self.variables[target_var] = EngramInteger(0)
                current = self.variables[target_var]
                
                if op == "add":
                    self.variables[target_var] = current + value
                elif op == "sub":
                    self.variables[target_var] = current - value
                elif op == "mul":
                    self.variables[target_var] = current * value
                elif op == "div":
                    try:
                        if value.value == 0:
                            self.raise_error("division_by_zero")
                    except AttributeError:
                        if int(value) == 0:
                            self.raise_error("division_by_zero")
                    self.variables[target_var] = current / value
                elif op == "mod":
                    self.variables[target_var] = EngramInteger(int(current.value) % int(value.value))
            else:
                var_value = self.evaluate_expression(var_expr)
                if op == "add":
                    return var_value + value
                elif op == "sub":
                    return var_value - value
                elif op == "mul":
                    return var_value * value
                elif op == "div":
                    try:
                        if value.value == 0:
                            self.raise_error("division_by_zero")
                    except AttributeError:
                        if int(value) == 0:
                            self.raise_error("division_by_zero")
                    return var_value / value
                elif op == "mod":
                    return EngramInteger(int(var_value.value) % int(value.value))
            return True
        
        mod_result = self.lexer.parse_modulo(line)
        if mod_result:
            left_expr, right_expr = mod_result
            left = self.evaluate_expression(left_expr)
            right = self.evaluate_expression(right_expr)
            result = EngramInteger(int(left.value) % int(right.value))
            self.output.append(str(result))
            return True
        
        return False
    
    def check_condition(self, condition: str) -> bool:
        if condition == "question_true":
            return bool(self.return_value) if self.return_value is not None else False
        
        if condition.startswith("return_check:"):
            parts = condition.split(":", 2)
            if len(parts) >= 3:
                func_name = parts[1]
                expected = parts[2]
                if func_name in self.functions:
                    saved_vars = dict(self.variables)
                    saved_return = self.return_value
                    self.return_value = None
                    self.execute_block(self.functions[func_name], 0, [])
                    result = self.return_value
                    self.return_value = saved_return
                    self.variables = saved_vars
                    expected_val = self.evaluate_expression(expected)
                    return result == expected_val
                return False
        
        result = self.lexer.parse_condition(condition)
        if result:
            left_expr, op, right_expr = result
            left = self.evaluate_expression(left_expr)
            right = self.evaluate_expression(right_expr)
            
            if op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == ">":
                return left > right
            elif op == "<":
                return left < right
            elif op == ">=":
                return left >= right
            elif op == "<=":
                return left <= right
        return False
    
    def execute_if(self, lines: list, start_idx: int) -> int:
        condition = self.lexer.parse_if(lines[start_idx])
        if not condition:
            return start_idx
        
        condition_met = self.check_condition(condition)
        
        i = start_idx + 1
        depth = 1
        if_body = []
        
        while i < len(lines) and depth > 0:
            line_lower = lines[i].lower()
            is_end = any(line_lower.startswith(syn) for syn in self.lexer.end_synonyms)
            is_if = any(line_lower.startswith(syn) for syn in self.lexer.if_synonyms) or \
                    any(line_lower.startswith(syn) for syn in self.lexer.question_if_synonyms) or \
                    any(line_lower.startswith(syn.split()[0]) for syn in self.lexer.return_check_synonyms if line_lower.startswith(syn.split()[0]))
            
            if is_end:
                depth -= 1
                if depth == 0:
                    break
            if is_if:
                depth += 1
            
            if depth > 0:
                if_body.append(lines[i])
            i += 1
        
        if condition_met:
            exec_result = self.execute_block(if_body, i, lines)
            if isinstance(exec_result, tuple):
                return exec_result
            return i
        
        return i
    
    def execute_loop(self, lines: list, start_idx: int) -> int:
        loop_info = self.lexer.parse_loop(lines[start_idx])
        if not loop_info:
            return start_idx
        
        loop_type, condition_or_times = loop_info
        
        i = start_idx + 1
        depth = 1
        loop_body = []
        
        while i < len(lines) and depth > 0:
            line_lower = lines[i].lower()
            is_end = any(line_lower.startswith(syn) for syn in self.lexer.end_synonyms)
            is_loop = any(line_lower.startswith(syn) for syn in self.lexer.loop_synonyms)
            
            if is_end:
                depth -= 1
                if depth == 0:
                    break
            if is_loop:
                depth += 1
            
            if depth > 0:
                loop_body.append(lines[i])
            i += 1
        
        if loop_type == "times":
            try:
                times = int(condition_or_times)
                if times < 0:
                    self.raise_error("negative_loop")
                for _ in range(times):
                    result = self.execute_block(loop_body, i, lines)
                    if isinstance(result, tuple) and result[0] == "break":
                        break
                    if isinstance(result, tuple) and result[0] == "continue":
                        continue
            except ValueError:
                self.raise_error("invalid_expression", expr=condition_or_times)
        else:
            iteration = 0
            max_iterations = 10000
            while self.check_condition(condition_or_times):
                result = self.execute_block(loop_body, i, lines)
                if isinstance(result, tuple) and result[0] == "break":
                    break
                if isinstance(result, tuple) and result[0] == "continue":
                    continue
                iteration += 1
                if iteration > max_iterations:
                    self.raise_error("nested_depth", msg="Infinite loop detected")
        
        return i
    
    def execute_block(self, block_lines: list, end_idx: int, original_lines: list) -> int:
        if not block_lines:
            return end_idx
        
        saved_output = self.output.copy()
        saved_vars = dict(self.variables)
        
        i = 0
        while i < len(block_lines):
            line = block_lines[i]
            
            if self.execute_print(line):
                i += 1
                continue
            if self.execute_set(line):
                i += 1
                continue
            if self.execute_input(line):
                i += 1
                continue
            if self.execute_arithmetic(line):
                i += 1
                continue
            
            if self.lexer.parse_break(line):
                return ("break", end_idx)
            
            if self.lexer.parse_continue(line):
                return ("continue", end_idx)
            
            return_val = self.lexer.parse_return(line)
            if return_val is not None:
                self.return_value = self.evaluate_expression(return_val) if return_val else None
                return end_idx
            elif any(line.lower().startswith(syn) for syn in self.lexer.return_synonyms):
                self.return_value = None
                return end_idx
            
            delete_target = self.lexer.parse_delete(line)
            if delete_target:
                if delete_target in self.variables:
                    del self.variables[delete_target]
                i += 1
                continue
            
            if any(line.lower().startswith(syn) for syn in self.lexer.if_synonyms):
                exec_result = self.execute_if(block_lines, i)
                if isinstance(exec_result, tuple):
                    return exec_result
                i = exec_result
                continue
            
            if any(line.lower().startswith(syn) for syn in self.lexer.loop_synonyms):
                i = self.execute_loop(block_lines, i)
                continue
            
            if any(line.lower().startswith(syn) for syn in self.lexer.end_synonyms):
                pass
            else:
                if line.strip():
                    self.raise_error("unknown_command", cmd=line.strip()[:30])
            
            i += 1
        
        return end_idx
    
    def execute(self, code: str) -> list:
        lines = self.lexer.tokenize(code)
        
        if not lines:
            self.raise_error("empty_code")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            context_mod = self.lexer.parse_context_modifier(line)
            if context_mod:
                mod_type, rest, param = context_mod
                
                if mod_type == "context":
                    old_context = self.current_context
                    self.current_context = param
                    line_to_exec = rest
                    
                    if self.execute_print(line_to_exec):
                        pass
                    elif self.execute_set(line_to_exec):
                        pass
                    elif self.execute_arithmetic(line_to_exec):
                        pass
                    else:
                        self.raise_error("unknown_command", cmd=line_to_exec[:30])
                    
                    self.current_context = old_context
                    i += 1
                    continue
                
                elif mod_type == "sense":
                    resolved = self.resolve_context_keyword(param)
                    
                    if resolved == "print":
                        if self.execute_print(rest):
                            i += 1
                            continue
                    elif resolved == "set":
                        if self.execute_set(rest):
                            i += 1
                            continue
                    elif resolved == "add":
                        if self.execute_arithmetic(rest):
                            i += 1
                            continue
                    
                    self.raise_error("unknown_command", cmd=rest[:30])
            
            if self.execute_print(line):
                i += 1
                continue
            if self.execute_set(line):
                i += 1
                continue
            if self.execute_input(line):
                i += 1
                continue
            if self.execute_arithmetic(line):
                i += 1
                continue
            if self.execute_string_op(line):
                i += 1
                continue
            if self.execute_stack_op(line):
                i += 1
                continue
            if self.execute_array_op(line):
                i += 1
                continue
            if self.execute_object_op(line):
                i += 1
                continue
            if self.execute_file_op(line):
                i += 1
                continue
            
            for syn in self.lexer.set_synonyms:
                pattern = rf'^{syn}\s+context\s+name\s+(\w+)$'
                match = __import__('re').match(pattern, line, __import__('re').IGNORECASE)
                if match:
                    context_name = match.group(1)
                    self.contexts[context_name] = {}
                    i += 1
                    break
            else:
                if line.lower().startswith("use context"):
                    parts = line.split()
                    if len(parts) >= 3:
                        self.current_context = parts[2]
                        i += 1
                        continue
                
                is_if_line = False
                if any(line.lower().startswith(syn) for syn in self.lexer.if_synonyms):
                    is_if_line = True
                elif any(line.lower().startswith(syn) for syn in self.lexer.question_if_synonyms):
                    is_if_line = True
                elif any(line.lower().startswith(syn.split()[0]) for syn in self.lexer.return_check_synonyms if len(syn.split()) > 0):
                    result = self.lexer.parse_if(line)
                    if result and result.startswith("return_check:"):
                        is_if_line = True
                
                if is_if_line:
                    i = self.execute_if(lines, i)
                    continue
                
                if any(line.lower().startswith(syn) for syn in self.lexer.loop_synonyms):
                    i = self.execute_loop(lines, i)
                    continue
                
                func_def = self.lexer.parse_function_def(line)
                if func_def:
                    i += 1
                    func_body = []
                    depth = 1
                    while i < len(lines) and depth > 0:
                        check_line = lines[i].lower()
                        if any(check_line.startswith(syn) for syn in self.lexer.end_synonyms):
                            depth -= 1
                            if depth == 0:
                                break
                        if any(check_line.startswith(syn) for syn in self.lexer.function_synonyms):
                            depth += 1
                        if depth > 0:
                            func_body.append(lines[i])
                        i += 1
                    self.functions[func_def] = func_body
                    continue
                
                func_call = self.lexer.parse_function_call(line)
                if func_call:
                    if isinstance(func_call, tuple):
                        func_name, args_str = func_call
                    else:
                        func_name = func_call
                        args_str = None
                    
                    if func_name in self.functions:
                        saved_vars = dict(self.variables)
                        self.current_function = func_name
                        self.return_value = None
                        
                        if args_str:
                            args = [a.strip() for a in args_str.split(',')]
                            func_def_line = None
                            for syn in self.lexer.function_synonyms:
                                pattern = rf'^{syn}[:\s]+' + func_name + r'$'
                                for l in lines[max(0, i-10):i]:
                                    if __import__('re').match(pattern, l, __import__('re').IGNORECASE):
                                        func_def_line = l
                                        break
                            if func_def_line:
                                for syn in self.lexer.function_synonyms:
                                    param_pattern = rf'^{syn}[:\s]+\w+\s+with\s+parameters?\s+(.+)$'
                                    match = __import__('re').match(param_pattern, func_def_line, __import__('re').IGNORECASE)
                                    if match:
                                        params = [p.strip() for p in match.group(1).split(',')]
                                        for j, param in enumerate(params):
                                            if j < len(args):
                                                self.variables[param] = self.evaluate_expression(args[j])
                                        break
                        
                        self.execute_block(self.functions[func_name], i, lines)
                        self.variables = saved_vars
                        self.current_function = None
                    else:
                        self.raise_error("function_not_found", func=func_name)
                    i += 1
                    continue
                
                delete_target = self.lexer.parse_delete(line)
                if delete_target:
                    if delete_target in self.variables:
                        del self.variables[delete_target]
                    if delete_target in self.functions:
                        del self.functions[delete_target]
                    if delete_target in self.contexts:
                        del self.contexts[delete_target]
                    i += 1
                    continue
                
                if self.lexer.parse_halt(line):
                    return self.output
                
                import_file = self.lexer.parse_import(line)
                if import_file:
                    import os
                    found_file = import_file
                    if not os.path.exists(import_file):
                        found_file = os.path.join(os.path.dirname(lines[0] if lines else '.'), import_file)
                    
                    if os.path.exists(found_file):
                        try:
                            with open(found_file, 'r') as f:
                                imported_code = f.read()
                            imported_lines = self.lexer.tokenize(imported_code)
                            
                            j = 0
                            while j < len(imported_lines):
                                imp_line = imported_lines[j]
                                
                                func_def = self.lexer.parse_function_def(imp_line)
                                if func_def:
                                    j += 1
                                    func_body = []
                                    depth = 1
                                    while j < len(imported_lines) and depth > 0:
                                        check_line = imported_lines[j].lower()
                                        if any(check_line.startswith(syn) for syn in self.lexer.end_synonyms):
                                            depth -= 1
                                            if depth == 0:
                                                break
                                        if any(check_line.startswith(syn) for syn in self.lexer.function_synonyms):
                                            depth += 1
                                        if depth > 0:
                                            func_body.append(imported_lines[j])
                                        j += 1
                                    self.functions[func_def] = func_body
                                    continue
                                
                                set_result = self.lexer.parse_set(imp_line)
                                if set_result:
                                    var_name, expr = set_result
                                    value = self.evaluate_expression(expr)
                                    self.variables[var_name] = value
                                
                                if self.lexer.parse_halt(imp_line):
                                    return self.output
                                
                                j += 1
                        except Exception as e:
                            pass
                    i += 1
                    continue
                
                return_val = self.lexer.parse_return(line)
                if return_val is not None:
                    self.return_value = self.evaluate_expression(return_val) if return_val else None
                    i += 1
                    continue
                
                if line.strip() and not any(line.lower().startswith(syn) for syn in self.lexer.end_synonyms):
                    self.raise_error("unknown_command", cmd=line.strip()[:30])
            
            i += 1
        
        return self.output


def main():
    if len(sys.argv) < 2:
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                    ENGRAM - English Programming Language           ║")
        print("╠═══════════════════════════════════════════════════════════════════╣")
        print("║  Usage: python -m engram <file.engram>                             ║")
        print("║                                                                           ║")
        print("║  Example:                                                          ║")
        print("║    say: \"Hello, World!\"                                               ║")
        print("║    set x to 10                                                        ║")
        print("║    add 5 to x                                                          ║")
        print("║    if x greater than 10 then                                          ║")
        print("║        say: \"x is big\"                                                 ║")
        print("║        end                                                            ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        sys.exit(0)
    
    filename = sys.argv[1]
    if not os.path.exists(filename):
        eh = ErrorHandler()
        eh.raise_error("file_not_found", filename=filename)
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except Exception as e:
        eh = ErrorHandler()
        eh.raise_error("file_read_error", filename=filename, details=str(e))
    
    if not code.strip():
        eh = ErrorHandler()
        eh.raise_error("empty_code")
    
    interpreter = EngramInterpreter()
    try:
        result = interpreter.execute(code)
    except EngramError:
        raise
    
    for line in result:
        print(line)


if __name__ == "__main__":
    main()