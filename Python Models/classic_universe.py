"""
finalized_cosmos_sim.py
A robust cosmological simulator with proper type safety and organization.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import math, random
from typing import Union

# ==============================================
#  0.  GLOBAL CONSTANTS
# ==============================================
class Universe:
    c = 2.997_924_58e8           # Speed of light (m/s)
    G = 6.674_30e-11             # Gravitational constant (N m²/kg²)
    h = 6.626_070_15e-34         # Planck's constant (J s)

    def __init__(self):
        self.superclusters: list[SuperCluster] = []

    def add_supercluster(self, sc: "SuperCluster"):
        self.superclusters.append(sc)

    def run(self, steps: int = 6, dt: float = 86_400):
        """Propagate simulation for 'steps' iterations with timestep dt."""
        print(f"Running universe simulation for {steps} steps...")
        
        for k in range(steps):
            # Integrate all star systems
            total_systems = 0
            for sc in self.superclusters:
                for gc in sc.galaxy_clusters:
                    for gal in gc.galaxies:
                        for ss in gal.star_systems:
                            ss.integrate(dt)
                            total_systems += 1
            
            # Quantum events every other step
            if k % 2 == 0:
                self._random_quantum_event(k)
        
        print(f"Simulation complete. Integrated {total_systems} star systems.")

    def _random_quantum_event(self, step):
        """Safely perform a quantum measurement on a random star."""
        try:
            # Safely navigate hierarchy
            if not self.superclusters:
                return
            sc = random.choice(self.superclusters)
            
            if not sc.galaxy_clusters:
                return
            gc = random.choice(sc.galaxy_clusters)
            
            if not gc.galaxies:
                return
            gal = random.choice(gc.galaxies)
            
            if not gal.star_systems:
                return
            ss = random.choice(gal.star_systems)
            
            # Quantum measurement
            spin = random.choice(("up", "down"))
            print(f"[step {step:02}] Quantum spin measurement on {ss.primary.name}: {spin}")
            
        except (IndexError, AttributeError) as e:
            print(f"[step {step:02}] Quantum event failed: {e}")

# ==============================================
#  1.  CONTAINER CLASSES
# ==============================================
@dataclass
class SuperCluster:
    name: str
    galaxy_clusters: list["GalaxyCluster"] = field(default_factory=list)
    
    def add_galaxy_cluster(self, gc: "GalaxyCluster"): 
        self.galaxy_clusters.append(gc)

@dataclass
class GalaxyCluster:
    name: str
    galaxies: list["Galaxy"] = field(default_factory=list)
    
    def add_galaxy(self, g: "Galaxy"): 
        self.galaxies.append(g)

@dataclass
class Nebula:
    name: str
    nebula_type: str = "emission"
    mass: float = 1e31
    x: float = 0.0
    y: float = 0.0
    size: float = 1e16

@dataclass
class GlobularCluster:
    name: str
    star_count: int = 100_000
    mass: float = 1e35
    x: float = 0.0
    y: float = 0.0

@dataclass
class Quasar:
    name: str
    luminosity: float = 1e40
    central_black_hole_mass: float = 1e9 * 1.989e30
    x: float = 0.0
    y: float = 0.0

@dataclass
class Galaxy:
    name: str
    star_systems: list["StarSystem"] = field(default_factory=list)
    nebulae: list[Nebula] = field(default_factory=list)
    globular_clusters: list[GlobularCluster] = field(default_factory=list)
    central_black_hole: "BlackHole | None" = None
    quasar: "Quasar | None" = None

    def add_star_system(self, ss: "StarSystem"): 
        self.star_systems.append(ss)
    def add_nebula(self, n: Nebula): 
        self.nebulae.append(n)
    def add_globular_cluster(self, gc: GlobularCluster): 
        self.globular_clusters.append(gc)

# ==============================================
#  2.  CELESTIAL BODIES
# ==============================================
@dataclass
class CelestialBody:
    name: str
    mass: float
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0

    def force_from(self, other: "CelestialBody") -> tuple[float, float]:
        dx, dy = other.x - self.x, other.y - self.y
        r2 = dx*dx + dy*dy
        if r2 < 1e-10:  # Avoid division by zero
            return (0.0, 0.0)
        F = Universe.G * self.mass * other.mass / r2
        r = math.sqrt(r2)
        return F*dx/r, F*dy/r

    def update(self, fx, fy, dt):
        if self.mass <= 0:
            return  # Avoid division by zero
        ax, ay = fx / self.mass, fy / self.mass
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

# Specific body types
class Star(CelestialBody): pass
class WhiteDwarf(Star): pass
class NeutronStar(Star): pass
class BlackHole(CelestialBody): pass
class Moon(CelestialBody): pass
class Asteroid(CelestialBody): pass

class Planet(CelestialBody):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moons: list[Moon] = []
    
    def add_moon(self, moon: Moon):
        self.moons.append(moon)

# ==============================================
#  3.  STAR SYSTEM
# ==============================================
@dataclass
class StarSystem:
    name: str
    primary: Union[Star, BlackHole]
    planets: list[Planet] = field(default_factory=list)
    asteroids: list[Asteroid] = field(default_factory=list)
    stellar_remnants: list[Union[WhiteDwarf, NeutronStar]] = field(default_factory=list)

    def add_planet(self, p: Planet): 
        self.planets.append(p)
    def add_asteroid(self, a: Asteroid): 
        self.asteroids.append(a)
    def add_stellar_remnant(self, sr: Union[WhiteDwarf, NeutronStar]): 
        self.stellar_remnants.append(sr)

    def integrate(self, dt: float):
        """N-body gravitational integration using Euler method."""
        # Collect all bodies
        bodies = [self.primary] + self.planets + self.asteroids + self.stellar_remnants
        
        # Add all moons
        for planet in self.planets:
            bodies.extend(planet.moons)
        
        n = len(bodies)
        if n < 2:
            return
        
        forces = [[0.0, 0.0] for _ in range(n)]

        # Calculate pairwise forces
        for i in range(n):
            for j in range(i + 1, n):
                fx, fy = bodies[i].force_from(bodies[j])
                forces[i][0] += fx
                forces[i][1] += fy
                forces[j][0] -= fx  # Newton's 3rd law
                forces[j][1] -= fy

        # Update all bodies
        for body, (fx, fy) in zip(bodies, forces):
            body.update(fx, fy, dt)

# ==============================================
#  4.  UNIVERSE BUILDER
# ==============================================
def build_demo_universe() -> Universe:
    """Build a comprehensive demo universe with all object types."""
    universe = Universe()
    # Add small random perturbations to demonstrate butterfly effect
    perturbation_scale = 1e-6  # Very small changes
    
    # Build hierarchy
    supercluster = SuperCluster("Laniakea-Toy")
    galaxy_cluster = GalaxyCluster("Virgo-Cluster-Toy")
    galaxy = Galaxy("MilkyWay-Toy")
    
    # Add galactic features
    galaxy.add_nebula(Nebula("Orion Nebula", "emission", 2e31, 3e19, 2e19, 1e17))
    galaxy.add_nebula(Nebula("Crab Nebula", "supernova", 4.6e29, 5e19, 4e19, 2e17))
    galaxy.add_globular_cluster(GlobularCluster("M13", 300_000, 6e35, -1e20, 2e20))
    galaxy.add_globular_cluster(GlobularCluster("Omega Centauri", 1_500_000, 4e36, 5e19, -2e19))
    galaxy.quasar = Quasar("Toy Quasar", 1e41, 1.2e9*1.989e30, 0.0, 0.0)
    galaxy.central_black_hole = BlackHole("SgrA*-Toy", 4e6*1.989e30, 0, 0)
    
    # Build Solar System
    sun = Star("Sun-Toy", 1.989e30, 0, 0)
    solar_system = StarSystem("Solar-System-Toy", sun)
    
    # Planets
    earth = Planet("Earth-Toy", 5.972e24, 1.496e11, 0, 0, 29_780)
    moon = Moon("Moon-Toy", 7.348e22, 1.496e11 + 3.84e8, 0, 0, 29_780 + 1_022)
    earth.add_moon(moon)
    solar_system.add_planet(earth)
    
    mars = Planet("Mars-Toy", 6.39e23, 2.279e11, 0, 0, 24_077)
    solar_system.add_planet(mars)
    
    # Asteroids (properly categorized)
    ceres = Asteroid("Ceres-Toy", 9.4e20, 4.14e11, 0, 0, 17_882)
    solar_system.add_asteroid(ceres)
    
    # Stellar remnants (in separate category)
    white_dwarf = WhiteDwarf("WD-Toy", 0.6*1.989e30, -5e11, 0, 0, -15_000)
    neutron_star = NeutronStar("NS-Toy", 1.4*1.989e30, 6e11, 0, 0, 12_000)
    solar_system.add_stellar_remnant(white_dwarf)
    solar_system.add_stellar_remnant(neutron_star)
    
    # Assemble hierarchy
    galaxy.add_star_system(solar_system)
    galaxy_cluster.add_galaxy(galaxy)
    supercluster.add_galaxy_cluster(galaxy_cluster)
    universe.add_supercluster(supercluster)
    
    return universe

# ==============================================
#  5.  CLEAN MAIN LOOP
# ==============================================
import time
def main():
    """Main simulation loop with comprehensive reporting."""
    # Initialize with current time for true randomness
    seed = int(time.time() * 1000000) % (2**32)
    random.seed(seed)
    print(f"Random seed: {seed}")
    print("=" * 60)
    print("COSMIC HIERARCHY SIMULATOR")
    print("=" * 60)
    
    # Build and run simulation
    universe = build_demo_universe()
    universe.run(steps=6, dt=86_400)  # 6 days
    
    # Safe navigation to galaxy
    try:
        galaxy = universe.superclusters[0].galaxy_clusters[0].galaxies[0]
        solar_system = galaxy.star_systems[0]
    except (IndexError, AttributeError) as e:
        print(f"Error accessing simulation results: {e}")
        return
    
    # Report galaxy features
    print("\n" + "=" * 60)
    print("GALAXY INVENTORY")
    print("=" * 60)
    
    print(f"\nGalaxy: {galaxy.name}")
    if galaxy.central_black_hole:
        print(f"Central Black Hole: {galaxy.central_black_hole.name}, "
              f"mass = {galaxy.central_black_hole.mass:.2e} kg")
    
    if galaxy.quasar:
        print(f"Quasar: {galaxy.quasar.name}, "
              f"luminosity = {galaxy.quasar.luminosity:.2e} W")
    
    print(f"\nNebulae ({len(galaxy.nebulae)}):")
    for nebula in galaxy.nebulae:
        print(f"  • {nebula.name} ({nebula.nebula_type}), "
              f"mass = {nebula.mass:.2e} kg")
    
    print(f"\nGlobular Clusters ({len(galaxy.globular_clusters)}):")
    for cluster in galaxy.globular_clusters:
        print(f"  • {cluster.name}, {cluster.star_count:,} stars, "
              f"mass = {cluster.mass:.2e} kg")
    
    # Report star system details
    print("\n" + "=" * 60)
    print("STAR SYSTEM FINAL POSITIONS")
    print("=" * 60)
    
    AU = 1.496e11  # Astronomical Unit in meters
    
    print(f"\nStar System: {solar_system.name}")
    print(f"Primary: {solar_system.primary.name}")
    print(f"  Position: x = {solar_system.primary.x/AU:+6.3f} AU, "
          f"y = {solar_system.primary.y/AU:+6.3f} AU")
    
    print(f"\nPlanets ({len(solar_system.planets)}):")
    for planet in solar_system.planets:
        print(f"  • {planet.name:12s} x = {planet.x/AU:+6.3f} AU, "
              f"y = {planet.y/AU:+6.3f} AU")
        
        # Safely handle moons (only Planet objects have moons)
        if planet.moons:
            for moon in planet.moons:
                print(f"    └─ {moon.name:10s} x = {moon.x/AU:+6.3f} AU, "
                      f"y = {moon.y/AU:+6.3f} AU")
    
    print(f"\nAsteroids ({len(solar_system.asteroids)}):")
    for asteroid in solar_system.asteroids:
        print(f"  • {asteroid.name:12s} x = {asteroid.x/AU:+6.3f} AU, "
              f"y = {asteroid.y/AU:+6.3f} AU")
    
    print(f"\nStellar Remnants ({len(solar_system.stellar_remnants)}):")
    for remnant in solar_system.stellar_remnants:
        print(f"  • {remnant.name:12s} x = {remnant.x/AU:+6.3f} AU, "
              f"y = {remnant.y/AU:+6.3f} AU")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()