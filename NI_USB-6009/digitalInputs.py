import numpy

import PyDAQmx
from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx import TaskHandle, int32, Task
from ctypes import byref

class DigitalInputs():
    """Class to create a digital inputs
    
    Usage: digitalInputs = DigitalInputs(lines)
        lines: list of strings e.g ["Dev1/port0/line1", "Dev1/port0/line0"]

    Methods:
        read(line) - return the value of the input line,
            line: string - line to bo read e.g "Dev1/port0/line1"
        readAll() - return a dictionary line:value
    """

    def __init__(self, lines):
        if type(lines) == type(""):
            self.lines = [lines]
        else:
            self.lines  = lines
        self.task = Task()
        self._configure()
        

    def _configure(self):
        tasks = dict([(name,Task()) for name in self.lines])
        for line in self.lines:
            tasks[line].CreateDIChan(line,"", PyDAQmx.DAQmx_Val_ChanForAllLines)
        self.tasks = tasks

    def read(self, line):
        self.tasks[line].StartTask()
        data = numpy.zeros((1,), dtype=numpy.uint8)
        read = int32()
        self.tasks[line].ReadDigitalU8(1,10.0,DAQmx_Val_GroupByScanNumber,data,1,byref(read),None)
        self.tasks[line].StopTask()
        return (data[0] >> (int(line[-1]))) & 1

    def readAll(self):
        return dict([(line,self.read(line)) for line in self.lines])


if __name__ == '__main__':
    digitalInputs = DigitalInputs(["Dev1/port0/line1", "Dev1/port0/line0"])

    print (digitalInputs.readAll())
    print (digitalInputs.readAll())
    print (digitalInputs.readAll())
    print (digitalInputs.readAll())
    print (digitalInputs.read("Dev1/port0/line0"))
    print (digitalInputs.read("Dev1/port0/line1"))
