 

## Entender las clases **InterruptVector()** y **Clock()** y poder explicar como funcionan

### InterruptVector() 

La clase InterruptVector() emula el interrupt vector table del hardware. En nuestro modelo, nuestra clase tiene una variable de instancia de tipo diccionario, en el cual, la clave del mismo representa el tipo de las interrupciones y el valor que corresponde a dicha clave, el handler para ese tipo de interrupción. A través de del método register de dicha clase, el sistema operativo le puede proporcionar al hardware los handlers para las interrupciones y así poder escucharlo. Una vez registrados nuestros handlers para las interrupciones en nuestro Interrupt Vector Table, el hardware puede utilizar el método handle() de la clase InterruptVector() para indicarle al handler correspondiente a cada interrupción registrada , que maneje las mismas.

### Clock()

La clase Clock() emula el reloj del hardware que ayuda a sincronizar los ciclos de ejecución. Para representarlo en nuestro modelo el mismo tiene dos variables de instancia: 

 1. La variable _subscribers, que representa una lista con las partes del hardware a la cual el reloj les avisará que está realizando un nuevo "tick". Para añadir un suscriptor nuestra clase cuenta con el método addSuscriber().
 2. La variable _running, que representa el estado del reloj (si está corriendo o no).

**El reloj cuenta con dos métodos principales:**

 1.  stop(): Simplemente lo que hace es parar el reloj, por lo tanto setea su estado interno de la variable _running en falso, lo que indica que está parado
 2. start(): Este método setea el estado de la variable running en true, lo que indica que el reloj empieza a funcionar. Además crea un objeto de tipo Thread que toma como parámetro otro método privado del reloj llamado __start(). Al hacer esto, cuando le enviamos start() a este objeto de tipo Thread, automáticamente llama al método __start() que fue pasado por parámetro al momento de la creación.

**Que pasa cuando el Thread llama al metodo __start()?**

Cuando el Thread se inicia y se llama automáticamente al metodo __start() se setea una variable interna que representa el numero de ticks del reloj en 0. A partir de allí, mientras que el estado de la variable _running se encuentre en verdadero, comienza un ciclo en el cual nuestro reloj va haciendo "ticks" y el numero de tick interno va aumentado en 1.

**Hasta ahora perfecto. Pero que es un tick? Para que sirve?**

Cuando el reloj hace "tick" informa por pantalla el numero de tick que se está ejecutando, pero aun mas importante, avisa a cada uno de sus suscriptores (partes del hardware) que se realizo un tick, por lo tanto cada uno de estos recibirá el mensaje .tick(numero de tick). Los suscriptores del reloj saben como reaccionar a ese mensaje, y cada uno realizará una acción distinta dependiendo de sus implementaciones del método .tick(tickNbr).

Por último, el reloj tiene un método llamado do_ticks(), que permite realizar un número fijo de ticks (pasados por parámetro). 

## Explicar cómo se llegan a ejecutar **KillInterruptionHandler.execute()**

Al levantar nuestro Kernel, el mismo genera una variable que contiene una instancia de la clase KillInterruptionHandler. Además de eso, registra en el vector de interrupciones la referencia a este objeto, para que pueda ser llamado por el.
Cuando el CPU de nuestro modelo ejecuta una operación del tipo Exit genera un pedido de interrupción de sistema (IRQ) del tipo #KILL. Acto seguido le envía al vector de interrupciones el mensaje handle con la IRQ generada como parámetro.
Cuando nuestro vector de interrupciones recibe este mensaje, indica que se va a manejar la interrupción y le pide a nuestro sistema operativo que se encargue de ello.

**Pero como sabe nuestro hardware a que manejador de IRQ llamar en función de la IRQ generada?**

Como mencionamos anteriormente, el Kernel guarda en el vector de interrupciones las "direcciones" de las rutinas a ejecutar dependiendo de cada IRQ. En nuestro modelo, el Kernel() registra en un diccionario generado por la clase InterruptVector(), la referencia a una instancia de la clase KillInterruptionHandler().
De esta manera, cuando se llama al método handle(irq) de nuestro vector de interrupciones, lo que termina pasando es que se busca en el diccionario de esta clase la entrada cuyo valor sea #KILL, y a ese objeto se le termina enviado el mensaje execute. Así es como se termina ejecutando la sentencia KillInterruptionHandler.execute()


