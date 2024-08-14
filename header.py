import os


def init():
    if os.path.exists("/usr/bin/figlet") or os.path.exists("/usr/local/bin/figlet"):
        os.system('figlet -f "ANSI Shadow" "z-core"')
    else:
        print("z-core")
