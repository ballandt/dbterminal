import sqlite3, sys
import os.path

def file_terminal(arg):
    conn = sqlite3.connect(arg)
    c = conn.cursor()
    print("*" * 50)
    print("**" + arg + "**")
    print("tables:")
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for e in c.fetchall():
        print(e[0])
    print("*" * 50)
    run = True
    while run:
        inp = input(os.path.basename(arg)+">").lower()
        if inp == "/exit":
            run = False
        elif inp[:6] == "select":
            c.execute(inp)
            print(c.fetchall())
        else:
            c.execute(inp)
        conn.commit()
    print("Closing connection...")
    conn.close()
    print("Connection closed successfully.")
    return 0

def connect(arg):
    if os.path.isfile(arg):
        print("Opening file\nChecking validity")
        with open(arg, "r") as file:
            if file.readline(13) == "SQLite format":
                print("Valid sqlite file")
                file.close()
                pass
            else:
                print("Error: File is not in Sqlite format.")
                file.close()
                return 1
        file_terminal(arg)
        return 0



def launch(argv):
    """Main terminal"""
    if argv[1]:
        connect(argv[1])
    else:
        run = True
        while run:
            inp = input(">>> ")
            com, arg = inp.split(" ")
            if com == "connect":
                connect(arg)
            elif com == "exit":
                return 0

if __name__ == "__main__":
    launch(sys.argv)