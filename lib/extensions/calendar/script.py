try: from PySide.QtGui import QCursor
except: from PyQt4.QtGui import QCursor
common.calendar = QCalendarWidget(None)
common.calendar.setWindowFlags(Qt.Popup)
common.calendar.move(QCursor.pos().x(), QCursor.pos().y())
common.calendar.show()
