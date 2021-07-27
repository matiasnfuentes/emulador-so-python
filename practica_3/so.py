#!/usr/bin/env python

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


## emulates the  Interruptions Handlers
class AbstractInterruptionHandler:
    def __init__(self, kernel):
        self._kernel = kernel

    @property
    def kernel(self):
        return self._kernel

    def execute(self, irq):
        log.logger.error("-- EXECUTE MUST BE OVERRIDEN in class {classname}".format(classname=self.__class__.__name__))

    def runProgramIfPosible(self, pcb):
        if self.kernel.pcbTable.runningPcb:

            pcb.state = ProcessState.READY
            self.kernel.readyQ.append(pcb)
        else:
            pcb.state = ProcessState.RUNNING
            self.kernel.pcbTable.runningPcb = pcb
            self.kernel.dispatcher.load(pcb)

    def tryToRunReadyQ(self):
        if self.kernel.readyQ:
            readyPCB = self.kernel.readyQ.pop(0)
            readyPCB.state = ProcessState.RUNNING
            self.kernel.pcbTable.runningPcb = readyPCB
            self.kernel.dispatcher.load(readyPCB)


class NewInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        currentProgram = irq.parameters
        pid = self.kernel.pcbTable.getNewPID()
        baseDir = self.kernel.loader.loadPage(currentProgram)
        newPcb = Pcb(pid, baseDir, currentProgram)
        log.logger.info("\n Executing program: {name}".format(name=newPcb.path))
        log.logger.info(HARDWARE)
        self.kernel.pcbTable.add(newPcb)
        self.runProgramIfPosible(newPcb)


class KillInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        log.logger.info(" Program Finished ")
        pcb = self.kernel.pcbTable.runningPcb
        pcb.state = ProcessState.TERMINATED
        self.kernel.dispatcher.save(pcb)
        self.kernel.pcbTable.runningPcb = None
        self.tryToRunReadyQ()


class IoInInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        runningProcess = self.kernel.pcbTable.runningPcb
        self.kernel.dispatcher.save(runningProcess)
        self.kernel.pcbTable.runningPcb = None
        operation = irq.parameters
        runningProcess.state = ProcessState.WAITING
        self.kernel.ioDeviceController.runOperation(runningProcess, operation)
        log.logger.info(self.kernel.ioDeviceController)
        self.tryToRunReadyQ()


class IoOutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.ioDeviceController.getFinishedPCB()
        self.runProgramIfPosible(pcb)
        log.logger.info(self.kernel.ioDeviceController)


class Loader:

    def __init__(self):
        self._currentPosition = 0

    def loadProgram(self, program):
        progSize = len(program.instructions)
        baseDir = self._currentPosition
        for index in range(0, progSize):
            inst = program.instructions[index]
            HARDWARE.memory.write(self._currentPosition, inst)
            self._currentPosition += 1
        return baseDir


class Dispatcher:

    def load(self, pcb):
        log.logger.info("Dispatcher Load: {pcb}".format(pcb=pcb))
        HARDWARE.cpu.pc = pcb.pc
        HARDWARE.mmu.baseDir = pcb.baseDir

    def save(self, pcb):
        log.logger.info("Dispatcher Save: {pcb}".format(pcb=pcb))
        pcb.pc = HARDWARE.cpu.pc
        HARDWARE.cpu.pc = -1


# emulates the core of an Operative System
class Kernel:

    def __init__(self):
        ## setup interruption handlers
        self._newHandler = NewInterruptionHandler(self)
        HARDWARE.interruptVector.register(NEW_INTERRUPTION_TYPE, self._newHandler)
        killHandler = KillInterruptionHandler(self)
        HARDWARE.interruptVector.register(KILL_INTERRUPTION_TYPE, killHandler)

        ioInHandler = IoInInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_IN_INTERRUPTION_TYPE, ioInHandler)

        ioOutHandler = IoOutInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_OUT_INTERRUPTION_TYPE, ioOutHandler)

        ## controls the Hardware's I/O Device
        self._ioDeviceController = IoDeviceController(HARDWARE.ioDevice)

        ## setup loader
        self._loader = Loader()

        ## setup dispatcher
        self._dispatcher = Dispatcher()

        ## setup PCB Table
        self._pcbTable = PcbTable()

        ## Inizializate ReadyQ
        self._readyQ = []

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
    def readyQ(self):
        return self._readyQ

    ## emulates a "system call" for programs execution
    def run(self, program):
        irq = IRQ(NEW_INTERRUPTION_TYPE, program)
        self._newHandler.execute(irq)

    def __repr__(self):
        return "Kernel "
