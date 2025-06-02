# Mathematical Universe Simulator

A programmable, extensible simulation of the universe as a mathematical construct, built in JavaScript/Node.js. This project models physics, time, space, and cosmic objects from first principles, laying a modular foundation for exploring physical laws and constants in a toy universe.

---

## Project Goals
- **Model the universe as a mathematical/computational system**  
  Use programming as an analogy to implement core physical laws and structures.
- **Enable extensible, modular building**  
  Start simple (gravity, motion, relativity), then allow rapid expansion—adding new physics, objects, and phenomena.
- **Serve as a learning, experimentation, and research tool**  
  Visualize and experiment with how universal laws shape emergent behavior—planets, stars, galaxies, time dilation, and beyond.
- **Facilitate scientific curiosity & collaboration**  
  Welcome contributors with ideas from physics, math, computation, and education.

---

## Tech Stack
- **Node.js / JavaScript (ES6+)**  
  Simulation core and framework logic.
- **VSCode**  
  Recommended development environment.
- **Console Output (currently)**  
  Future versions may include visualization via HTML Canvas/WebGL.

---

## Features
- **Physics-Based Object Model**  
  Planets, stars, black holes, galaxies, etc.
- **3D Spherical Space**  
  Objects use spherical and cartesian coordinates.
- **Laws of Physics**  
  - Newton's Laws of Motion  
  - Universal Gravitation  
  - Conservation Laws (energy, momentum)  
  - Relativistic Time Dilation  
  - (Planned: Maxwell's equations, thermodynamics, quantum effects)
- **Configurable Constants**  
  Real physical constants, user scaling.
- **Extensible Universe**  
  Add or adjust cosmic object classes, or plug in new laws.
- **Relativistic & Cosmological Dynamics**  
  Hubble expansion, proper time, event horizons.
- **Console-based Run Loop**  
  Live simulation stats with emoji for clarity.

---

## How to Use
### **1. Clone the Repository**
```bash
git clone https://github.com/Juno445/Universe-simulator.git
cd Universe-simulator/js
```
### **2. Install Dependencies**
_No dependencies needed for core simulation._  
(If you expand with visualization, you may add packages later.)
### **3. Start the Simulation**
```bash
npm start
# or
node universe.js
```
You will see ongoing simulation output in your terminal.  
Press **Ctrl+C** to stop.
### **4. Customize the Universe**
- **Edit `universe.js`**  
  Add new objects (planets, stars, black holes, etc.) in the `createSolarSystem()` (or create your own!) function.
- **Modify Physical Laws or Constants**  
  Adjust the `CONSTANTS` object to explore different universes.
- **Add new physics**  
  (e.g. electromagnetism, thermodynamics) by extending the Universe and CosmicObject classes.
### **5. Development**
We recommend using [Visual Studio Code](https://code.visualstudio.com/) for code navigation and debugging.

---

## Contributing
Contributions are welcome!  
Help us add:
- New object types (neutron stars, asteroids, comets)
- Visualization (web, desktop, or 3D graphics)
- Improved physics (Maxwell, Einstein, quantum theory)
- Educational docs, code comments, tests
- Optimizations (simulation speed, numerical accuracy)
Open an [issue](https://github.com/Juno445/Universe-simulator/issues) or submit a pull request!

---

## Roadmap
- [ ] HTML Canvas or WebGL visualization
- [ ] Complex stellar & galactic evolution
- [ ] Quantum/thermodynamic effects
- [ ] Save/load universe states
- [ ] Modular plugin system for laws/objects
- [ ] User-driven star/galaxy/cluster generation

---

## License
MIT License.  
See [LICENSE](LICENSE) for details.
