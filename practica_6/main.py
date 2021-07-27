from kernelBuilder import *
import log

##
##  MAIN 
##
if __name__ == '__main__':
    log.setupLogger()
    log.logger.info('Starting emulator')

    ## setup our hardware and set memory size to 25 "cells"
    HARDWARE.setup(16)

    ## Switch on computer
    HARDWARE.switchOn()

    ## new create the Operative System Kernel
    # "booteamos" el sistema operativo
    # Tipos de algoritmos de selección de vicitma:
    # VictimAlgorithim.FiFo
    # VictimAlgorithim.LRU
    # VictimAlgorithim.Clock

    kernel = KERNEL_BUILDER.buildKernel(SchedulerType.FirstComeFirstServed, 4, VictimAlgorithim.FiFo)

    # Ahora vamos a intentar ejecutar 3 programas a la vez
    ##################
    prg1 = Program("prg1.exe", [ASM.CPU(2), ASM.IO(), ASM.IO(),ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    prg2 = Program("prg2.exe", [ASM.CPU(25)])
    prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.IO(), ASM.IO(), ASM.CPU(1)])

    # execute all programs "concurrently"
    kernel.fileSystem.write(prg1.name, prg1.instructions)
    kernel.fileSystem.write(prg2.name, prg2.instructions)
    kernel.fileSystem.write(prg3.name, prg3.instructions)

    kernel.run(prg1.name, 3)
    kernel.run(prg2.name, 2)
    kernel.run(prg3.name, 4)
