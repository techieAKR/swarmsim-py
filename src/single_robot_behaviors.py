import pygame
import math
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROBOT_SIZE = 20
SENSOR_RANGE = 100
WALL_THICKNESS = 10
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 2
        self.sensor_angles = [-45, -30, -15, 0, 15, 30, 45]  # Sensor angles in degrees
        self.sensor_readings = [SENSOR_RANGE] * len(self.sensor_angles)
        self.trail = []  # For vacuum cleaner visualization
        self.wall_follow_state = "searching"  # For wall follower
        self.wall_distance = 40  # Desired distance from wall
        
    def sense_walls(self, walls):
        """Update sensor readings based on wall distances"""
        for i, angle_offset in enumerate(self.sensor_angles):
            angle = self.angle + math.radians(angle_offset)
            min_distance = SENSOR_RANGE
            
            # Cast ray from robot position
            for distance in range(1, SENSOR_RANGE):
                x = self.x + distance * math.cos(angle)
                y = self.y + distance * math.sin(angle)
                
                # Check collision with walls
                for wall in walls:
                    if wall.collidepoint(x, y):
                        min_distance = distance
                        break
                        
                if min_distance < SENSOR_RANGE:
                    break
                    
            self.sensor_readings[i] = min_distance
    
    def collision_avoidance(self):
        """Behavior a: Collision avoidance"""
        # If front sensors detect close obstacles, turn
        front_sensors = self.sensor_readings[2:5]  # Middle three sensors
        
        if min(front_sensors) < 40:
            # Turn away from closest obstacle
            left_avg = sum(self.sensor_readings[:3]) / 3
            right_avg = sum(self.sensor_readings[4:]) / 3
            
            if left_avg < right_avg:
                self.angle += 0.1  # Turn right
            else:
                self.angle -= 0.1  # Turn left
        else:
            # Move forward with slight random wandering
            self.angle += random.uniform(-0.02, 0.02)
        
        # Update position
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
    
    def wall_follower(self):
        """Behavior b: Wall following"""
        front_distance = self.sensor_readings[3]  # Front sensor
        right_distance = self.sensor_readings[5]  # Right sensor
        right_front_distance = self.sensor_readings[4]  # Right-front sensor
        
        if self.wall_follow_state == "searching":
            # Search for wall
            if min(self.sensor_readings) < 50:
                self.wall_follow_state = "following"
            else:
                # Wander until wall found
                self.angle += random.uniform(-0.05, 0.05)
                self.x += self.speed * math.cos(self.angle)
                self.y += self.speed * math.sin(self.angle)
        
        elif self.wall_follow_state == "following":
            # Follow wall on the right side
            if front_distance < 30:
                # Turn left if too close to front wall
                self.angle -= 0.1
            elif right_distance > self.wall_distance + 10:
                # Turn right if too far from wall
                self.angle += 0.05
            elif right_distance < self.wall_distance - 10:
                # Turn left if too close to wall
                self.angle -= 0.05
            else:
                # Move forward
                self.x += self.speed * math.cos(self.angle)
                self.y += self.speed * math.sin(self.angle)
    
    def vacuum_cleaner(self):
        """Behavior c: Vacuum cleaner with coverage strategy"""
        # Add current position to trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 500:  # Limit trail length
            self.trail.pop(0)
        
        # Implement a spiral/systematic coverage pattern
        front_distance = self.sensor_readings[3]
        
        if front_distance < 30:
            # Hit obstacle, turn 90 degrees
            self.angle += math.pi / 2
        else:
            # Move in expanding spiral pattern
            spiral_factor = len(self.trail) * 0.0001
            self.angle += 0.02 + spiral_factor
            
            # Add some randomness to avoid getting stuck
            if random.random() < 0.05:
                self.angle += random.uniform(-math.pi/4, math.pi/4)
        
        # Update position
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
    
    def draw(self, screen, color=BLUE):
        """Draw robot and sensors"""
        # Draw robot body
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ROBOT_SIZE)
        
        # Draw direction indicator
        end_x = self.x + ROBOT_SIZE * 1.5 * math.cos(self.angle)
        end_y = self.y + ROBOT_SIZE * 1.5 * math.sin(self.angle)
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 3)
        
        # Draw sensors
        for i, (angle_offset, distance) in enumerate(zip(self.sensor_angles, self.sensor_readings)):
            angle = self.angle + math.radians(angle_offset)
            end_x = self.x + distance * math.cos(angle)
            end_y = self.y + distance * math.sin(angle)
            
            # Color sensors based on distance
            if distance < 30:
                sensor_color = RED
            elif distance < 60:
                sensor_color = YELLOW
            else:
                sensor_color = GREEN
                
            pygame.draw.line(screen, sensor_color, (self.x, self.y), (end_x, end_y), 1)

class Simulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Robot Behaviors Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.mode = "collision_avoidance"  # Default mode
        
        # Create walls (boundaries and obstacles)
        self.walls = [
            pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS),  # Top
            pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS),  # Bottom
            pygame.Rect(0, 0, WALL_THICKNESS, SCREEN_HEIGHT),  # Left
            pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, SCREEN_HEIGHT),  # Right
            # Add some obstacles
            pygame.Rect(200, 200, 100, 20),
            pygame.Rect(500, 300, 20, 100),
            pygame.Rect(300, 400, 80, 80),
        ]
        
        # Create robot at random position
        self.robot = Robot(
            random.randint(50, SCREEN_WIDTH - 50),
            random.randint(50, SCREEN_HEIGHT - 50)
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.mode = "collision_avoidance"
                    print("Mode: Collision Avoidance")
                elif event.key == pygame.K_2:
                    self.mode = "wall_follower"
                    self.robot.wall_follow_state = "searching"
                    print("Mode: Wall Follower")
                elif event.key == pygame.K_3:
                    self.mode = "vacuum_cleaner"
                    self.robot.trail = []
                    print("Mode: Vacuum Cleaner")
                elif event.key == pygame.K_r:
                    # Reset robot position
                    self.robot = Robot(
                        random.randint(50, SCREEN_WIDTH - 50),
                        random.randint(50, SCREEN_HEIGHT - 50)
                    )
    
    def update(self):
        # Update sensor readings
        self.robot.sense_walls(self.walls)
        
        # Execute behavior based on mode
        if self.mode == "collision_avoidance":
            self.robot.collision_avoidance()
        elif self.mode == "wall_follower":
            self.robot.wall_follower()
        elif self.mode == "vacuum_cleaner":
            self.robot.vacuum_cleaner()
        
        # Keep robot within bounds
        self.robot.x = max(ROBOT_SIZE, min(SCREEN_WIDTH - ROBOT_SIZE, self.robot.x))
        self.robot.y = max(ROBOT_SIZE, min(SCREEN_HEIGHT - ROBOT_SIZE, self.robot.y))
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw walls and obstacles
        for wall in self.walls:
            pygame.draw.rect(self.screen, GRAY, wall)
        
        # Draw vacuum trail if in vacuum mode
        if self.mode == "vacuum_cleaner" and len(self.robot.trail) > 1:
            for i in range(1, len(self.robot.trail)):
                pygame.draw.line(self.screen, (200, 200, 255), 
                               self.robot.trail[i-1], self.robot.trail[i], 3)
        
        # Draw robot
        robot_color = BLUE
        if self.mode == "wall_follower":
            robot_color = GREEN
        elif self.mode == "vacuum_cleaner":
            robot_color = RED
            
        self.robot.draw(self.screen, robot_color)
        
        # Draw mode text
        font = pygame.font.Font(None, 36)
        mode_text = font.render(f"Mode: {self.mode.replace('_', ' ').title()}", True, BLACK)
        self.screen.blit(mode_text, (10, 10))
        
        # Draw instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Press 1: Collision Avoidance",
            "Press 2: Wall Follower",
            "Press 3: Vacuum Cleaner",
            "Press R: Reset Robot"
        ]
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, BLACK)
            self.screen.blit(text, (10, 50 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
