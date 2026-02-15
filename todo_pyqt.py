import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QMessageBox,
    QLabel, QComboBox, QDateEdit, QStackedWidget
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont

conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    priority TEXT,
    due_date TEXT,
    status TEXT
)
""")

conn.commit()


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart To-Do App")
        self.setGeometry(300, 100, 600, 720)

        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.login_page = self.create_login_page()
        self.todo_page = self.create_todo_page()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.todo_page)

        self.current_user_id = None

        # Default Theme
        self.set_pink_theme()


    def set_pink_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #FCE4EC; color: #880E4F; }
            QPushButton {
                background-color: #F8BBD0;
                padding: 12px;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F48FB1; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #FADADD;
                padding: 10px;
                border-radius: 12px;
                font-size: 16px;
            }
            QListWidget {
                background-color: #FFF0F5;
                border-radius: 20px;
                font-size: 16px;
                padding: 12px;
            }
        """)

    def set_green_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #E8F5E9; color: #1B5E20; }
            QPushButton {
                background-color: #A5D6A7;
                padding: 12px;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #81C784; }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #C8E6C9;
                padding: 10px;
                border-radius: 12px;
                font-size: 16px;
            }
            QListWidget {
                background-color: #F1F8E9;
                border-radius: 20px;
                font-size: 16px;
                padding: 12px;
            }
        """)


    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("💖 Smart Login")
        title.setFont(QFont("Arial", 26))
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("🔐 Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("📝 Register")
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        page.setLayout(layout)
        return page


    def create_todo_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("🌿 My Tasks")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter your task...")
        layout.addWidget(self.task_input)

        self.priority_box = QComboBox()
        self.priority_box.addItems(["High 🔴", "Medium 🟡", "Low 🟢"])
        layout.addWidget(self.priority_box)

        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        layout.addWidget(self.date_picker)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add")
        add_btn.clicked.connect(self.add_task)
        btn_layout.addWidget(add_btn)

        complete_btn = QPushButton("✔ Complete")
        complete_btn.clicked.connect(self.mark_completed)
        btn_layout.addWidget(complete_btn)

        layout.addLayout(btn_layout)

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_task)
        layout.addWidget(delete_btn)

        theme_btn = QPushButton("🎨 Switch Theme")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)

        logout_btn = QPushButton("🚪 Logout")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        page.setLayout(layout)
        return page


    def toggle_theme(self):
        if "#FCE4EC" in self.styleSheet():
            self.set_green_theme()
        else:
            self.set_pink_theme()


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        cursor.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            self.current_user_id = user[0]
            self.load_tasks()
            self.stack.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "User Registered!")
        except:
            QMessageBox.warning(self, "Error", "Username already exists!")

    def logout(self):
        self.username_input.clear()
        self.password_input.clear()
        self.task_list.clear()
        self.stack.setCurrentIndex(0)

    def add_task(self):
        task = self.task_input.text()
        priority = self.priority_box.currentText()
        due_date = self.date_picker.date().toString("yyyy-MM-dd")

        if task:
            cursor.execute("""
                INSERT INTO tasks (user_id, task, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_user_id, task, priority, due_date, "Pending"))
            conn.commit()
            self.task_input.clear()
            self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        cursor.execute("""
            SELECT task, priority, due_date, status
            FROM tasks WHERE user_id=?
        """, (self.current_user_id,))
        rows = cursor.fetchall()

        for row in rows:
            text = f"{row[0]} | {row[1]} | 📅 {row[2]} | {row[3]}"
            self.task_list.addItem(text)

    def delete_task(self):
        selected = self.task_list.currentItem()
        if selected:
            task_name = selected.text().split(" | ")[0]
            cursor.execute("""
                DELETE FROM tasks
                WHERE task=? AND user_id=?
            """, (task_name, self.current_user_id))
            conn.commit()
            self.load_tasks()

    def mark_completed(self):
        selected = self.task_list.currentItem()
        if selected:
            task_name = selected.text().split(" | ")[0]
            cursor.execute("""
                UPDATE tasks
                SET status='Completed ✔'
                WHERE task=? AND user_id=?
            """, (task_name, self.current_user_id))
            conn.commit()
            self.load_tasks()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
