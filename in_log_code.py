import file

file.read_code()
def filecode_to_log():
    '''
    以便在本地调试时记录代码到文件code_log.txt中
    '''
    file.write_code(0,'''
#ifndef ONLINE_JUDGE_ONE
    freopen("code_in.txt", "r", stdin);
    freopen("code_log.txt", "w", stdout);
#endif
''')
def code_pc_is_none():
    '''
    检查是否需要忽略
    '''
    hl_h_list=['enum','struct','class','union']#忽略关键词
    code=file.code#读取code
    hl_list=[]#格式:(开始行号,结束行号)
    re_e_list={'}':'{',
               ']':'[',
               ')':'('}
    strak=[]#栈
    strak_id=[]#栈对应行号
    i=0#行号
    while i<len(code):
        if len(strak)==0:
            if code[i] in hl_h_list:
                while code[i]!='{':
                    i+=1
                strak.append(code[i])
                strak_id.append(i)
        else:
            if code[i] in re_e_list.values():
                strak.append(code[i])
            elif code[i] in re_e_list.keys():
                while re_e_list[code[i]]!=strak[-1]:
                    strak.pop()
                    strak_id.pop()
                strak.pop()
                hl_list.append( (strak_id[-1],i) )
                strak_id.pop()
            else:
                pass
        i+=1
    return hl_list
hl_list=code_pc_is_none()
def code_block():
    '''
    code的整体块
    '''
    block_list={'for', 'if','else','while','switch','do','catch'}
    
    pass