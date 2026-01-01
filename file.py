'''
用于对code进行读写
write_code(pc:int, code:str) 用于写入code
read_code() 读取code
sleep_code_file() 用于将code写入文件
'''

import token
end_add_code = []#格式:行号->代码
code=[]
def in_code(pc:int, code:str):
    '''
    用于写入code
    '''
    global end_add_code
    end_add_code.append((pc,code))

def read_code():
    '''
    读取code
    '''
    global code
    code=token.tokenize_cpp(
        open("code.cpp","r").read()
    )
    return code

def sleep_code_file():
    '''
    用于将code写入文件
    '''
    global code,end_add_code
    pc_list=token.token_pc(code)
    with open("code.cpp","w") as f:
        for pc,add_code in end_add_code:
            try:
                code.insert(pc_list[pc][0],add_code)
            except:
                code.append(add_code)
        for i in range(len(code)):
            f.write(code[i])