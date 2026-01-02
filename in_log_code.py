'''
插入代码到日志文件中
'''
import re
import token as token_mod
import file

# C++保留关键字集合
RESERVED_KEYWORDS = {
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

def extract_identifiers(code_str: str) -> list[tuple[int, str]]:
    '''
    从源代码字符串中提取标识符及其字符位置，返回 [(pos, name), ...]
    会移除注释与字符串，并过滤保留关键字。
    '''
    # 移除注释与字符串，用空格占位保持位置
    pattern = r'//.*?$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'"\\])*\''  # 修正字符串转义
    def _repl(m):
        return ' ' * (m.end() - m.start())
    clean = re.sub(pattern, _repl, code_str, flags=re.S | re.M)

    # 匹配 C/C++ 标识符
    ident_re = re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9]*\b')
    result = []
    for m in ident_re.finditer(clean):
        name = m.group(0)
        if name not in RESERVED_KEYWORDS:
            result.append((m.start(), name))
    return result

def insert_debug_headers():
    '''
    在代码文件开头插入调试相关的头文件和宏定义
    '''
    header_code = '''
#ifndef ONLINE_JUDGE_ONE
    freopen("code_in.txt", "r", stdin);
    freopen("code_log.txt", "w", stdout);
#endif
#include <bits/stdc++.h>
int __ONLINE_JUDGE_ONE_START_SIZE__ = 0;
class __ONLINE_JUDGE_ONE_IN_FN__ {
public:
    __ONLINE_JUDGE_ONE_IN_FN__() { __ONLINE_JUDGE_ONE_START_SIZE__++; }
    ~__ONLINE_JUDGE_ONE_IN_FN__() { __ONLINE_JUDGE_ONE_START_SIZE__--; }
};
'''
    file.schedule_insert(-1, header_code)  # -1 表示插入到最开头

def instrument_code(tokens: list[str], original_code: str):
    '''
    对token列表进行插桩，插入日志代码
    '''
    # 获取行信息
    line_info = token_mod.token_pc(tokens)  # [(start_idx, end_idx, line_num), ...]
    line_map = {}  # token_idx -> line_num
    for start, end, line in line_info:
        for i in range(start, end + 1):
            line_map[i] = line
    
    # 获取忽略范围
    ignore_ranges = token_mod.get_ignore_ranges(tokens)
    
    def is_in_ignore_range(token_idx: int) -> bool:
        """检查token索引是否在忽略范围内"""
        for start, end in ignore_ranges:
            if start <= token_idx <= end:
                return True
        return False
    
    # 提取标识符位置（基于原始字符串）
    identifiers = extract_identifiers(original_code)
    
    # 对每个标识符进行插桩
    for char_pos, var_name in identifiers:
        # 将字符位置映射到token索引
        token_idx = None
        current_pos = 0
        
        for idx, token in enumerate(tokens):
            if current_pos <= char_pos < current_pos + len(token):
                token_idx = idx
                break
            current_pos += len(token)
        
        if token_idx is None:
            continue
        
        # 检查是否在忽略范围内
        if is_in_ignore_range(token_idx):
            continue
        
        # 检查是否是函数调用（下一个token是 '('）
        if token_idx + 1 < len(tokens) and tokens[token_idx + 1] == '(':
            continue
        
        # 检查是否为类型名（简单判断：前一个token是否是类型关键字）
        # 这里可以添加更复杂的类型检查
        
        # 获取行号
        line_num = line_map.get(token_idx, 0)
        
        # 构造安全的变量名（去除可能的问题字符）
        safe_var_name = re.sub(r'[^a-zA-Z0-9_]', '', var_name)
        
        # 准备日志代码
        log_code = f'''
#ifndef ONLINE_JUDGE_ONE
    std::cout << "{line_num}:" << __ONLINE_JUDGE_ONE_START_SIZE__ << ":mem:{token_idx}:" 
              << typeid({safe_var_name}).name() << ':' << std::hex << {safe_var_name} << std::dec << std::endl;
#endif
'''
        # 在该token之后插入
        file.schedule_insert(token_idx, log_code)

def main():
    """主函数：读取代码、插桩、写回"""
    # 读取原始代码
    with open("code.cpp", "r", encoding="utf-8") as f:
        original_code = f.read()
    
    # Tokenize
    tokens = token_mod.tokenize_cpp(original_code)
    
    # 插入调试头文件
    insert_debug_headers()
    
    # 插桩
    instrument_code(tokens, original_code)
    
    # 写回文件
    file.write_code(tokens)

if __name__ == "__main__":
    main()