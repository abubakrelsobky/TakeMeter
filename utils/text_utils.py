import re

def clean_text(s):
    if not isinstance(s,str): return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s
