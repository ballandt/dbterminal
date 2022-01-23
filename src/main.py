import sqlite3
import cmd
import sys

db_path = sys.argv[1]
db_name = db_path.split("\\")[-1]


class Terminal(cmd.Cmd):
    intro = db_path
    prompt = ""
    active_table = None

    def __init__(self, db, cursor):
        super().__init__()
        self.db = db
        self.cursor = cursor
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        self.tables = [e[0] for e in self.cursor.fetchall()]
        Terminal.prompt = f"{db_name}>"

    def default(self, line: str) -> bool:
        print(f"Error: '{line.split(' ')[0]}' is not a valid command")
        return False

    def do_close(self, line):
        self.db.commit()
        self.db.close()
        return True

    def do_print(self, line):
        if line == "tables":
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            for e in self.cursor.fetchall():
                print(e[0])
        elif line == "all":
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            print(c.fetchall())
        elif line == "columns":
            if not Terminal.active_table:
                print("Error: no active table")
            else:
                self.cursor.execute(
                    f"PRAGMA table_info({Terminal.active_table});"
                )
                for e in self.cursor.fetchall():
                    print(f"'{e[1]}' of type {e[2].upper()}")
        elif line.split(" ")[0] == "column":
            self.cursor.execute(
                f"PRAGMA table_info({Terminal.active_table});"
            )
            table_names = [e[1] for e in self.cursor.fetchall()]
            if not line.split(" ")[1] in table_names:
                print(f"Error: column {line.split(' ')[1]} does not exist.")
            else:
                self.cursor.execute(f"SELECT {line.split(' ')[1]} FROM "
                                    f"{Terminal.active_table}")
                for e in self.cursor.fetchall():
                    print(e[0])
        elif line == "table":
            if not Terminal.active_table:
                print("Error: no active table")
            else:
                self.cursor.execute(
                    f"SELECT * FROM {Terminal.active_table};"
                )
                values = self.cursor.fetchall()
                self.cursor.execute(
                    f"PRAGMA table_info({Terminal.active_table});"
                )
                table_names = [e[1] for e in self.cursor.fetchall()]
                max_len = []
                for i in range(len(values[0])):
                    sorted_by_len = sorted([str(e[i]) for e in values],
                                           key=len,
                                           reverse=True)
                    if len(table_names[i]) < len(sorted_by_len[0]):
                        max_len.append(len(sorted_by_len[0]))
                    else:
                        max_len.append(len(table_names[i]))
                for i in range(len(table_names)):
                    print(table_names[i], end="")
                    print((max_len[i]-len(table_names[i]))*" ", end="|")
                print("")
                for i in range(len(table_names)):
                    print(max_len[i]*"-", end="")
                    print("|", end="")
                print("")
                for i in range(len(values)):
                    for j in range(len(table_names)):
                        print(values[i][j], end="")
                        print((max_len[j]-len(str(values[i][j])))*" ", end="|")
                    print("")
        return False

    def do_enter(self, line):
        line = line.split(" ")
        if line[0] == "table":
            if Terminal.active_table:
                print(f"Error: table {Terminal.active_table} not still active")
            else:
                if line[1] in self.tables:
                    Terminal.active_table = line[1]
                    Terminal.prompt = f"{Terminal.prompt[:-1]} " \
                                      f"table: {line[1]}>"
                else:
                    print(f"Error: table {line[1]} not found.")
        return False

    def do_exit(self, line):
        if line.split(" ")[0] == "table":
            if not Terminal.active_table:
                print("Error: no active table to exit")
            else:
                Terminal.active_table = None
                Terminal.prompt = f"{Terminal.prompt.split(' table:')[0]}>"
        return False

    def do_add(self, line):
        args = line.split(" ")
        if args[0] == "table":
            if not args[0] in self.tables:
                com = f"CREATE TABLE {args[1]} ("
                for e in args[2:]:
                    com += e.replace(":", " ") + ", "
                com = com[:-2] + ")"
                self.cursor.execute(com)
        elif args[0] == "row":
            if not Terminal.active_table:
                print("Error: no active table")
            else:
                com = f"INSERT INTO {Terminal.active_table} VALUES " \
                      f"{tuple(args[1:])}"
                try:
                    self.cursor.execute(com)
                    self.db.commit()
                except sqlite3.OperationalError:
                    print("Error: input did not fit in the pattern")

    def do_exe(self, line):
        self.cursor.execute(line)
        self.db.commit()
        return False


if __name__ == "__main__":
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    Terminal(conn, c).cmdloop()