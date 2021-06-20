from kernelBuilder import *
import log

##
##  MAIN 
##
if __name__ == '__main__':
    log.setupLogger()
    log.logger.info('Starting emulator')

    ## setup our hardware and set memory size to 25 "cells"
    HARDWARE.setup(25)

    ## Switch on computer
    HARDWARE.switchOn()

    ## new create the Operative System Kernel
    # "booteamos" el sistema operativo
    # Available scheduler options:
        # FirstComeFirstServed
        # Priority
        # PriorityPreentive
        # RoundRobin

    kernel = KERNEL_BUILDER.buildKernel(SchedulerType.Priority)

    # Ahora vamos a intentar ejecutar 3 programas a la vez
    ##################
    prg1 = Program("prg1.exe", [ASM.CPU(2), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    prg2 = Program("prg2.exe", [ASM.CPU(7)])
    prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])


    # execute all programs "concurrently"
    kernel.run(prg1, 0)
    kernel.run(prg2, 4)
    kernel.run(prg3, 2)
    sleep(35)
    kernel.statTable.showStats()




