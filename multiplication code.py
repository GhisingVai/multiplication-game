import tkinter as tk
from tkinter import messagebox
from functools import partial
import time

#Class Definition of GameState for holding game state at any moment
class GameState:
    def __init__(self, number, human_score, computer_score, bank, human_turn):
        self.number = number        
        self.human_score = human_score
        self.computer_score = computer_score
        self.bank = bank
        self.human_turn = human_turn

#Class Defination of GameTreeNode for building the game tree.
#Tree will be used for making decision. 
class GameTreeNode:
    def __init__(self, state, move=None):
        self.state = state
        self.move = move
        self.children = []

# This function calculates the result of applying a given multiplier to current state number.
def simulate_move(state, multiplier):
    new_number = state.number * multiplier

    #calculate score based on the players turn 
    #checks if it is even or odd and give score 
    if state.human_turn:
        new_human_score = state.human_score + (-1 if new_number % 2 == 0 else 1)
        new_computer_score = state.computer_score
    else:
        new_computer_score = state.computer_score + (-1 if new_number % 2 == 0 else 1)
        new_human_score = state.human_score

    #For the calculation of bank point
    new_bank = state.bank + (1 if (new_number % 10 == 0 or new_number % 10 == 5) else 0)

    
    return GameState(new_number, new_human_score, new_computer_score, new_bank, not state.human_turn)

#function decleartion for generating the tree with the depth until >5000 is reach
def generate_game_tree(node, depth):
    if depth == 0 or node.state.number >= 5000:
        return
    
    #for loop to simulate the move and create the child node
    for m in [2, 3, 4]:
        child_state = simulate_move(node.state, m)
        child_node = GameTreeNode(child_state, m)
        node.children.append(child_node)
        generate_game_tree(child_node, depth - 1) #generate the game tree for the child node recursively.

#function decleration for assigning the value to game state. 
def evaluate_state(state, initial_human_start):
    if state.number >= 5000:
        if state.human_turn:
            computer_final = state.computer_score + state.bank
            human_final = state.human_score
            return float('inf') if computer_final > human_final else float('-inf')
        else:
            human_final = state.human_score + state.bank
            computer_final = state.computer_score
            return float('-inf') if human_final > computer_final else float('inf')

    #Evaluate the computer turn and check additional condition for herustic evaluation function
    if not state.human_turn:
        #check the human pattern
        human_pattern = (initial_human_start and 
                         state.number % 3 == 0 and 
                         (state.number // 3) % 3 == 0)
        #check if human is using some patern like (2,2,2) or (3,3,3).
        # used in computer turn for hersutic function
        if human_pattern:
            return -3.0
        
        #assigning odd number bonus for herustic function
        if state.number % 2 == 1:
            odd_bonus = 2.5
        elif state.number * 3 % 2 == 1:
            odd_bonus = 1.5
        else:
            odd_bonus = 0

        #variable declaration for herustic function 
        progress = state.number / 5000
        score_diff = state.computer_score - state.human_score
        bank_value = (0.4 + 0.6 * progress) * state.bank
        #herustic function. also it has the human pattern condition involved ehich is metioned above
        return (score_diff * 4) + bank_value + odd_bonus + (0.15 * progress)

    #Evaluate the human turn
    #variable declaration for herustic function 

    progress = state.number / 5000
    score_diff = state.human_score - state.computer_score
    bank_value = (0.4 + 0.6 * progress) * state.bank
    #herustic function
    return (score_diff * 4) + bank_value + (0.15 * progress)

# function of Alpha-Beta Algorithm Implementation
def alphabeta(node, depth, alpha, beta, maximizingPlayer, initial_human_start):
    #checks the condition: if it is base/terminal/maximum depth state 
    if depth == 0 or node.state.number >= 5000 or not node.children:
        return evaluate_state(node.state, initial_human_start)

    if maximizingPlayer:
        value = float('-inf')
        for child in node.children:
            value = max(value, alphabeta(child, depth-1, alpha, beta, False, initial_human_start))
            alpha = max(alpha, value)
            if beta <= alpha:   # Beta cut-off here
                break
        return value
    else:
        value = float('inf')
        for child in node.children:
            value = min(value, alphabeta(child, depth-1, alpha, beta, True, initial_human_start))
            beta = min(beta, value)
            if beta <= alpha: #alpha cut-off here
                break
        return value

# Function to build the game ehich helps alfa-beta algo to chose best move
# this is not minimax algorithm implementation
def minimax_decision(state, initial_human_start, depth=5):
    start_time = time.perf_counter()
    
    #creating root node for the game tree
    root = GameTreeNode(state)
    generate_game_tree(root, depth)

    #defult varible declaration for best value and move
    best_value = float('-inf')
    best_moves = []

    #loop for evaluating move from the root
    for child in root.children:
        value = alphabeta(child, depth-1, float('-inf'), float('inf'), False, initial_human_start)
        if value > best_value:
            best_value = value
            best_moves = [child.move]
        elif value == best_value:
            best_moves.append(child.move)

    #for checking the time consumed for calculation
    elapsed_time = time.perf_counter() - start_time

    #additional herustics factor verification when computer is moving
    if not state.human_turn:
        human_pattern = (initial_human_start and 
                         state.number % 3 == 0 and 
                         (state.number // 3) % 3 == 0)
        if human_pattern:
            non_3_moves = [m for m in best_moves if m != 3]
            if non_3_moves:
                return max(non_3_moves), elapsed_time

        odd_moves = [m for m in best_moves if (state.number * m) % 2 == 1]
        if odd_moves:
            return max(odd_moves), elapsed_time

        bank_moves = [m for m in best_moves if (state.number * m) % 10 in [0, 5]]
        if bank_moves:
            return max(bank_moves), elapsed_time

    return (max(best_moves) if best_moves else 3), elapsed_time

# function for Minimax Algorithm Implementation
def minimax_no_ab(node, depth, maximizingPlayer, initial_human_start):
    #checks the condition: if it is base/terminal/maximum depth state 
    if depth == 0 or node.state.number >= 5000 or not node.children:
        return evaluate_state(node.state, initial_human_start)
    
    #Evaluates for the MAX/MIN value
    if maximizingPlayer:
        value = float('-inf')
        for child in node.children:
            value = max(value, minimax_no_ab(child, depth-1, False, initial_human_start))
        return value
    else:
        value = float('inf')
        for child in node.children:
            value = min(value, minimax_no_ab(child, depth-1, True, initial_human_start))
        return value

def minimax_decision_no_ab(current_state, initial_human_start, depth=5):
    start_time = time.perf_counter()
       
    #creating root node for the game tree
    root = GameTreeNode(current_state)
    generate_game_tree(root, depth)

    best_value = float('-inf')
    best_moves = []

    #loop for evaluating move from the root
    for child in root.children:
        value = minimax_no_ab(child, depth-1, False, initial_human_start)
        if value > best_value:
            best_value = value
            best_moves = [child.move]
        elif value == best_value:
            best_moves.append(child.move)

    elapsed_time = time.perf_counter() - start_time
   
    #additional herustics factor verification when computer is moving
    if not current_state.human_turn:
        human_pattern = (initial_human_start and 
                         current_state.number % 3 == 0 and 
                         (current_state.number // 3) % 3 == 0)
        if human_pattern:
            non_3_moves = [m for m in best_moves if m != 3]
            if non_3_moves:
                return max(non_3_moves), elapsed_time

        odd_moves = [m for m in best_moves if (current_state.number * m) % 2 == 1]
        if odd_moves:
            return max(odd_moves), elapsed_time

        bank_moves = [m for m in best_moves if (current_state.number * m) % 10 in [0, 5]]
        if bank_moves:
            return max(bank_moves), elapsed_time

    return (max(best_moves) if best_moves else 3), elapsed_time

# ----------------------------
# GUI Implementation
# ----------------------------

class MultiplicationGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Strategic Multiplication Game")
        self.root.geometry("450x750")

        self.current_number = 0
        self.human_score = 0
        self.computer_score = 0
        self.bank = 0
        self.human_turn = True
        self.game_active = False
        self.initial_human_start = True

        self.setup_ui()

    def setup_ui(self):
        # Welcome Frame
        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(pady=20)

        tk.Label(self.welcome_frame, text="Group 38 Game", font=("Arial", 16)).pack()
        
        

        tk.Label(self.welcome_frame, text="Starting number (25-40):").pack(pady=5)
        self.start_entry = tk.Entry(self.welcome_frame)
        self.start_entry.pack()

        self.first_player = tk.StringVar(value="human")
        tk.Label(self.welcome_frame, text="First player:").pack(pady=5)
        tk.Radiobutton(self.welcome_frame, text="Human", variable=self.first_player, value="human").pack()
        tk.Radiobutton(self.welcome_frame, text="Computer", variable=self.first_player, value="computer").pack()

        self.algorithm = tk.StringVar(value="alphabeta")
        tk.Label(self.welcome_frame, text="Algorithm:").pack(pady=5)
        tk.Radiobutton(self.welcome_frame, text="AlphaBeta", variable=self.algorithm, value="alphabeta").pack()
        tk.Radiobutton(self.welcome_frame, text="Minimax", variable=self.algorithm, value="minimax").pack()

        tk.Button(self.welcome_frame, text="Start Game", command=self.start_game).pack(pady=20)

        # Game Frame
        self.game_frame = tk.Frame(self.root)
        self.status_label = tk.Label(self.game_frame, font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.button_frame = tk.Frame(self.game_frame)
        self.button_frame.pack(pady=10)

        # Moves button for human player
        self.mult_buttons = []
        for i, mult in enumerate([2, 3, 4]):
            btn = tk.Button(self.button_frame, text=f"×{mult}", width=5,
                           command=partial(self.human_move, mult))
            btn.grid(row=0, column=i, padx=5)
            self.mult_buttons.append(btn)
            btn.config(state="disabled")

        #For creating log
        self.log_text = tk.Text(self.game_frame, height=15, width=40, state="disabled")
        self.log_text.pack(pady=10)

        #for displaying the winner of the game
        self.winner_label = tk.Label(self.game_frame, font=("Arial", 14, "bold"))

        # Control Frame
        self.control_frame = tk.Frame(self.root)
        tk.Button(self.control_frame, text="New Game", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=5)

    def start_game(self):
        try:
            start_num = int(self.start_entry.get())
            if 25 <= start_num <= 40:
                self.current_number = start_num
                self.human_score = 0
                self.computer_score = 0
                self.bank = 0
                self.human_turn = (self.first_player.get() == "human")
                self.initial_human_start = self.human_turn
                self.game_active = True

                self.welcome_frame.pack_forget()
                self.game_frame.pack()
                self.control_frame.pack(pady=10)

                self.update_display()
                self.log_message(f"Game started with {self.current_number}")

                if not self.human_turn:
                    self.root.after(1000, self.computer_move)
            else:
                messagebox.showerror("Error", "Number must be between 25-40")
        except ValueError:
            messagebox.showerror("Error", "Invalid number")

    def update_display(self):
        status = (
            f"Number: {self.current_number}\n"
            f"Human: {self.human_score}  Computer: {self.computer_score}\n"
            f"Bank: {self.bank}\n"
            f"{'Your turn' if self.human_turn else 'Computer thinking...'}"
        )
        self.status_label.config(text=status)

        for btn in self.mult_buttons:
            btn.config(state="normal" if self.human_turn else "disabled")

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def human_move(self, multiplier):
        #for human to go first
        if not self.human_turn or not self.game_active:
            return

        self.current_number *= multiplier
        self.update_score()
        self.log_message(f"You multiplied by {multiplier} → {self.current_number}")

        if self.check_game_over():
            return

        self.human_turn = False
        self.update_display()
        self.root.after(1000, self.computer_move)

    def computer_move(self):
      # for computer to go first
        if self.human_turn or not self.game_active:
            return

        state = GameState(
            self.current_number,
            self.human_score,
            self.computer_score,
            self.bank,
            self.human_turn
        )


        algo_name = "Minimax" if self.algorithm.get() == "minimax" else "Alpha-Beta"
        
        #execution of selected algorithm (alfebeta or minimax)
        if self.algorithm.get() == "minimax":
            multiplier, elapsed_time = minimax_decision_no_ab(state, self.initial_human_start)
        else:
            multiplier, elapsed_time = minimax_decision(state, self.initial_human_start)

        time_complexity = "O(b^d)" if self.algorithm.get() == "minimax" else "O(b^(d/2))"
        
        # Format time with up to 9 decimal places
        formatted_time = "{0:.9f}".format(elapsed_time).rstrip('0').rstrip('.') if '.' in "{0:.9f}".format(elapsed_time) else "{0:.9f}".format(elapsed_time)
        self.log_message(f"Computer used {algo_name} ({time_complexity}) - Decision took {formatted_time} seconds")
        
        self.current_number *= multiplier
        self.update_score()
        self.log_message(f"Computer multiplied by {multiplier} → {self.current_number}")

        if self.check_game_over():
            return

        self.human_turn = True
        self.update_display()

    def update_score(self):
        # for recording the player score and bank score
        if self.human_turn:
            if self.current_number % 2 == 0:
                self.human_score -= 1
            else:
                self.human_score += 1
        else:
            if self.current_number % 2 == 0:
                self.computer_score -= 1
            else:
                self.computer_score += 1

        if self.current_number % 10 in [0, 5]:
            self.bank += 1

    def check_game_over(self):
        #For game ending results
        if self.current_number >= 5000:
            if self.human_turn:
                self.human_score += self.bank
                if self.human_score == self.computer_score:
                    winner = "Draw"
                else:
                    winner = "Human" if self.human_score > self.computer_score else "Computer"
            else:
                self.computer_score += self.bank
                if self.computer_score == self.human_score:
                    winner = "Draw"
                else:
                    winner = "Computer" if self.computer_score > self.human_score else "Human"

            self.game_active = False
            self.update_display()
            self.winner_label.config(
                text=f"Game Over!\n{winner} wins!\n"
                     f"Final Scores:\nHuman: {self.human_score}\n"
                     f"Computer: {self.computer_score}"
            )
            self.winner_label.pack(pady=10)
            return True
        return False

    def reset_game(self):
        #for new game button function
        self.game_frame.pack_forget()
        self.control_frame.pack_forget()
        self.winner_label.pack_forget()
        self.welcome_frame.pack()
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    game = MultiplicationGame(root)
    root.mainloop()