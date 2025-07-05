# Tutorial 1: Understanding Swarm Behaviors

## Introduction

Welcome to SwarmSim-Py! This tutorial will introduce you to the fundamental concepts of swarm robotics and how they're implemented in our simulator.

## What is Swarm Robotics?

Swarm robotics studies how large numbers of relatively simple robots can work together to accomplish complex tasks through local interactions. Key principles include:

- **Decentralization**: No single robot controls the swarm
- **Local Sensing**: Robots only know about their immediate neighbors
- **Emergence**: Complex behaviors arise from simple rules
- **Robustness**: The swarm continues functioning even if individuals fail

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/techieakr/swarmsim-py.git
cd swarmsim-py

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Running Your First Simulation

```python
from swarmsim import Robot, Simulation

# Create a simulation
sim = Simulation()

# Add a single robot
robot = Robot(x=400, y=300)
sim.add_robot(robot)

# Run the simulation
sim.run()
```

## Understanding Robot Sensors

Each robot in SwarmSim-Py has distance sensors arranged in a fan pattern:

```
        Front
          |
    -45° -|- +45°
      \  |  /
       \ | /
        \|/
      Robot
```

### Sensor Readings

```python
# Access sensor data
for i, distance in enumerate(robot.sensor_readings):
    angle = robot.sensor_angles[i]
    print(f"Sensor at {angle}°: {distance} units")
```

### Sensor Visualization

- **Green**: No obstacles detected (far)
- **Yellow**: Obstacle at medium distance
- **Red**: Obstacle very close

## Basic Behaviors

### 1. Collision Avoidance

The simplest behavior - avoid hitting walls and obstacles:

```python
def collision_avoidance(self):
    # Check front sensors
    front_sensors = self.sensor_readings[2:5]
    
    if min(front_sensors) < 40:  # Obstacle detected
        # Compare left vs right
        left_avg = sum(self.sensor_readings[:3]) / 3
        right_avg = sum(self.sensor_readings[4:]) / 3
        
        # Turn away from obstacles
        if left_avg < right_avg:
            self.angle += 0.1  # Turn right
        else:
            self.angle -= 0.1  # Turn left
```

**Key Concepts**:
- Reactive control
- No memory needed
- Simple but effective

### 2. Wall Following

More complex behavior using states:

```python
class WallFollower:
    def __init__(self):
        self.state = "searching"  # or "following"
        self.desired_distance = 40
    
    def update(self):
        if self.state == "searching":
            # Look for walls
            if min(self.sensor_readings) < 50:
                self.state = "following"
        else:
            # Maintain distance from wall
            self.follow_wall()
```

**Key Concepts**:
- Finite State Machine (FSM)
- Behavioral persistence
- Goal-oriented movement

### 3. Area Coverage

Systematic exploration for tasks like cleaning or mapping:

```python
def vacuum_behavior(self):
    # Spiral pattern with randomization
    self.angle += 0.02  # Base spiral
    
    # Add randomness to avoid getting stuck
    if random.random() < 0.05:
        self.angle += random.uniform(-π/4, π/4)
    
    # Record covered area
    self.trail.append((self.x, self.y))
```

**Key Concepts**:
- Coverage algorithms
- Path planning
- Exploration vs exploitation

## Exercises

### Exercise 1: Custom Obstacle Avoidance
Modify the collision avoidance behavior to:
- Move faster when path is clear
- Slow down near obstacles
- Prefer turning right

### Exercise 2: Improved Wall Following
Enhance the wall follower to:
- Handle corners better
- Follow on left side instead of right
- Maintain smoother distance

### Exercise 3: Coverage Metrics
Add metrics to measure:
- Percentage of area covered
- Time to reach 90% coverage
- Overlap/efficiency

## Common Pitfalls

1. **Oscillation**: Robot gets stuck switching between two states
   - Solution: Add hysteresis or momentum

2. **Local Minima**: Robot gets trapped in corners
   - Solution: Add random exploration or memory

3. **Sensor Noise**: Real sensors are imperfect
   - Solution: Filter readings or use probabilistic approaches

## Next Steps

In [Tutorial 2](tutorial_02_custom.md), we'll learn how to:
- Create custom robot behaviors
- Implement communication between robots
- Design emergent swarm behaviors

## Further Reading

- Brambilla, M., et al. (2013). "Swarm robotics: a review from the swarm engineering perspective"
- Şahin, E. (2005). "Swarm robotics: From sources of inspiration to domains of application"
- Reynolds, C. W. (1987). "Flocks, herds and schools: A distributed behavioral model"