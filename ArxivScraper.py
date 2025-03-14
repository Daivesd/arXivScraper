import sys
import platform
from PySide6 import QtWidgets, QtCore, QtGui
import arxiv
from datetime import datetime, timedelta, timezone
import os
import sqlite3
import subprocess
import pandas as pd

class FinderWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("arXiv Barrel Scraper")
        self.refresh_interval = 60 * 60
        self.time_remaining = self.refresh_interval
        self.last_fetched_papers = set()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.tray_icon = None
        self.setup_ui()
        self.setup_tray_icon()

    def setup_database(self):
        # Might be used in the wrong place, do some debugging to check this out. 
        
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbname_edit.text())
        print(f'Debug message: trying to connect at DB at {db_path}')
        self.db_conn = sqlite3.connect(db_path)
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            authors TEXT,
            title TEXT,
            url TEXT UNIQUE,
            keyword TEXT
        )''')
        self.db_conn.commit()

    def add_paper_to_database(self, date, authors, title, url, keyword):
        try:
            self.db_cursor.execute("INSERT INTO papers (date, authors, title, url, keyword) VALUES (?, ?, ?, ?, ?)",
                                   (date, authors, title, url, keyword))
            self.db_conn.commit()
        except sqlite3.IntegrityError:
            pass  # Paper already exists in the database

    def fetch_existing_papers(self):
        self.db_cursor.execute("SELECT url FROM papers")
        return {row[0] for row in self.db_cursor.fetchall()}

    def fetch_papers(self):
        self.setup_database()
        keywords_raw = self.keyword_edit.text().strip()
        if not keywords_raw:
            QtWidgets.QMessageBox.critical(self, "Input Error", "Please enter at least one keyword.")
            return
        
        keywords = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]
        days_back = int(self.days_back_combo.currentText())
        max_results = int(self.max_results_combo.currentText())
        
        new_papers = set()
        self.results_table.setRowCount(0)
        existing_papers = self.fetch_existing_papers()
        
        for keyword in keywords:
            try:
                papers = self.fetch_arxiv_papers(keyword, days_back, max_results)
                for paper in papers:
                    if paper.entry_id not in existing_papers:
                        self.add_paper_to_database(
                            paper.published.strftime("%Y-%m-%d"),
                            ", ".join(a.name for a in paper.authors),
                            paper.title,
                            paper.entry_id,
                            keyword
                        )
                    
                    row = self.results_table.rowCount()
                    self.results_table.insertRow(row)
                    title_item = QtWidgets.QTableWidgetItem(paper.title)
                    title_item.setData(QtCore.Qt.UserRole, paper.entry_id)
                    title_item.setForeground(QtGui.QBrush(QtGui.QColor("#00BFFF")))
                    title_item.setFont(QtGui.QFont("Arial", weight=QtGui.QFont.Bold))
                    title_item.setFlags(QtCore.Qt.ItemIsEnabled)
                    authors_item = QtWidgets.QTableWidgetItem(", ".join(a.name for a in paper.authors))
                    date_str = paper.published.strftime("%Y-%m-%d")
                    date_item = QtWidgets.QTableWidgetItem(date_str)
                    date_item.setData(QtCore.Qt.UserRole, QtCore.QDate.fromString(date_str, "yyyy-MM-dd"))
                    keyword_item = QtWidgets.QTableWidgetItem(keyword)
                    self.results_table.setItem(row, 0, date_item)
                    self.results_table.setItem(row, 1, authors_item)
                    self.results_table.setItem(row, 2, title_item)
                    self.results_table.setItem(row, 3, keyword_item)
                    new_papers.add(paper.entry_id)
                self.results_table.setSortingEnabled(True) 
            except Exception as e:
                print(f"Error fetching papers for {keyword}: {e}")
        
        new_paper_ids = new_papers - self.last_fetched_papers
        if new_paper_ids:
            self.show_notification(len(new_paper_ids))
        self.last_fetched_papers = new_papers

    def closeEvent(self, event):
        self.db_conn.close()
        event.accept()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QHBoxLayout()
        self.keyword_label = QtWidgets.QLabel("Enter Keywords (comma-separated):")
        self.keyword_edit = QtWidgets.QLineEdit("racetrack, josephson, cryogenic memory, single flux quantum")
        form_layout.addWidget(self.keyword_label)
        form_layout.addWidget(self.keyword_edit)
        layout.addLayout(form_layout)

        dbname_form_layout = QtWidgets.QHBoxLayout()
        self.dbname_label = QtWidgets.QLabel("Enter Database name (cant be bothered with checking extensions, make sure you add the .db please):")
        self.dbname_edit = QtWidgets.QLineEdit("Papers.db")
        dbname_form_layout.addWidget(self.dbname_label)
        dbname_form_layout.addWidget(self.dbname_edit)
        layout.addLayout(dbname_form_layout)

        dropdown_layout = QtWidgets.QHBoxLayout()
        self.days_back_label = QtWidgets.QLabel("Days Back:")
        self.days_back_combo = QtWidgets.QComboBox()
        self.days_back_combo.setEditable(True)
        self.days_back_combo.addItem("7")
        self.days_back_combo.addItems(["1", "3", "14"])
        dropdown_layout.addWidget(self.days_back_label)
        dropdown_layout.addWidget(self.days_back_combo)

        self.max_results_label = QtWidgets.QLabel("Max Results per Keyword:")
        self.max_results_combo = QtWidgets.QComboBox()
        self.max_results_combo.setEditable(True)
        self.max_results_combo.addItem("10")
        self.max_results_combo.addItems(["5", "20", "50"])
        dropdown_layout.addWidget(self.max_results_label)
        dropdown_layout.addWidget(self.max_results_combo)
        layout.addLayout(dropdown_layout)

        self.fetch_button = QtWidgets.QPushButton("Fetch Papers")
        self.fetch_button.clicked.connect(self.start_fetching)
        layout.addWidget(self.fetch_button)

        self.interrupt_button = QtWidgets.QPushButton("Interrupt")
        self.interrupt_button.setEnabled(False)
        self.interrupt_button.clicked.connect(self.stop_fetching)
        layout.addWidget(self.interrupt_button)

        self.view_db_button = QtWidgets.QPushButton("View Database")
        self.view_db_button.clicked.connect(self.open_database_viewer)
        layout.addWidget(self.view_db_button)

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setSortingEnabled(True)
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Date", "Authors", "Title", "Keyword"])
        self.results_table.setColumnWidth(0, 100)
        self.results_table.setColumnWidth(1, 625)
        self.results_table.setColumnWidth(2, 625)
        self.results_table.setColumnWidth(3, 100)
        self.results_table.cellClicked.connect(self.open_paper_link)
        layout.addWidget(self.results_table)

        self.timer_label = QtWidgets.QLabel("Next refresh in: 60:00")
        self.timer_label.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(self.timer_label)

        self.setLayout(layout)
    
    def open_paper_link(self, row, column):
        if column == 2:  # Only process clicks on the "Title" column
            url = self.results_table.item(row, column).data(QtCore.Qt.UserRole)
            if url:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def setup_tray_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_icon.png")
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(icon_path), self)
        menu = QtWidgets.QMenu()
        restore_action = menu.addAction("Restore")
        restore_action.triggered.connect(self.showNormal)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.QApplication.quit)
        nothing_action = menu.addAction("This button does nothing :)")
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()
        self.tray_icon.setVisible(True)

    def tray_icon_clicked(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        #self.tray_icon.showMessage("FML", QtWidgets.QSystemTrayIcon.Information)

    def start_fetching(self):
        self.fetch_button.setEnabled(False)
        self.interrupt_button.setEnabled(True)
        self.fetch_papers()
        print(f'Debug message: database name is {self.dbname_edit.text().strip()}')
        self.timer.start(1000)

    def stop_fetching(self):
        self.timer.stop()
        self.time_remaining = self.refresh_interval
        self.timer_label.setText("Next refresh in: 60:00")
        self.fetch_button.setEnabled(True)
        self.interrupt_button.setEnabled(False)

    def update_timer(self):
        self.time_remaining -= 1
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.setText(f"Next refresh in: {minutes:02}:{seconds:02}")
        
        if self.time_remaining <= 0:
            self.time_remaining = self.refresh_interval
            self.fetch_papers()

    def fetch_arxiv_papers(self, topic, days_back=7, max_results=6):
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days_back)
        query_str = f'all:"{topic}" AND submittedDate:[{start_date.strftime("%Y%m%d%H%M")} TO {now.strftime("%Y%m%d%H%M")}]'
        
        search = arxiv.Search(
            query=query_str,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        client = arxiv.Client()
        return list(client.results(search))

    def show_notification(self, new_paper_count):
        message = f"{new_paper_count} new paper(s) found on arXiv!"
        system = platform.system()
        
        if system == "Windows":
            from plyer import notification
            notification.notify(title="Panic Attack", message=message, timeout=5)
        elif system == "Darwin":
            os.system(f"osascript -e 'display notification \"{message}\" with title \"Panic Attack\"'")
        elif system == "Linux":
            os.system(f"notify-send \"Panic Attack\" \"{message}\"")

    def open_database_viewer(self):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbname_edit.text())
        subprocess.Popen(["python", "DatabaseViewer.py", db_path])
