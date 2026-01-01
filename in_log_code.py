'''
插入代码到日志文件中
'''
import file
import token
import re
file.read_code()
block=[]
def filecode_to_log():
    '''
    以便在本地调试时记录代码到文件code_log.txt中
    '''
    file.in_code(0,'''
#ifndef ONLINE_JUDGE_ONE
    freopen("code_in.txt", "r", stdin);
    freopen("code_log.txt", "w", stdout);
#endif
#include <bits/stdc++.h>
''')
def keyword_mark(code):
    '''
    从源代码字符串中提取标识符及其位置，返回列表 [(pos, name), ...]
    会去掉注释与字符串，并过滤保留关键字。
    '''
    reservedKeyword = {
        'alignas','alignof','and','and_eq','asm','auto','bitand','bitor','bool','break',
        'case','catch','char','char8_t','char16_t','char32_t','class','compl','concept',
        'const','consteval','constexpr','constinit','const_cast','continue','co_await',
        'co_return','co_yield','decltype','default','delete','do','double','dynamic_cast',
        'else','enum','explicit','export','extern','false','float','for','friend','goto',
        'if','import','inline','int','long','module','mutable','namespace','new','noexcept',
        'not','not_eq','nullptr','operator','or','or_eq','private','protected','public',
        'register','reinterpret_cast','requires','return','short','signed','sizeof','static',
        'static_assert','static_cast','struct','switch','template','this','thread_local','throw',
        'true','try','typedef','typeid','typename','union','unsigned','using','virtual','void',
        'volatile','wchar_t','while','xor','xor_eq','final','override'
    }

    # 去掉注释与字符串，但保留位置信息（用空格替换文本）
    pattern = r'//.*?$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'"\\])*\''  # 修正字符串转义
    def _repl(m):
        return ' ' * (m.end() - m.start())
    clean = re.sub(pattern, _repl, code, flags=re.S | re.M)

    # 匹配 C/C++ 标识符
    ident_re = re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9]*\b')
    result = []
    for m in ident_re.finditer(clean):
        name = m.group(0)
        if name in reservedKeyword:
            continue
        result.append((m.start(), name))
    return result
def in_log(code_list=None):
    '''
    插入日志代码
    '''
    # 使用文件中最新代码字符串作为主数据
    code = file.code
    pc_list = token.token_pc(code)  # 获取每行代码的起始与终止位置，假设返回 (start,end,line_no)
    bleck_list = token.code_block()  # 不可分割代码块（未直接使用）
    keyword_list = keyword_mark(code)  # [(pos,name), ...]
    hl_list = token.code_pc_is_none(code)  # 忽略区间列表，假设 [(start,end), ...]
    filecode_to_log()#插入文件头
    # 指针用于遍历忽略区间与行区间
    h = 0
    p = 0
    hl = hl_list[h] if hl_list else (0, -1)
    pc_token = pc_list[p] if pc_list else (0, len(code), 0)

    inserts = []  # collect (pos, text)
    for pos, name in keyword_list:
        # advance hl pointer while pos beyond current hl
        while h + 1 < len(hl_list) and pos > hl[1]:
            h += 1
            hl = hl_list[h]
        # advance pc pointer to find the line containing pos
        while p + 1 < len(pc_list) and pos > pc_token[1]:
            p += 1
            pc_token = pc_list[p]

        # 检查是否在忽略区间内以及是否在该行有效范围内
        if not (hl[0] <= pos <= hl[1]) and (pc_token[0] <= pos <= pc_token[1]):
            # 跳过函数调用：如果下一个非空字符是 '(', 则视为函数调用
            after_idx = pos + len(name)
            # 跳过空白
            j = after_idx
            while j < len(code) and code[j].isspace():
                j += 1
            if j < len(code) and code[j] == '(':
                continue

            line_no = pc_token[2] if len(pc_token) > 2 else 0
            text = f'std::cout << "{line_no}:mem:{pos}:" << typeid({name}).name() << ':' << std::hex << {name} << std::endl;'
            inserts.append((after_idx, text))

    # 为避免插入后影响后续位置，从后向前插入
    for insert_pos, text in sorted(inserts, key=lambda x: x[0], reverse=True):
        file.in_code(insert_pos, text)
