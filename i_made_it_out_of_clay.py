# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

class Dreidel_Game:
    """A class to construct and play a game of Dreidel"""
    
    
    def __init__(self, player_count, ante_count, gelt_start_count, max_turns, \
                 verbose=False):
        
        self.ante_count = ante_count
        self.player_count = player_count
        self.gelt_start_count = gelt_start_count
        
        self.verbose = verbose
        self.max_turns = max_turns
        self.current_player = 0
    
    def initialize_states(self):
        
        self.turn_count = 0
        self.pot_size = self.ante_count * self.player_count
        self.wallets = np.ones(self. player_count) * \
                       (self.gelt_start_count - self.ante_count)
        self.current_player = 0
        
    def ante_up(self):
        """take from players wallets to fill the pot"""
        
        for ind, wallet in enumerate(self.wallets):
                    if wallet >= self.ante_count:
                        self.pot_size += self.ante_count
                        self.wallets[ind] -= self.ante_count
                    else:
                        self.pot_size += wallet
                        self.wallets[ind] = 0
    
    def take_turn(self):
        """play one round of dreidel"""
        
        if self.wallets[self.current_player] > 0:
            
            self.turn_count += 1 # only update if player can play
            
            spin_value = np.random.randint(4)
            
            if spin_value == 0:
                '''nun'''
                if self.verbose: print(f"Player {self.current_player+1} \
                                         spinned a nun")
            elif spin_value == 1:
                '''spun a gimmel, get all'''
                if self.verbose: print(f"Player {self.current_player+1} \
                                         spinned a gimmel")
                self.wallets[self.current_player] += self.pot_size
                self.pot_size = 0
                
                self.ante_up()
                        
            elif spin_value == 2:
                '''spun a Hey, get half'''
                if self.verbose: print(f"Player {self.current_player+1} \
                                         spinned a Hey")
                winnings = np.floor(self.pot_size/2)
                self.wallets[self.current_player] += winnings
                self.pot_size -= winnings
                
                if self.pot_size == 0:
                    self.ante_up()
                               
            else:
                '''spun a shin, give one'''
                if self.verbose: print(f"Player {self.current_player+1} \
                                         spinned a shin")
                self.wallets[self.current_player] -= 1
                self.pot_size += 1
                
            if self.verbose: print(f"Pot size: {self.pot_size}, wallets={self.wallets}")
                
                      
            assert (self.pot_size + self.wallets.sum() <= self.player_count * self.gelt_start_count), \
            f"Inflation! There is more gelt in circulation than at game start"
            
            assert (self.pot_size > 0), f"Pot size is {self.pot_size} on turn {self.turn_count}"
            
            assert (self.wallets.min() >= 0), "Somebody has negative gelt"
            
        # finally!   
        self.current_player += 1
        if self.current_player > len(self.wallets)-1: self.current_player = 0
        
    
    def play_game(self):
        """Main function to play one game of dreidel with the 
           given configuration"""
           
        self.initialize_states()
        
        while np.count_nonzero(self.wallets) > 1 and self.turn_count < 5000:
            
            
            if self.verbose: print(f'Turn: {self.turn_count} wallets are \
                                     {self.wallets}. \
                                     The pot is {self.pot_size}')
            
            self.take_turn()
            
        # whoever wins gets the contents of the pot
        self.wallets[self.wallets.argmax()] += self.pot_size
            
        if self.verbose: print(f'It took {self.turn_count} turns. \
                                 Winner has {self.wallets.max()} gelt')
        
        if self.turn_count >= self.max_turns: self.turn_count = self.max_turns
        
        return (self.turn_count, self.wallets.max())
        
    def analyze_configuration(self, games_to_play=500):
        """run repeated games with the given configuration. Plot the results
           in a histogram"""
        
        
        print(f'Running {games_to_play} simulations')
        
        self.counts = np.zeros(games_to_play)
        self.winnings = np.zeros(games_to_play)
        
        for ind in range(games_to_play):
            
            count, win = self.play_game()
            self.counts[ind] = count
            self.winnings[ind] = win
            
        f, a = plt.subplots(nrows=1, ncols=2)
        
        f.suptitle(f'Players={self.player_count}, ante size={self.ante_count}, starting gelt={self.gelt_start_count}')
        
        a[0].hist(self.counts, bins=60, cumulative=False, normed=True)
        a[0].set_title(f'Probability Density')
        a[0].xaxis.set_label_text('number of turns')
        a[0].yaxis.set_label_text('number of turns')
        
        a[1].hist(self.counts, bins=120, cumulative=True, normed=True)
        a[1].set_title(f'Cumulative')
        a[1].xaxis.set_label_text('number of turns')
        plt.show()
  

plt.close('all') 
         
g = Dreidel_Game(2, 1, 3, 500, verbose=False)
g.play_game()
g.analyze_configuration(games_to_play=3000)               
   
 
g = Dreidel_Game(2, 1, 4, 500, verbose=False)
g.play_game()
g.analyze_configuration(games_to_play=3000)

g = Dreidel_Game(4, 1, 3, 500, verbose=False)
g.play_game()
g.analyze_configuration(games_to_play=3000)


        