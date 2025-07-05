# Tutorial 3: Analyzing Emergent Properties

## Introduction

Understanding emergent properties is crucial in swarm robotics. This tutorial teaches you how to measure, analyze, and optimize swarm behaviors using scientific methods.

## What Are Emergent Properties?

Emergent properties are characteristics that arise from collective interactions but aren't present in individual robots:

- **Flocking**: Birds form cohesive groups without central coordination
- **Ant Trails**: Optimal paths emerge from pheromone deposits
- **Aggregation**: Robots cluster without explicit clustering commands

## Setting Up Analysis Tools

### Required Libraries

```python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial import distance_matrix
from scipy.stats import entropy
import seaborn as sns
```

### Data Collection Framework

```python
class SwarmAnalyzer:
    def __init__(self, simulation):
        self.sim = simulation
        self.data = {
            'positions': [],
            'velocities': [],
            'states': [],
            'clusters': [],
            'timestamps': []
        }
        
    def collect_data(self):
        """Collect data at each timestep"""
        snapshot = {
            'time': self.sim.current_time,
            'positions': [(r.x, r.y) for r in self.sim.robots],
            'velocities': [(r.vx, r.vy) for r in self.sim.robots],
            'states': [r.state for r in self.sim.robots],
        }
        
        for key, value in snapshot.items():
            self.data[key].append(value)
```

## Key Metrics for Swarm Analysis

### 1. Spatial Metrics

#### Cluster Analysis

```python
def analyze_clusters(positions, eps=50):
    """Identify and analyze robot clusters"""
    from sklearn.cluster import DBSCAN
    
    # Cluster detection
    clustering = DBSCAN(eps=eps, min_samples=2)
    labels = clustering.fit_predict(positions)
    
    # Calculate metrics
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    # Cluster sizes
    cluster_sizes = []
    for label in set(labels):
        if label != -1:
            size = list(labels).count(label)
            cluster_sizes.append(size)
    
    return {
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'cluster_sizes': cluster_sizes,
        'largest_cluster': max(cluster_sizes) if cluster_sizes else 0,
        'clustering_coefficient': 1 - (n_noise / len(positions))
    }
```

#### Dispersion Metrics

```python
def calculate_dispersion(positions):
    """Measure how spread out robots are"""
    positions = np.array(positions)
    
    # Center of mass
    center = np.mean(positions, axis=0)
    
    # Average distance from center
    distances = np.linalg.norm(positions - center, axis=1)
    avg_distance = np.mean(distances)
    std_distance = np.std(distances)
    
    # Convex hull area (requires scipy)
    from scipy.spatial import ConvexHull
    if len(positions) >= 3:
        hull = ConvexHull(positions)
        area = hull.volume  # In 2D, volume is area
    else:
        area = 0
    
    return {
        'center_of_mass': center,
        'avg_distance_from_center': avg_distance,
        'std_distance': std_distance,
        'convex_hull_area': area,
        'density': len(positions) / area if area > 0 else 0
    }
```

### 2. Movement Metrics

#### Velocity Alignment

```python
def calculate_alignment(velocities):
    """Measure how aligned robot movements are"""
    velocities = np.array(velocities)
    
    # Normalize velocities
    speeds = np.linalg.norm(velocities, axis=1)
    
    # Filter out stationary robots
    moving = speeds > 0.1
    if np.sum(moving) < 2:
        return 0
    
    moving_vels = velocities[moving]
    moving_speeds = speeds[moving]
    
    # Normalized velocities (directions)
    directions = moving_vels / moving_speeds[:, np.newaxis]
    
    # Average direction
    avg_direction = np.mean(directions, axis=0)
    
    # Alignment measure (1 = perfect alignment, 0 = random)
    alignment = np.linalg.norm(avg_direction)
    
    return alignment
```

#### Order Parameter

```python
def calculate_order_parameter(robots):
    """Global order parameter (0=disorder, 1=order)"""
    if len(robots) == 0:
        return 0
        
    # Sum of normalized velocities
    total_velocity = np.zeros(2)
    count = 0
    
    for robot in robots:
        speed = math.sqrt(robot.vx**2 + robot.vy**2)
        if speed > 0:
            total_velocity[0] += robot.vx / speed
            total_velocity[1] += robot.vy / speed
            count += 1
    
    if count == 0:
        return 0
        
    return np.linalg.norm(total_velocity) / count
```

### 3. Communication Metrics

#### Information Flow

```python
def analyze_information_flow(communication_log):
    """Analyze how information spreads"""
    # Build communication graph
    import networkx as nx
    
    G = nx.DiGraph()
    
    for message in communication_log:
        G.add_edge(message['sender'], message['receiver'], 
                  time=message['timestamp'])
    
    # Calculate metrics
    metrics = {
        'avg_degree': np.mean([G.degree(n) for n in G.nodes()]),
        'clustering_coeff': nx.average_clustering(G.to_undirected()),
        'connected_components': nx.number_weakly_connected_components(G),
        'diameter': nx.diameter(G) if nx.is_connected(G.to_undirected()) else -1
    }
    
    return metrics
```

### 4. Task Performance Metrics

#### Coverage Efficiency

```python
def calculate_coverage(trail_points, arena_size, cell_size=10):
    """Measure area coverage efficiency"""
    # Discretize arena into cells
    n_cells_x = arena_size[0] // cell_size
    n_cells_y = arena_size[1] // cell_size
    
    visited = set()
    
    for point in trail_points:
        cell_x = int(point[0] // cell_size)
        cell_y = int(point[1] // cell_size)
        visited.add((cell_x, cell_y))
    
    total_cells = n_cells_x * n_cells_y
    coverage_ratio = len(visited) / total_cells
    
    return {
        'coverage_ratio': coverage_ratio,
        'cells_visited': len(visited),
        'total_cells': total_cells
    }
```

## Visualization Techniques

### 1. Time Series Plots

```python
def plot_swarm_metrics(analyzer):
    """Plot metrics over time"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Extract time series data
    times = analyzer.data['timestamps']
    
    # Plot 1: Number of clusters
    cluster_counts = []
    for positions in analyzer.data['positions']:
        clusters = analyze_clusters(positions)
        cluster_counts.append(clusters['n_clusters'])
    
    axes[0, 0].plot(times, cluster_counts)
    axes[0, 0].set_title('Number of Clusters')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Clusters')
    
    # Plot 2: Average dispersion
    dispersions = []
    for positions in analyzer.data['positions']:
        disp = calculate_dispersion(positions)
        dispersions.append(disp['avg_distance_from_center'])
    
    axes[0, 1].plot(times, dispersions)
    axes[0, 1].set_title('Swarm Dispersion')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Avg Distance from Center')
    
    # Plot 3: Velocity alignment
    alignments = []
    for velocities in analyzer.data['velocities']:
        align = calculate_alignment(velocities)
        alignments.append(align)
    
    axes[1, 0].plot(times, alignments)
    axes[1, 0].set_title('Velocity Alignment')
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('Alignment (0-1)')
    
    # Plot 4: State distribution
    state_counts = pd.DataFrame(analyzer.data['states']).apply(pd.Series.value_counts)
    state_counts.T.plot(ax=axes[1, 1], kind='area', stacked=True)
    axes[1, 1].set_title('Robot State Distribution')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Number of Robots')
    
    plt.tight_layout()
    plt.show()
```

### 2. Spatial Visualizations

```python
def create_heatmap(positions_over_time, arena_size, bins=20):
    """Create movement heatmap"""
    all_positions = []
    for positions in positions_over_time:
        all_positions.extend(positions)
    
    x_coords = [p[0] for p in all_positions]
    y_coords = [p[1] for p in all_positions]
    
    plt.figure(figsize=(10, 8))
    plt.hist2d(x_coords, y_coords, bins=bins, cmap='hot')
    plt.colorbar(label='Robot Visits')
    plt.title('Robot Movement Heatmap')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.xlim(0, arena_size[0])
    plt.ylim(0, arena_size[1])
    plt.show()
```

### 3. Network Visualizations

```python
def visualize_robot_network(robots, communication_range=100):
    """Visualize communication network"""
    import networkx as nx
    
    # Build network
    G = nx.Graph()
    positions = {}
    
    for i, robot in enumerate(robots):
        G.add_node(i)
        positions[i] = (robot.x, robot.y)
    
    # Add edges for robots in communication range
    for i in range(len(robots)):
        for j in range(i+1, len(robots)):
            dist = np.linalg.norm(
                np.array(positions[i]) - np.array(positions[j])
            )
            if dist <= communication_range:
                G.add_edge(i, j, weight=1/dist)
    
    # Draw network
    plt.figure(figsize=(10, 8))
    nx.draw(G, positions, 
            node_color='lightblue',
            node_size=100,
            edge_color='gray',
            width=[G[u][v]['weight'] for u, v in G.edges()],
            alpha=0.7)
    plt.title('Robot Communication Network')
    plt.axis('equal')
    plt.show()
```

## Parameter Optimization

### Grid Search

```python
def parameter_sweep(param_ranges, metric_function, n_trials=5):
    """Systematic parameter exploration"""
    from itertools import product
    
    results = []
    
    # Generate all parameter combinations
    param_names = list(param_ranges.keys())
    param_values = [param_ranges[name] for name in param_names]
    
    for values in product(*param_values):
        params = dict(zip(param_names, values))
        
        # Run multiple trials
        trial_results = []
        for trial in range(n_trials):
            result = run_simulation_with_params(params)
            metric = metric_function(result)
            trial_results.append(metric)
        
        # Store results
        results.append({
            **params,
            'metric_mean': np.mean(trial_results),
            'metric_std': np.std(trial_results),
            'trials': trial_results
        })
    
    return pd.DataFrame(results)

# Example usage
param_ranges = {
    'num_robots': [10, 20, 30],
    'sensor_range': [40, 60, 80],
    'wait_time': [60, 120, 180]
}

results = parameter_sweep(
    param_ranges,
    lambda sim: sim.get_final_cluster_count(),
    n_trials=10
)