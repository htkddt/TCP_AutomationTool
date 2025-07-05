import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QCalendarWidget, QDialog, QPushButton, QDial, QHBoxLayout,
    QToolButton, QMenu, QSizePolicy
)
from PyQt5.QtCore import QDate, QTime, Qt


class TimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chọn giờ, phút và giây")

        # Tạo 3 QDial cho giờ, phút, giây
        self.hour_dial = QDial()
        self.hour_dial.setRange(0, 23)
        self.hour_dial.setNotchesVisible(True)
        self.hour_dial.setWrapping(True)

        self.minute_dial = QDial()
        self.minute_dial.setRange(0, 59)
        self.minute_dial.setNotchesVisible(True)
        self.minute_dial.setWrapping(True)

        self.second_dial = QDial()
        self.second_dial.setRange(0, 59)
        self.second_dial.setNotchesVisible(True)
        self.second_dial.setWrapping(True)

        # Nhãn hiển thị thời gian đã chọn
        self.label = QLabel()
        self.label.setStyleSheet("font-size: 24px; text-align: center;")

        # Kết nối thay đổi
        self.hour_dial.valueChanged.connect(self.update_label)
        self.minute_dial.valueChanged.connect(self.update_label)
        self.second_dial.valueChanged.connect(self.update_label)

        # Nút xác nhận
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)

        # Layout cho các dial
        dial_layout = QHBoxLayout()
        dial_layout.addWidget(self.hour_dial)
        dial_layout.addWidget(self.minute_dial)
        dial_layout.addWidget(self.second_dial)

        layout = QVBoxLayout()
        layout.addLayout(dial_layout)
        layout.addWidget(self.label)
        layout.addWidget(ok_btn)
        self.setLayout(layout)

        # Đặt giá trị thời gian hiện tại
        now = QTime.currentTime()
        self.hour_dial.setValue(now.hour())
        self.minute_dial.setValue(now.minute())
        self.second_dial.setValue(now.second())
        self.update_label()

    def update_label(self):
        h = self.hour_dial.value()
        m = self.minute_dial.value()
        s = self.second_dial.value()
        self.label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def selected_time(self):
        h = self.hour_dial.value()
        m = self.minute_dial.value()
        s = self.second_dial.value()
        return QTime(h, m, s)


class DateTimePicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Date & Time Picker")

        self.date_label = QLabel("Ngày:")
        self.time_label = QLabel("Giờ:")

        self.date_edit = QLineEdit()
        self.date_edit.setReadOnly(True)
        self.date_edit.setText(QDate.currentDate().toString("dd/MM/yyyy"))
        self.date_edit.mousePressEvent = self.open_calendar

        self.time_edit = QLineEdit()
        self.time_edit.setReadOnly(True)
        self.time_edit.setText(QTime.currentTime().toString("HH:mm"))
        self.time_edit.mousePressEvent = self.open_time_dialog

        layout = QVBoxLayout()
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_edit)
        self.setLayout(layout)

    def open_calendar(self, event):
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())

        # Giao diện đơn giản giống hình
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                font-size: 16px;
            }

            QCalendarWidget QToolButton {
                background-color: #ffffff;
                color: #000000;
                font-size: 16px;
                icon-size: 24px;
            }

            QCalendarWidget QMenu {
                background-color: #ffffff;
                border: 1px solid #ccc;
                font-size: 14px;
            }

            QCalendarWidget QMenu::item {
                padding: 5px 10px;
            }

            QCalendarWidget QMenu::item:selected {
                background-color: #2d8cf0;
                color: white;
            }
        """)

        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn ngày")
        dialog.setMinimumSize(620, 300)
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)

        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if prev_btn: prev_btn.hide()
        if next_btn: next_btn.hide()

        month_btn = self.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        year_btn = self.calendar.findChild(QToolButton, "qt_calendar_yearbutton")
        if month_btn:
            month_btn.setMinimumWidth(300)
            month_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if year_btn: 
            year_btn.setMinimumWidth(300)
            year_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            year_btn.setPopupMode(QToolButton.InstantPopup)
            menu = QMenu()
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 5px 10px;
                }
                QMenu::item:selected {
                    background-color: #2d8cf0;
                    color: white;
                }
            """)

        current_year = QDate.currentDate().year()
        for y in range(current_year - 5, current_year + 6):
            action = menu.addAction(str(y))
            action.triggered.connect(
                lambda checked, year=y: 
                self.calendar.setSelectedDate(QDate(year, self.calendar.selectedDate().month(), self.calendar.selectedDate().day()))
                )
        year_btn.setMenu(menu)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        if dialog.exec_():
            selected_date = self.calendar.selectedDate()
            self.date_edit.setText(selected_date.toString("dd/MM/yyyy"))

    def open_time_dialog(self, event):
        dialog = TimeDialog(self)
        if dialog.exec_():
            selected_time = dialog.selected_time()
            self.time_edit.setText(selected_time.toString("HH:mm"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DateTimePicker()
    window.show()
    sys.exit(app.exec_())
