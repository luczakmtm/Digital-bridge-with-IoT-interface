import numpy
numpy.set_printoptions(threshold=10000)

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx import TaskHandle, int32
from ctypes import byref
import time

class MultiChannelAnalogInput():
    """Class to create a multi-channel analog input
    
    Usage: AI = MultiChannelInput(physicalChannel)
        physicalChannel: a string or a list of strings
    optional parameter: limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        read(name) - return the value of the input name,
            name: string - port to bo read e.g "Dev1/ai0"
        readAll() - return a dictionary name:value
    """

    def __init__(self, physicalChannel, sampleRate=1000, numberOfSamples=1000, limit=None, reset=False):
        self.sampleRate = sampleRate
        self.numberOfSamples = numberOfSamples

        if type(physicalChannel) == type(""):
            self.physicalChannel = [physicalChannel]
        else:
            self.physicalChannel  =physicalChannel
        self.numberOfChannel = physicalChannel.__len__()
        if limit is None:
            self.limit = dict([(name, (-10.0,10.0)) for name in self.physicalChannel])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in self.physicalChannel])
        else:
            self.limit = dict([(name, limit[i]) for  i,name in enumerate(self.physicalChannel)])           
        if reset:
            DAQmxResetDevice(physicalChannel[0].split('/')[0] )
        self.configure()

    def configure(self):
        taskHandles = dict([(name,TaskHandle(0)) for name in self.physicalChannel])
        for name in self.physicalChannel:
            DAQmxCreateTask("",byref(taskHandles[name]))
            DAQmxCreateAIVoltageChan(taskHandles[name],name,"",DAQmx_Val_RSE,
                                     self.limit[name][0],self.limit[name][1],
                                     DAQmx_Val_Volts,None)
            DAQmxCfgSampClkTiming(taskHandles[name],"",self.sampleRate,DAQmx_Val_Rising,DAQmx_Val_ContSamps,self.numberOfSamples)
        self.taskHandles = taskHandles

    def readAll(self):
        return dict([(name,self.read(name)) for name in self.physicalChannel])

    def read(self,name = None):
        if name is None:
            name = self.physicalChannel[0]
        taskHandle = self.taskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((self.numberOfSamples,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,self.numberOfSamples,10.0,DAQmx_Val_GroupByChannel,data,self.numberOfSamples,byref(read),None)
        DAQmxStopTask(taskHandle)
        return data


if __name__ == '__main__':
    f = open('result', 'w')
    multipleAI = MultiChannelAnalogInput(["Dev1/ai0", "Dev1/ai1"], sampleRate=5000, numberOfSamples=5000)
    a = time.time()
    for x in range(5):
        result = multipleAI.read() # 6.5s / 5 = 1.3s
        # result = multipleAI.readAll() # 13s = 2 inputs x 5 read x 1.3s
    readTime = time.time() - a
    f.write(str(result))
    f.close()
    print (readTime)
