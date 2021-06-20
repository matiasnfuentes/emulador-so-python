from enum import Enum

class ProcessState(Enum):
    NEW = 1
    READY = 2
    RUNNING = 3
    WAITING = 4
    TERMINATED = 5

class Pcb():

    def __init__(self, pid, baseDir, program, priority):
        self.__pid = pid
        self.__baseDir = baseDir
        self.__pc = 0
        self.__state = ProcessState.NEW
        self.__path = program.name
        self.__priority = priority

    @property
    def pid(self):
        return self.__pid

    @property
    def baseDir(self):
        return self.__baseDir

    @property
    def pc(self):
        return self.__pc

    @pc.setter
    def pc(self, value):
        self.__pc = value

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    @property
    def path(self):
        return self.__path

    @property
    def priority(self):
        return self.__priority

    def __repr__(self):
        return "PCB(pid={pid}, state={state}, pc={pc}, path={path})"\
         .format(pid=self.__pid, state=self.__state, pc=self.__pc, path=self.__path)


class PcbTable():

    def __init__(self):
        self.__currentPID = None
        self.__pcbs = {}
        self.__runningPcb = None

    def getNewPID(self):
        if self.__currentPID is not None:
            self.__currentPID+=1
        else:
            self.__currentPID = 0
        return self.__currentPID

    def get(self, pid):
        del self.__pcbs[pid]

    def add(self, pcb):
        self.__pcbs[pcb.pid] = pcb

    def remove(self, pid):
        del self.__pcbs[pid]

    @property
    def runningPcb(self):
        return self.__runningPcb

    @runningPcb.setter
    def runningPcb(self, value):
        self.__runningPcb = value

    def getPcbs(self):
        return self.__pcbs.values()

    def pcbCount(self):
        return len(self.__pcbs)


