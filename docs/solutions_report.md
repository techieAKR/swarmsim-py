# Collective Robotics Tutorial 2 - Solutions Report

## Task 1: Single Robot Behaviors

### 1a) Collision Avoidance Behavior

**Implementation Strategy:**
The collision avoidance behavior uses a reactive approach with 7 distance sensors arranged in a fan pattern from -45° to +45°. The robot continuously:

1. **Senses** the environment using ray-casting to detect walls and obstacles
2. **Evaluates** the front three sensors to determine if obstacles are ahead
3. **Decides** turn direction based on comparing left vs right sensor averages
4. **Moves** forward with slight random wandering when path is clear

**Key Design Decisions:**
- Sensor threshold of 40 units triggers avoidance behavior
- Gradual turning (0.1 radians) prevents oscillation
- Random wandering (±0.02 radians) prevents getting stuck in loops

### 1b) Wall Follower Behavior

**Implementation Strategy:**
The wall follower implements a finite state machine with two states:

1. **Searching State**: Robot wanders randomly until detecting a wall within 50 units
2. **Following State**: Robot maintains constant distance (40 units) from wall on right side

**Control Algorithm:**
```
IF front_distance < 30:
    turn_left()  # Avoid hitting corner
ELIF right_distance > desired_distance + 10:
    turn_right()  # Get closer to wall
ELIF right_distance < desired_distance - 10:
    turn_left()  # Move away from wall
ELSE:
    move_forward()  # Maintain distance
```

**Challenges Solved:**
- Corner handling by prioritizing front sensor
- Smooth following without sliding against wall
- Robust to irregular wall shapes

### 1c) Vacuum Cleaner Behavior

**Implementation Strategy:**
The vacuum cleaner uses a hybrid approach combining systematic coverage with randomization:

1. **Spiral Pattern**: Base movement follows expanding spiral for systematic coverage
2. **Obstacle Handling**: 90° turns when hitting obstacles
3. **Randomization**: 5% chance of random direction change prevents predictable patterns
4. **Trail Visualization**: Shows covered area (last 500 positions)

**Coverage Strategy Analysis:**
- Spiral ensures central areas are covered first
- Randomization helps reach corners and edges
- Obstacle avoidance prevents getting stuck
- Visual trail helps identify missed spots

### 1d) Additional Behaviors Explored

During development, I experimented with:
- **Random Walk**: Pure random movement (inefficient for coverage)
- **Lawn Mower**: Back-and-forth pattern (difficult with obstacles)
- **Potential Fields**: Attraction/repulsion forces (complex but smooth)

## Task 2: Swarm Behaviors

### 2a) Basic Stop Behavior

**Implementation:**
Simple proximity detection where robots stop upon detecting neighbors within 30 units.

**Observations:**
- Quick cluster formation
- Permanent clusters (robots never leave)
- Even distribution of small clusters
- No global aggregation

### 2b) Timed Stop with Cluster Leaving

**Implementation Features:**
- Wait timer (120 frames = 2 seconds at 60 FPS)
- Cluster size detection
- State machine: Moving → Stopped → Leaving → Moving

**Leave Decision Logic:**
```python
cluster_size = count_nearby_robots()
IF cluster_size < 3 OR random() < 0.1:
    state = "leaving"
    direction = opposite_of_cluster_center
```

**Improvements over 2a:**
- Dynamic cluster formation
- Small clusters dissolve
- Larger clusters persist longer
- More interesting emergent behavior

### 2c) Aggregation Behavior (Final Version)

**Advanced Features Implemented:**

1. **Attraction Forces**:
   - Robots attracted to small clusters (< 5 robots)
   - Slow down near large clusters
   - Bias toward arena center when alone

2. **Adaptive Leave Probability**:
   ```python
   leave_prob = 0.001 if cluster_size > 10 else 0.01 / (cluster_size + 1)
   ```
   - Very low probability to leave large clusters
   - Higher probability for small clusters

3. **Rejoin Mechanism**:
   - Leaving robots can immediately rejoin if they detect large cluster
   - Creates dynamic equilibrium

**Emergent Properties:**
- Single large cluster formation (15-18 robots)
- Occasional robots leave and rejoin
- Stable aggregation with dynamics
- Self-organizing behavior

## Performance Analysis

### Computational Complexity:
- Neighbor detection: O(n²) for n robots
- Could optimize with spatial hashing for larger swarms
- Current implementation handles 20 robots at 60 FPS

### Parameter Sensitivity Study:

| Parameter | Effect on Aggregation |
|-----------|----------------------|
| SENSOR_RANGE | Larger = faster aggregation |
| WAIT_TIME | Longer = more stable clusters |
| AGGREGATION_DISTANCE | Smaller = denser clusters |
| leave_probability | Lower = more permanent clusters |

## Lessons Learned

1. **Simplicity Creates Complexity**: Simple local rules generate complex global behaviors
2. **Parameter Tuning is Crucial**: Small changes in parameters dramatically affect swarm behavior
3. **State Machines are Powerful**: FSMs provide clear structure for behavior implementation
4. **Visualization is Essential**: Real-time visualization crucial for understanding emergent behaviors

## Future Improvements

1. **Communication**: Add explicit message passing between robots
2. **Heterogeneous Swarms**: Different robot types with specialized roles
3. **Environmental Factors**: Add resources, gradients, or targets
4. **Learning**: Implement reinforcement learning for parameter optimization
5. **Scalability**: Optimize for 100+ robot swarms

## Conclusion

This tutorial successfully demonstrated the progression from single robot reactive behaviors to complex swarm aggregation. The custom simulator proved effective for rapid prototyping and parameter experimentation. The implementations show how local interactions without global coordination can achieve collective behaviors, a fundamental principle in swarm robotics.

The key insight is that aggregation emerges from the balance between attraction (joining clusters) and repulsion (leaving clusters), with parameters controlling this balance to achieve desired swarm dynamics.