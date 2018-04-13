import os,sys,time
PATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(PATH)
sys.path.append(PATH)
# print(sys.path)
from core import main

if __name__ == '__main__':
    main.ArgvHandler()
