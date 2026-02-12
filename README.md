This program has been created to simulate charges in a magnetic field.

### Usage
To create a simulation a display must first be initialised:
```py
display = Display(400, 400, "Magnetism Simulation")
```
A simple magnet can be simulated by initialising a magnet object and attaching it to the display:
```py
magnet = Magnet((200, 200))
display.attach(magnet)
```
Multiple magnets can also be added to interact with one another
```py
magnets = list()
magnets.append(Magnet((200, 150), magnets, 90))
magnets.append(Magnet((200, 250), magnets, -90))
for magnet in magnets:
    display.attach(magnet)
```
Finally, the display loop must be run
```py
display.run()
```