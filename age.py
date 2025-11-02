import sys
import os
import json
from datetime import datetime, date
from PyQt6 import QtCore, QtWidgets, QtGui

# ---------- Configuration ----------
CONFIG = {
    "DOB_Age": "1994-07-12",
    "DOB_College": "2015-04-07",
    "Width": 300,
    "Height": 140,
    "StateFile": os.path.join(os.getenv("LOCALAPPDATA"), "AgeWidget", "state.json"),
    "UpdateHour": 0
}

# Ensure state folder exists
state_dir = os.path.dirname(CONFIG["StateFile"])
os.makedirs(state_dir, exist_ok=True)

# Load/save state
def load_state():
    if os.path.exists(CONFIG["StateFile"]):
        try:
            with open(CONFIG["StateFile"], "r") as f:
                return json.load(f)
        except:
            return {"lastDate": ""}
    return {"lastDate": ""}

def save_state(state):
    with open(CONFIG["StateFile"], "w") as f:
        json.dump(state, f)

state = load_state()

# Calculate age
def get_age_parts(from_date: date, to_date: date):
    if to_date < from_date:
        return (0,0,0)
    years = to_date.year - from_date.year
    anniversary = from_date.replace(year=from_date.year + years)
    if anniversary > to_date:
        years -= 1
        anniversary = from_date.replace(year=from_date.year + years)
    months = 0
    while True:
        try:
            new_month = (anniversary.month + months + 1 - 1) % 12 + 1
            new_year = anniversary.year + (anniversary.month + months + 1 - 1)//12
            new_date = anniversary.replace(year=new_year, month=new_month)
            if new_date <= to_date:
                months += 1
            else:
                break
        except:
            break
    month_start = anniversary.replace(month=(anniversary.month + months - 1) % 12 + 1)
    days = (to_date - month_start).days
    return years, months, days

# ---------- PyQt Widget ----------
class AgeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Age Widget")
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(CONFIG["Width"], CONFIG["Height"])

        # Main layout
        self.card = QtWidgets.QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        self.card.setGeometry(0, 0, CONFIG["Width"], CONFIG["Height"])

        layout = QtWidgets.QVBoxLayout(self.card)
        layout.setContentsMargins(12,12,12,12)

        self.title_label = QtWidgets.QLabel("Age Widget")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: black;")
        layout.addWidget(self.title_label)

        self.age_label = QtWidgets.QLabel("Calculating...")
        self.age_label.setStyleSheet("font-size: 18px; font-weight: semi-bold; color: black;")
        layout.addWidget(self.age_label)

        self.college_label = QtWidgets.QLabel("")
        self.college_label.setStyleSheet("font-size: 11px; color: black;")
        layout.addWidget(self.college_label)

        # Button layout
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        self.close_btn = QtWidgets.QPushButton("✕ Close")
        self.close_btn.setFixedSize(70,24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid gray;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffdddd;
            }
        """)
        self.close_btn.clicked.connect(self.close_widget)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        # System tray
        self.tray_icon = QtWidgets.QSystemTrayIcon(
			self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)
		)
        self.tray_icon.setToolTip("Age Widget")
        tray_menu = QtWidgets.QMenu()
        open_action = tray_menu.addAction("Open Widget")
        open_action.triggered.connect(self.show_widget)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close_widget)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Timer to update daily
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.ensure_daily_update)
        self.timer.start(30 * 1000)  # check every 30 sec

        # Initial update
        self.update_widget()

    def update_widget(self):
        now = date.today()
        dob = datetime.strptime(CONFIG["DOB_Age"], "%Y-%m-%d").date()
        ag_years, ag_months, ag_days = get_age_parts(dob, now)
        self.age_label.setText(f"{ag_years} years  {ag_months} months  {ag_days} days")

        dob2 = datetime.strptime(CONFIG["DOB_College"], "%Y-%m-%d").date()
        col_years, col_months, col_days = get_age_parts(dob2, now)
        self.college_label.setText(f"College: {col_years} years {col_months} months {col_days} days")

        self.title_label.setText(f"Age · Updated: {now.isoformat()}")
        state["lastDate"] = now.isoformat()
        save_state(state)

    def ensure_daily_update(self):
        today = date.today().isoformat()
        if state.get("lastDate") != today:
            self.update_widget()

    def close_widget(self):
        self.tray_icon.hide()
        QtWidgets.QApplication.quit()

    def show_widget(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = AgeWidget()

    # Position at top-right
    screen = app.primaryScreen().availableGeometry()
    widget.move(screen.width() - CONFIG["Width"] - 24, 24)

    widget.show()
    sys.exit(app.exec())
