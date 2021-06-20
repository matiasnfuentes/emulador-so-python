#!/usr/bin/env python
import math

from hardware import *
from pcb import *
import log


## emulates a compiled program
class Program:

    def __init__(self, name, instructions):
        self._name = name
        self._instructions = self.expand(instructions)

    @property
    def name(self):
        return self._name

    @property
    def instructions(self):
        return self._instructions

    def addInstr(self, instruction):
        self._instructions.append(instruction)

    def expand(self, instructions):
        expanded = []
        for i in instructions:
            if isinstance(i, list):
                ## is a list of instructions
                expanded.extend(i)
            else:
                ## a single instr (a String)
                expanded.append(i)

        ## now test if last instruction is EXIT
        ## if not... add an EXIT as final instruction
        last = expanded[-1]
        if not ASM.isEXIT(last):
            expanded.append(INSTRUCTION_EXIT)

        return expanded

    def __repr__(self):
        return "Program({name}, {instructions})".format(name=self._name, instructions=self._instructions)


class FileSystem():

    def __init__(self):
        self.__disk = {}

    def getProgram(self, path):
        return self.__disk.get(path)

    def write(self, path, program):
        self.__disk[path] = program

    def formatDisk(self):
        self.__disk.clear()


class OutOfMemory(Exception):
    pass


class MemoryManager():

    def __init__(self, frameSize):
        self._frameSize = frameSize
        numberOfFrames = int(HARDWARE.memory.size / frameSize)
        self.__freeFrames = []
        for i in range(numberOfFrames):
            self.__freeFrames.append(i)

    def getFreeFrame(self):
        try:
            if self.__freeFrames:
                return self.__freeFrames.pop(0)
            else:
                raise OutOfMemory
        except OutOfMemory:
            print("The frame count isn't enough")

    def setFreeFrame(self, frameNumber):
        self.__freeFrames.append(frameNumber)


class AbstractScheduler:

    def __init__(self):
        self.__readyQ = []

    @property
    def readyQ(self):
        return self.__readyQ

    @readyQ.setter
    def readyQ(self, value):
        self.__readyQ = value

    def add(self, pcb):
        pcb.state = ProcessState.READY
        self.readyQ.append(pcb)

    def getNext(self):
        return self.readyQ.pop(0)

    def hasNext(self):
        return len(self.readyQ) != 0

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False


class SchedulerFCFS(AbstractScheduler):
    pass


class SchedulerPriority(AbstractScheduler):
    def __init__(self):
        super().__init__()
        self.readyQ = [[], [], [], [], []]
        self.__pcbCount = 0
        HARDWARE.clock.addSubscriber(self)

    def add(self, pcb):
        pcb.state = ProcessState.READY
        self.readyQ[pcb.priority].append((pcb, HARDWARE.clock.currentTick))
        self.__pcbCount += 1

    def getNext(self):
        index = 0
        next = None
        while not self.readyQ[index] and index < 4:
            index += 1
        if self.readyQ[index]:
            next = self.readyQ[index].pop(0)[0]
            self.__pcbCount -= 1
        return next

    def hasNext(self):
        return self.__pcbCount != 0

    def tick(self, nmrTick):
        for i in range(1, 5):
            while self.readyQ[i] and nmrTick - self.readyQ[i][0][1] >= 3:
                elementToAge = self.readyQ[i].pop()
                self.readyQ[i - 1].append((elementToAge[0], nmrTick))
                log.logger.info("New priority {prio} for {pcb}".format(prio=i - 1, pcb=elementToAge[0]))


class SchedulerPriorityPRENTIVE(SchedulerPriority):

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return pcbToAdd.priority < pcbInCPU.priority


class SchedulerRoundRobin(AbstractScheduler):

    def __init__(self):
        super().__init__()
        HARDWARE.timer.quantum = 3


## emulates an Input/Output device controller (driver)
class IoDeviceController:

    def __init__(self, device):
        self._device = device
        self._waiting_queue = []
        self._currentPCB = None

    def runOperation(self, pcb, instruction):
        pair = {'pcb': pcb, 'instruction': instruction}
        # append: adds the element at the end of the queue
        self._waiting_queue.append(pair)
        # try to send the instruction to hardware's device (if is idle)
        self.__load_from_waiting_queue_if_apply()

    def getFinishedPCB(self):
        finishedPCB = self._currentPCB
        self._currentPCB = None
        self.__load_from_waiting_queue_if_apply()
        return finishedPCB

    def __load_from_waiting_queue_if_apply(self):
        if (len(self._waiting_queue) > 0) and self._device.is_idle:
            ## pop(): extracts (deletes and return) the first element in queue
            pair = self._waiting_queue.pop(0)
            # print(pair)
            pcb = pair['pcb']
            instruction = pair['instruction']
            self._currentPCB = pcb
            self._device.execute(instruction)

    def __repr__(self):
        return "IoDeviceController for {deviceID} running: {currentPCB} waiting: {waiting_queue}".format(
            deviceID=self._device.deviceId, currentPCB=self._currentPCB, waiting_queue=self._waiting_queue)


class StatTable():
    def __init__(self, kernel):
        self.__kernel = kernel
        self.__stats = []

    @property
    def stats(self):
        return self.__stats

    def addStat(self, stat):
        self.__stats.append(stat)

    def convertToWaitingTime(self, state):
        if state == '.':
            return 1
        else:
            return 0

    def convertToReturnTime(self, state):
        if state != 'T':
            return 1
        else:
            return 0

    def avgTime(self, list):
        return sum(list) / len(list)

    ## Returns a tuple with average waiting time, and
    ## the waiting time of each process
    def waitingTimes(self):
        processesNumber = self.__kernel.pcbTable.pcbCount()
        processesWaitingTime = [0] * processesNumber
        processesReturnTime = [0] * processesNumber
        for stat in self.stats:
            for index, e in enumerate(stat):
                processesWaitingTime[index] = processesWaitingTime[index] + self.convertToWaitingTime(e)
                processesReturnTime[index] = processesReturnTime[index] + self.convertToReturnTime(e)
        avgWaitingTime = self.avgTime(processesWaitingTime)
        avgReturnTime = self.avgTime(processesReturnTime)
        return dict([('processesWaitingTime', processesWaitingTime),
                     ('processesReturnTime', processesReturnTime),
                     ('avgWaitingTime', avgWaitingTime),
                     ('avgReturnTime', avgReturnTime)])

    ## Shows a complete statistics of processes execution
    def showStats(self):
        headerGantt = ["Tick"] + list(range(1, self.__kernel.pcbTable.pcbCount() + 1))
        index = list(range(1, len(self.__stats) + 1))
        log.logger.info(tabulate(self.__stats, headers=headerGantt, tablefmt='psql', showindex=index))
        times = self.waitingTimes()
        headerWaiting = ["Proceso", "Tiempo de espera"]
        log.logger.info(
            tabulate(enumerate(times['processesWaitingTime'], start=1), headers=headerWaiting, tablefmt='psql'))
        log.logger.info("Tiempo de espera promedio: {avgTime}".format(avgTime=times['avgWaitingTime']))
        headerReturn = ["Proceso", "Tiempo de retorno"]
        log.logger.info(
            tabulate(enumerate(times['processesReturnTime'], start=1), headers=headerReturn, tablefmt='psql'))
        log.logger.info("Tiempo de retorno promedio: {avgTime}".format(avgTime=times['avgReturnTime']))


## emulates the  Interruptions Handlers
class AbstractInterruptionHandler:
    def __init__(self, kernel):
        self._kernel = kernel

    @property
    def kernel(self):
        return self._kernel

    def execute(self, irq):
        log.logger.error("-- EXECUTE MUST BE OVERRIDEN in class {classname}".format(classname=self.__class__.__name__))

    def runPCB(self, pcb):
        HARDWARE.timer.reset()
        pcb.state = ProcessState.RUNNING
        self.kernel.pcbTable.runningPcb = pcb
        self.kernel.dispatcher.load(pcb)

    def runNext(self):
        pcb = self.kernel.scheduler.getNext()
        self.runPCB(pcb)

    def tryToRunReadyQ(self):
        if self.kernel.scheduler.hasNext():
            self.runNext()

    def saveProcessState(self, processState):
        process = self.kernel.pcbTable.runningPcb
        self.kernel.dispatcher.save(process)
        self.kernel.pcbTable.runningPcb = None
        process.state = processState
        return process

    def runProgramIfPosible(self, pcb):
        pcbInCPU = self.kernel.pcbTable.runningPcb
        if pcbInCPU:
            if self.kernel.scheduler.mustExpropiate(pcbInCPU, pcb):
                pcbReady = self.saveProcessState(ProcessState.READY)
                self.kernel.scheduler.add(pcbReady)
                self.runPCB(pcb)
            else:
                pcb.state = ProcessState.READY
                self.kernel.scheduler.add(pcb)
        else:
            self.runPCB(pcb)


class StatsInterruptionHandler(AbstractInterruptionHandler):

    def __init__(self, kernel):
        super().__init__(kernel)
        self.__SWITCHER = {
            ProcessState.RUNNING: 'R',
            ProcessState.WAITING: 'W',
            ProcessState.READY: '.',
            ProcessState.TERMINATED: 'T'
        }

    def getState(self, pcb):
        return self.__SWITCHER.get(pcb.state)

    def execute(self, irq):
        stat = []
        pcbs = self.kernel.pcbTable.getPcbs()
        for pcb in pcbs:
            stat.append(self.getState(pcb))
        self.kernel.statTable.addStat(stat)


class TimeoutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        if (self.kernel.scheduler.hasNext()):
            process = self.saveProcessState(ProcessState.READY)
            self.kernel.scheduler.add(process)
            self.runNext()
        else:
            HARDWARE.timer.reset()


class NewInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        path = irq.parameters[0]
        program = self.kernel.fileSystem.getProgram(path)
        priority = irq.parameters[1]
        pid = self.kernel.pcbTable.getNewPID()
        pagesCount = math.ceil(len(program) / self.kernel.frameSize)
        pageTable = []
        for i in range(pagesCount):
            frame = self.kernel.memoryManager.getFreeFrame()
            pageTable.append(frame)
        newPcb = Pcb(pid, pageTable, path, priority)
        self.kernel.loader.loadProgram(program, pageTable)
        log.logger.info("\n Executing program: {name}".format(name=newPcb.path))
        log.logger.info(HARDWARE)
        self.kernel.pcbTable.add(newPcb)
        self.runProgramIfPosible(newPcb)



class KillInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        log.logger.info(" Program Finished ")
        pageTable = self.kernel.pcbTable.runningPcb.pageTable
        for p in pageTable:
            self.kernel.memoryManager.setFreeFrame(p)
        self.saveProcessState(ProcessState.TERMINATED)
        self.tryToRunReadyQ()


class IoInInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        processToIO = self.saveProcessState(ProcessState.WAITING)
        operation = irq.parameters
        self.kernel.ioDeviceController.runOperation(processToIO, operation)
        log.logger.info(self.kernel.ioDeviceController)
        self.tryToRunReadyQ()


class IoOutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.ioDeviceController.getFinishedPCB()
        self.runProgramIfPosible(pcb)
        log.logger.info(self.kernel.ioDeviceController)


class Loader:

    def __init__(self, kernel, frameSize):
        self._currentPosition = 0
        self._kernel = kernel
        self._frameSize = frameSize

    def loadProgram(self, instructions, pageTable):
        for i, instruction in enumerate(instructions):
            frame = pageTable[math.floor(i / self._frameSize)]
            offset = i % self._frameSize
            position = (frame * self._frameSize) + offset
            HARDWARE.memory.write(position, instructions[i])

class Dispatcher:

    def load(self, pcb):
        log.logger.info("Dispatcher Load: {pcb}".format(pcb=pcb))
        HARDWARE.cpu.pc = pcb.pc
        HARDWARE.mmu.resetTLB()
        for page, frame in enumerate(pcb.pageTable):
            HARDWARE.mmu.setPageFrame(page, frame)


    def save(self, pcb):
        log.logger.info("Dispatcher Save: {pcb}".format(pcb=pcb))
        pcb.pc = HARDWARE.cpu.pc
        HARDWARE.cpu.pc = -1


# emulates the core of an Operative System
class Kernel:

    def __init__(self, scheduler, frameSize):
        ## setup interruption handlers
        self._newHandler = NewInterruptionHandler(self)
        HARDWARE.interruptVector.register(NEW_INTERRUPTION_TYPE, self._newHandler)

        killHandler = KillInterruptionHandler(self)
        HARDWARE.interruptVector.register(KILL_INTERRUPTION_TYPE, killHandler)

        ioInHandler = IoInInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_IN_INTERRUPTION_TYPE, ioInHandler)

        ioOutHandler = IoOutInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_OUT_INTERRUPTION_TYPE, ioOutHandler)

        timeOutHandler = TimeoutInterruptionHandler(self)
        HARDWARE.interruptVector.register(TIMEOUT_INTERRUPTION_TYPE, timeOutHandler)

        statsHandler = StatsInterruptionHandler(self)
        HARDWARE.interruptVector.register(STAT_INTERRUPTION_TYPE, statsHandler)

        ## controls the Hardware's I/O Device
        self._ioDeviceController = IoDeviceController(HARDWARE.ioDevice)

        ## setup loader
        self._loader = Loader(self, frameSize)

        ## setup dispatcher
        self._dispatcher = Dispatcher()

        ## setup PCB Table
        self._pcbTable = PcbTable()

        ## Inizializate Scheduler
        self._scheduler = scheduler

        ## Inizializate StatTable
        self._statTable = StatTable(self)

        ## Inizializate FileSystem
        self._fileSystem = FileSystem()

        ## Inizializate StatTable
        self._memoryManager = MemoryManager(frameSize)

        ## Inizializate FrameSize
        self._frameSize = frameSize
        HARDWARE.mmu.frameSize = frameSize


    @property
    def ioDeviceController(self):
        return self._ioDeviceController

    @property
    def loader(self):
        return self._loader

    @property
    def dispatcher(self):
        return self._dispatcher

    @property
    def pcbTable(self):
        return self._pcbTable

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def statTable(self):
        return self._statTable

    @property
    def fileSystem(self):
        return self._fileSystem

    @property
    def memoryManager(self):
        return self._memoryManager

    @property
    def frameSize(self):
        return self._frameSize

    ## emulates a "system call" for programs execution
    def run(self, program, priority):
        irq = IRQ(NEW_INTERRUPTION_TYPE, (program, priority))
        self._newHandler.execute(irq)

    def __repr__(self):
        return "Kernel "
