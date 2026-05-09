import numpy as np
import matplotlib.pyplot as plt

def generate_torus_xor(grid_size=64, R=10, r=4):
    """
    R = distance from the center of the tube to the center of the torus
    r = radius of the tube
    """
    # 1. Generate the XOR Transversal Grid
    x_indices = np.arange(grid_size)
    y_indices = np.arange(grid_size)
    xor_matrix = np.bitwise_xor.outer(x_indices, y_indices)

    # 2. Generate Probability Data Set (Normalized 0 to 1)
    # This represents the stacking of values scaled to a probability density
    prob_data = xor_matrix / xor_matrix.max()

    # 3. Define the Parametric Space (U and V)
    u = np.linspace(0, 2 * np.pi, grid_size)
    v = np.linspace(0, 2 * np.pi, grid_size)
    U, V = np.meshgrid(u, v)

    # 4. Apply the XOR Stacking to the Torus Geometry
    # We use the XOR probability data to perturb the tube radius 'r'
    # This effectively 'stacks' the logic onto the physical structure
    displacement = prob_data * 2  # Scaling the XOR effect
    
    X = (R + (r + displacement) * np.cos(V)) * np.cos(U)
    Y = (R + (r + displacement) * np.cos(V)) * np.sin(U)
    Z = (r + displacement) * np.sin(V)

    return X, Y, Z, prob_data

# Execution
grid_res = 128
X, Y, Z, probabilities = generate_torus_xor(grid_size=grid_res)

# --- Visualization ---
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Map the XOR probabilities to the surface color (C)
surface = ax.plot_surface(X, Y, Z, facecolors=plt.cm.magma(probabilities), 
                          shade=False, antialiased=True)

ax.set_title(f"XOR Transversal Torus ({grid_res}x{grid_res} Stack)")
ax.view_init(elev=30, azim=45)
plt.axis('off')
plt.show()

# Output the first 5x5 slice of the probability dataset
print("Sample Probability Data Set (XOR Transversal):")
print(probabilities[:5, :5])