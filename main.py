import re
code=[]
code_write_end=[]
def code_in_log():
    '''
    code_in_log会插入
    #ifndef ONLINE_JUDGE_ONE
        freopen("code_in.txt", "r", stdin);
        freopen("code_log.txt", "w", stdout);
    #endif
    到代码文件开头
    以便在本地调试时记录代码到文件code_log.txt中
    '''
    pass