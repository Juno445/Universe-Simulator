import time, math, random
from dataclasses import dataclass, field
from typing import Union

# ========== UNIVERSAL CONSTANTS ==========
class Universe:
    c = 2.997_924_58e8
    G = 6.674_30e-11
    h = 6.626_070_15e-34

    def __init__(self):
        self.superclusters: list[SuperCluster] = []

    def add_supercluster(self, sc):
        self.superclusters.append(sc)

    def run(self, steps=6, dt=86_400):
        for k in range(steps):
            for sc in self.superclusters:
                for gc in sc.galaxy_clusters:
                    for gal in gc.galaxies:
                        for ss in gal.star_systems:
                            ss.integrate(dt)
            if k % 2 == 0:
                self._random_quantum_event(k)

    def _random_quantum_event(self, step):
        try:
            sc = random.choice(self.superclusters)
            gc = random.choice(sc.galaxy_clusters)
            gal = random.choice(gc.galaxies)
            if not gal.star_systems: return
            ss = random.choice(gal.star_systems)
            spin = random.choice(("up", "down"))
            print(f"[step {step:02}] Quantum spin measurement on {ss.primary.name}: {spin}")
        except Exception:
            pass

# ========== HIERARCHICAL CONTAINERS ==========
@dataclass
class SuperCluster:
    name: str
    galaxy_clusters: list["GalaxyCluster"] = field(default_factory=list)
    def add_galaxy_cluster(self, gc): self.galaxy_clusters.append(gc)

@dataclass
class GalaxyCluster:
    name: str
    galaxies: list["Galaxy"] = field(default_factory=list)
    def add_galaxy(self, g): self.galaxies.append(g)

@dataclass
class Nebula:
    name: str; nebula_type: str = "emission"
    mass: float = 1e31; x: float = 0.; y: float = 0.; size: float = 1e16

@dataclass
class GlobularCluster:
    name: str; star_count: int = 100_000
    mass: float = 1e35; x: float = 0.; y: float = 0.

@dataclass
class Quasar:
    name: str
    luminosity: float = 1e40
    central_black_hole_mass: float = 1e9 * 1.989e30
    x: float = 0.; y: float = 0.

@dataclass
class Galaxy:
    name: str
    star_systems: list["StarSystem"] = field(default_factory=list)
    nebulae: list[Nebula] = field(default_factory=list)
    globular_clusters: list[GlobularCluster] = field(default_factory=list)
    central_black_hole: "BlackHole | None" = None
    quasar: "Quasar | None" = None
    def add_star_system(self, ss): self.star_systems.append(ss)
    def add_nebula(self, n): self.nebulae.append(n)
    def add_globular_cluster(self, gc): self.globular_clusters.append(gc)

# ========== CELESTIAL BODIES ==========
@dataclass
class CelestialBody:
    name: str
    mass: float
    x: float; y: float
    vx: float = 0.; vy: float = 0.
    def force_from(self, other):  # Newtonian gravity, 2D
        dx, dy = other.x - self.x, other.y - self.y
        r2 = dx*dx + dy*dy
        if r2 < 1e-10:  # skip singularity
            return (0., 0.)
        F = Universe.G * self.mass * other.mass / r2
        r = math.sqrt(r2)
        return F*dx/r, F*dy/r
    def update(self, fx, fy, dt):
        if self.mass <= 0: return
        ax, ay = fx / self.mass, fy / self.mass
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

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
    def add_moon(self, moon): self.moons.append(moon)

# ========== STAR SYSTEM ==========
@dataclass
class StarSystem:
    name: str
    primary: Union[Star, BlackHole]
    planets: list[Planet] = field(default_factory=list)
    asteroids: list[Asteroid] = field(default_factory=list)
    stellar_remnants: list[Union[WhiteDwarf, NeutronStar]] = field(default_factory=list)
    def add_planet(self, p): self.planets.append(p)
    def add_asteroid(self, a): self.asteroids.append(a)
    def add_stellar_remnant(self, sr): self.stellar_remnants.append(sr)
    def integrate(self, dt):
        bodies = [self.primary] + self.planets + self.asteroids + self.stellar_remnants
        for planet in self.planets:
            bodies.extend(planet.moons)
        n = len(bodies)
        if n < 2: return
        forces = [[0.,0.] for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                fx, fy = bodies[i].force_from(bodies[j])
                forces[i][0] += fx;    forces[i][1] += fy
                forces[j][0] -= fx;    forces[j][1] -= fy
        for body, (fx, fy) in zip(bodies, forces):
            body.update(fx, fy, dt)

# ========== DEMO UNIVERSE BUILDER (with CHAOS) ==========
def build_demo_universe(perturb=True, magnitude=1e-6) -> Universe:
    universe = Universe()
    supercluster = SuperCluster("Laniakea-Toy")
    galaxy_cluster = GalaxyCluster("Virgo-Cluster-Toy")
    galaxy = Galaxy("MilkyWay-Toy")

    # Nebulae, globular clusters, Quasar
    galaxy.add_nebula(Nebula("Orion Nebula", "emission", 2e31, 3e19, 2e19, 1e17))
    galaxy.add_nebula(Nebula("Crab Nebula", "supernova", 4.6e29, 5e19, 4e19, 2e17))
    galaxy.add_globular_cluster(GlobularCluster("M13", 300_000, 6e35, -1e20, 2e20))
    galaxy.add_globular_cluster(GlobularCluster("Omega Centauri", 1_500_000, 4e36, 5e19, -2e19))
    galaxy.quasar = Quasar("Toy Quasar", 1e41, 1.2e9*1.989e30, 0.0, 0.0)
    galaxy.central_black_hole = BlackHole("SgrA*-Toy", 4e6*1.989e30, 0, 0)

    # Star system: Apply butterfly effect by adding tiny perturbations
    def pert(v, scale=1.0):
        if perturb:
            return v * (1 + random.uniform(-magnitude, magnitude)*scale) \
                + random.uniform(-magnitude, magnitude)*scale*v
        else:
            return v

    sun = Star("Sun-Toy", 1.989e30, pert(0.), pert(0.))
    ss = StarSystem("Solar-System-Toy", sun)

    AU = 1.496e11
    earth = Planet("Earth-Toy", 5.972e24,
                   pert(AU), pert(0.0, 0.05),   # x, y
                   0.0, pert(29_780, 0.01))    # vx, vy
    moon = Moon("Moon-Toy", 7.348e22,
                earth.x + pert(3.84e8, 0.2), earth.y,
                0.0, earth.vy + pert(1_022,0.05))
    earth.add_moon(moon)
    ss.add_planet(earth)

    mars = Planet("Mars-Toy", 6.39e23,
                  pert(2.279e11), pert(0.0, 0.05),
                  0.0, pert(24_077, 0.01))
    ss.add_planet(mars)

    ceres = Asteroid("Ceres-Toy", 9.4e20,
                     pert(4.14e11), pert(0.0, 0.05),
                     0.0, pert(17_882, 0.01))
    ss.add_asteroid(ceres)

    wd = WhiteDwarf("WD-Toy", 0.6*1.989e30,
                    pert(-5e11), pert(0.0,0.04), 0.0, pert(-15_000,0.01))
    ns = NeutronStar("NS-Toy", 1.4*1.989e30,
                     pert(6e11), pert(0.0,0.04), 0.0, pert(12_000,0.01))
    ss.add_stellar_remnant(wd)
    ss.add_stellar_remnant(ns)

    galaxy.add_star_system(ss)
    galaxy_cluster.add_galaxy(galaxy)
    supercluster.add_galaxy_cluster(galaxy_cluster)
    universe.add_supercluster(supercluster)
    return universe

# ========== MAIN LOOP (WITH CHAOS) ==========
def main():
    print("="*60)
    print("COSMIC BUTTERFLY EFFECT SANDBOX")
    print("="*60)
    # Use system time for non-repeatable results (chaos)
    seed = int(time.time()*1000000) % (2**32)
    random.seed(seed)
    print(f"Random seed: {seed}\n")

    # Build and run universe
    universe = build_demo_universe(perturb=True, magnitude=1)  # smaller magnitude shows subtler chaos!
    universe.run(steps=10, dt=86_400)

    # Reporting
    try:
        gal = universe.superclusters[0].galaxy_clusters[0].galaxies[0]
        ss = gal.star_systems[0]
    except Exception as e:
        print("Error: ", e)
        return

    print("\n" + "="*60)
    print("GALAXY FEATURES")
    print("="*60)
    if gal.central_black_hole:
        print(f"Central Black Hole: {gal.central_black_hole.name}, mass = {gal.central_black_hole.mass:.2e} kg")
    print(f"Quasar: {gal.quasar.name}, luminosity = {gal.quasar.luminosity:.2e} W\n")
    print(f"Nebulae ({len(gal.nebulae)}): " +
          ", ".join([n.name for n in gal.nebulae]))
    print(f"Globular Clusters ({len(gal.globular_clusters)}): " +
          ", ".join([c.name for c in gal.globular_clusters]))

    AU = 1.496e11
    print("\nSolar System Final Positions (AU):")
    print(f"Primary: {ss.primary.name}, x={ss.primary.x/AU:.6f}, y={ss.primary.y/AU:.6f}")
    print("Planets:")
    for planet in ss.planets:
        print(f"  • {planet.name:10s} x={planet.x/AU:+.6f}, y={planet.y/AU:+.6f}")
        for moon in planet.moons:
            print(f"    └─ {moon.name:10s} x={moon.x/AU:+.6f}, y={moon.y/AU:+.6f}")
    print("Asteroids:")
    for asteroid in ss.asteroids:
        print(f"  • {asteroid.name:10s} x={asteroid.x/AU:+.6f}, y={asteroid.y/AU:+.6f}")
    print("Stellar Remnants:")
    for rem in ss.stellar_remnants:
        print(f"  • {rem.name:10s} x={rem.x/AU:+.6f}, y={rem.y/AU:+.6f}")

    print("="*60)
    print("SIMULATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()