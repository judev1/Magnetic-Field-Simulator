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
Multiple magnets can also be added to interact with one another using a magnet manager:
```py
mm = MagnetManager(display)
mm.attach(Magnet((100, 150), 45))
mm.attach(Magnet((100, 250), -45))
```
A ferrite which rotates under the influence of a magnetic field can also be added:
```py
mm.attach(FerriteDipole((300, 200)))
```
Alternatively, you can run my three magnet dipole simulation:
```py
three_magnet_simulation(display) # as simple as that
```
Finally, the display loop must be run
```py
display.run()
```