# -*- coding: utf-8 -*-
import sys
import os

import numpy as np
import pulp
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QGridLayout,
    QApplication,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QWidget,
    QButtonGroup,
    QHBoxLayout,
)


class data(QWidget):
    def __init__(self, layout, i, j, val="0"):
        super().__init__()
        self.text = QLabel(text="*X<SUB>{}</SUB>".format(j))
        self.line = QLineEdit()
        self.line.setText(val)
        self.line.setMaxLength(6)
        layout.addWidget(self.line, i, 2 * j + 2)
        layout.addWidget(self.text, i, 2 * j + 3)

    def delete(self):
        self.text.setParent(None)
        self.line.setParent(None)

    def getdata(self):
        return self.line.text()


class yhead(QWidget):
    def __init__(self, layout, i, val0="0", val1=">"):
        super().__init__()
        self.line0 = QLineEdit()
        self.line1 = QLineEdit()
        self.line0.setText(val0)
        self.line1.setText(val1)
        self.line1.setFixedWidth(20)
        self.line0.setMaxLength(6)
        self.line1.setMaxLength(2)
        layout.addWidget(self.line0, i, 0)
        layout.addWidget(self.line1, i, 1)

    def delete(self):
        self.line0.setParent(None)
        self.line1.setParent(None)

    def getdata(self):
        return self.line0.text(), self.line1.text()


class target(QWidget):
    def __init__(self, layout, info="target = ", b0="max", b1="min"):
        super().__init__()
        self.layout0 = QHBoxLayout()
        self.layout1 = QGridLayout()
        self.layout2 = QHBoxLayout()

        self.layout = QHBoxLayout()

        self.text = QLabel(text=info)

        self.rb0 = QRadioButton(b0, self)
        self.rb1 = QRadioButton(b1, self)
        self.rb0.setChecked(True)
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb0, 0)
        self.bg1.addButton(self.rb1, 1)

        self.layout0.addWidget(self.text)
        self.layout2.addWidget(self.rb0)
        self.layout2.addWidget(self.rb1)
        self.layout.addLayout(self.layout0)
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        layout.addLayout(self.layout)
        self.x = []

    def addpara(self, val="0"):
        self.x.append(data(self.layout1, i=0, j=len(self.x), val=val))

    def delete(self):
        self.x.pop().delete()

    def getdata(self):
        return self.bg1.checkedId(), [t.getdata() for t in self.x]

    def setsense(self, val):
        if val:
            self.rb0.setChecked(True)
        else:
            self.rb1.setChecked(True)


class variable(QWidget):
    def __init__(self, layout, head="x: ", b0="float", b1="int", isV=False):
        super().__init__()
        self.isV = isV
        text = QLabel(text=head)
        self.layout_ = QHBoxLayout()

        self.rb0 = QRadioButton(b0, self)
        self.rb1 = QRadioButton(b1, self)

        self.bound0 = QLineEdit()
        self.bound1 = QLineEdit()
        self.bound0.setText("0")
        self.bound1.setText("Nan")

        self.rb0.setChecked(True)
        self.bg1 = QButtonGroup(self)
        self.bg1.addButton(self.rb0, 0)
        self.bg1.addButton(self.rb1, 1)
        self.layout_.addWidget(text)
        if not self.isV:
            self.name = QLineEdit()
            self.layout_.addWidget(self.name)
        self.layout_.addWidget(self.rb0)
        self.layout_.addWidget(self.rb1)
        self.layout_.addWidget(self.bound0)
        self.layout_.addWidget(self.bound1)

        layout.addLayout(self.layout_)

    def delete(self):
        for i in reversed(range(self.layout_.count())):
            self.layout_.itemAt(i).widget().setParent(None)

    def getdata(self):
        if not self.isV:
            return self.name.text(), self.bg1.checkedId()
        else:
            return self.bg1.checkedId(), self.bound0.text(), self.bound1.text()


class DynAddObject(QDialog):
    def __init__(self, parent=None):
        super(DynAddObject, self).__init__(parent)

        self.txtpath = None
        self.addButton = QPushButton(u"AddConstrain")
        self.add1Button = QPushButton(u"AddVariable")
        self.rmButton = QPushButton(u"RemoveConstrain")
        self.rm1Button = QPushButton(u"RemoveVarisble")
        self.dButton = QPushButton(u"Calculate")
        self.rButton = QPushButton(u"Reload")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout_control = QGridLayout()
        self.layout_table = QGridLayout()
        self.layout_variable = QVBoxLayout()
        self.layout_result = QVBoxLayout()

        self.layout_control.addWidget(self.addButton, 1, 0)
        self.layout_control.addWidget(self.rmButton, 1, 1)
        self.layout_control.addWidget(self.add1Button, 2, 0)
        self.layout_control.addWidget(self.rm1Button, 2, 1)
        self.layout_control.addWidget(self.dButton, 3, 0)
        self.layout_control.addWidget(self.rButton, 3, 1)

        self.layout.addLayout(self.layout_control)
        self.layout.addLayout(self.layout_variable)

        self.layout.addLayout(self.layout_table)
        self.layout.addLayout(self.layout_result)

        self.rmButton.clicked.connect(self.remove_constraint)
        self.addButton.clicked.connect(self.add_constraint)
        self.add1Button.clicked.connect(self.addVariable)
        self.rm1Button.clicked.connect(self.rmVariable)
        self.dButton.clicked.connect(self.getInfo)
        self.rButton.clicked.connect(self.recompose)

        self.lines = []
        self.y = []
        self.variable = []
        self.head = target(self.layout_variable)

    def setBrowerPath(self):
        return QtWidgets.QFileDialog.getOpenFileName(self, "Cherche", os.getcwd())[0]

    def addVariable(self):

        if len(self.lines) == 0:
            self.y.append(yhead(self.layout_table, 0))
            self.lines.append([data(self.layout_table, 0, 0)])
        else:
            row = len(self.lines)
            col = len(self.lines[0])
            for i in range(row):
                self.lines[i].append(data(self.layout_table, i, col))
        self.head.addpara()
        self.variable.append(
            variable(
                self.layout_variable,
                head="X<SUB>{}</SUB>:".format(len(self.variable)),
                isV=True,
            )
        )

    def rmVariable(self):
        if len(self.variable) > 0:
            row = len(self.lines)
            for i in range(row):
                d = self.lines[i].pop()
                d.delete()
            v = self.variable.pop()
            v.delete()
            self.head.delete()

    def remove_constraint(self):
        if len(self.lines) > 0:
            target = self.lines.pop()
            for d in target:
                d.delete()
            self.y.pop().delete()

    def add_constraint(self):
        if len(self.lines) == 0:
            self.y.append(yhead(self.layout_table, 0))
            self.lines.append([data(self.layout_table, 0, 0)])
            self.head.addpara()
            self.variable.append(
                variable(
                    self.layout_variable,
                    head="X<SUB>{}</SUB>:".format(len(self.variable)),
                    isV=True,
                )
            )
        else:
            row = len(self.lines)
            col = len(self.lines[0])
            self.y.append(yhead(self.layout_table, row))
            self.lines.append([data(self.layout_table, row, i) for i in range(col)])

    def clear(self):
        while len(self.lines) > 0:
            self.remove_constraint()
        while len(self.variable) > 0:
            self.rmVariable()

    def getInfo(self):
        sense, target = self.head.getdata()
        f = lambda x: float(x) if x != "Nan" else None
        x = [
            ("X{}".format(i), v.getdata()[0], f(v.getdata()[1]), f(v.getdata()[2]))
            for i, v, in enumerate(self.variable)
        ]
        data = [[c.getdata() for c in t] for t in self.lines]
        y = [t.getdata() for t in self.y]
        s = pSolver(sense=sense, target=target, x=x, y=y, data=data)
        res = {
            "Status": s.getStatus(),
            "Result": s.getResult(),
            "Solution": s.getSolu(),
        }
        panel(self.layout_result, res)

    def recompose(self):
        path = self.setBrowerPath()
        self.clear()
        x, y, z = readMat(path)
        sig, target = z
        self.head.setsense(sig)
        [
            self.head.addpara(t)
            or self.variable.append(
                variable(
                    self.layout_variable,
                    head="X<SUB>{}</SUB>:".format(len(self.variable)),
                    isV=True,
                )
            )
            for t in target
        ]

        for i in range(len(x)):
            self.y.append(yhead(self.layout_table, i, y[i][1], y[i][0]))
            self.lines.append(
                [data(self.layout_table, i, j, val=t) for j, t in enumerate(x[i])]
            )


def readMat(path="test.txt"):
    x = []
    y = []
    z = None
    with open(path, "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            assert len(line.split(" ")) > 2, "Error file format"
            d = {">": "<", "<": ">"}
            term = line.split(" ")
            if term[-1] == "?":
                z = (term[-2] == "<", term[:-2])
            else:
                x.append(term[:-2])
                y.append([d[t] if t in "<>" else t for t in term[-2:]])

    return x, y, z


class panel(QWidget):
    def __init__(self, layout, block):
        super().__init__()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        for k in block.keys():
            text = QLabel(text="{}:".format(k))
            text1 = QLabel(text="{}".format(block.get(k)))
            text1.setAlignment(Qt.AlignCenter)
            layout.addWidget(text)
            layout.addWidget(text1)


class pSolver:
    def __init__(self, sense, target, x, y, data):
        self.data = np.asarray([[float(t0) for t0 in t1] for t1 in data])
        self.target = np.asarray([float(t) for t in target])
        self.sense = pulp.LpMaximize if sense == 0 else pulp.LpMinimize
        self.var = np.asarray(
            [
                pulp.LpVariable(
                    name=t1,
                    cat=pulp.LpContinuous if t2 == 0 else pulp.LpInteger,
                    lowBound=b0,
                    upBound=b1,
                )
                for (t1, t2, b0, b1) in x
            ]
        )
        self.y = y
        self.prob = pulp.LpProblem("TheProblem", self.sense)
        self.prob += self.target.dot(self.var)
        matrix = self.data.dot(self.var)
        for i, (val, sig) in enumerate(self.y):
            if sig == ">" or sig == ">=":
                self.prob += matrix[i] <= float(val)
            elif sig == "<" or sig == "<=":
                self.prob += matrix[i] >= float(val)
            elif sig == "=" or sig == "==":
                self.prob += matrix[i] == float(val)
            else:
                print(sig, " error value")
        self.status = self.prob.solve()
        self.reult = pulp.value(self.prob.objective)

    def getStatus(self):
        return self.status

    def getResult(self):
        return self.reult

    def getSolu(self):
        return "".join(
            ["{}: {}\n".format(i.name, i.varValue) for i in self.prob.variables()]
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = DynAddObject()
    form.show()
    app.exec_()
