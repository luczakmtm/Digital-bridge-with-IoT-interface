import numpy
numpy.set_printoptions(threshold=20000)

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx import TaskHandle, int32
from ctypes import byref
import time

class MultiChannelAnalogInput():
    """Class to create a multi-channel analog input
    
    Usage: AI = MultiChannelInput(physicalChannels, sampleRate=1000, numberOfSamples=1000, limit=None, reset=False)
        physicalChannels: a string or a list of strings
    optional parameter: sampleRate: number
                        numberOfSamples: number
                        limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        readSingleChannel(channel) - return array of ridden values from channel,
            channel: string - channel to bo read e.g "Dev1/ai0"
        readTwoChannels(channels) - return tuple with two arrays of ridden values from channels,,
            channels: string - channels to bo read e.g "Dev1/ai0:1"
    """

    def __init__(self, physicalChannels, sampleRate=1000, numberOfSamples=1000, limit=None, reset=False):
        self.sampleRate = sampleRate
        self.numberOfSamples = numberOfSamples
        self.timeout = 10.0

        if type(physicalChannels) == type(""):
            self.physicalChannels = [physicalChannels]
        else:
            self.physicalChannels  =physicalChannels
        self.numberOfChannel = physicalChannels.__len__()
        if limit is None:
            self.limit = dict([(name, (-10.0,10.0)) for name in self.physicalChannels])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in self.physicalChannels])
        else:
            self.limit = dict([(name, limit[i]) for  i,name in enumerate(self.physicalChannels)])           
        if reset:
            DAQmxResetDevice(physicalChannels[0].split('/')[0] )
        self.configure()

    def configure(self):
        taskHandles = dict([(name,TaskHandle(0)) for name in self.physicalChannels])
        for name in self.physicalChannels:
            DAQmxCreateTask("",byref(taskHandles[name]))
            DAQmxCreateAIVoltageChan(taskHandles[name],name,"",DAQmx_Val_RSE,
                                     self.limit[name][0],self.limit[name][1],
                                     DAQmx_Val_Volts,None)
            DAQmxCfgSampClkTiming(taskHandles[name],"",self.sampleRate,DAQmx_Val_Rising,DAQmx_Val_ContSamps,self.numberOfSamples)
        self.taskHandles = taskHandles

    def readSingleChannel(self,name = None):
        if name is None:
            name = self.physicalChannels[0]
        taskHandle = self.taskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((self.numberOfSamples,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,self.numberOfSamples,self.timeout,DAQmx_Val_GroupByChannel,data,(self.numberOfSamples),byref(read),None)
        DAQmxStopTask(taskHandle)
        return data

    def readTwoChannels(self,name = None):
        if name is None:
            name = self.physicalChannels[0]
        taskHandle = self.taskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((2*self.numberOfSamples,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,self.numberOfSamples,self.timeout,DAQmx_Val_GroupByChannel,data,(2*self.numberOfSamples),byref(read),None)
        DAQmxStopTask(taskHandle)
        return data[0:self.numberOfSamples-1], data[self.numberOfSamples:]


if __name__ == '__main__':
    f = open('result', 'w')
    multipleAI = MultiChannelAnalogInput(["Dev1/ai0:1", "Dev1/ai2"], sampleRate=5000, numberOfSamples=5000)
    a = time.time()
    for x in range(5):
        # średni czas odczytu 1.3s dla NI USB-6009 na maszynie wirtualnej, 1.02s dla symulowanej NI PCIe-6351 na fizycznym komputerze 
        result = multipleAI.readTwoChannels() # 6.5s / 5 = 1.3s 
        # result = multipleAI.readSingleChannel("Dev1/ai2") # 6.5s / 5 = 1.3s
    readTime = time.time() - a
    f.write(str(result))
    f.close()
    print (readTime)
