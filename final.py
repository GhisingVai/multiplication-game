import tkinter as tk
from tkinter import messagebox
from functools import partial

# ----------------------------
# Class Definitions
# ----------------------------

# Represents the state of the game including the current number, scores, bank and whose turn it is.
class GameState:
    def __init__(self, number, human_score, computer_score, bank, human_turn):
        self.number = number                    # Current number in the game
        self.human_score = human_score          # Current score for the human player
        self.computer_score = computer_score    # Current score for the computer
        self.bank = bank                        # Bank points accumulated
        self.human_turn = human_turn            # Boolean: True if it's human's turn, False otherwise

# Represents a node in the game tree, storing a game state, the move that led to this state, and child nodes.
class GameTreeNode:
    def __init__(self, state, move=None):
        self.state = state      # The game state at this node
        self.move = move        # The multiplier used to reach this state (2, 3, or 4)
        self.children = []      # List of child nodes (subsequent moves)

# ----------------------------
# Game Tree and Evaluation Functions
# ----------------------------

# Simulates a move by applying a multiplier to the current state's number and updating scores and bank.
def simulate_move(state, multiplier):
    new_number = state.number * multiplier

    # Update scores based on whose turn it is and whether new_number is even or odd.
    if state.human_turn:
        new_human_score = state.human_score + (-1 if new_number % 2 == 0 else 1)
        new_computer_score = state.computer_score
    else:
        new_computer_score = state.computer_score + (-1 if new_number % 2 == 0 else 1)
        new_human_score = state.human_score

    # Update bank: if the last digit of new_number is 0 or 5, increase the bank by 1.
    new_bank = state.bank + (1 if (new_number % 10 == 0 or new_number % 10 == 5) else 0)

    # Return a new GameState with the updated values and toggle the turn.
    return GameState(new_number, new_human_score, new_computer_score, new_bank, not state.human_turn)

# Recursively generates the game tree up to a given depth.
def generate_game_tree(node, depth):
    # Stop recursion if depth is zero or if the current number is 5000 or above.
    if depth == 0 or node.state.number >= 5000:
        return

    # For each possible multiplier (2, 3, 4), simulate the move and create a new child node.
    for m in [2, 3, 4]:
        child_state = simulate_move(node.state, m)
        child_node = GameTreeNode(child_state, m)
        node.children.append(child_node)
        generate_game_tree(child_node, depth - 1)

# Evaluates the game state and returns a score indicating how favorable it is.
def evaluate_state(state, initial_human_start):
    # If the game-ending condition is reached (number >= 5000), determine the final score.
    if state.number >= 5000:
        if state.human_turn:
            computer_final = state.computer_score + state.bank
            human_final = state.human_score
            # Return infinity if computer wins, negative infinity otherwise.
            return float('inf') if computer_final > human_final else float('-inf')
        else:
            human_final = state.human_score + state.bank
            computer_final = state.computer_score
            return float('-inf') if human_final > computer_final else float('inf')

    # Evaluation for the computer's turn.
    if not state.human_turn:
        # Check for a specific pattern when human started (e.g., a ×3 pattern)
        human_pattern = (initial_human_start and 
                         state.number % 3 == 0 and 
                         (state.number // 3) % 3 == 0)

        # Apply a strong penalty if the human's pattern continues.
        if human_pattern:
            return -3.0

        # Add bonus if the number is odd; if multiplying by 3 makes it odd, a smaller bonus is applied.
        if state.number % 2 == 1:
            odd_bonus = 2.5
        elif state.number * 3 % 2 == 1:
            odd_bonus = 1.5
        else:
            odd_bonus = 0

        progress = state.number / 5000
        score_diff = state.computer_score - state.human_score
        bank_value = (0.4 + 0.6 * progress) * state.bank

        # Combine the various components into the final evaluation score.
        return (score_diff * 4) + bank_value + odd_bonus + (0.15 * progress)

    # Evaluation for the human's turn (simpler calculation).
    progress = state.number / 5000
    score_diff = state.human_score - state.computer_score
    bank_value = (0.4 + 0.6 * progress) * state.bank
    return (score_diff * 4) + bank_value + (0.15 * progress)

# ----------------------------
# Alpha–Beta Pruning Implementation
# ----------------------------

def alphabeta(node, depth, alpha, beta, maximizingPlayer, initial_human_start):
    # If at leaf node or game-ending condition, evaluate the state.
    if depth == 0 or node.state.number >= 5000 or not node.children:
        return evaluate_state(node.state, initial_human_start)

    if maximizingPlayer:
        value = float('-inf')
        # Loop over each child and update the best value for the maximizing player.
        for child in node.children:
            value = max(value, alphabeta(child, depth-1, alpha, beta, False, initial_human_start))
            alpha = max(alpha, value)
            # Prune branches that cannot influence the outcome.
            if beta <= alpha:
                break
        return value
    else:
        value = float('inf')
        # Loop over each child and update the best value for the minimizing player.
        for child in node.children:
            value = min(value, alphabeta(child, depth-1, alpha, beta, True, initial_human_start))
            beta = min(beta, value)
            # Prune branches that cannot influence the outcome.
            if beta <= alpha:
                break
        return value

# Decision function that uses alpha-beta pruning to determine the best move.
def minimax_decision(state, initial_human_start, depth=5):
    # Create the root of the game tree.
    root = GameTreeNode(state)
    generate_game_tree(root, depth)

    best_value = float('-inf')
    best_moves = []

    # Evaluate each possible move from the root.
    for child in root.children:
        value = alphabeta(child, depth-1, float('-inf'), float('inf'), False, initial_human_start)
        # Update the best move list based on the evaluation.
        if value > best_value:
            best_value = value
            best_moves = [child.move]
        elif value == best_value:
            best_moves.append(child.move)

    # When the computer can choose, further prioritize based on game-specific strategy.
    if not state.human_turn:
        human_pattern = (initial_human_start and 
                         state.number % 3 == 0 and 
                         (state.number // 3) % 3 == 0)
        if human_pattern:
            non_3_moves = [m for m in best_moves if m != 3]
            if non_3_moves:
                return max(non_3_moves)  # Prefer ×4 over ×2 if available

        odd_moves = [m for m in best_moves if (state.number * m) % 2 == 1]
        if odd_moves:
            return max(odd_moves)

        bank_moves = [m for m in best_moves if (state.number * m) % 10 in [0, 5]]
        if bank_moves:
            return max(bank_moves)

    # Return the move with the highest multiplier from the best moves list.
    return max(best_moves) if best_moves else 3

# ----------------------------
# Pure Minimax Implementation (Without Alpha–Beta Pruning)
# ----------------------------

def minimax_no_ab(node, depth, maximizingPlayer, initial_human_start):
    # Base condition: evaluate the state if at a leaf node or game over.
    if depth == 0 or node.state.number >= 5000 or not node.children:
        return evaluate_state(node.state, initial_human_start)
    
    if maximizingPlayer:
        value = float('-inf')
        # Recursively determine the maximum value.
        for child in node.children:
            value = max(value, minimax_no_ab(child, depth-1, False, initial_human_start))
        return value
    else:
        value = float('inf')
        # Recursively determine the minimum value.
        for child in node.children:
            value = min(value, minimax_no_ab(child, depth-1, True, initial_human_start))
        return value

# Decision function using pure minimax (without pruning) to select the best move.
def minimax_decision_no_ab(current_state, initial_human_start, depth=5):
    # Create the root of the game tree.
    root = GameTreeNode(current_state)
    generate_game_tree(root, depth)

    best_value = float('-inf')
    best_moves = []

    # Evaluate each move from the root.
    for child in root.children:
        value = minimax_no_ab(child, depth-1, False, initial_human_start)
        if value > best_value:
            best_value = value
            best_moves = [child.move]
        elif value == best_value:
            best_moves.append(child.move)

    # Additional strategy if it's the computer's turn.
    if not current_state.human_turn:
        human_pattern = (initial_human_start and 
                         current_state.number % 3 == 0 and 
                         (current_state.number // 3) % 3 == 0)
        if human_pattern:
            non_3_moves = [m for m in best_moves if m != 3]
            if non_3_moves:
                return max(non_3_moves)
        odd_moves = [m for m in best_moves if (current_state.number * m) % 2 == 1]
        if odd_moves:
            return max(odd_moves)
        bank_moves = [m for m in best_moves if (current_state.number * m) % 10 in [0, 5]]
        if bank_moves:
            return max(bank_moves)

    return max(best_moves) if best_moves else 3

# ----------------------------
# Graphical User Interface (GUI) Implementation
# ----------------------------

# Main game class that handles the GUI and game logic.
class MultiplicationGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Strategic Multiplication Game")
        self.root.geometry("450x750")

        # Initialize game variables.
        self.current_number = 0
        self.human_score = 0
        self.computer_score = 0
        self.bank = 0
        self.human_turn = True
        self.game_active = False
        self.initial_human_start = True

        # Set up the user interface.
        self.setup_ui()

    def setup_ui(self):
        # ----------------------------
        # Welcome Frame: Allows user to choose game settings.
        # ----------------------------
        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(pady=20)

        # Game title.
        tk.Label(self.welcome_frame, text="Strategic Multiplication Game", font=("Arial", 16)).pack()

        # Input field for the starting number.
        tk.Label(self.welcome_frame, text="Starting number (25-40):").pack(pady=5)
        self.start_entry = tk.Entry(self.welcome_frame)
        self.start_entry.pack()

        # Radio buttons to choose who goes first.
        self.first_player = tk.StringVar(value="human")
        tk.Label(self.welcome_frame, text="First player:").pack(pady=5)
        tk.Radiobutton(self.welcome_frame, text="Human", variable=self.first_player, value="human").pack()
        tk.Radiobutton(self.welcome_frame, text="Computer", variable=self.first_player, value="computer").pack()

        # Radio buttons to select the algorithm (AlphaBeta or pure Minimax).
        self.algorithm = tk.StringVar(value="alphabeta")
        tk.Label(self.welcome_frame, text="Algorithm:").pack(pady=5)
        tk.Radiobutton(self.welcome_frame, text="AlphaBeta", variable=self.algorithm, value="alphabeta").pack()
        tk.Radiobutton(self.welcome_frame, text="Minimax", variable=self.algorithm, value="minimax").pack()

        # Button to start the game.
        tk.Button(self.welcome_frame, text="Start Game", command=self.start_game).pack(pady=20)

        # ----------------------------
        # Game Frame: Displays game status, buttons, and logs.
        # ----------------------------
        self.game_frame = tk.Frame(self.root)

        # Label to show current game status (number, scores, bank, turn).
        self.status_label = tk.Label(self.game_frame, font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Frame to hold multiplier buttons.
        self.button_frame = tk.Frame(self.game_frame)
        self.button_frame.pack(pady=10)

        # Create multiplier buttons for 2, 3, and 4.
        self.mult_buttons = []
        for i, mult in enumerate([2, 3, 4]):
            btn = tk.Button(self.button_frame, text=f"×{mult}", width=5,
                            command=partial(self.human_move, mult))
            btn.grid(row=0, column=i, padx=5)
            self.mult_buttons.append(btn)
            btn.config(state="disabled")  # Disable buttons until game starts.

        # Text widget to display game logs.
        self.log_text = tk.Text(self.game_frame, height=10, width=40, state="disabled")
        self.log_text.pack(pady=10)

        # Label to display the winner once the game is over.
        self.winner_label = tk.Label(self.game_frame, font=("Arial", 14, "bold"))

        # ----------------------------
        # Control Frame: Contains New Game and Quit buttons.
        # ----------------------------
        self.control_frame = tk.Frame(self.root)
        tk.Button(self.control_frame, text="New Game", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=5)

    # ----------------------------
    # Game Initialization and Update Methods
    # ----------------------------

    # Starts the game after validating the input.
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

                # Hide welcome frame and display game and control frames.
                self.welcome_frame.pack_forget()
                self.game_frame.pack()
                self.control_frame.pack(pady=10)

                self.update_display()
                self.log_message(f"Game started with {self.current_number}")

                # If computer goes first, schedule its move.
                if not self.human_turn:
                    self.root.after(1000, self.computer_move)
            else:
                messagebox.showerror("Error", "Number must be between 25-40")
        except ValueError:
            messagebox.showerror("Error", "Invalid number")

    # Updates the game status display and the state of the multiplier buttons.
    def update_display(self):
        status = (
            f"Number: {self.current_number}\n"
            f"Human: {self.human_score}  Computer: {self.computer_score}\n"
            f"Bank: {self.bank}\n"
            f"{'Your turn' if self.human_turn else 'Computer thinking...'}"
        )
        self.status_label.config(text=status)

        # Enable multiplier buttons only during the human's turn.
        for btn in self.mult_buttons:
            btn.config(state="normal" if self.human_turn else "disabled")

    # Appends a message to the game log.
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    # ----------------------------
    # Game Moves: Human and Computer Moves
    # ----------------------------

    # Handles the human player's move.
    def human_move(self, multiplier):
        if not self.human_turn or not self.game_active:
            return

        # Update the current number based on the chosen multiplier.
        self.current_number *= multiplier
        self.update_score()
        self.log_message(f"You multiplied by {multiplier} → {self.current_number}")

        # Check if the game is over after the move.
        if self.check_game_over():
            return

        # Switch turn to computer and update display.
        self.human_turn = False
        self.update_display()
        self.root.after(1000, self.computer_move)

    # Handles the computer player's move.
    def computer_move(self):
        if self.human_turn or not self.game_active:
            return

        # Create a game state object from the current game variables.
        state = GameState(
            self.current_number,
            self.human_score,
            self.computer_score,
            self.bank,
            self.human_turn
        )

        # Choose the decision algorithm based on the user's selection.
        if self.algorithm.get() == "minimax":
            multiplier = minimax_decision_no_ab(state, self.initial_human_start)
        else:
            multiplier = minimax_decision(state, self.initial_human_start)

        # Update the current number and score based on the computer's move.
        self.current_number *= multiplier
        self.update_score()
        self.log_message(f"Computer multiplied by {multiplier} → {self.current_number}")

        # Check if the game is over after the move.
        if self.check_game_over():
            return

        # Switch turn back to the human and update display.
        self.human_turn = True
        self.update_display()

    # Updates the scores and bank based on the current number.
    def update_score(self):
        if self.human_turn:
            # Adjust human score: subtract if even, add if odd.
            if self.current_number % 2 == 0:
                self.human_score -= 1
            else:
                self.human_score += 1
        else:
            # Adjust computer score: subtract if even, add if odd.
            if self.current_number % 2 == 0:
                self.computer_score -= 1
            else:
                self.computer_score += 1

        # Increase bank if the current number ends in 0 or 5.
        if self.current_number % 10 in [0, 5]:
            self.bank += 1

    # Checks if the game is over (i.e. current number >= 5000) and declares a winner or draw.
    def check_game_over(self):
        if self.current_number >= 5000:
            # Add bank points to the player who made the last move.
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

    # Resets the game to the initial state.
    def reset_game(self):
        self.game_frame.pack_forget()
        self.control_frame.pack_forget()
        self.winner_label.pack_forget()
        self.welcome_frame.pack()
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

# ----------------------------
# Program Entry Point
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = MultiplicationGame(root)
    root.mainloop()
