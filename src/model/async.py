import multiprocessing
import sys
import traceback
from enum import Enum
from multiprocessing import Process, Queue, Value

from PyQt5.QtCore import QObject, pyqtSignal, QThread

from model import errors


class SignalType(Enum):
    PROGRESS = 2,
    COMPLETED = 3,
    CANCELLED = 4,
    ERRORED = 5,


"""
An object that the child process uses to send information to the PyQT thread
"""


class ProcessSignals():
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


"""
An object that the PyQT thread uses to receive data from the child process
"""


class AsyncPyQTSignals(QObject):
    started = pyqtSignal()
    progress = pyqtSignal(object)
    completed = pyqtSignal(object)
    cancelled = pyqtSignal()
    errored = pyqtSignal(object)


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
        self.pyqtSignals.started.emit()

        p = Process(target=wrappedJobFn, args=(self.jobFn, self.processSignals, *self.args))
        p.start()
        while self.running:
            self._processOutput(self.processSignals.queue.get())

    #
    # def runJob(self, *args):
    #     try:
    #         self.jobFn(self.processSignals, *args)
    #     except Exception as e:
    #         traceback.print_exc()
    #         self.processSignals.errored(e)

    def _processOutput(self, output):
        if output[0] is SignalType.PROGRESS:
            self.pyqtSignals.progress.emit(output[1:])
            return

        if output[0] is SignalType.COMPLETED:
            self.pyqtSignals.completed.emit(output[1:])
            self.running = False
            return

        if output[0] is SignalType.CANCELLED:
            self.pyqtSignals.cancelled.emit()
            self.running = False
            return

        if output[0] is SignalType.ERRORED:
            self.pyqtSignals.errored.emit(output[1:])
            self.running = False
            return

    def halt(self):
        self.processSignals.setHalt()


class UFloatAsyncTask(QThread):

    def __init__(self, signals, inputs):
        super().__init__()

        n = multiprocessing.cpu_count()
        fragments = self._split(inputs, n)

        def _processUFloatsFn(processSignals, id, inputs):
            outputs = []
            for i, input in enumerate(inputs):
                if processSignals.halt():
                    return
                processSignals.progress(i / len(inputs))
                value = errors.ufloat(*input)
                outputs.append(value)
            processSignals.completed(id, outputs)

        outputsCount = 0

        def progress():
            nonlocal outputsCount
            outputsCount += 1
            signals.progress.emit(outputsCount / len(inputs))

        threadCount = 0
        outputs = [[] for _ in fragments]

        def completed(output):
            nonlocal threadCount, outputs
            threadID, threadOutput = output
            threadCount += 1
            outputs[id] = threadOutput
            if threadCount == n:
                signals.completed.emit(outputs)

        internalSignals = AsyncPyQTSignals()
        internalSignals.progress.connect(progress)
        internalSignals.completed.connect(completed)

        signals.started.emit()
        self.tasks = []
        for i in range(n):
            task = AsyncTask(internalSignals, _processUFloatsFn, i, fragments[i])
            task.start()
            self.tasks.append(task)

    def halt(self):
        for task in self.tasks:
            task.halt()

    def _split(self, a, n):
        k, m = divmod(len(a), n)
        return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
