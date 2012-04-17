# -*- encoding: utf-8 -*-

def is_cn_char(i):
    if len(i)>1:return True
    return 0x4e00<=ord(i)<0x9fa6


def get_cn_first_letter(str,codec="UTF8"):
    if codec!="GBK":
        if codec!="unicode":
            str=str.decode(codec)
        str=str.encode("GBK")
    if not str: return ''
    if not is_cn_char(str): return str
    
    if str<"\xb0\xa1" or str>"\xd7\xf9":
        return ""
    if str<"\xb0\xc4":
        return "a"
    if str<"\xb2\xc0":
        return "b"
    if str<"\xb4\xed":
        return "c"
    if str<"\xb6\xe9":
        return "d"
    if str<"\xb7\xa1":
        return "e"
    if str<"\xb8\xc0":
        return "f"
    if str<"\xb9\xfd":
        return "g"
    if str<"\xbb\xf6":
        return "h"
    if str<"\xbf\xa5":
        return "j"
    if str<"\xc0\xab":
        return "k"
    if str<"\xc2\xe7":
        return "l"
    if str<"\xc4\xc2":
        return "m"
    if str<"\xc5\xb5":
        return "n"
    if str<"\xc5\xbd":
        return "o"
    if str<"\xc6\xd9":
        return "p"
    if str<"\xc8\xba":
        return "q"
    if str<"\xc8\xf5":
        return "r"
    if str<"\xcb\xf9":
        return "s"
    if str<"\xcd\xd9":
        return "t"
    if str<"\xce\xf3":
        return "w"
    if str<"\xd1\x88":
        return "x"
    if str<"\xd4\xd0":
        return "y"
    if str<"\xd7\xf9":
        return "z"

def get_initial(name):
    s_list = [ get_cn_first_letter(s.strip()) for s in name]
    r_list = [ s.upper() for s in s_list]
    
    return ''.join(r_list)