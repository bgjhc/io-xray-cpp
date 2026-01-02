'''
用于对code进行读写
'''
import token

# 存储待插入的代码片段
_pending_inserts = []  # 格式: (token_idx, code_str)

def schedule_insert(token_idx: int, code: str):
    '''
    计划在某token索引后插入代码片段
    '''
    global _pending_inserts
    _pending_inserts.append((token_idx, code))

def read_code(filename: str = "code.cpp") -> list[str]:
    '''
    读取C++文件并返回token列表
    '''
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return token.tokenize_cpp(content)

def write_code(tokens: list[str], filename: str = "code.cpp"):
    '''
    将token列表写入文件，并执行所有计划的插入
    '''
    global _pending_inserts
    # 按token索引降序排序，避免插入位置偏移
    _pending_inserts.sort(key=lambda x: x[0], reverse=True)
    
    # 执行插入
    for idx, code in _pending_inserts:
        if idx < len(tokens):
            tokens.insert(idx + 1, code)
        else:
            tokens.append(code)
    
    # 写入文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(''.join(tokens))
    
    # 清空待插入列表
    _pending_inserts.clear()