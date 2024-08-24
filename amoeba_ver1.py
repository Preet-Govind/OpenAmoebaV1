import pygame
import numpy as np
import random
import math
from pygame.locals import QUIT

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Amoeba Simulation")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
toxic_color = (255, 0, 0)

# Amoeba class
class Amoeba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_size = 30
        self.points = self.generate_points()
        self.speed = 10
        self.energy = 1000
        self.consumed_food = 0
        self.age = 0
        self.history = []
        self.direction = random.uniform(0, 2 * math.pi)  # Random initial direction

    def generate_points(self):
        points = []
        num_points = 12
        for i in range(num_points):
            angle = math.radians(i * (360 / num_points))
            radius = self.base_size + random.randint(-10, 10)
            x = self.x + math.cos(angle) * radius
            y = self.y + math.sin(angle) * radius
            points.append([x, y])
        return points

    def update(self, food_items, obstacles, toxic_zones):
        self.age += 0.01  # Increment age
        self.manage_energy()
        self.manage_health()  # Manage health based on age
        state = self.get_state(food_items, obstacles, toxic_zones)
        action = self.ai_decision(state)
        self.perform_action(action, food_items, obstacles, toxic_zones)
        self.points = self.generate_points()
        self.history.append((self.x, self.y))
        if len(self.history) > 100:  # Limit history length to prevent memory overflow
            self.history.pop(0)

        # Reproduction condition
        if self.base_size > 50 and random.random() < 0.01:  # Amoeba can reproduce if it grows beyond a certain size
            self.reproduce(food_items, obstacles, toxic_zones)

    def get_state(self, food_items, obstacles, toxic_zones):
        # Sense food and toxic gradients
        food_gradient = self.calculate_food_gradient(food_items)
        toxic_gradient = self.calculate_toxic_gradient(toxic_zones)
        return np.array([
            food_gradient[0], food_gradient[1], 
            toxic_gradient[0], toxic_gradient[1], 
            self.energy / 1000
        ])

    def calculate_food_gradient(self, food_items):
        dx = dy = 0
        for food in food_items:
            distance = self.distance_to(food.x, food.y)
            if distance < 100:  # Sensory range
                weight = 1 / (distance + 1e-5)  # Avoid division by zero
                angle = math.atan2(food.y - self.y, food.x - self.x)
                dx += weight * math.cos(angle)
                dy += weight * math.sin(angle)
        return dx, dy

    def calculate_toxic_gradient(self, toxic_zones):
        dx = dy = 0
        for toxic in toxic_zones:
            distance = self.distance_to(toxic.x, toxic.y)
            if distance < 100:  # Sensory range
                weight = 1 / (distance + 1e-5)  # Avoid division by zero
                angle = math.atan2(self.y - toxic.y, self.x - toxic.x)
                dx += weight * math.cos(angle)
                dy += weight * math.sin(angle)
        return dx, dy

    def ai_decision(self, state):
        # Use a dummy AI decision here; replace with actual AI model predictions if necessary
        return np.array([random.uniform(-1, 1), random.uniform(-1, 1)])

    def perform_action(self, action, food_items, obstacles, toxic_zones):
        if food_items:
            closest_food = min(food_items, key=lambda food: self.distance_to(food.x, food.y))
            if self.distance_to(closest_food.x, closest_food.y) < 50:  # Proximity sensing
                self.move_towards(closest_food.x, closest_food.y)
                if self.distance_to(closest_food.x, closest_food.y) < 10:
                    food_items.remove(closest_food)
                    self.consumed_food += 1
                    self.energy += 500  # Increase energy with food
                    self.base_size += 1
            else:
                if random.random() < 0.1:
                    self.perform_random_walk()
        else:
            if obstacles:
                closest_obstacle = min(obstacles, key=lambda o: self.distance_to(o.x, o.y))
                self.avoid_obstacle(closest_obstacle.x, closest_obstacle.y)
            if toxic_zones:
                closest_toxic = min(toxic_zones, key=lambda t: self.distance_to(t.x, t.y))
                self.avoid_toxic_zone(closest_toxic.x, closest_toxic.y)
        self.energy -= 0.5  # Reduced energy consumption per update

    def perform_random_walk(self):
        self.direction += random.uniform(-0.5, 0.5)  # Randomly change direction
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

    def avoid_obstacle(self, obs_x, obs_y):
        angle = math.atan2(self.y - obs_y, self.x - obs_x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def avoid_toxic_zone(self, toxic_x, toxic_y):
        angle = math.atan2(self.y - toxic_y, self.x - toxic_x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def distance_to(self, x, y):
        return math.hypot(x - self.x, y - self.y)

    def move_towards(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def manage_energy(self):
        if self.energy <= 0:
            self.energy = 0
            self.speed = 0  # Amoeba dies or becomes inactive

    def manage_health(self):
        self.energy -= self.age * 0.05
        if self.energy <= 0:
            self.energy = 0
            self.speed = 0  # Amoeba dies or becomes inactive

    def reproduce(self, food_items, obstacles, toxic_zones):
        new_amoeba = Amoeba(self.x + random.randint(-20, 20), self.y + random.randint(-20, 20))
        new_amoeba.base_size = self.base_size / 2
        new_amoeba.energy = self.energy / 2
        food_items.append(new_amoeba)  # Adding new amoeba to food items list for demonstration

    def draw(self, screen):
        #pygame.draw.polygon(screen, green, self.points)
        pygame.draw.circle(screen, white, (int(self.x), int(self.y)), 10)
        # Draw the amoeba’s history
        for i in range(1, len(self.history)):
            pygame.draw.line(screen, white, self.history[i-1], self.history[i], 2)

    def draw_status(self, screen):
        font = pygame.font.SysFont(None, 24)
        energy_text = font.render(f'Energy: {int(self.energy)}', True, white)
        age_text = font.render(f'Age: {int(self.age)}', True, white)
        consumedFood_text = font.render(f'Food: {int(self.consumed_food)}', True, white)
        direction_text = font.render(f'Direction: {int(self.direction)}', True, white)
        screen.blit(energy_text, (10, 10))
        screen.blit(age_text, (10, 40))
        screen.blit(consumedFood_text, (10, 70))
        screen.blit(direction_text, (10, 100))

# Food class
class Food:
    def __init__(self):
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.size = 6

    def draw(self, screen):
        pygame.draw.circle(screen, green, (self.x, self.y), self.size)

# Obstacle class
class Obstacle:
    def __init__(self):
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.size = 20

    def draw(self, screen):
        pygame.draw.rect(screen, blue, pygame.Rect(self.x, self.y, self.size, self.size))

# ToxicZone class
class ToxicZone:
    def __init__(self):
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.size = 20

    def draw(self, screen):
        pygame.draw.circle(screen, red, (self.x, self.y), self.size)

# Environment class
class AmoebaEnvironment:
    def __init__(self):
        self.food_items = [Food() for _ in range(10)]
        self.obstacles = [Obstacle() for _ in range(5)]
        self.toxic_zones = [ToxicZone() for _ in range(3)]
        self.amoeba = Amoeba(width // 2, height // 2)

    def generate_data(self):
        # Here you would add the code to generate data for training
        pass

    def train_model(self):
        # Here you would add the code to train the model
        pass

    def draw_objects(self):
        for food in self.food_items:
            food.draw(screen)
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        for toxic in self.toxic_zones:
            toxic.draw(screen)
        self.amoeba.draw(screen)
        self.amoeba.draw_status(screen)

    def update_objects(self):
        self.amoeba.update(self.food_items, self.obstacles, self.toxic_zones)

def run_simulation():
    clock = pygame.time.Clock()
    env = AmoebaEnvironment()
    env.generate_data()  # Generate data for training
    env.train_model()    # Train the model

    running = True
    while running:
        screen.fill(black)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.update_objects()
        env.draw_objects()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run_simulation()
