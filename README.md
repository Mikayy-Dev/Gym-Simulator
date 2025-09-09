<<<<<<< HEAD
# Gym Sim
=======
# Gym-Simulator v0.4
>>>>>>> d2493eee2dbb6dec82b06d2369d5f408df6ace49

A gym management simulation game where you run a fitness center and keep your customers happy!

## Overview

Gym Sim is a top-down simulation game where you manage a gym, interact with equipment, serve customers (NPCs), and maintain a clean and organized environment. Your goal is to keep your gym members happy by cleaning equipment, organizing weights, and providing good service.

## Controls

### Movement
- **W, A, S, D** - Move your character around the gym
- **Left Shift** - Sprint (drains stamina)

### Game Controls
- **Escape** - Pause the game
- **I** - Open/Close skill points inventory
- **Right Mouse Click** - Interact with gym equipment and objects

### Dialogue Controls
- **1, 2, 3** - Select dialogue options when talking to NPCs
- **Escape** - End dialogue

### Debug Controls (Debug Mode Only)
- **Tab** - Toggle all hitbox visualizations
- **J** - Toggle interaction hitboxes
- **O** - Toggle NPC path visualization

## Gameplay Features

### Gym Management
- **Equipment Maintenance**: Clean dirty equipment by right-clicking on it
- **Weight Organization**: Pick up weight plates from the floor and organize them
- **Equipment Control**: Turn off running equipment that's been left unattended
- **Customer Service**: Interact with gym members and provide assistance

### Skill System
- **Speed**: Increases your movement speed
- **Endurance**: Increases your stamina capacity and regeneration
- **Management**: Improves NPC happiness and gym efficiency
- **Skill Points**: Earn points by completing tasks and leveling up
- **Maximum Level**: Each skill can be upgraded to level 5

### Progress System
- **Progress Bar**: Shows your current level progress
- **Leveling Up**: Complete tasks to gradually fill the progress bar and level up, long periods of time without tasks completed and the progress is drained. 
- **Skill Point Rewards**: Earn skill points at levels 2, 4, 6, 8, and 10

### NPC System
- **Customer Flow**: NPCs arrive, check in at the front desk, work out, and leave
- **Customer Happiness**: Keep customers happy by maintaining clean equipment and organized weights

### Gym Equipment
- **Benches**: For bench press workouts
- **Treadmills**: For cardio exercises
- **Dumbbell Racks**: For weight training
- **Squat Racks**: For squat exercises
- **Front Desk**: Customer check-in point
- **Trash Cans**: For disposing of items

### Interaction System
- **Right-click** on equipment to interact
- **Cleaning**: Right-click dirty equipment to clean it
- **Weight Management**: Right-click weight plates on the floor to pick them up
- **Equipment Control**: Right-click running equipment to turn it off
- **Range Requirement**: You must be close enough to equipment to interact with it

## Game Mechanics

### Stamina System
- **Base Stamina**: 25 points
- **Sprint Cost**: Drains stamina while sprinting
- **Regeneration**: Stamina regenerates over time when not sprinting
- **Endurance Skill**: Increases maximum stamina and regeneration rate

### Happiness System
- **Base Happiness**: Starts at 50%
- **Happiness Events**: Various events affect customer happiness
  - Dirty equipment decreases happiness
  - Clean equipment increases happiness
  - Organized weights increase happiness
  - Unattended running equipment decreases happiness
  - Empty dumbbell racks decrease happiness
  - Queue timeouts decrease happiness

### Time System
- **Game Clock**: Tracks in-game time
- **NPC Departure**: NPCs leave after 60 seconds



