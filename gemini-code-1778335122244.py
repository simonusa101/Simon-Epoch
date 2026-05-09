import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class TorusLogicEngine:
    def __init__(self, resolution=128, major_radius=10, minor_radius=4):
        self.res = resolution
        self.R = major_radius
        self.r = minor_radius
        self.xor_matrix = None
        self.prob_data = None

    def generate_xor_transversal(self):
        """Generates the bitwise XOR transversal and normalizes it."""
        x = np.arange(self.res)
        y = np.arange(self.res)
        # Transversal logic: XOR outer product
        self.xor_matrix = np.bitwise_xor.outer(x, y)
        # Normalize to probability dataset (0.0 to 1.0)
        self.prob_data = self.xor_matrix / self.xor_matrix.max()
        return self.prob_data

    def generate_geometry(self, displacement_factor=1.5):
        """Maps the XOR stack onto a toroidal coordinate system."""
        if self.prob_data is None:
            self.generate_xor_transversal()

        # Parametric mesh
        u = np.linspace(0, 2 * np.pi, self.res)
        v = np.linspace(0, 2 * np.pi, self.res)
        U, V = np.meshgrid(u, v)

        # Stacking logic: XOR data influences the minor radius (tube thickness)
        # This creates the physical 'texture' of the logic on the torus
        stacking_effect = self.prob_data * displacement_factor
        
        X = (self.R + (self.r + stacking_effect) * np.cos(V)) * np.cos(U)
        Y = (self.R + (self.r + stacking_effect) * np.cos(V)) * np.sin(U)
        Z = (self.r + stacking_effect) * np.sin(V)
        
        return X, Y, Z

    def export_data(self, filename="xor_probability_set.csv"):
        """Exports the raw probability data for replication."""
        df = pd.DataFrame(self.prob_data)
        df.to_csv(filename, index=False)
        print(f"Dataset exported to {filename}")

def visualize_results(X, Y, Z, colors):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Use the probability data to define the surface color (Magma/Plasma maps)
    surf = ax.plot_surface(X, Y, Z, facecolors=plt.cm.magma(colors), 
                           shade=False, antialiased=True)
    
    ax.set_title("XOR Transversal Stacking on Torus Structure")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    # Initialize and run
    engine = TorusLogicEngine(resolution=256)
    probs = engine.generate_xor_transversal()
    X, Y, Z = engine.generate_geometry()
    
    # Save for GitHub replication
    engine.export_data()
    
    # Show visual result
    visualize_results(X, Y, Z, probs)