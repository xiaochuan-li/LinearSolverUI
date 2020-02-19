# *_*coding:utf-8 *_*
import os
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory

from scipy.optimize import linprog


class el:
    def __init__(self, r, i, j, width=6, height=1, val=0):
        self.v = StringVar()
        self.v.set(val)
        self.e = Entry(r, width=width, textvariable=self.v)
        self.e.grid(row=i, column=2 * j)
        self.l = Label(r, text="X{}".format(j).ljust(4, " "), height=height)
        self.l.grid(row=i, column=2 * j + 1)

    def get(self):
        return self.v.get()

    def delete(self):
        self.l.destroy()
        self.e.destroy()


class ye2:
    def __init__(self, r, i, width=2, hint="<", isEnd=False):
        self.v0 = StringVar()
        self.v0.set(hint)
        self.e = Entry(r, width=width, textvariable=self.v0)
        self.e.grid(row=i, column=int(isEnd))
        self.l = None
        if isEnd:
            self.l = Label(r, text="Y{}".format(i).ljust(4, " "), height=1)
            self.l.grid(row=i, column=2)

    def get(self):
        return self.v0.get()

    def delete(self):
        self.e.destroy()
        if self.l:
            self.l.destroy()


def solver(x_data, y_data):
    c_signal = 1
    c = None
    A1 = []
    A2 = []
    b1 = []
    b2 = []
    for i, (sig, value) in enumerate(y_data):
        assert sig in "<>=", "error format"
        if value == "?" or value == "？":
            c_signal = 1 if sig == ">" else -1
            c = [c_signal * float(x) for x in x_data[i]]
        elif sig == "=":
            A1.append([float(x) for x in x_data[i]])
            b1.append(float(value))
        else:
            signal = 1 if sig == "<" else -1
            A2.append([signal * float(x) for x in x_data[i]])
            b2.append(signal * float(value))

    if len(A1) == 0:
        A1 = None
        b1 = None
    if len(A2) == 0:
        A2 = None
        b2 = None
    res = linprog(c, A2, b2, A1, b1, bounds=None)
    new_res = {
        "result": c_signal * res.get("fun"),
        "status": res.get("success"),
        "x_res": res.get("x"),
    }

    return new_res


class value:
    def __init__(self, i):
        self.val = i

    def get(self):
        return self.val


def readMat(path="test.txt"):
    x = []
    y = []
    try:
        with open(path, "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                assert len(line.split(" ")) > 2
                "Error file format"
                x.append([value(t) for t in line.split(" ")[:-2]])
                y.append([value(t) for t in line.split(" ")[-2:]])
    except:
        return None, None
    return x, y


class saveUI:
    def __init__(self):
        self.dir = "./"
        self.name = "newfile.txt"
        self.root = Tk()
        self.bt = Button(
            self.root, text="choose dir", command=lambda: self.selectPath()
        )
        self.label = Label(self.root, text="filename:")
        self.entry = Entry(self.root)
        self.comfirm = Button(
            self.root, text="confirm", command=lambda: self.get_path()
        )
        self.bt.grid(row=1, column=0)
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.comfirm.grid(row=1, column=1)
        self.root.mainloop()

    def selectPath(self):
        self.dir = askdirectory(title=u"select a dir")

    def get_path(self):
        name = self.entry.get()
        if name != "":
            self.name = name
        self.root.destroy()

    def __call__(self):
        return os.path.join(self.dir, self.name)


class inter:
    def __init__(self):
        t = Table()
        c = controlPanal(t)
        c()


class controlPanal:
    def __init__(self, table):
        self.root = Tk()
        table.root.update()
        screen_height = table.root.winfo_screenheight()
        screen_width = table.root.winfo_screenwidth()
        win_height = table.root.winfo_height()
        win_width = table.root.winfo_width()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        table.root.geometry("+{}+{}".format(x, y - 240))
        self.root.geometry("+{}+{}".format(x - 240, y - 240))
        self.b0 = Button(
            self.root,
            text="commit".center(20, " "),
            width=25,
            command=lambda: table.cal(),
        )
        self.b0.grid(row=5, column=0)
        self.b3 = Button(
            self.root,
            text="choose".center(20, " "),
            width=25,
            command=lambda: table.selectPath(),
        )
        self.b3.grid(row=4, column=0)
        self.b1 = Button(
            self.root,
            text="add row".center(20, " "),
            width=25,
            command=lambda: table.addrow(),
        )
        self.b1.grid(row=0, column=0)
        self.b2 = Button(
            self.root,
            text="add col".center(20, " "),
            width=25,
            command=lambda: table.addcol(),
        )
        self.b2.grid(row=1, column=0)
        self.b1 = Button(
            self.root,
            text="remove row".center(20, " "),
            width=25,
            command=lambda: table.rmrow(),
        )
        self.b1.grid(row=2, column=0)
        self.b2 = Button(
            self.root,
            text="remove col".center(20, " "),
            width=25,
            command=lambda: table.rmcol(),
        )
        self.b2.grid(row=3, column=0)
        self.b2 = Button(
            self.root,
            text="save".center(20, " "),
            width=25,
            command=lambda: table.savedata(),
        )
        self.b2.grid(row=6, column=0)
        self.b4 = Button(
            self.root,
            text="quit".center(20, " "),
            width=25,
            command=lambda: table.root.destroy() or self.root.destroy(),
        )
        self.b4.grid(row=7, column=0)

    def __call__(self, *args, **kwargs):
        self.root.mainloop()


class Table:
    def __init__(self):
        self.y_s = []
        self.row = 0
        self.col = 0
        self.para = []
        self.root = Tk()
        self.root.overrideredirect(True)
        self.f0 = Frame(self.root)
        self.f0.grid(row=0, column=0)
        Label(self.f0, text="Coefficient for constrains:").grid(row=0, column=0)
        self.fdata = Frame(self.root)
        self.fdata.grid(row=1, column=0)
        self.f1 = Frame(self.fdata)
        self.f1.grid(row=0, column=0)
        self.f2 = Frame(self.fdata)
        self.f2.grid(row=0, column=1)
        self.fres = Frame(self.root)
        self.fres.grid(row=2, column=0)
        Label(self.fres, text="Result:").grid(row=0, column=0)

    def __call__(self, *args, **kwargs):
        self.root.mainloop()

    def selectPath(self):
        path_ = askopenfilename(title=u"select a file")
        x, y = readMat(path_)
        if not x or not y:
            return
        self.complete(x, y)
        return self.cal()

    def rmrow(self):
        temprow = self.para.pop()
        tempcol = self.y_s.pop()
        [t.delete() for t in temprow]
        [t.delete() for t in tempcol]
        self.row -= 1

    def rmcol(self):
        [t.pop().delete() for t in self.para]
        self.col -= 1

    def complete(self, x, y):
        while self.row > 0:
            self.rmrow()
        while self.col > 0:
            self.rmcol()
        for i in range(len(x)):
            self.para.append(
                [self.add_data(i, j, x[i][j].get()) for j in range(len(x[0]))]
            )
            self.y_s.append(self.add_y(i, v_s=y[i][0].get(), val=y[i][1].get()))
        self.row = len(x)
        self.col = len(x[0])

    def add_data(self, i, j, val=0):
        return el(r=self.f1, i=i, j=j, val=val)

    def add_y(self, row, v_s="<", val=0):
        return (
            ye2(r=self.f2, i=row, hint=v_s),
            ye2(r=self.f2, i=row, width=6, hint=str(val), isEnd=True),
        )

    def addrow(self):
        if self.col == 0 and self.row == 0:
            self.para.append([self.add_data(0, 0)])
            self.y_s.append(self.add_y(0))
            self.col += 1
            self.row += 1
            return
        new_row = []
        for i in range(self.col):
            new_row.append(self.add_data(self.row, i))
        self.y_s.append(self.add_y(self.row))
        if len(new_row) != 0:
            self.row += 1
            self.para.append(new_row)

    def addcol(self):
        if self.col == 0 and self.row == 0:
            self.para.append([self.add_data(0, 0)])
            self.y_s.append(self.add_y(0))
            self.col += 1
            self.row += 1
            return
        for i in range(self.row):
            self.para[i].append(self.add_data(i, self.col))
        self.col += 1

    def solver(self, x, y):
        res = solver(x, y)
        x_res = res.get("x_res")
        y_res = res.get("result")
        status = res.get("status")
        restr1 = "status: " + str(status)
        restr2 = "X: " + ",".join([str(t) for t in x_res])
        restr3 = "Y: " + str(y_res)
        Label(self.fres, text=restr1).grid(row=1, column=0)
        Label(self.fres, text=restr2).grid(row=2, column=0)
        Label(self.fres, text=restr3).grid(row=3, column=0)
        return solver(x, y)

    def cal(self):
        x = [[float(t.get()) for t in x] for x in self.para]
        y = [(t1.get(), t2.get()) for (t1, t2) in self.y_s]
        return self.solver(x, y)

    def savedata(self):
        newui = saveUI()
        with open(newui(), "w") as f:
            for i, line in enumerate(self.para):
                f.write(
                    " ".join([t.get() for t in line])
                    + " "
                    + " ".join([t.get() for t in self.y_s[i]])
                    + "\n"
                )
            f.close()


if __name__ == "__main__":
    u = inter()
