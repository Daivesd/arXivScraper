import sys
import os
import sqlite3
import pandas as pd
from PySide6 import QtWidgets, QtGui, QtCore

class DatabaseViewer(QtWidgets.QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Database Viewer")
        self.resize(1000, 800)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.filter_data)
        layout.addWidget(self.search_edit)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        self.export_button = QtWidgets.QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_button)
        
        self.setLayout(layout)

    def load_data(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT date, authors, title, url, keyword FROM papers")
        data = cursor.fetchall()
        connection.close()

        self.table.setRowCount(len(data))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Authors", "Title", "URL", "Keyword"])

        self.table.setColumnWidth(0, 100)  # Date
        self.table.setColumnWidth(1, 250)  # Authors
        self.table.setColumnWidth(2, 400)  # Title
        self.table.setColumnWidth(3, 300)  # URL
        self.table.setColumnWidth(4, 150)  # Keyword


        self.table.setWordWrap(True) 
        self.table.resizeRowsToContents() 

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                
                if col_idx == 3:  # URL column
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#00BFFF")))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  
                    item.setData(QtCore.Qt.UserRole, col_data)  
                    
                self.table.setItem(row_idx, col_idx, item)

        self.table.cellClicked.connect(self.open_url)  
        self.original_data = data  
    
    def filter_data(self):
        filter_text = self.search_edit.text().lower()
        for row in range(self.table.rowCount()):
            row_visible = any(filter_text in self.table.item(row, col).text().lower() for col in range(self.table.columnCount()))
            self.table.setRowHidden(row, not row_visible)
    
    def export_to_csv(self):
        df = pd.DataFrame(self.original_data, columns=["Date", "Authors", "Title", "URL", "Keyword"])
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if save_path:
            df.to_csv(save_path, index=False)
            QtWidgets.QMessageBox.information(self, "Export Successful", "Database exported to CSV successfully!")
    
    def open_url(self, row, column):
        if column == 3:  # URL column
            url = self.table.item(row, column).data(QtCore.Qt.UserRole)  # Retrieve stored URL
            if url:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    db_path = "Papers.db" 
    viewer = DatabaseViewer(db_path)
    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())