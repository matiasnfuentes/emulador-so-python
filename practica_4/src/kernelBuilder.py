from so import *

class SchedulerType(Enum):
    FirstComeFirstServed = 1
    Priority = 2
    PriorityPreentive = 3
    RoundRobin = 4

class KernelBuilder():

    def buildKernel(self, schedulerType):
        SWITCHER = {
            SchedulerType.FirstComeFirstServed: SchedulerFCFS(),
            SchedulerType.Priority: SchedulerPriority(),
            SchedulerType.PriorityPreentive: SchedulerPriorityPRENTIVE(),
            SchedulerType.RoundRobin: SchedulerRoundRobin()
        }
        return Kernel(SWITCHER.get(schedulerType))

KERNEL_BUILDER = KernelBuilder()