import random, pygame, torch, torch.nn as nn, torch.optim as optim, numpy as np
from collections import deque
from classes import Trash, Container, Pos, Scale
from constants import WIDTH, HEIGHT, FPS, levels

class TrashDashEnv:
    #Environment of the game turn into a class with valid format for the agent
    def __init__(self):
        pygame.init()
        Container.load_container_sprite()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.time_multiplier = 1.0  
        self.reset()

    def reset(self):
        self.trashes, self.containers = [], []
        self.actual_level = self.score = 0
        self.life_bar = 300
        self.level_start = pygame.time.get_ticks()
        self.game_time = 0 
        
        scale = Scale(170, 170)
        spacing = (WIDTH - scale.w * 4) // 5
        for i, tipo in enumerate(["A", "B", "C", "D"]):
            x = spacing * (i + 1) + scale.w * i
            self.containers.append(Container(self.screen, tipo, Pos(x, 550), scale))
        return self.get_state()

    def step(self, action):
        pygame.event.pump()
        reward, done = 0, False
        
       
        dt = self.clock.get_time() * self.time_multiplier
        self.game_time += dt
        
        if self.trashes:
            target = max(self.trashes, key=lambda t: t.rect.bottom)
            chosen = ["A", "B", "C", "D"][action]
            if chosen == target.trash_type:
                reward, self.score = 15, self.score + 1
                self.trashes.remove(target)
                print(f"✅ {target.trash_type} → {chosen} CORRECTO")
            else:
                reward, self.life_bar = -10, self.life_bar - 5
                print(f"❌ {target.trash_type} → {chosen} INCORRECTO")

        # Spawn and move trash according to speed mode
        denom = max(1, int(levels[self.actual_level]["trash_spawn_denominator"] / self.time_multiplier))
        if random.randint(1, denom) == 1 and len(self.trashes) < 6:
            tipo = random.choice(["A", "B", "C", "D"])
            pos = Pos(random.randint(50, WIDTH - 100), 0)
            scale = Scale(*levels[self.actual_level]["scale"])
            vel = random.randint(*levels[self.actual_level]["velocity"])
            # Velocidad también se multiplica por el tiempo acelerado
            vel = int(vel * self.time_multiplier)
            self.trashes.append(Trash(tipo, pos, scale, vel))
        
        for trash in self.trashes[:]:
            trash.gravity()
            if trash.rect.top > HEIGHT:
                self.trashes.remove(trash)
                self.life_bar -= 3
                reward -= 3
        
        # Verified end game
        game_secs = self.game_time // 1000
        level_duration = levels[self.actual_level]["duration"]
        
        if game_secs >= level_duration:
            extra_lives = levels[self.actual_level]["extra_lives"]
            self.life_bar += extra_lives
            # Limitar la vida máxima a 300
            self.life_bar = min(self.life_bar, 300)
            self.actual_level += 1
            if self.actual_level >= len(levels):
                done = True
            else:
                self.game_time = 0  # Reset time per level
                
        if self.life_bar <= 0:
            done = True

        return self.get_state(), reward, done

    def get_state(self):
        state = [
            self.life_bar / 300,
            len(self.trashes) / 6,
            self.actual_level / 10,
        ]
        
        sorted_trashes = sorted(self.trashes, key=lambda t: t.rect.bottom, reverse=True)[:3]
        
        for i in range(3):
            if i < len(sorted_trashes):
                trash = sorted_trashes[i]
                state.extend([
                    trash.rect.centerx / WIDTH,
                    trash.rect.centery / HEIGHT,
                    "ABCD".index(trash.trash_type) / 3,
                    trash.rect.bottom / HEIGHT,
                    1.0
                ])
            else:
                state.extend([0, 0, 0, 0, 0])
        
        return torch.tensor(state, dtype=torch.float32).unsqueeze(0)

    def render(self):
        self.screen.fill((220, 220, 220))
        
        for container in self.containers:
            container.draw(self.screen)
        for trash in self.trashes:
            trash.draw(self.screen)
        
        # Mostrar tiempo de juego acelerado
        game_secs = self.game_time // 1000
        total_secs = levels[self.actual_level]["duration"]
        remaining = max(0, total_secs - game_secs)
        percent = min(100, (game_secs / total_secs) * 100)
        
        font = pygame.font.Font(None, 36)
        info = f"Nivel: {self.actual_level + 1}/10 | Score: {self.score} | Vida: {self.life_bar} | {remaining}s ({percent:.0f}%)"
        self.screen.blit(font.render(info, True, (0, 0, 0)), (10, 10))
        
        pygame.display.flip()
        self.clock.tick(FPS)

    def set_time_multiplier(self, multiplier):
        self.time_multiplier = multiplier

#inherits from pytorch.nn.module
class DQN(nn.Module):
    def __init__(self):
        super().__init__()
        #define the characteristic of the neural network layers
        self.net = nn.Sequential(
            #recieves 18 values describing the actual state, passed to 128 neurons
            nn.Linear(18, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            #progresively reduce the information each layer until it returns 4 output values representing the Q-value
            #for each of the 4 posible actions
            nn.Linear(32, 4)
        )
    
    def forward(self, x):
        return self.net(x)

class Agent:
    def __init__(self):
        #original net
        self.q_net = DQN()
        #copy of net
        self.target_net = DQN()
        #copied the parameters of the orginal net into the copy
        #Its better to use a fixed net to calculate the refernce values as it improves the stabilization of learning
        self.target_net.load_state_dict(self.q_net.state_dict())
        #optimizazer Adam, a version of the descending gradient that adapts the learning rate (lr) automatically
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=0.001)
        #define the memory of the agent (5000 experiences)
        self.memory = deque(maxlen=5000)
        #exploration rates and limits of the agent
        self.epsilon = 0.9
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        #every 100 steps we copy q_net to target_net
        self.update_target_freq = 100
        #step counter
        self.step_count = 0
        
    def act(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        
        with torch.no_grad():
            q_values = self.q_net(state)
            return q_values.argmax().item()
    
    def learn(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
        if len(self.memory) < 128:
            return
            
        batch_size = 64
        batch = random.sample(self.memory, batch_size)
        
        states = torch.cat([s for s, _, _, _, _ in batch])
        actions = torch.tensor([a for _, a, _, _, _ in batch], dtype=torch.long)
        rewards = torch.tensor([r for _, _, r, _, _ in batch], dtype=torch.float32)
        next_states = torch.cat([ns for _, _, _, ns, _ in batch])
        dones = torch.tensor([d for _, _, _, _, d in batch], dtype=torch.bool)
        
        current_q = self.q_net(states).gather(1, actions.unsqueeze(1))
        
        with torch.no_grad():
            next_actions = self.q_net(next_states).argmax(1)
            next_q = self.target_net(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
            next_q[dones] = 0.0
            target_q = rewards + 0.99 * next_q
        
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        self.optimizer.zero_grad()
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(self.q_net.parameters(), 1.0)
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.step_count += 1
        if self.step_count % self.update_target_freq == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())

def run_game(agent, training=True, episode_num=0, render=True, speed_mode="normal"):
    env = TrashDashEnv()
    
    # Configure multipliers based on speed mode
    if speed_mode == "ultra_fast":
        time_multiplier = 8.0  
        render_every = 15      
        fps_multiplier = 4     
        speed_text = "🚀 ULTRA FAST (8x)"
        speed_color = (255, 50, 50)
    elif speed_mode == "fast":
        time_multiplier = 4.0  
        render_every = 8       
        fps_multiplier = 2   
        speed_text = "🏃 FAST (4x)"
        speed_color = (255, 150, 50)
    elif speed_mode == "medium":
        time_multiplier = 2.0 
        render_every = 4
        fps_multiplier = 1.5
        speed_text = "⚡ MEDIUM (2x)"
        speed_color = (255, 200, 50)
    else:  # normal
        time_multiplier = 1.0
        render_every = 1
        fps_multiplier = 1
        speed_text = "🐌 NORMAL (1x)"
        speed_color = (100, 255, 100)
    
    env.set_time_multiplier(time_multiplier)
    #Reset config
    state = env.reset()
    total_reward = 0
    paused = False
    start_time = pygame.time.get_ticks()
    correct_actions = 0
    total_actions = 0
    frame_count = 0
    current_speed_mode = speed_mode
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return total_reward, (pygame.time.get_ticks() - start_time) // 1000, correct_actions, total_actions
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return total_reward, (pygame.time.get_ticks() - start_time) // 1000, correct_actions, total_actions
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_f and training:
                    if current_speed_mode == "normal":
                        current_speed_mode = "medium"
                        time_multiplier = 2.0
                        render_every = 4
                        fps_multiplier = 1.5
                        speed_text = "⚡ MEDIUM (2x)"
                        speed_color = (255, 200, 50)
                    elif current_speed_mode == "medium":
                        current_speed_mode = "fast"
                        time_multiplier = 4.0
                        render_every = 8
                        fps_multiplier = 2
                        speed_text = "🏃 FAST (4x)"
                        speed_color = (255, 150, 50)
                    elif current_speed_mode == "fast":
                        current_speed_mode = "ultra_fast"
                        time_multiplier = 8.0
                        render_every = 15
                        fps_multiplier = 4
                        speed_text = "🚀 ULTRA FAST (8x)"
                        speed_color = (255, 50, 50)
                    else:  # ultra_fast
                        current_speed_mode = "normal"
                        time_multiplier = 1.0
                        render_every = 1
                        fps_multiplier = 1
                        speed_text = "🐌 NORMAL (1x)"
                        speed_color = (100, 255, 100)
                    
                    env.set_time_multiplier(time_multiplier)
                    print(f"Actual Speed: {speed_text}")
        
        if paused:
            if render:
                env.render()
            continue
        
        # Only take action if trash
        if env.trashes:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            
            total_actions += 1
            if reward > 0:
                correct_actions += 1
            
            if training:
                agent.learn(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
        else:
            next_state, reward, done = env.step(0)
            state = next_state
            total_reward += reward
        
        # Render based on mode
        frame_count += 1
        if render and frame_count % render_every == 0:
            env.screen.fill((220, 220, 220))
            
            for container in env.containers:
                container.draw(env.screen)
            for trash in env.trashes:
                trash.draw(env.screen)
            
            # Info of game
            current_level = min(env.actual_level, len(levels) - 1)
            game_secs = env.game_time // 1000
            total_secs = levels[current_level]["duration"]
            remaining = max(0, total_secs - game_secs)
            percent = min(100, (game_secs / total_secs) * 100)
            
            font = pygame.font.Font(None, 36)
            info = f"Level: {current_level + 1}/10 | Score: {env.score} | Life: {env.life_bar} | {remaining}s ({percent:.0f}%)"
            env.screen.blit(font.render(info, True, (0, 0, 0)), (10, 10))
            
            # Info during training
            if training:
                font24 = pygame.font.Font(None, 24)
                epsilon_text = f"Epsilon: {agent.epsilon:.3f}"
                accuracy_text = f"Accuracy: {(correct_actions/max(total_actions,1)*100):.1f}%"
                episode_text = f"Episode: {episode_num}"
                
                # Background 
                info_surface = pygame.Surface((280, 120))
                info_surface.set_alpha(200)
                info_surface.fill((0, 0, 0))
                env.screen.blit(info_surface, (WIDTH - 290, 50))
                
                # Text
                env.screen.blit(font24.render(episode_text, True, (255, 255, 255)), (WIDTH - 280, 60))
                env.screen.blit(font24.render(epsilon_text, True, (255, 255, 255)), (WIDTH - 280, 80))
                env.screen.blit(font24.render(accuracy_text, True, (255, 255, 255)), (WIDTH - 280, 100))
                env.screen.blit(font24.render(speed_text, True, speed_color), (WIDTH - 280, 120))
                
                
                controls_text = "SPACE: Pause | F: Change Speed | ESC: EXIT"
                control_font = pygame.font.Font(None, 20)
                env.screen.blit(control_font.render(controls_text, True, (76, 185, 39)), (10, HEIGHT - 25))
            
            pygame.display.flip()
            env.clock.tick(FPS * fps_multiplier)
        
        if done:
            duration = (pygame.time.get_ticks() - start_time) // 1000
            accuracy = (correct_actions / max(total_actions, 1)) * 100
            game_duration = env.game_time // 1000 
            
            if training:
                print(f"💀 Episode {episode_num} Finished")
                print(f"   Life: {env.life_bar} | accuracy: {accuracy:.1f}%")
            
            return total_reward, game_duration, correct_actions, total_actions
