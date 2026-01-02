'''
token_pc 和 tokenize_cpp 函数的实现
'''
import re

def tokenize_cpp(code: str) -> list[str]:
    '''
    将C++代码字符串分割成token列表，保留注释和字符串字面量完整性。
    '''
    symbols = set('(){}[];,.:+-*/%&|^~=!<>?#')
    i = 0
    n = len(code)
    tokens = []
    buf = []

    def flush_buf():
        if buf:
            tokens.append(''.join(buf))
            buf.clear()

    while i < n:
        ch = code[i]

        # 换行符单独作为一个token
        if ch == '\n':
            flush_buf()
            tokens.append('\n')
            i += 1
            continue

        # 其他空白字符作为分隔符
        if ch.isspace():
            flush_buf()
            i += 1
            continue

        # 行注释 // ...
        if ch == '/' and i + 1 < n and code[i+1] == '/':
            flush_buf()
            j = i + 2
            while j < n and code[j] != '\n':
                j += 1
            tokens.append(code[i:j])
            i = j
            continue

        # 块注释 /* ... */
        if ch == '/' and i + 1 < n and code[i+1] == '*':
            flush_buf()
            j = i + 2
            while j < n - 1 and not (code[j] == '*' and code[j+1] == '/'):
                j += 1
            j = min(j + 2, n)
            tokens.append(code[i:j])
            i = j
            continue

        # 字符串字面量 "..." 或 '...'
        if ch == '"' or ch == "'":
            flush_buf()
            quote = ch
            j = i + 1
            while j < n:
                if code[j] == '\\' and j + 1 < n:
                    j += 2
                    continue
                if code[j] == quote:
                    j += 1
                    break
                j += 1
            tokens.append(code[i:j])
            i = j
            continue

        # 原始字符串字面量 R"delim(...)delim"
        if ch == 'R' and i + 1 < n and code[i+1] == '"':
            flush_buf()
            k = i + 2
            while k < n and code[k] != '(':
                k += 1
            if k >= n:
                buf.append(ch)
                i += 1
                continue
            delim = code[i+2:k]
            term = ')' + delim + '"'
            j = k + 1
            while j < n:
                if code.startswith(term, j):
                    j += len(term)
                    break
                j += 1
            tokens.append(code[i:j])
            i = j
            continue

        # 标识符或数字
        if ch.isalnum() or ch == '_':
            buf.append(ch)
            i += 1
            while i < n and (code[i].isalnum() or code[i] == '_'):
                buf.append(code[i])
                i += 1
            continue

        # 符号字符
        if ch in symbols:
            flush_buf()
            tokens.append(ch)
            i += 1
            continue

        # 其他字符
        flush_buf()
        tokens.append(ch)
        i += 1

    flush_buf()
    return tokens

def token_pc(code: list[str]) -> list[tuple[int, int, int]]:
    '''
    分析每行token的起始与终止索引，返回 [(start_idx, end_idx, line_num), ...]
    - 总结就是每行的token范围和对应的行号
    '''
    pc_list = []
    hi = 0
    pc = 0
    for i, token in enumerate(code):
        if token == '\n':
            pc_list.append((hi, i, pc + 1))
            hi = i + 1
            pc += 1
    return pc_list

def get_ignore_ranges(tokens: list[str]) -> list[tuple[int, int]]:
    '''
    获取不应插桩的代码块范围（如class/struct/enum定义）
    返回 [(start_token_idx, end_token_idx), ...]
    '''
    ignore_keywords = {'enum', 'struct', 'class', 'union'}
    ignore_ranges = []
    i = 0
    n = len(tokens)
    
    while i < n:
        # 检查是否为忽略关键词
        if tokens[i] in ignore_keywords:
            # 找到后面的 {
            j = i + 1
            while j < n and tokens[j] != '{':
                j += 1
            if j >= n:
                break
            
            # 匹配大括号
            start_idx = j
            brace_count = 1
            j += 1
            while j < n and brace_count > 0:
                if tokens[j] == '{':
                    brace_count += 1
                elif tokens[j] == '}':
                    brace_count -= 1
                j += 1
            
            if brace_count == 0:
                ignore_ranges.append((start_idx, j - 1))
                i = j
                continue
        
        i += 1
    
    return ignore_ranges

def code_block(tokens: list[str]) -> list[tuple[int, int]]:
    '''
    识别不可分割的代码块（如for/if/while等控制语句）
    返回 [(block_start_idx, block_end_idx), ...]
    '''
    block_keywords = {'for', 'if', 'else', 'while', 'switch', 'do', 'catch'}
    block_ranges = []
    
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i] in block_keywords:
            start_idx = i
            # 跳过关键字，找到代码块结束（; 或 {）
            while i < n and tokens[i] not in {';', '{', '\n'}:
                i += 1
            
            if i < n and tokens[i] == '{':
                # 匹配大括号
                brace_count = 1
                i += 1
                while i < n and brace_count > 0:
                    if tokens[i] == '{':
                        brace_count += 1
                    elif tokens[i] == '}':
                        brace_count -= 1
                    i += 1
                block_ranges.append((start_idx, i - 1))
            else:
                # 单行语句
                block_ranges.append((start_idx, i))
        
        i += 1
    
    return block_ranges