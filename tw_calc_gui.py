import sys
from datetime import timedelta, datetime, date
from math import hypot
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QSizePolicy, QLabel, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QGridLayout, QHBoxLayout,
    QVBoxLayout, QWidget, QDialog, QTabWidget, QApplication)
from PyQt5.QtGui import QFont


class StyleSheet:

    qtextedit_style = "QTextEdit { background-color: white }"
    qwidget_style = "QWidget { background-color: #F4E4BC }"
    qlabel_style = "QLabel { color: #803000; background-color: #F4E4BC}"
    qlineedit_style = "QLineEdit { background-color: white }"
    qcombobox_style = "QComboBox, QListView { background-color: white }"
    qbutton_style = "QPushButton { color: white; margin-top: 0px; \
    margin-bottom: 0; margin-right: 2px; margin-left: 2px; padding: \
    3px; border: 1px solid black; border-radius: 5px; font: bold, 12px; \
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #947A62, \
    stop:0.22 #7B5C3D, stop:0.3 #6C4824, stop:1 #6C4824)} \
    QPushButton:hover { color: white; margin-top: 0px; margin-bottom: 0; \
    margin-right: 2px; margin-left: 2px; padding: 3px; border: 1px \
    solid black; border-radius: 5px; font: bold, 12px; background-color: \
    qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B69471, stop:0.22 #9F764D, \
    stop:0.3 #8F6133, stop:1 #6C4D2D)}"


class TWCalculator:
    @staticmethod
    def world_speed(world):

        if world == "79" or world == "en79" or world == "w79":
            w_speed = 1.2
        elif world == "80" or world == "en80" \
                or world == "w80":
            w_speed = 1.5 * 0.7
        else:
            w_speed = 1.0

        return w_speed

    @staticmethod
    def arrival(arrival_time, arrival_date):

        arr_time = arrival_time.replace(".", ":")
        h, m, s, ms = arr_time.split(":")

        if h == "":
            hrs = 0
        else:
            hrs = int(h)

        if m == "":
            mins = 0
        else:
            mins = int(m)

        if s == "":
            secs = 0
        else:
            secs = int(s)

        if ms == "":
            milsecs = 0
        else:
            milsecs = int(ms)

        arrival_time = timedelta(seconds=secs, milliseconds=milsecs,
                                 minutes=mins, hours=hrs)

        arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d")

        arrival = arrival_date + arrival_time

        return arrival

    @staticmethod
    def unit_speed(unit):
        u_speed = 0
        if (unit == "Spearman" or unit == "Axeman" or
                unit == "Archer"):
            u_speed = 18
        elif unit == "Swordsman":
            u_speed = 22
        elif unit == "Scout":
            u_speed = 9
        elif (unit == "Light Cavalry" or unit ==
                "Mounted Archer" or unit == "Paladin"):
            u_speed = 10
        elif unit == "Heavy Cavalry":
            u_speed = 11
        elif unit == "Ram" or unit == "catapult":
            u_speed = 30
        elif unit == "Nobleman":
            u_speed = 35

        return u_speed

    @staticmethod
    def distance(vill1, vill2):

        vill1_x, vill1_y = vill1.split("|")
        vill2_x, vill2_y = vill2.split("|")

        if vill1_x == '':
            v1_x = 0
        else:
            v1_x = vill1_x
        if vill1_y == '':
            v1_y = 0
        else:
            v1_y = vill1_y
        if vill2_x == '':
            v2_x = 0
        else:
            v2_x = vill2_x
        if vill2_y == '':
            v2_y = 0
        else:
            v2_y = vill2_y

        x = abs(int(v1_x) - int(v2_x))
        y = abs(int(v1_y) - int(v2_y))
        dist = hypot(x, y)

        return dist

    @staticmethod
    def duration(vill1, vill2, world, unit1):

        dist = TWCalculator.distance(vill1, vill2)
        world_speed = TWCalculator.world_speed(world)
        unit_speed = TWCalculator.unit_speed(unit1)

        speed = timedelta(minutes=unit_speed / world_speed)

        duration = dist * speed
        seconds_rounding = timedelta(seconds=1)
        half_sec = timedelta(microseconds=500000)
        micros = duration % seconds_rounding

        if micros != 0:
            if micros >= half_sec:
                duration -= micros + seconds_rounding
            else:
                duration -= micros

        return duration

    @staticmethod
    def send(arrival_time, arrival_date, vill1,
             vill2, world, unit1):

        send_time = (TWCalculator.arrival(arrival_time,
                     arrival_date) - TWCalculator.duration(
            vill1, vill2, world, unit1))

        return send_time

    @staticmethod
    def return_time(arrival_time, arrival_date, vill1,
                    vill2, world, unit1):
        return_time = (TWCalculator.arrival(arrival_time, arrival_date) +
                       TWCalculator.duration(vill1, vill2,
                                             world, unit1))

        return_time = return_time - timedelta(
            microseconds=return_time.microsecond)

        return return_time

    @staticmethod
    def backtime(vill1, vill2, vill3, world,
                 unit1, unit2, arrival_time, arrival_date):

        """Calculate duration from attacking village to defending village,
        then add duration to arrival_time to give return_time. Calculate
        distance from backtiming village to attacking village then
        calculate send_time."""

        backtime_time = (TWCalculator.return_time(arrival_time, arrival_date,
                                                  vill1, vill2, world, unit1) -
                         TWCalculator.duration(vill1,
                         vill3, world, unit2))

        return backtime_time


class TWCalculatorsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.style = StyleSheet
        attack_planner = TWSendTime()
        backtimer = TWBackTime()

        self.tabs = QTabWidget(self)
        self.tabs.addTab(attack_planner, "Attack Planner")
        self.tabs.addTab(backtimer, "Backtime Calculator")

        self.setGeometry(500, 400, 280, 430)
        self.setWindowTitle('Tribal Wars Calculator')

        self.setStyleSheet(self.style.qwidget_style)


class BBCodePopUp(QDialog):
    def __init__(self):
        super().__init__()

        self.style = StyleSheet

        self.output = QTextEdit()
        self.output.setReadOnly(1)
        self.output.setFont(QFont('Courier', 10))
        self.output.setStyleSheet(self.style.qtextedit_style)
        self.output.selectAll()

        dialog_hbox = QHBoxLayout()
        dialog_hbox.addWidget(self.output)

        self.setLayout(dialog_hbox)

        self.setGeometry(520, 420, 550, 150)
        self.setWindowTitle("BB-Codes")
        self.setStyleSheet(self.style.qwidget_style)


class TWSendTime(QWidget):
    def __init__(self):
        super().__init__()

        self.style = StyleSheet

        self.calculator = TWCalculator

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_font = QFont('Verdana', 10, QFont.Bold)
        le_font = QFont('Verdana', 9)

        # World Input
        self.world_lbl = QLabel("World:")
        self.world_lbl.setFont(lbl_font)
        self.world_lbl.setStyleSheet(self.style.qlabel_style)
        self.world_le = QLineEdit()
        self.world_le.setSizePolicy(size_policy)
        self.world_le.setMaximumSize(QSize(40, 24))
        self.world_le.setFont(le_font)
        self.world_le.setStyleSheet(self.style.qlineedit_style)
        self.world_le.selectAll()

        # Attacking village Input
        self.vill1_lbl = QLabel("Attacking village\ncoordinates:")
        self.vill1_lbl.setFont(lbl_font)
        self.vill1_lbl.setStyleSheet(self.style.qlabel_style)
        self.vill1_le = QLineEdit()
        self.vill1_le.setInputMask("000|000")
        self.vill1_le.setText("500|500")
        self.vill1_le.setSizePolicy(size_policy)
        self.vill1_le.setMaximumSize(QSize(60, 24))
        self.vill1_le.setAlignment(Qt.AlignCenter)
        self.vill1_le.setFont(le_font)
        self.vill1_le.setStyleSheet(self.style.qlineedit_style)
        self.vill1_le.selectAll()

        # Defending village Input
        self.vill2_lbl = QLabel("Target village\ncoordinates:")
        self.vill2_lbl.setFont(lbl_font)
        self.vill2_lbl.setStyleSheet(self.style.qlabel_style)
        self.vill2_le = QLineEdit()
        self.vill2_le.inputMask()
        self.vill2_le.setInputMask('000|000')
        self.vill2_le.setText("500|500")
        self.vill2_le.setSizePolicy(size_policy)
        self.vill2_le.setMaximumSize(QSize(60, 24))
        self.vill2_le.setAlignment(Qt.AlignCenter)
        self.vill2_le.setFont(le_font)
        self.vill2_le.setStyleSheet(self.style.qlineedit_style)

        # Unit Input
        self.unit_lbl = QLabel("Slowest unit:")
        self.unit_lbl.setFont(lbl_font)
        self.unit_lbl.setStyleSheet(self.style.qlabel_style)
        self.unit_combo = QComboBox(self)
        self.unit_combo.addItem("Spearman")
        self.unit_combo.addItem("Swordsman")
        self.unit_combo.addItem("Axeman")
        self.unit_combo.addItem("Archer")
        self.unit_combo.addItem("Scout")
        self.unit_combo.addItem("Light Cavalry")
        self.unit_combo.addItem("Mounted Archer")
        self.unit_combo.addItem("Heavy Cavalry")
        self.unit_combo.addItem("Ram")
        self.unit_combo.addItem("Catapult")
        self.unit_combo.addItem("Paladin")
        self.unit_combo.addItem("Nobleman")
        self.unit_combo.setSizePolicy(size_policy)
        self.unit_combo.setFont(le_font)
        self.unit_combo.setMaxVisibleItems(12)
        self.unit_combo.setStyleSheet(self.style.qcombobox_style)

        # Arrival date Input
        self.arrival_date_lbl = QLabel("Arrival date:")
        self.arrival_date_lbl.setStyleSheet(self.style.qlabel_style)
        self.arrival_date_lbl.setFont(lbl_font)
        self.arrival_date_le = QLineEdit()
        self.arrival_date_le.setSizePolicy(size_policy)
        self.arrival_date_le.setMaximumSize(QSize(100, 24))
        self.arrival_date_le.setInputMask('0000-00-00')
        self.arrival_date_le.setText(str(date.today()))
        self.arrival_date_le.setFont(le_font)
        self.arrival_date_le.setStyleSheet(self.style.qlineedit_style)
        self.arrival_date_le.selectAll()

        # Arrival time Input
        self.arrival_time_lbl = QLabel("Arrival time:")
        self.arrival_time_lbl.setStyleSheet(self.style.qlabel_style)
        self.arrival_time_lbl.setFont(lbl_font)
        self.arrival_time_le = QLineEdit()
        self.arrival_time_le.setSizePolicy(size_policy)
        self.arrival_time_le.setMaximumSize(QSize(100, 24))
        self.arrival_time_le.setInputMask('00:00:00.000')
        self.arrival_time_le.setText(
            ((datetime.utcnow()).strftime("%H:%M:%S.%f")).rstrip('0'))
        self.arrival_time_le.setFont(le_font)
        self.arrival_time_le.setStyleSheet(self.style.qlineedit_style)

        # Output for distance and duration
        self.calc_te = QTextEdit()
        self.calc_te.setReadOnly(1)
        self.calc_te.setFont(le_font)
        self.calc_te.setStyleSheet("QTextEdit { background-color: white } ")

        # Buttons for calculating, resetting, cancelling and BB-Code formatting.
        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.setStyleSheet(self.style.qbutton_style)
        self.calc_btn.clicked.connect(self.text_output)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(self.style.qbutton_style)
        self.reset_btn.clicked.connect(self.reset)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(self.style.qbutton_style)

        self.bbcode_btn = QPushButton("BB-Code Format")
        self.bbcode_btn.clicked.connect(self.show_dialog)
        self.bbcode_btn.setStyleSheet(self.style.qbutton_style)

        grid = QGridLayout()
        grid.addWidget(self.world_lbl, 1, 0)
        grid.addWidget(self.world_le, 1, 1)
        grid.addWidget(self.vill1_lbl, 2, 0)
        grid.addWidget(self.vill1_le, 2, 1)
        grid.addWidget(self.vill2_lbl, 3, 0)
        grid.addWidget(self.vill2_le, 3, 1)
        grid.addWidget(self.unit_lbl, 4, 0)
        grid.addWidget(self.unit_combo, 4, 1)
        grid.addWidget(self.arrival_date_lbl, 5, 0)
        grid.addWidget(self.arrival_date_le, 5, 1)
        grid.addWidget(self.arrival_time_lbl, 6, 0)
        grid.addWidget(self.arrival_time_le, 6, 1)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.calc_btn)
        btn_hbox.addWidget(self.reset_btn)
        btn_hbox.addWidget(self.cancel_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(btn_hbox)
        vbox.addWidget(self.calc_te)
        vbox.addWidget(self.bbcode_btn)

        self.setLayout(vbox)

        QWidget.setTabOrder(self.world_le, self.vill1_le)
        QWidget.setTabOrder(self.vill1_le, self.vill2_le)
        QWidget.setTabOrder(self.vill2_le, self.unit_combo)
        QWidget.setTabOrder(self.unit_combo, self.arrival_date_le)
        QWidget.setTabOrder(self.arrival_date_le, self.arrival_time_le)
        QWidget.setTabOrder(self.arrival_time_le, self.calc_btn)
        QWidget.setTabOrder(self.calc_btn, self.reset_btn)
        QWidget.setTabOrder(self.reset_btn, self.cancel_btn)
        QWidget.setTabOrder(self.cancel_btn, self.bbcode_btn)

        self.setMaximumSize(275, 360)
        self.setStyleSheet(self.style.qwidget_style)

    def text_output(self):

        vill1 = self.vill1_le.text()
        vill2 = self.vill2_le.text()
        world = self.world_le.text()
        unit = self.unit_combo.currentText()
        arrival_time = self.arrival_time_le.text()
        arrival_date = self.arrival_date_le.text()
        distance = str(round(self.calculator.distance(vill1, vill2), 2))
        duration = str(self.calculator.duration(vill1, vill2,
                                                world, unit))
        send_time = str(self.calculator.send(
            arrival_time, arrival_date, vill1, vill2, world, unit)).rstrip('0')

        self.calc_te.setPlainText("""Distance to defending village: %s
Duration to defending village: %s
Send attack at: %s
""" % (distance, duration, send_time))

    def show_dialog(self):

        world = self.world_le.text()
        vill1 = self.vill1_le.text()
        vill2 = self.vill2_le.text()
        unit = self.unit_combo.currentText()
        arrival_time = self.arrival_time_le.text()
        arrival_date = self.arrival_date_le.text()
        arrival = str(self.calculator.arrival(
            arrival_time, arrival_date)).rstrip('0')
        duration = str(self.calculator.duration(vill1, vill2,
                                                world, unit))
        send = str(self.calculator.send(
            arrival_time, arrival_date, vill1, vill2, world, unit)).rstrip('0')

        dialog = BBCodePopUp()

        dialog.output.setText("Launch %s from [coord]%s[/coord] to \
[coord]%s[/coord] at [b]%s[/b] ([i]arriving at %s after %s travel time[/i])" %
                              (unit, vill1, vill2, send, arrival, duration))
        dialog.exec()

    def reset(self):

        self.vill1_le.clear()
        self.vill2_le.clear()
        self.unit_combo.setCurrentIndex(0)
        self.arrival_time_le.setText(
            ((datetime.utcnow()).strftime("%H:%M:%S.%f")).rstrip('0'))
        self.calc_te.clear()


class TWBackTime(QWidget):
    def __init__(self):
        super().__init__()

        self.style = StyleSheet

        self.calculator = TWCalculator

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_font = QFont('Verdana', 10, QFont.Bold)
        le_font = QFont('Verdana', 9)

        # World Input
        self.world_lbl = QLabel("World:")
        self.world_lbl.setFont(lbl_font)
        self.world_lbl.setStyleSheet(self.style.qlabel_style)
        self.world_le = QLineEdit()
        self.world_le.setSizePolicy(size_policy)
        self.world_le.setMaximumSize(QSize(40, 24))
        self.world_le.setFont(le_font)
        self.world_le.setStyleSheet(self.style.qlineedit_style)

        # Attacking village Input
        self.vill1_lbl = QLabel("Attacking village\ncoordinates:")
        self.vill1_lbl.setFont(lbl_font)
        self.vill1_lbl.setStyleSheet(self.style.qlabel_style)
        self.vill1_le = QLineEdit()
        self.vill1_le.setInputMask('000|000')
        self.vill1_le.setSizePolicy(size_policy)
        self.vill1_le.setMaximumSize(QSize(60, 24))
        self.vill1_le.setAlignment(Qt.AlignCenter)
        self.vill1_le.setFont(le_font)
        self.vill1_le.setStyleSheet(self.style.qlineedit_style)

        # Defending village Input
        self.vill2_lbl = QLabel("Defending village\ncoordinates:")
        self.vill2_lbl.setFont(lbl_font)
        self.vill2_lbl.setStyleSheet(self.style.qlabel_style)
        self.vill2_le = QLineEdit()
        self.vill2_le.inputMask()
        self.vill2_le.setInputMask('000|000')
        self.vill2_le.setSizePolicy(size_policy)
        self.vill2_le.setMaximumSize(QSize(60, 24))
        self.vill2_le.setAlignment(Qt.AlignCenter)
        self.vill2_le.setFont(le_font)
        self.vill2_le.setStyleSheet(self.style.qlineedit_style)

        # Backtiming village Input
        self.vill3_lbl = QLabel("Backtime village\ncoordinates:")
        self.vill3_lbl.setFont(lbl_font)
        self.vill3_lbl.setStyleSheet(self.style.qlabel_style)
        self.vill3_le = QLineEdit()
        self.vill3_le.inputMask()
        self.vill3_le.setInputMask('000|000')
        self.vill3_le.setSizePolicy(size_policy)
        self.vill3_le.setMaximumSize(QSize(60, 24))
        self.vill3_le.setAlignment(Qt.AlignCenter)
        self.vill3_le.setFont(le_font)
        self.vill3_le.setStyleSheet(self.style.qlineedit_style)
        self.vill3_opt_lbl = QLabel("(optional)")

        # Unit Input for attacking village
        self.unit1_lbl = QLabel("Attacking village\nslowest unit:")
        self.unit1_lbl.setFont(lbl_font)
        self.unit1_lbl.setStyleSheet(self.style.qlabel_style)
        self.unit1_combo = QComboBox(self)
        self.unit1_combo.addItem("Spearman")
        self.unit1_combo.addItem("Swordsman")
        self.unit1_combo.addItem("Axeman")
        self.unit1_combo.addItem("Archer")
        self.unit1_combo.addItem("Scout")
        self.unit1_combo.addItem("Light Cavalry")
        self.unit1_combo.addItem("Mounted Archer")
        self.unit1_combo.addItem("Heavy Cavalry")
        self.unit1_combo.addItem("Ram")
        self.unit1_combo.addItem("Catapult")
        self.unit1_combo.addItem("Paladin")
        self.unit1_combo.addItem("Nobleman")
        self.unit1_combo.setSizePolicy(size_policy)
        self.unit1_combo.setFont(le_font)
        self.unit1_combo.setMaxVisibleItems(12)
        self.unit1_combo.setStyleSheet(self.style.qcombobox_style)

        # Unit Input for backtiming village
        self.unit2_lbl = QLabel("Backtime village\nslowest unit:")
        self.unit2_lbl.setFont(lbl_font)
        self.unit2_lbl.setStyleSheet(self.style.qlabel_style)
        self.unit2_combo = QComboBox(self)
        self.unit2_combo.addItem("Spearman")
        self.unit2_combo.addItem("Swordsman")
        self.unit2_combo.addItem("Axeman")
        self.unit2_combo.addItem("Archer")
        self.unit2_combo.addItem("Scout")
        self.unit2_combo.addItem("Light Cavalry")
        self.unit2_combo.addItem("Mounted Archer")
        self.unit2_combo.addItem("Heavy Cavalry")
        self.unit2_combo.addItem("Ram")
        self.unit2_combo.addItem("Catapult")
        self.unit2_combo.addItem("Paladin")
        self.unit2_combo.addItem("Nobleman")
        self.unit2_combo.setSizePolicy(size_policy)
        self.unit2_combo.setFont(le_font)
        self.unit2_combo.setMaxVisibleItems(12)
        self.unit2_combo.setStyleSheet(self.style.qcombobox_style)

        # Arrival date Input
        self.arrival_date_lbl = QLabel("Arrival date:")
        self.arrival_date_lbl.setStyleSheet(self.style.qlabel_style)
        self.arrival_date_lbl.setFont(lbl_font)
        self.arrival_date_le = QLineEdit()
        self.arrival_date_le.setSizePolicy(size_policy)
        self.arrival_date_le.setMaximumSize(QSize(100, 24))
        self.arrival_date_le.setInputMask('0000-00-00')
        self.arrival_date_le.setText(str(date.today()))
        self.arrival_date_le.setFont(le_font)
        self.arrival_date_le.setStyleSheet(self.style.qlineedit_style)

        # Arrival time Input
        self.arrival_time_lbl = QLabel("Incoming attack\narrival time:")
        self.arrival_time_lbl.setStyleSheet(self.style.qlabel_style)
        self.arrival_time_lbl.setFont(lbl_font)
        self.arrival_time_le = QLineEdit()
        self.arrival_time_le.setSizePolicy(size_policy)
        self.arrival_time_le.setMaximumSize(QSize(100, 24))
        self.arrival_time_le.setInputMask('00:00:00.000')
        self.arrival_time_le.setText(
            ((datetime.utcnow()).strftime("%H:%M:%S.%f")).rstrip('0'))
        self.arrival_time_le.setFont(le_font)
        self.arrival_time_le.setStyleSheet(self.style.qlineedit_style)

        # Output for distance and duration
        self.calc_te = QTextEdit()
        self.calc_te.setReadOnly(1)
        self.calc_te.setFont(le_font)
        self.calc_te.setStyleSheet(self.style.qtextedit_style)

        # Buttons for calculating, resetting, and cancelling.
        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.setStyleSheet(self.style.qbutton_style)
        self.calc_btn.clicked.connect(self.text_output)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(self.style.qbutton_style)
        self.reset_btn.clicked.connect(self.reset)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(self.style.qbutton_style)
        self.bbcode_btn = QPushButton("BB-Code Format")
        self.bbcode_btn.clicked.connect(self.show_dialog)
        self.bbcode_btn.setStyleSheet(self.style.qbutton_style)

        grid = QGridLayout()
        grid.addWidget(self.world_lbl, 1, 0)
        grid.addWidget(self.world_le, 1, 1)
        grid.addWidget(self.vill1_lbl, 2, 0)
        grid.addWidget(self.vill1_le, 2, 1)
        grid.addWidget(self.vill2_lbl, 3, 0)
        grid.addWidget(self.vill2_le, 3, 1)
        grid.addWidget(self.vill3_lbl, 4, 0)
        grid.addWidget(self.vill3_le, 4, 1)
        grid.addWidget(self.unit1_lbl, 5, 0)
        grid.addWidget(self.unit1_combo, 5, 1)
        grid.addWidget(self.unit2_lbl, 6, 0)
        grid.addWidget(self.unit2_combo, 6, 1)
        grid.addWidget(self.arrival_date_lbl, 7, 0)
        grid.addWidget(self.arrival_date_le, 7, 1)
        grid.addWidget(self.arrival_time_lbl, 8, 0)
        grid.addWidget(self.arrival_time_le, 8, 1)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.calc_btn)
        btn_hbox.addWidget(self.reset_btn)
        btn_hbox.addWidget(self.cancel_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(btn_hbox)
        vbox.addWidget(self.calc_te)
        vbox.addWidget(self.bbcode_btn)

        self.setLayout(vbox)

        QWidget.setTabOrder(self.world_le, self.vill1_le)
        QWidget.setTabOrder(self.vill1_le, self.vill2_le)
        QWidget.setTabOrder(self.vill2_le, self.vill3_le)
        QWidget.setTabOrder(self.vill3_le, self.unit1_combo)
        QWidget.setTabOrder(self.unit1_combo, self.unit2_combo)
        QWidget.setTabOrder(self.unit2_combo, self.arrival_date_le)
        QWidget.setTabOrder(self.arrival_date_le, self.arrival_time_le)
        QWidget.setTabOrder(self.arrival_time_le, self.calc_btn)
        QWidget.setTabOrder(self.calc_btn, self.reset_btn)
        QWidget.setTabOrder(self.reset_btn, self.cancel_btn)
        QWidget.setTabOrder(self.cancel_btn, self.bbcode_btn)

        self.setMaximumSize(275, 400)
        self.setStyleSheet(self.style.qwidget_style)

    def text_output(self):

        vill1 = self.vill1_le.text()
        vill2 = self.vill2_le.text()
        if self.vill3_le.text() == "|":
            vill3 = self.vill2_le.text()
        else:
            vill3 = self.vill3_le.text()
        world = self.world_le.text()
        unit1 = self.unit1_combo.currentText()
        unit2 = self.unit2_combo.currentText()
        arrival_date = self.arrival_date_le.text()
        arrival_time = self.arrival_time_le.text()

        distance1 = str(round(self.calculator.distance(vill1, vill2), 2))
        duration1 = str(self.calculator.duration(vill1, vill2,
                                                 world, unit1))
        distance2 = str(round(self.calculator.distance(vill1, vill3), 2))
        duration2 = str(self.calculator.duration(vill1, vill3,
                                                 world, unit2))
        return_time = str(self.calculator.return_time(
            arrival_time, arrival_date, vill1, vill2, world, unit1))
        backtime_time = str(self.calculator.backtime(
            vill1, vill2, vill3, world, unit1, unit2, arrival_time,
            arrival_date)).rstrip('0')
        self.calc_te.setPlainText("""Distance to defending village: %s
Duration to defending village: %s
Distance from backtiming village: %s
Duration from backtiming village: %s
Attacker's troops return at: %s
Send backtime at: %s
""" % (distance1, duration1, distance2, duration2, return_time, backtime_time))

    def show_dialog(self):

        vill1 = self.vill1_le.text()
        vill2 = self.vill2_le.text()
        if self.vill3_le.text() != "|":
            vill3 = self.vill3_le.text()
        else:
            vill3 = self.vill2_le.text()
        world = self.world_le.text()
        unit1 = self.unit1_combo.currentText()
        unit2 = self.unit2_combo.currentText()
        arrival_date = self.arrival_date_le.text()
        arrival_time = self.arrival_time_le.text()

        duration2 = str(self.calculator.duration(vill1, vill3,
                                                 world, unit2))

        return_time = str(self.calculator.return_time(
            arrival_time, arrival_date, vill1, vill2, world, unit1))
        backtime_time = str(self.calculator.backtime(vill1, vill2, vill3,
                world, unit1, unit2, arrival_time, arrival_date)).rstrip('0')

        dialog = BBCodePopUp()

        dialog.output.setText("Launch %s from [coord]%s[/coord] to \
[coord]%s[/coord] at [b]%s[/b] ([i]arriving at %s after %s travel time[/i])" %
                (unit2, vill3, vill1, backtime_time, return_time, duration2))
        dialog.exec()

    def reset(self):

        self.vill1_le.clear()
        self.vill2_le.clear()
        self.vill3_le.clear()
        self.unit2_combo.setCurrentIndex(0)
        self.arrival_time_le.setText(
            ((datetime.utcnow()).strftime("%H:%M:%S.%f")).rstrip('0'))
        self.calc_te.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tw = TWCalculatorsWindow()
    tw.show()
    sys.exit(app.exec_())
