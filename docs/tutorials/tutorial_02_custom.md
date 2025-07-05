# Tutorial 2: Implementing Custom Behaviors

## Introduction

Now that you understand basic behaviors, let's create custom behaviors and explore swarm intelligence. We'll build from simple individual behaviors to complex collective behaviors.

## Architecture Overview

```python
# Basic behavior structure
class CustomBehavior:
    def __init__(self, robot):
        self.robot = robot
        self.state = "idle"
        
    def update(self):
        # Sense
        self.sense_environment()
        
        # Think
        action = self.decide_action()
        
        # Act
        self.execute_action(action)
```

## Creating Your First Custom Behavior

### Step 1: Define the Behavior Class

```python
from swarmsim.core import Behavior
import math

class PhotoTaxisBehavior(Behavior):
    """Move toward light sources"""
    
    def __init__(self, robot):
        super().__init__(robot)
        self.light_source = (500, 400)  # Target position
        
    def update(self):
        # Calculate direction to light
        dx = self.light_source[0] - self.robot.x
        dy = self.light_source[1] - self.robot.y
        
        # Calculate angle to light
        target_angle = math.atan2(dy, dx)
        
        # Smooth turning toward light
        angle_diff = target_angle - self.robot.angle
        self.robot.angle += 0.1 * angle_diff
        
        # Move forward
        self.robot.move_forward()
```

### Step 2: Integrate with Robot

```python
# Add behavior to robot
robot = Robot(x=100, y=100)
robot.behavior = PhotoTaxisBehavior(robot)

# In simulation loop
robot.behavior.update()
```

## Advanced Individual Behaviors

### 1. Obstacle-Aware Navigation

```python
class SmartNavigator(Behavior):
    def __init__(self, robot, target):
        super().__init__(robot)
        self.target = target
        self.obstacle_memory = []
        
    def update(self):
        # Check for obstacles
        if self.detect_obstacle():
            self.avoid_obstacle()
        else:
            self.move_to_target()
    
    def detect_obstacle(self):
        return min(self.robot.sensor_readings) < 30
    
    def avoid_obstacle(self):
        # Remember obstacle position
        self.obstacle_memory.append({
            'position': (self.robot.x, self.robot.y),
            'time': self.robot.sim_time
        })
        
        # Use tangent bug algorithm
        self.follow_obstacle_boundary()
```

### 2. Energy-Aware Behavior

```python
class EnergyAwareBehavior(Behavior):
    def __init__(self, robot):
        super().__init__(robot)
        self.energy = 100.0
        self.charging_stations = [(100, 100), (700, 500)]
        
    def update(self):
        # Consume energy when moving
        if self.robot.speed > 0:
            self.energy -= 0.1
        
        # Switch behavior based on energy
        if self.energy < 20:
            self.seek_charging_station()
        else:
            self.perform_task()
    
    def seek_charging_station(self):
        # Find nearest station
        nearest = self.find_nearest(self.charging_stations)
        self.move_toward(nearest)
        
        # Charge if at station
        if self.distance_to(nearest) < 20:
            self.energy = min(100, self.energy + 1)
```

## Swarm Behaviors

### 1. Flocking Behavior

Implement Reynolds' three rules:

```python
class FlockingBehavior(Behavior):
    def __init__(self, robot):
        super().__init__(robot)
        self.separation_radius = 30
        self.alignment_radius = 50
        self.cohesion_radius = 50
        
    def update(self):
        neighbors = self.robot.sense_neighbors()
        
        # Calculate three components
        separation = self.calculate_separation(neighbors)
        alignment = self.calculate_alignment(neighbors)
        cohesion = self.calculate_cohesion(neighbors)
        
        # Weighted sum
        force = (
            separation * 1.5 +
            alignment * 1.0 +
            cohesion * 1.0
        )
        
        # Apply force to robot
        self.robot.apply_force(force)
    
    def calculate_separation(self, neighbors):
        """Avoid crowding neighbors"""
        force = Vector(0, 0)
        close_neighbors = [n for n in neighbors 
                          if n.distance < self.separation_radius]
        
        for neighbor in close_neighbors:
            # Push away from neighbor
            diff = self.robot.position - neighbor.position
            diff.normalize()
            diff /= neighbor.distance  # Stronger when closer
            force += diff
            
        return force
    
    def calculate_alignment(self, neighbors):
        """Align with neighbors' heading"""
        if not neighbors:
            return Vector(0, 0)
            
        # Average heading of neighbors
        avg_heading = Vector(0, 0)
        for n in neighbors:
            avg_heading += n.velocity
            
        avg_heading /= len(neighbors)
        return avg_heading - self.robot.velocity
    
    def calculate_cohesion(self, neighbors):
        """Move toward group center"""
        if not neighbors:
            return Vector(0, 0)
            
        # Average position of neighbors
        center = Vector(0, 0)
        for n in neighbors:
            center += n.position
            
        center /= len(neighbors)
        return center - self.robot.position
```

### 2. Formation Control

Create geometric patterns:

```python
class FormationBehavior(Behavior):
    def __init__(self, robot, formation_type="line"):
        super().__init__(robot)
        self.formation_type = formation_type
        self.assigned_position = None
        
    def update(self):
        if self.assigned_position is None:
            self.calculate_formation_position()
            
        # Move to assigned position
        error = self.assigned_position - self.robot.position
        
        if error.magnitude() > 5:
            self.robot.move_toward(self.assigned_position)
        else:
            self.maintain_formation()
    
    def calculate_formation_position(self):
        """Assign positions based on robot ID"""
        if self.formation_type == "line":
            spacing = 40
            self.assigned_position = Vector(
                100 + self.robot.id * spacing,
                300
            )
        elif self.formation_type == "circle":
            angle = (2 * math.pi * self.robot.id) / self.robot.swarm_size
            radius = 100
            self.assigned_position = Vector(
                400 + radius * math.cos(angle),
                300 + radius * math.sin(angle)
            )
```

### 3. Task Allocation

Distributed task assignment:

```python
class TaskAllocationBehavior(Behavior):
    def __init__(self, robot):
        super().__init__(robot)
        self.current_task = None
        self.task_bids = {}
        
    def update(self):
        if self.current_task is None:
            self.bid_on_tasks()
        else:
            self.execute_task()
    
    def bid_on_tasks(self):
        """Market-based task allocation"""
        available_tasks = self.sense_tasks()
        
        for task in available_tasks:
            # Calculate bid based on distance and capability
            distance = self.distance_to(task.position)
            capability = self.evaluate_capability(task.type)
            
            bid = capability / (distance + 1)
            self.broadcast_bid(task.id, bid)
        
        # Wait for auction results
        if self.auction_complete():
            self.current_task = self.get_won_task()
```

## Communication Patterns

### 1. Local Broadcasting

```python
class Broadcaster:
    def __init__(self, robot, range=100):
        self.robot = robot
        self.range = range
        self.messages = []
        
    def broadcast(self, message):
        """Send message to nearby robots"""
        self.messages.append({
            'sender': self.robot.id,
            'position': (self.robot.x, self.robot.y),
            'data': message,
            'timestamp': time.time()
        })
    
    def receive_messages(self, all_messages):
        """Filter messages within range"""
        received = []
        for msg in all_messages:
            distance = self.distance_to(msg['position'])
            if distance <= self.range and msg['sender'] != self.robot.id:
                received.append(msg)
        return received
```

### 2. Stigmergic Communication

```python
class PheromoneSystem:
    def __init__(self, width, height, evaporation_rate=0.99):
        self.pheromone_map = np.zeros((width, height))
        self.evaporation_rate = evaporation_rate
        
    def deposit(self, x, y, intensity=1.0):
        """Robot deposits pheromone"""
        self.pheromone_map[int(x), int(y)] += intensity
        
    def sense(self, x, y, radius=20):
        """Robot senses local pheromone concentration"""
        x1 = max(0, int(x - radius))
        x2 = min(self.width, int(x + radius))
        y1 = max(0, int(y - radius))
        y2 = min(self.height, int(y + radius))
        
        return np.mean(self.pheromone_map[x1:x2, y1:y2])
    
    def update(self):
        """Evaporate pheromones"""
        self.pheromone_map *= self.evaporation_rate
```

## Testing Your Behaviors

### Unit Testing

```python
import unittest

class TestFlockingBehavior(unittest.TestCase):
    def setUp(self):
        self.robot = Robot(x=100, y=100)
        self.behavior = FlockingBehavior(self.robot)
        
    def test_separation(self):
        # Add close neighbor
        neighbor = Robot(x=110, y=100)
        neighbors = [{'robot': neighbor, 'distance': 10}]
        
        force = self.behavior.calculate_separation(neighbors)
        
        # Should push away (negative x direction)
        self.assertLess(force.x, 0)
        
    def test_cohesion(self):
        # Add distant neighbors
        neighbors = [
            {'robot': Robot(x=200, y=100), 'distance': 100},
            {'robot': Robot(x=300, y=100), 'distance': 200}
        ]
        
        force = self.behavior.calculate_cohesion(neighbors)
        
        # Should attract (positive x direction)
        self.assertGreater(force.x, 0)
```

### Behavior Validation

```python
def validate_behavior(behavior_class, num_robots=10, steps=1000):
    """Test behavior in simulation"""
    sim = Simulation()
    
    # Add robots with behavior
    for i in range(num_robots):
        robot = Robot(
            x=random.randint(50, 750),
            y=random.randint(50, 550)
        )
        robot.behavior = behavior_class(robot)
        sim.add_robot(robot)
    
    # Run and collect metrics
    metrics = []
    for step in range(steps):
        sim.update()
        metrics.append(sim.calculate_metrics())
    
    return analyze_metrics(metrics)
```

## Best Practices

1. **Modular Design**: Keep behaviors independent and reusable
2. **Parameter Tuning**: Make key values configurable
3. **Graceful Degradation**: Handle edge cases and failures
4. **Documentation**: Comment complex algorithms
5. **Testing**: Validate behaviors in isolation and together

## Exercises

### Exercise 1: Predator-Prey
Implement two behaviors:
- Predators that chase prey
- Prey that flee from predators

### Exercise 2: Resource Collection
Create a foraging behavior where robots:
- Search for resources
- Collect and return to base
- Communicate resource locations

### Exercise 3: Pattern Formation
Design a behavior that makes robots form:
- Letters or numbers
- Dynamic patterns that change over time
- Patterns that adapt to robot failures

## Next Steps

In [Tutorial 3](tutorial_03_analysis.md), we'll learn to:
- Analyze emergent behaviors
- Measure swarm performance
- Optimize parameters
- Visualize swarm dynamics

## Resources

- [Behavior Trees](https://robotics.stackexchange.com/questions/7226/behavior-trees-vs-finite-state-machines)
- [Bio-inspired Algorithms](https://www.sciencedirect.com/topics/computer-science/bio-inspired-algorithm)
- [Multi-Robot Systems](http://www.cs.cmu.edu/~motionplanning/lecture/lecture24.pdf)