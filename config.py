# config.py
"""
SwarmSim-Py Configuration File
Adjust these parameters to customize simulation behavior
"""

# Display Settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60
FULLSCREEN = False

# Robot Configuration
ROBOT_SIZE = 10
ROBOT_SPEED = 2.0
MAX_SPEED = 3.0
SENSOR_RANGE = 100
SENSOR_COUNT = 7
SENSOR_ANGLES = [-45, -30, -15, 0, 15, 30, 45]  # in degrees

# Swarm Configuration
NUM_ROBOTS = 20
INITIAL_DISTRIBUTION = "random"  # "random", "grid", "circle"

# Behavior Parameters
AGGREGATION_DISTANCE = 30
WAIT_TIME = 120  # frames
LEAVE_PROBABILITY = 0.01
WALL_FOLLOW_DISTANCE = 40
COLLISION_THRESHOLD = 40

# Visualization
SHOW_SENSORS = True
SHOW_TRAILS = True
TRAIL_LENGTH = 500
SHOW_CONNECTIONS = True
SHOW_STATISTICS = True

# Colors (R, G, B)
COLORS = {
    "background": (255, 255, 255),
    "robot_moving": (0, 0, 255),
    "robot_stopped": (255, 0, 0),
    "robot_leaving": (255, 255, 0),
    "wall": (128, 128, 128),
    "sensor_close": (255, 0, 0),
    "sensor_medium": (255, 255, 0),
    "sensor_far": (0, 255, 0),
    "trail": (200, 200, 255),
    "connection": (200, 200, 200),
}

# Physics
BOUNCE_DAMPING = 0.8
FRICTION = 0.98

# Data Collection
SAVE_METRICS = True
METRICS_INTERVAL = 60  # frames
OUTPUT_DIR = "results/"