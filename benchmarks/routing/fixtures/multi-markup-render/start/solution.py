from parser import parse
from renderer import render

def solve(record):
    return render(*parse(record))
