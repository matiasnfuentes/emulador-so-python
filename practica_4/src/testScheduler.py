from so import *
from pcb import *
import unittest

# PCB(pid,baseDir,path,priority)

prg1 = Program("prg1.exe", [ASM.CPU(2), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
prg2 = Program("prg2.exe", [ASM.CPU(7)])
prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])

pcb1 = Pcb(1, 0, prg1, 3)
pcb2 = Pcb(2, 5, prg2, 4)
pcb3 = Pcb(3, 15, prg3, 1)

mysteriousPCB = Pcb(99, 99, prg1, 0)

HARDWARE.setup(25)


class SchedulerFCFSTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = SchedulerFCFS()
        self.scheduler.add(pcb1)
        self.scheduler.add(pcb2)
        self.scheduler.add(pcb3)

    def test_agrego_un_pcb_y_esta_en_readyQ(self):
        self.scheduler.add(mysteriousPCB)
        self.assertTrue(mysteriousPCB in self.scheduler.readyQ)

    def test_pido_el_proximo_y_me_da_pcb_1_porque_fue_el_primero_en_agregarse(self):
        self.assertEqual(pcb1, self.scheduler.getNext())

    def test_has_next_exitoso(self):
        self.assertTrue(self.scheduler.hasNext())

    def test_popeo_los_elementos_de_la_ready_q_y_no_tengo_proximo(self):
        self.scheduler.getNext()
        self.scheduler.getNext()
        self.scheduler.getNext()
        self.assertFalse(self.scheduler.hasNext())

    def test_must_expropiate_da_falso_ya_que_este_scheduler_no_debe_expropiar(self):
        self.assertFalse(self.scheduler.mustExpropiate(pcb1, pcb2))

class SchedulerPriorityTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = SchedulerPriority()
        self.scheduler.add(pcb1)
        self.scheduler.add(pcb2)
        self.scheduler.add(pcb3)

    def test_agrego_un_pcb_y_esta_en_readyQ(self):
        self.scheduler.add(mysteriousPCB)
        pcbInReadyQ = self.scheduler.readyQ[0].pop()[0]
        self.assertEqual(mysteriousPCB, pcbInReadyQ)

    def test_pido_el_proximo_y_me_da_pcb_3_porque_fue_es_el_de_mayor_prioridad(self):
        self.assertEqual(pcb3, self.scheduler.getNext())

    def test_has_next_exitoso_porque_tengo_3_elementos(self):
        self.assertTrue(self.scheduler.hasNext())

    def test_popeo_los_elementos_de_la_ready_q_y_no_tengo_proximo(self):
        self.scheduler.getNext()
        self.scheduler.getNext()
        self.scheduler.getNext()
        self.assertFalse(self.scheduler.hasNext())

    def test_must_expropiate_da_falso_ya_que_este_scheduler_no_es_expropiativo(self):
        self.assertFalse(self.scheduler.mustExpropiate(pcb1, pcb3))

class SchedulerPriorityPreentiveTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = SchedulerPriorityPRENTIVE()

    ##Los métodos getNext, hasNext y add se heredan del scheduler anterior.

    def test_must_expropiate_da_verdadero_ya_que_el_pcb3_es_el_de_mayor_prioridad(self):
        self.assertTrue(self.scheduler.mustExpropiate(pcb1, pcb3))

    def test_must_expropiate_da_falso_ya_que_el_pcb3_es_el_de_mayor_prioridad(self):
        self.assertFalse(self.scheduler.mustExpropiate(pcb3, pcb1))

class SchedulerRoundRobinTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = SchedulerRoundRobin()

    # Los métodos getNext, hasNext, mustExpropiate y add se heredan
    # del abstract scheduler y ya fueron testeados.

    def test_inicio_el_scheduler_round_robin_y_se_setea_el_timer_en_true_con_quantum_3(self):
        self.assertEqual(3, HARDWARE.timer.quantum)


if __name__=='__main__':
    unittest.main()