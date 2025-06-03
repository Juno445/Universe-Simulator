import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# GPU acceleration imports
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("GPU acceleration available with CuPy")
except ImportError:
    import numpy as cp
    GPU_AVAILABLE = False
    print("CuPy not found, falling back to CPU")

class GPUSolarSystem:
    def __init__(self, use_gpu=True):
        self.use_gpu = use_gpu and GPU_AVAILABLE
        self.xp = cp if self.use_gpu else np

        # Planet data with real orbital parameters
        self.planet_data = {
            "Mercury": [0.383, 0.39, 0.24, 7.0, 0.206, 77.5, [0.5, 0.5, 0.5]],
            "Venus": [0.949, 0.72, 0.62, 3.4, 0.007, 131.5, [1.0, 0.6, 0.0]],
            "Earth": [1.0, 1.0, 1.0, 0.0, 0.017, 102.9, [0.0, 0.5, 1.0]],
            "Mars": [0.532, 1.52, 1.88, 1.8, 0.093, 336.0, [1.0, 0.0, 0.0]],
            "Jupiter": [11.21, 5.2, 11.86, 1.3, 0.048, 14.8, [1.0, 0.6, 0.0]],
            "Saturn": [9.45, 9.58, 29.46, 2.5, 0.056, 92.4, [1.0, 0.8, 0.0]],
            "Uranus": [4.01, 19.22, 84.01, 0.8, 0.046, 170.0, [0.0, 1.0, 1.0]],
            "Neptune": [3.88, 30.05, 164.8, 1.8, 0.010, 44.0, [0.0, 0.0, 1.0]]
        }

        # Convert to GPU arrays
        try:
            self.setup_gpu_arrays()
            print(f"Successfully initialized with {len(self.names)} planets using {'GPU' if self.use_gpu else 'CPU'}")
        except Exception as e:
            print(f"Error setting up arrays: {e}")
            print("Falling back to CPU...")
            self.use_gpu = False
            self.xp = np
            self.setup_gpu_arrays()

    def setup_gpu_arrays(self):
        """Convert planet data to GPU arrays for parallel processing"""
        try:
            n_planets = len(self.planet_data)

            # Create structured arrays for all planet parameters
            # Convert lists to arrays BEFORE passing to CuPy/NumPy functions
            self.radii = self.xp.array([data[0] for data in self.planet_data.values()])
            self.distances = self.xp.array([data[1] for data in self.planet_data.values()])
            self.periods = self.xp.array([data[2] for data in self.planet_data.values()])

            # Convert to array first, then apply radians
            inclinations_degrees = [data[3] for data in self.planet_data.values()]
            self.inclinations = self.xp.radians(self.xp.array(inclinations_degrees))

            self.eccentricities = self.xp.array([data[4] for data in self.planet_data.values()])

            # Convert to array first, then apply radians
            longitude_perihelia_degrees = [data[5] for data in self.planet_data.values()]
            self.longitude_perihelia = self.xp.radians(self.xp.array(longitude_perihelia_degrees))

            # Colors stay as NumPy arrays (for matplotlib compatibility)
            self.colors = np.array([data[6] for data in self.planet_data.values()])
            self.names = list(self.planet_data.keys())

            print(f"Arrays created successfully:")
            print(f"  - Radii shape: {self.radii.shape}")
            print(f"  - Distances shape: {self.distances.shape}")
            print(f"  - Using backend: {type(self.xp).__name__}")

        except Exception as e:
            print(f"Error in setup_gpu_arrays: {e}")
            raise

    def calculate_positions_gpu(self, time_array):
        """Calculate all planet positions in parallel on GPU"""
        try:
            # Ensure time_array is the right type
            if not isinstance(time_array, (type(self.xp.array([])), np.ndarray)):
                time_array = self.xp.array(time_array)

            # Broadcast time across all planets
            time_broadcast = self.xp.outer(time_array, self.xp.ones(len(self.names)))
            periods_broadcast = self.xp.outer(self.xp.ones(len(time_array)), self.periods)

            # Vectorized orbital calculations
            mean_motion = 2 * self.xp.pi / periods_broadcast
            mean_anomaly = mean_motion * time_broadcast

            # Solve Kepler's equation (vectorized)
            eccentricities_broadcast = self.xp.outer(self.xp.ones(len(time_array)), self.eccentricities)
            eccentric_anomaly = mean_anomaly + eccentricities_broadcast * self.xp.sin(mean_anomaly)

            # True anomaly calculation (vectorized)
            true_anomaly = 2 * self.xp.arctan2(
                self.xp.sqrt(1 + eccentricities_broadcast) * self.xp.sin(eccentric_anomaly / 2),
                self.xp.sqrt(1 - eccentricities_broadcast) * self.xp.cos(eccentric_anomaly / 2)
            )

            # Distance calculation (vectorized)
            distances_broadcast = self.xp.outer(self.xp.ones(len(time_array)), self.distances)
            distance = distances_broadcast * (1 - eccentricities_broadcast**2) / (
                1 + eccentricities_broadcast * self.xp.cos(true_anomaly)
            )

            # Position in orbital plane
            longitude_perihelia_broadcast = self.xp.outer(self.xp.ones(len(time_array)), self.longitude_perihelia)
            angle = true_anomaly + longitude_perihelia_broadcast
            x_orbital = distance * self.xp.cos(angle)
            y_orbital = distance * self.xp.sin(angle)

            # Apply orbital inclination
            inclinations_broadcast = self.xp.outer(self.xp.ones(len(time_array)), self.inclinations)
            x = x_orbital
            y = y_orbital * self.xp.cos(inclinations_broadcast)
            z = y_orbital * self.xp.sin(inclinations_broadcast)

            return x, y, z

        except Exception as e:
            print(f"Error in calculate_positions_gpu: {e}")
            raise

    def create_static_plot(self):
        """Create a static plot showing current positions and orbits"""
        try:
            fig = plt.figure(figsize=(15, 12))
            ax = fig.add_subplot(111, projection='3d')

            # Plot the Sun
            ax.scatter(0, 0, 0, color='yellow', s=500, label='Sun', edgecolors='orange', linewidth=2)

            # Plot orbits and planets
            for i, name in enumerate(self.names):
                # Create orbit path
                orbit_time = self.xp.linspace(0, float(self.periods[i]), 200)
                orbit_x, orbit_y, orbit_z = self.calculate_positions_gpu(orbit_time)

                # Convert to CPU if needed
                if self.use_gpu:
                    orbit_x = cp.asnumpy(orbit_x)
                    orbit_y = cp.asnumpy(orbit_y)
                    orbit_z = cp.asnumpy(orbit_z)

                # Plot orbit
                ax.plot(orbit_x[:, i], orbit_y[:, i], orbit_z[:, i],
                       color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

                # Plot current planet position (at time = 0)
                current_time = self.xp.array([0.0])
                x, y, z = self.calculate_positions_gpu(current_time)

                if self.use_gpu:
                    x, y, z = cp.asnumpy(x), cp.asnumpy(y), cp.asnumpy(z)

                size = max(20, min(200, 50 * float(self.radii[i])))
                ax.scatter(x[0, i], y[0, i], z[0, i], color=self.colors[i], s=size,
                          label=name, edgecolors='black', linewidth=0.5, alpha=0.8)

            # Customize the plot
            self.customize_plot(ax)

        except Exception as e:
            print(f"Error creating static plot: {e}")
            raise

    def customize_plot(self, ax):
        """Customize the 3D plot with labels, title, and legend"""
        try:
            ax.set_xlabel('X (AU)', fontsize=12)
            ax.set_ylabel('Y (AU)', fontsize=12)
            ax.set_zlabel('Z (AU)', fontsize=12)
            ax.set_title('Solar System - GPU Accelerated\n(Including Eccentricity and Inclination)', fontsize=14)

            # Set equal aspect ratio and limits
            max_dist = float(self.xp.max(self.distances))
            ax.set_xlim([-max_dist*1.1, max_dist*1.1])
            ax.set_ylim([-max_dist*1.1, max_dist*1.1])
            ax.set_zlim([-max_dist*0.2, max_dist*0.2])

            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error customizing plot: {e}")
            raise

class HighPerformanceMatplotlib:
    def __init__(self, solar_system):
        self.solar_system = solar_system

    def create_optimized_animation(self, duration=50, speed_multiplier=10, trail_length=100):
        """High-performance matplotlib animation with GPU calculations"""
        try:
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')

            # Pre-calculate many time steps on GPU
            time_steps = self.solar_system.xp.linspace(0, duration, duration * 10)
            all_positions_x, all_positions_y, all_positions_z = self.solar_system.calculate_positions_gpu(time_steps)

            # Convert to CPU if using GPU
            if self.solar_system.use_gpu:
                all_positions_x = cp.asnumpy(all_positions_x)
                all_positions_y = cp.asnumpy(all_positions_y)
                all_positions_z = cp.asnumpy(all_positions_z)

            # Set up plot
            ax.set_xlabel('X (AU)')
            ax.set_ylabel('Y (AU)')
            ax.set_zlabel('Z (AU)')
            ax.set_title(f'GPU-Accelerated Solar System Animation\nUsing: {"GPU (CuPy)" if self.solar_system.use_gpu else "CPU (NumPy)"}')

            max_dist = float(self.solar_system.xp.max(self.solar_system.distances))
            ax.set_xlim([-max_dist*1.1, max_dist*1.1])
            ax.set_ylim([-max_dist*1.1, max_dist*1.1])
            ax.set_zlim([-max_dist*0.2, max_dist*0.2])

            # Plot sun
            ax.scatter(0, 0, 0, color='yellow', s=300, label='Sun')

            # Initialize planet points
            planet_scatters = []
            trail_lines = []

            for i, name in enumerate(self.solar_system.names):
                size = max(10, min(100, 30 * float(self.solar_system.radii[i])))
                scatter = ax.scatter([], [], [], color=self.solar_system.colors[i], s=size, label=name)
                planet_scatters.append(scatter)
                trail_lines.append([[], [], []])

            def animate(frame):
                if frame >= len(time_steps):
                    return planet_scatters

                for i, scatter in enumerate(planet_scatters):
                    x, y, z = all_positions_x[frame, i], all_positions_y[frame, i], all_positions_z[frame, i]
                    scatter._offsets3d = ([x], [y], [z])

                    # Update trails
                    trail_lines[i][0].append(x)
                    trail_lines[i][1].append(y)
                    trail_lines[i][2].append(z)

                    # Keep trail length manageable
                    if len(trail_lines[i][0]) > trail_length:
                        trail_lines[i][0].pop(0)
                        trail_lines[i][1].pop(0)
                        trail_lines[i][2].pop(0)

                    # Draw trail
                    if len(trail_lines[i][0]) > 1:
                        ax.plot(trail_lines[i][0], trail_lines[i][1], trail_lines[i][2],
                               color=self.solar_system.colors[i], alpha=0.3, linewidth=1)

                return planet_scatters

            anim = animation.FuncAnimation(fig, animate, frames=len(time_steps),
                                         interval=50, blit=False, repeat=True)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.show()
            return anim

        except Exception as e:
            print(f"Error creating animation: {e}")
            raise

# Main execution
def main():
    try:
        print("Initializing GPU-accelerated Solar System...")

        # Create solar system with GPU acceleration
        solar_system = GPUSolarSystem(use_gpu=True)

        print(f"\nSuccessfully created solar system with {len(solar_system.names)} planets")

        # Create static plot first
        print("Creating static visualization...")
        solar_system.create_static_plot()

        # Create animation
        print("Creating animation...")
        matplotlib_system = HighPerformanceMatplotlib(solar_system)
        anim = matplotlib_system.create_optimized_animation(duration=30, speed_multiplier=20)

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()