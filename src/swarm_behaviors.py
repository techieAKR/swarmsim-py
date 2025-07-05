import pygame
import math
import random
import numpy as np
from collections import defaultdict

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
ROBOT_SIZE = 10
NUM_ROBOTS = 20
SENSOR_RANGE = 50
FPS = 60
WAIT_TIME = 120  # Frames to wait when stopped
AGGREGATION_DISTANCE = 30  # Distance to consider robots as neighbors

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

class SwarmRobot:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 1.5
        self.max_speed = 2.0
        self.state = "moving"  # "moving", "stopped", "leaving"
        self.wait_timer = 0
        self.neighbors = []
        self.cluster_size = 0
        self.leave_probability = 0.01  # Probability to leave cluster
        
    def sense_neighbors(self, robots):
        """Detect nearby robots"""
        self.neighbors = []
        for robot in robots:
            if robot.id != self.id:
                distance = math.sqrt((self.x - robot.x)**2 + (self.y - robot.y)**2)
                if distance < SENSOR_RANGE:
                    self.neighbors.append({
                        'robot': robot,
                        'distance': distance,
                        'angle': math.atan2(robot.y - self.y, robot.x - self.x)
                    })
        
        # Sort by distance
        self.neighbors.sort(key=lambda n: n['distance'])
        
    def basic_stop_behavior(self):
        """Task 2a: Stop when close to another robot"""
        if self.neighbors and self.neighbors[0]['distance'] < AGGREGATION_DISTANCE:
            self.state = "stopped"
            self.speed = 0
        else:
            self.state = "moving"
            self.speed = self.max_speed
            # Random walk
            self.angle += random.uniform(-0.1, 0.1)
    
    def timed_stop_behavior(self):
        """Task 2b: Stop with timer and leave small clusters"""
        if self.state == "moving":
            if self.neighbors and self.neighbors[0]['distance'] < AGGREGATION_DISTANCE:
                self.state = "stopped"
                self.wait_timer = WAIT_TIME
                self.speed = 0
        
        elif self.state == "stopped":
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                # Count cluster size
                cluster_count = sum(1 for n in self.neighbors if n['distance'] < AGGREGATION_DISTANCE)
                
                # Leave small clusters more likely
                if cluster_count < 3 or random.random() < 0.1:
                    self.state = "leaving"
                    self.wait_timer = 30  # Time to leave cluster
                    # Turn away from cluster center
                    if self.neighbors:
                        avg_angle = sum(n['angle'] for n in self.neighbors) / len(self.neighbors)
                        self.angle = avg_angle + math.pi  # Opposite direction
                else:
                    self.wait_timer = WAIT_TIME  # Stay in cluster
        
        elif self.state == "leaving":
            self.speed = self.max_speed * 1.5  # Move faster when leaving
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self.state = "moving"
                self.speed = self.max_speed
        
        # Movement for moving and leaving states
        if self.state == "moving":
            self.angle += random.uniform(-0.1, 0.1)
            self.speed = self.max_speed
    
    def aggregation_behavior(self):
        """Task 2c: Tweaked aggregation behavior"""
        # Calculate local cluster metrics
        close_neighbors = [n for n in self.neighbors if n['distance'] < AGGREGATION_DISTANCE]
        self.cluster_size = len(close_neighbors)
        
        if self.state == "moving":
            if close_neighbors:
                # Attraction to neighbors
                if self.cluster_size < 5:  # Join small clusters
                    # Move toward nearest neighbor
                    self.angle = close_neighbors[0]['angle']
                    self.speed = self.max_speed
                    
                    if close_neighbors[0]['distance'] < 20:
                        self.state = "stopped"
                        self.wait_timer = WAIT_TIME * 2  # Stay longer in clusters
                else:
                    # Slow down near large clusters
                    self.speed = self.max_speed * 0.5
            else:
                # Random walk with bias toward center
                center_angle = math.atan2(SCREEN_HEIGHT/2 - self.y, SCREEN_WIDTH/2 - self.x)
                self.angle = 0.9 * self.angle + 0.1 * center_angle + random.uniform(-0.2, 0.2)
                self.speed = self.max_speed
        
        elif self.state == "stopped":
            self.wait_timer -= 1
            self.speed = 0
            
            # Occasionally leave based on cluster size
            leave_prob = 0.001 if self.cluster_size > 10 else 0.01 / (self.cluster_size + 1)
            
            if self.wait_timer <= 0 or random.random() < leave_prob:
                self.state = "leaving"
                self.wait_timer = 20
                # Turn away from cluster
                if close_neighbors:
                    avg_x = sum(n['robot'].x for n in close_neighbors) / len(close_neighbors)
                    avg_y = sum(n['robot'].y for n in close_neighbors) / len(close_neighbors)
                    self.angle = math.atan2(self.y - avg_y, self.x - avg_x)
        
        elif self.state == "leaving":
            self.speed = self.max_speed * 1.2
            self.wait_timer -= 1
            
            # Small chance to rejoin immediately if see large cluster
            if self.cluster_size > 8 and random.random() < 0.3:
                self.state = "moving"
            elif self.wait_timer <= 0:
                self.state = "moving"
    
    def update_position(self):
        """Update robot position"""
        if self.speed > 0:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            
            # Bounce off walls
            if self.x < ROBOT_SIZE or self.x > SCREEN_WIDTH - ROBOT_SIZE:
                self.angle = math.pi - self.angle
                self.x = max(ROBOT_SIZE, min(SCREEN_WIDTH - ROBOT_SIZE, self.x))
            
            if self.y < ROBOT_SIZE or self.y > SCREEN_HEIGHT - ROBOT_SIZE:
                self.angle = -self.angle
                self.y = max(ROBOT_SIZE, min(SCREEN_HEIGHT - ROBOT_SIZE, self.y))
    
    def draw(self, screen):
        """Draw robot with state-based colors"""
        if self.state == "stopped":
            color = RED
        elif self.state == "leaving":
            color = YELLOW
        else:
            color = BLUE
        
        # Draw robot
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ROBOT_SIZE)
        
        # Draw direction for debugging
        end_x = self.x + ROBOT_SIZE * 2 * math.cos(self.angle)
        end_y = self.y + ROBOT_SIZE * 2 * math.sin(self.angle)
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 1)

class SwarmSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Swarm Robotics Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.mode = "basic"  # "basic", "timed", "aggregation"
        
        # Create swarm of robots
        self.robots = []
        for i in range(NUM_ROBOTS):
            x = random.randint(ROBOT_SIZE * 2, SCREEN_WIDTH - ROBOT_SIZE * 2)
            y = random.randint(ROBOT_SIZE * 2, SCREEN_HEIGHT - ROBOT_SIZE * 2)
            self.robots.append(SwarmRobot(x, y, i))
        
        # Statistics
        self.clusters = []
        
    def find_clusters(self):
        """Identify robot clusters for visualization"""
        visited = set()
        self.clusters = []
        
        for robot in self.robots:
            if robot.id not in visited:
                cluster = []
                stack = [robot]
                
                while stack:
                    current = stack.pop()
                    if current.id not in visited:
                        visited.add(current.id)
                        cluster.append(current)
                        
                        # Add neighbors to stack
                        for neighbor_info in current.neighbors:
                            neighbor = neighbor_info['robot']
                            if neighbor.id not in visited and neighbor_info['distance'] < AGGREGATION_DISTANCE:
                                stack.append(neighbor)
                
                if len(cluster) > 1:
                    self.clusters.append(cluster)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.mode = "basic"
                    print("Mode: Basic Stop Behavior")
                elif event.key == pygame.K_2:
                    self.mode = "timed"
                    print("Mode: Timed Stop Behavior")
                elif event.key == pygame.K_3:
                    self.mode = "aggregation"
                    print("Mode: Aggregation Behavior")
                elif event.key == pygame.K_r:
                    # Reset robots
                    self.robots = []
                    for i in range(NUM_ROBOTS):
                        x = random.randint(ROBOT_SIZE * 2, SCREEN_WIDTH - ROBOT_SIZE * 2)
                        y = random.randint(ROBOT_SIZE * 2, SCREEN_HEIGHT - ROBOT_SIZE * 2)
                        self.robots.append(SwarmRobot(x, y, i))
    
    def update(self):
        # Update sensor readings for all robots
        for robot in self.robots:
            robot.sense_neighbors(self.robots)
        
        # Update robot behaviors
        for robot in self.robots:
            if self.mode == "basic":
                robot.basic_stop_behavior()
            elif self.mode == "timed":
                robot.timed_stop_behavior()
            elif self.mode == "aggregation":
                robot.aggregation_behavior()
            
            robot.update_position()
        
        # Find clusters
        self.find_clusters()
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw cluster connections
        for cluster in self.clusters:
            if len(cluster) > 2:
                # Calculate cluster center
                center_x = sum(r.x for r in cluster) / len(cluster)
                center_y = sum(r.y for r in cluster) / len(cluster)
                
                # Draw connections to center
                for robot in cluster:
                    pygame.draw.line(self.screen, (200, 200, 200), 
                                   (robot.x, robot.y), (center_x, center_y), 1)
        
        # Draw robots
        for robot in self.robots:
            robot.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        mode_text = font.render(f"Mode: {self.mode.title()}", True, BLACK)
        self.screen.blit(mode_text, (10, 10))
        
        # Draw statistics
        font_small = pygame.font.Font(None, 24)
        stats = [
            f"Robots: {NUM_ROBOTS}",
            f"Clusters: {len(self.clusters)}",
            f"Largest cluster: {max(len(c) for c in self.clusters) if self.clusters else 0}"
        ]
        for i, stat in enumerate(stats):
            text = font_small.render(stat, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 10 + i * 25))
        
        # Draw instructions
        instructions = [
            "Press 1: Basic Stop",
            "Press 2: Timed Stop",
            "Press 3: Aggregation",
            "Press R: Reset"
        ]
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, BLACK)
            self.screen.blit(text, (10, 50 + i * 25))
        
        # Draw legend
        legend = [
            ("Moving", BLUE),
            ("Stopped", RED),
            ("Leaving", YELLOW)
        ]
        for i, (label, color) in enumerate(legend):
            pygame.draw.circle(self.screen, color, (15, 200 + i * 30), 8)
            text = font_small.render(label, True, BLACK)
            self.screen.blit(text, (30, 190 + i * 30))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    sim = SwarmSimulation()
    sim.run()
