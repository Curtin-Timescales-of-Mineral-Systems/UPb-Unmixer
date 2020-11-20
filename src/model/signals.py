from PyQt5.QtCore import pyqtSignal, QObject

from model.spot import Spot


class Signals(QObject):
    # Arguments: [success:bool, file:str]
    csv_imported = pyqtSignal([bool, str])

    # Arguments: [index:int, row:Row, allRows:list[Row]]
    row_updated = pyqtSignal(int)
    all_rows_updated = pyqtSignal()
    headers_updated = pyqtSignal()

    # Arguments: [task_description:str]
    task_started = pyqtSignal(str)
    # Arguments: [progress:float]
    task_progress = pyqtSignal(float)
    # Arguments: [success:bool, description:str]
    task_complete = pyqtSignal([bool, str])

    processing_started = pyqtSignal()
    processing_progress = pyqtSignal(object)
    processing_completed = pyqtSignal()
    processing_cancelled = pyqtSignal()
    processing_errored = pyqtSignal(object)