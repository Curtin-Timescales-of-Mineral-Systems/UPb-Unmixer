import traceback
from enum import Enum
from multiprocessing import Process, Queue, Value

from PyQt5.QtCore import pyqtSignal, QThread


class SignalType(Enum):
    PROGRESS = 2,
    COMPLETED = 3,
    CANCELLED = 4,
    ERRORED = 5,


class ProcessSignals:
    """
    An object that the child process uses to send information to the PyQT thread
    """

    def __init__(self):
        self.queue = Queue()
        self._halt = Value('i', 0)

    def progress(self, *args):
        self.queue.put((SignalType.PROGRESS, *args))

    def completed(self, *args):
        self.queue.put((SignalType.COMPLETED, *args))

    def cancelled(self, *args):
        self.queue.put((SignalType.CANCELLED, *args))

    def errored(self, *args):
        self.queue.put((SignalType.ERRORED, *args))

    def halt(self):
        return self._halt.value == 1

    def setHalt(self):
        self._halt.value = 1


# Can't be part of AsyncTask as this function must be picklable under windows:
# (see https://docs.python.org/2/library/multiprocessing.html#windows)
def wrappedJobFn(jobFn, processSignals, *args):
    try:
        jobFn(processSignals, *args)
    except Exception as e:
        traceback.print_exc()
        processSignals.errored(e)


class AsyncTask(QThread):
    """
    Runs a job in a separate process and forwards messages from the job to the
    main thread through a pyqtSignal.
    """
    msg_from_job = pyqtSignal(object)
    running = True

    def __init__(self, pyqtSignals, jobFn, *args):
        super().__init__()
        self.jobFn = jobFn
        self.args = args
        self.pyqtSignals = pyqtSignals
        self.processSignals = ProcessSignals()

    def run(self):
        self.running = True

        p = Process(target=wrappedJobFn, args=(self.jobFn, self.processSignals, *self.args))
        p.start()
        while self.running:
            self._processOutput(self.processSignals.queue.get())

    def _processOutput(self, output):
        if output[0] is SignalType.PROGRESS:
            self.pyqtSignals.processing_progress.emit(output[1:])
            return

        if output[0] is SignalType.COMPLETED:
            self.pyqtSignals.processing_completed.emit()
            self.running = False
            return

        if output[0] is SignalType.CANCELLED:
            self.pyqtSignals.processing_cancelled.emit()
            self.running = False
            return

        if output[0] is SignalType.ERRORED:
            self.pyqtSignals.processing_errored.emit(output[1:])
            self.running = False
            return

    def halt(self):
        self.processSignals.setHalt()
