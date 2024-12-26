import os
from data.db_init import initDB

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtSql import QSqlDatabase
from ui.main_window import MainWindow

# Create .db file if doesn't exist
if not os.path.exists('data/data.db'):
    initDB()
    print('Database created')

app = QApplication(sys.argv)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName('data/data.db')

window = MainWindow(app)
window.show()

sys.exit(app.exec())