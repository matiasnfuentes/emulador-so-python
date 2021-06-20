from so import *

class SchedulerType(Enum):
    FirstComeFirstServed = 1
    Priority = 2
    PriorityPreentive = 3
    RoundRobin = 4

class KernelBuilder():

    def buildKernel(self, schedulerType, frameSize):
        SWITCHER = {
            SchedulerType.FirstComeFirstServed: SchedulerFCFS(),
            SchedulerType.Priority: SchedulerPriority(),
            SchedulerType.PriorityPreentive: SchedulerPriorityPRENTIVE(),
            SchedulerType.RoundRobin: SchedulerRoundRobin()
        }
        return Kernel(SWITCHER.get(schedulerType), frameSize)

KERNEL_BUILDER = KernelBuilder()