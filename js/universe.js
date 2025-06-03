// ===== UNIVERSAL CONSTANTS =====
const CONSTANTS = {
    // Physical Constants (SI units, but we'll scale for simulation)
    c: 299792458,           // Speed of light (m/s)
    G: 6.67430e-11,         // Gravitational constant
    h: 6.62607015e-34,      // Planck constant
    e: 1.602176634e-19,     // Elementary charge
    k_B: 1.380649e-23,      // Boltzmann constant
    N_A: 6.02214076e23,     // Avogadro's number
    alpha: 1/137,           // Fine structure constant
    R: 8.314462618,         // Gas constant
    epsilon_0: 8.854187817e-12, // Permittivity of free space
    mu_0: 4 * Math.PI * 1e-7,   // Permeability of free space
    
    // Simulation scaling factors
    SCALE_DISTANCE: 1e-9,   // Scale down distances
    SCALE_TIME: 1e6,        // Scale up time steps
    SCALE_MASS: 1e-20       // Scale down masses
};

// ===== COORDINATE SYSTEM =====
class SphericalCoordinate {
    constructor(r, theta, phi) {
        this.r = r;         // Distance from center
        this.theta = theta; // Polar angle (0 to π)
        this.phi = phi;     // Azimuthal angle (0 to 2π)
    }
    
    toCartesian() {
        return {
            x: this.r * Math.sin(this.theta) * Math.cos(this.phi),
            y: this.r * Math.sin(this.theta) * Math.sin(this.phi),
            z: this.r * Math.cos(this.theta)
        };
    }
    
    static fromCartesian(x, y, z) {
        const r = Math.sqrt(x*x + y*y + z*z);
        const theta = r > 0 ? Math.acos(z / r) : 0;
        const phi = Math.atan2(y, x);
        return new SphericalCoordinate(r, theta, phi);
    }
}

// ===== BASE COSMIC OBJECT =====
class CosmicObject {
    constructor(position, velocity, mass, type) {
        this.position = position; // SphericalCoordinate
        this.velocity = velocity; // {x, y, z} in Cartesian
        this.mass = mass;
        this.type = type;
        this.age = 0;
        this.temperature = 0;
        this.properTime = 0; // For relativistic effects
    }
    
    // Calculate gravitational time dilation factor
    getTimeDilationFactor(universe) {
        let gravitationalPotential = 0;
        universe.objects.forEach(obj => {
            if (obj !== this) {
                const distance = this.distanceTo(obj);
                if (distance > 0) {
                    gravitationalPotential += CONSTANTS.G * obj.mass / distance;
                }
            }
        });
        
        // Simplified time dilation: dt_proper = dt * sqrt(1 - 2*phi/c^2)
        const factor = Math.sqrt(Math.abs(1 - 2 * gravitationalPotential / (CONSTANTS.c * CONSTANTS.c)));
        return Math.max(factor, 0.1); // Prevent extreme values
    }
    
    distanceTo(other) {
        const pos1 = this.position.toCartesian();
        const pos2 = other.position.toCartesian();
        return Math.sqrt(
            Math.pow(pos1.x - pos2.x, 2) +
            Math.pow(pos1.y - pos2.y, 2) +
            Math.pow(pos1.z - pos2.z, 2)
        );
    }
}

// ===== SPECIFIC OBJECT TYPES =====
class Star extends CosmicObject {
    constructor(position, velocity, mass, stellarType = 'main_sequence') {
        super(position, velocity, mass, 'star');
        this.stellarType = stellarType;
        this.luminosity = this.calculateLuminosity();
        this.temperature = this.calculateTemperature();
        this.lifespan = this.calculateLifespan();
    }
    
    calculateLuminosity() {
        const solarMass = 1.989e30;
        const solarLuminosity = 3.828e26;
        return solarLuminosity * Math.pow(this.mass / solarMass, 3.5);
    }
    
    calculateTemperature() {
        return 5778 * Math.pow(this.luminosity / 3.828e26, 0.25);
    }
    
    calculateLifespan() {
        const solarLifespan = 10e9;
        const solarMass = 1.989e30;
        return solarLifespan * Math.pow(solarMass / this.mass, 2.5);
    }
}

class Planet extends CosmicObject {
    constructor(position, velocity, mass, planetType = 'terrestrial') {
        super(position, velocity, mass, 'planet');
        this.planetType = planetType;
        this.moons = [];
        this.atmosphere = null;
        this.rings = null;
    }
    
    addMoon(moon) {
        this.moons.push(moon);
    }
}

class BlackHole extends CosmicObject {
    constructor(position, velocity, mass) {
        super(position, velocity, mass, 'black_hole');
        this.schwarzschildRadius = 2 * CONSTANTS.G * mass / (CONSTANTS.c * CONSTANTS.c);
        this.eventHorizon = this.schwarzschildRadius;
    }
    
    getTimeDilationFactor() {
        return 0.01; // Time moves very slowly near black holes
    }
}

// ===== UNIVERSE CLASS =====
class Universe {
    constructor(radius = 1e26) {
        this.radius = radius;
        this.objects = [];
        this.time = 0;
        this.hubbleConstant = 67.4;
        this.darkEnergyDensity = 0.685;
        this.darkMatterDensity = 0.265;
        this.baryonicMatterDensity = 0.05;
        this.stepCount = 0;
    }
    
    addObject(object) {
        this.objects.push(object);
    }
    
    calculateForces() {
        const forces = this.objects.map(() => ({fx: 0, fy: 0, fz: 0}));
        
        for (let i = 0; i < this.objects.length; i++) {
            for (let j = i + 1; j < this.objects.length; j++) {
                const obj1 = this.objects[i];
                const obj2 = this.objects[j];
                
                const gravForce = this.calculateGravitationalForce(obj1, obj2);
                
                forces[i].fx += gravForce.fx;
                forces[i].fy += gravForce.fy;
                forces[i].fz += gravForce.fz;
                
                forces[j].fx -= gravForce.fx;
                forces[j].fy -= gravForce.fy;
                forces[j].fz -= gravForce.fz;
            }
        }
        
        return forces;
    }
    
    calculateGravitationalForce(obj1, obj2) {
        const pos1 = obj1.position.toCartesian();
        const pos2 = obj2.position.toCartesian();
        
        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        const dz = pos2.z - pos1.z;
        
        const distanceSq = dx*dx + dy*dy + dz*dz + 1e-10;
        const distance = Math.sqrt(distanceSq);
        
        const force = CONSTANTS.G * obj1.mass * obj2.mass / distanceSq;
        
        return {
            fx: force * dx / distance,
            fy: force * dy / distance,
            fz: force * dz / distance
        };
    }
    
    update(dt = 1) {
        const forces = this.calculateForces();
        
        this.objects.forEach((obj, i) => {
            const ax = forces[i].fx / obj.mass;
            const ay = forces[i].fy / obj.mass;
            const az = forces[i].fz / obj.mass;
            
            const timeDilation = obj.getTimeDilationFactor(this);
            const effectiveDt = dt * timeDilation;
            
            obj.velocity.x += ax * effectiveDt;
            obj.velocity.y += ay * effectiveDt;
            obj.velocity.z += az * effectiveDt;
            
            // Apply speed of light limit
            const speed = Math.sqrt(obj.velocity.x**2 + obj.velocity.y**2 + obj.velocity.z**2);
            if (speed > CONSTANTS.c) {
                const factor = CONSTANTS.c / speed;
                obj.velocity.x *= factor;
                obj.velocity.y *= factor;
                obj.velocity.z *= factor;
            }
            
            const currentPos = obj.position.toCartesian();
            const newX = currentPos.x + obj.velocity.x * effectiveDt;
            const newY = currentPos.y + obj.velocity.y * effectiveDt;
            const newZ = currentPos.z + obj.velocity.z * effectiveDt;
            
            obj.position = SphericalCoordinate.fromCartesian(newX, newY, newZ);
            obj.properTime += effectiveDt;
            obj.age += effectiveDt;
        });
        
        this.time += dt;
        this.stepCount++;
    }
    
    printStatus() {
        console.clear();
        console.log('='.repeat(60));
        console.log(`🌌 UNIVERSE SIMULATION - Step ${this.stepCount}`);
        console.log(`⏰ Universe Time: ${(this.time / (365.25 * 86400)).toFixed(4)} years`);
        console.log('='.repeat(60));
        
        this.objects.forEach((obj, i) => {
            const pos = obj.position.toCartesian();
            const speed = Math.sqrt(obj.velocity.x**2 + obj.velocity.y**2 + obj.velocity.z**2);
            
            console.log(`${this.getObjectEmoji(obj.type)} ${obj.type.toUpperCase()} ${i + 1}:`);
            console.log(`   Position: r=${(obj.position.r / 1.496e11).toFixed(4)} AU`);
            console.log(`   Speed: ${(speed / 1000).toFixed(2)} km/s`);
            console.log(`   Proper Time: ${(obj.properTime / 86400).toFixed(2)} days`);
            
            if (obj.type === 'star') {
                console.log(`   Temperature: ${obj.temperature.toFixed(0)} K`);
                console.log(`   Luminosity: ${obj.luminosity.toExponential(2)} W`);
            }
            console.log('');
        });
    }
    
    getObjectEmoji(type) {
        const emojis = {
            'star': '⭐',
            'planet': '🪐',
            'black_hole': '🕳️',
            'galaxy': '🌌'
        };
        return emojis[type] || '⚫';
    }
}

// ===== INITIALIZATION =====
function createSolarSystem() {
    const universe = new Universe();
    
    // Create the Sun
    const sun = new Star(
        new SphericalCoordinate(0, Math.PI/2, 0),
        {x: 0, y: 0, z: 0},
        1.989e30 * CONSTANTS.SCALE_MASS
    );
    universe.addObject(sun);
    
    // Create Earth
    const earth = new Planet(
        new SphericalCoordinate(1.496e11 * CONSTANTS.SCALE_DISTANCE, Math.PI/2, 0),
        {x: 0, y: 29780, z: 0},
        5.972e24 * CONSTANTS.SCALE_MASS,
        'terrestrial'
    );
    universe.addObject(earth);
    
    // Create Jupiter
    const jupiter = new Planet(
        new SphericalCoordinate(7.785e11 * CONSTANTS.SCALE_DISTANCE, Math.PI/2, Math.PI/4),
        {x: 0, y: 13070, z: 0},
        1.898e27 * CONSTANTS.SCALE_MASS,
        'gas_giant'
    );
    universe.addObject(jupiter);
    
    return universe;
}

// ===== MAIN SIMULATION =====
console.log('🚀 Starting Universe Simulation...\n');

const myUniverse = createSolarSystem();
let running = true;

// Handle Ctrl+C to stop simulation gracefully
process.on('SIGINT', () => {
    console.log('\n\n🛑 Simulation stopped by user');
    running = false;
    process.exit(0);
});

function runSimulation() {
    if (!running) return;
    
    myUniverse.update(86400 * CONSTANTS.SCALE_TIME); // One day time step
    myUniverse.printStatus();
}

// Run simulation every 1 second
const interval = setInterval(() => {
    if (!running) {
        clearInterval(interval);
        return;
    }
    runSimulation();
}, 1000);

console.log('Press Ctrl+C to stop the simulation');