# Grupo 2

### Integrantes:

| Nombre y Apellido              |      Mail                      |     usuario Gitlab   |
| -----------------------------  | ------------------------------ | -------------------  |
| Nahuel Gomez                   |  Nahuelggt@gmail.com           |  Nahue507            |
| Matías Nahuel Fuentes          |  matiasnfuentes@gmail.com      |  matiasnfuentes      |


## Práctica 1: Aprobado

## Práctica 2: Aprobado

## Práctica 3: Aprobado

### Comentarios/Acotaciones: 

1) Si pueden, borren el metodo kernel.load_program(), ya no tiene sentido:

```
    def load_program(self, program):
        self._loader.loadProgram(program)
```


2) usen la constante NEW_INTERRUPTION_TYPE en lugar del String suelto: 
```
    ## emulates a "system call" for programs execution
    def run(self, program):
        irq = IRQ(NEW_INTERRUPTION_TYPE, program)
        self._newHandler.execute(irq)
```

3) Podrian agregarle el metodo ```__repr__``` al PCB para loguearlo mas facil
```
    def __repr__(self):
        return "PCB(pid={pid}, state={state}, pc={pc}, path={path})"
```

4) Y despues Loguear el PCB que entra y sale en el dispatcher:
```
    def save(self, pcb):
        log.logger.info("Dispatcher Save: {pcb}".format(pcb=pcb))

    def load(self, pcb):
        log.logger.info("Dispatcher Load: {pcb}".format(pcb=pcb))
```

5)  Logueen la memoria solo en el #NEW:
```
            log.logger.info("\n Executing program: {name}".format(name=readyPCB.path))
            log.logger.info(HARDWARE)
```
  (porque sino se confunde seguir un context switch)

