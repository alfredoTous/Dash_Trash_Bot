#!/usr/bin/env python3
import pygame
from time import sleep
import sys
import random
from classes import *
from constants import *
from AI import *


pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/bg_music_metal.wav")
pygame.mixer.music.set_volume(0.75)     
pygame.mixer.music.play(-1)  

sfx_correct = pygame.mixer.Sound("assets/sfx_correct.wav")
sfx_wrong   = pygame.mixer.Sound("assets/sfx_wrong.wav")

sfx_correct.set_volume(0.5)
sfx_wrong.set_volume(0.5)


font = pygame.font.SysFont(None, 36)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Game Title")   
clock = pygame.time.Clock()

def setup_containers():
    containers_scale = Scale(170,170)
    Container.load_container_sprite()

    spacing = (WIDTH - (containers_scale.w * 4)) // 5

    containers.clear()
    containers.append(Container(screen,"A",Pos(spacing,550), containers_scale))
    containers.append(Container(screen,"B",Pos(spacing*2 + containers_scale.w,550), containers_scale))
    containers.append(Container(screen,"C",Pos(spacing*3 + (containers_scale.w*2),550), containers_scale))
    containers.append(Container(screen,"D",Pos(spacing*4 + (containers_scale.w*3),550), containers_scale))

def text_to_screen(screen):
    level_text = font.render(f"Level: {actual_level + 1}", True, (0, 0, 0))
    screen.blit(level_text, (1100, 60))

    time_text = font.render(f"Time: {seconds}", True, (0,0,0))
    screen.blit(time_text, (1100,20))

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

def spawn_trash():
    trash_type = random.choice(["A", "B", "C", "D"])
    pos = Pos(random.randint(0, WIDTH - 50), 0) #Maybe change first zero to 50      
    scale = Scale(*levels[actual_level]["scale"])                             
    velocity = random.randint(*levels[actual_level]["velocity"])                 
    trashes.append(Trash(trash_type, pos, scale, velocity))

def draw_life_bar(screen, current, max_value):
    
    pygame.draw.rect(screen, (180, 180, 180), (20, 60, max_value, 20))  
    pygame.draw.rect(screen, (255, 50, 50), (20, 60, current, 20))      
    pygame.draw.rect(screen, (0, 0, 0), (20, 60, max_value, 20), 2)  


def main_menu():
    menu_running = True
    options = ["Play", "AI", "Instructions", "Difficulty", "Records", "Exit"]
    selected_option = 0
    font = pygame.font.SysFont(None, 60)
    title_font = pygame.font.SysFont(None, 80)

    while menu_running:
        screen.fill((50, 50, 80))  

        title = title_font.render("Main Menu", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_option] == "Play":
                        return "play"
                    elif options[selected_option] == "AI":
                        return "AI"
                    elif options[selected_option] == "Instructions":
                        return "instructions"
                    elif options[selected_option] == "Difficulty":
                        return "difficulty"
                    elif options[selected_option] == "Records":
                        return "records"
                    elif options[selected_option] == "Exit":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def play_game():

    global trashes, containers, actual_level, score, seconds

    trashes = []
    containers = []

    lives = 5
    actual_level = 0
    score = 0

    running = True
    dragging = None
    mouse_held = None 

    level_start_time = pygame.time.get_ticks()
    level_finished = False

    setup_containers()

    max_life_bar = 300
    life_bar = max_life_bar

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_held = True

            #if mouse button was released, detects trash-container collision
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                if dragging:
                    for container in containers:
                        if container.collides(dragging.rect):
                            if dragging.trash_type == container.container_type:
                                score += 1
                                sfx_correct.play()
                            else:
                                score -= 1
                                life_bar -= 5
                                sfx_wrong.play()
                            if dragging in trashes:
                                trashes.remove(dragging)
                            break
                    dragging = None
        
        seconds = (pygame.time.get_ticks() - level_start_time) // 1000
        if seconds >= levels[actual_level]["duration"]:
            level_finished = True

        #Allows grabing trash if mouse is pressed before reaching trash hitbox
        if mouse_held and dragging is None:
            mx, my = pygame.mouse.get_pos()
            for trash in trashes:
                #Gives +10px to trash hitbox
                hit_rect = trash.rect.inflate(10, 10)
                if hit_rect.collidepoint(mx, my):
                    dragging = trash
                    break

        #If dragging move trash to cursor position
        if dragging:
            mx, my = pygame.mouse.get_pos()
            dragging.rect.center = (mx, my)

        #Background color
        screen.fill((220, 220, 220)) 

        #Draw containers
        for container in containers:
            container.draw(screen)
            
        # Probability of 1/(level[trash_spawn_denominator]) of spawning trash per frame
        if random.randint(1, levels[actual_level]["trash_spawn_denominator"]) == 1:
            spawn_trash()

        for trash in trashes[:]:
            #Don't check collision nor give gravity while dragging trash  
            if trash is dragging:
                continue
            
            trash.gravity()
            #Remove if exceed screen        
            if trash.rect.top > HEIGHT:
                trashes.remove(trash)
                score -= 1
                life_bar -= 2
                sfx_wrong.play()

            #Checks container-trash collision
            for container in containers:
                if container.collides(trash.rect):
                    if trash.trash_type == container.container_type:
                        score += 1
                        sfx_correct.play()
                    else:
                        score -= 1
                        life_bar -= 3
                        sfx_wrong.play()
                    trashes.remove(trash)
                    break

        #Change levels
        if level_finished:
            actual_level += 1
            if actual_level >= len(levels):
                print("\nGame Completed")
                running = False
            else:
                level_start_time = pygame.time.get_ticks()
                level_finished = False
                lives += levels[actual_level]["extra_lives"]
                trashes.clear()  
                dragging = None
        
        
        #Detects mouse hovers and changes cursor
        mx, my = pygame.mouse.get_pos()
        hovering = any(trash.rect.collidepoint((mx, my)) for trash in trashes)

        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        #Draw trash
        for trash in trashes:
            trash.draw(screen)
        
        #Draw text: score,time,level
        text_to_screen(screen)

        #Draw live bar
        draw_life_bar(screen, life_bar, max_life_bar)

        if life_bar <= 0:
            running = False
            print("You Lost!")


        pygame.display.flip()
        clock.tick(FPS)

    print(f"Score: {score}")

game_state = "menu"

while True:
    if game_state == "menu":
        choice = main_menu()
        if choice == "play":
            game_state = "play"
        elif choice == "AI":
            game_state = "AI"

        elif choice == "instructions":
            
            pass
        elif choice == "difficulty":
            
            pass
        elif choice == "records":
            
            pass
        elif choice == "exit":
            pygame.quit()
            sys.exit()
            
    elif game_state == "play":
        play_game()
        game_state = "menu" 

    elif game_state == "AI":
        print("AI TRAINING")
        agent = Agent()
        
        best_duration = 0
        episodes_without_improvement = 0
        
        for ep in range(10):  
            print(f"\n--- Episode {ep + 1} ---")
            print("🎮 Training... (F = alternate speed, SPACE = pause, ESC = exit)")
            
            if ep < 3:
                initial_speed = "normal"
            elif ep < 5:
                initial_speed = "medium"
            elif ep < 6: 
                initial_speed = "fast"
            else:
                initial_speed = "ultra_fast"

            reward, duration, correct, total = run_game(agent, training=True, episode_num=ep + 1, render=True, speed_mode=initial_speed)
            accuracy = (correct / max(total, 1)) * 100
            
            print(f"Reward: {reward:.1f} | Epsilon: {agent.epsilon:.3f} | Accuracy: {accuracy:.1f}% ({correct}/{total})")

        
        print(f"\n✅ Finished Training")
        
        print("\nTesting trained AI at medium speed...")
        sleep(2)
        
        test_epsilon = 0.05
        agent.epsilon = test_epsilon

        print(f"\n--- Test with epsilon: {test_epsilon} ---")
        agent.epsilon = test_epsilon
        reward, duration, correct, total = run_game(agent, training=False, render=True, speed_mode="medium") #Change this speed for testing the model
        accuracy = (correct / max(total, 1)) * 100
        print(f"🏆 Score: {reward:.1f} Correct: {correct} Total: {total} Accuracy: {accuracy:.1f}% ({correct}/{total})")
        
        pygame.quit()