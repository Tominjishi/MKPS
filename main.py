import os
import sys
from data.db_init import init_db
from ui.main_window import MainWindow
# qt
from PySide6.QtWidgets import QApplication
from PySide6.QtSql import QSqlDatabase, QSqlQuery

# Create .db file if it doesn't exist
if not os.path.exists('data/data.db'):
    init_db()
    print('Database created')

app = QApplication(sys.argv)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName('data/data.db')
db.open()
QSqlQuery(db).exec("PRAGMA foreign_keys = ON")

window = MainWindow(app)
window.show()

sys.exit(app.exec())