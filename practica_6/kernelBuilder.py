from so import *

class SchedulerType(Enum):
    FirstComeFirstServed = 1
    Priority = 2
    PriorityPreentive = 3
    RoundRobin = 4


class KernelBuilder():

    def buildKernel(self, schedulerType, frameSize, algorithmType):
        SCHEDULER = {
            SchedulerType.FirstComeFirstServed: SchedulerFCFS(),
            SchedulerType.Priority: SchedulerPriority(),
            SchedulerType.PriorityPreentive: SchedulerPriorityPRENTIVE(),
            SchedulerType.RoundRobin: SchedulerRoundRobin()
        }
        return Kernel(SCHEDULER.get(schedulerType), frameSize, algorithmType)

KERNEL_BUILDER = KernelBuilder()