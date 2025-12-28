'''
token_pc 和 tokenize_cpp 函数的实现
'''
def tokenize_cpp(code: str):
    '''
    tokenize_cpp 的 Docstring
    
    :param code: 说明
    :type code: str
    :return: 说明
    :rtype: list[str]
    该函数将C++代码字符串分割成标记列表，保留注释和字符串字面量完整性。
    主要处理以下情况：
    - 标识符和数字（字母、数字、下划线组成的连续序列）
    - 符号（如括号、分号、运算符等）单独作为标记
    - 行注释（// 开头直到行尾）
    - 块注释（/* 开头直到 */）
    - 字符串字面量（双引号或单引号包围的内容，支持转义字符）
    - 原始字符串字面量（R"delim(...)delim" 格式）
    - 保留换行符作为单独标记
    - 忽略其他空白字符（空格、制表符等）作为分隔符
    返回的标记列表中，每个元素是一个字符串，表示代码中的一个逻辑单元。

    '''
    # 需要单独分割的符号
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

        # Newline must be preserved as token
        if ch == '\n':
            flush_buf()
            tokens.append('\n')
            i += 1
            continue

        # Whitespace (other than newline) - separate tokens but not kept
        if ch.isspace():
            flush_buf()
            i += 1
            continue

        # Line comment // ... (keep comment as one token, but keep newline separate)
        if ch == '/' and i + 1 < n and code[i+1] == '/':
            flush_buf()
            j = i + 2
            while j < n and code[j] != '\n':
                j += 1
            tokens.append(code[i:j])
            i = j
            continue

        # Block comment /* ... */
        if ch == '/' and i + 1 < n and code[i+1] == '*':
            flush_buf()
            j = i + 2
            while j < n - 1 and not (code[j] == '*' and code[j+1] == '/'):
                j += 1
            j = min(j + 2, n)
            tokens.append(code[i:j])
            i = j
            continue

        # String literal "..." or '...' (handle escapes)
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

        # Raw string literal R"delim(...)delim"
        if ch == 'R' and i + 1 < n and code[i+1] == '"':
            flush_buf()
            # find the '(' after the opening quote
            k = i + 2
            while k < n and code[k] != '(':
                k += 1
            if k >= n:
                # malformed, treat as normal identifier
                buf.append(ch)
                i += 1
                continue
            delim = code[i+2:k]
            # terminator is )delim"
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

        # Identifier/number (letters, digits, underscore)
        if ch.isalnum() or ch == '_':
            buf.append(ch)
            i += 1
            # consume subsequent alnum/_ chars
            while i < n and (code[i].isalnum() or code[i] == '_'):
                buf.append(code[i])
                i += 1
            continue

        # Symbols: treat each symbol character as its own token
        if ch in symbols:
            flush_buf()
            tokens.append(ch)
            i += 1
            continue

        # Fallback: any other char, treat as single token
        flush_buf()
        tokens.append(ch)
        i += 1

    flush_buf()
    return tokens
def token_pc(code: list[str]):
    '''
    用于分析每行token的起始与终止位置
    '''
    pc_list=[]
    hi=0
    for i in range(len(code)):
        if code[i]=='\n':
            pc_list.append( (hi,i) )
            hi=i+1
    return pc_list