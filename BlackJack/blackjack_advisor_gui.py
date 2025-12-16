import tkinter as tk
from tkinter import ttk, messagebox
import blackjack_advisor as ba

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        (r1,g1,b1) = self.winfo_rgb(self.color1)
        (r2,g2,b2) = self.winfo_rgb(self.color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.tag_lower("gradient")

class BlackjackAdvisorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Advisor")
        self.root.geometry("650x550")
        
        # Gradient Background (Casino Green)
        self.gradient_bg = GradientFrame(root, "#053d1e", "#1e824c", highlightthickness=0)
        self.gradient_bg.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.running_count = 0
        self.cards_seen_total = 0
        self.num_decks = 8
        self.rules = {'s17': True, 'das': False, 'surrender': False}
        
        self.create_widgets()
        self.reset_session()

    def create_widgets(self):
        # Main container with padding to show gradient
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(main_container, text="Configuration (School Tournament Rules)")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(config_frame, text="Decks:").pack(side="left", padx=5)
        self.decks_var = tk.IntVar(value=8)
        ttk.Entry(config_frame, textvariable=self.decks_var, width=5).pack(side="left", padx=5)
        
        # H17: Dealer Hits Soft 17. If True, s17=False.
        self.h17_var = tk.BooleanVar(value=False) 
        ttk.Checkbutton(config_frame, text="H17", variable=self.h17_var).pack(side="left", padx=5)
        
        self.das_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="DAS", variable=self.das_var).pack(side="left", padx=5)
        
        self.surrender_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Surrender", variable=self.surrender_var).pack(side="left", padx=5)
        
        ttk.Button(config_frame, text="Reset / Apply", command=self.reset_session).pack(side="right", padx=10)

        # --- Status Frame ---
        status_frame = ttk.LabelFrame(main_container, text="Status")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for status
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(2, weight=1)
        status_frame.columnconfigure(3, weight=1)

        self.rc_label = ttk.Label(status_frame, text="RC: 0", font=("Arial", 12, "bold"))
        self.rc_label.grid(row=0, column=0, pady=10)
        
        self.tc_label = ttk.Label(status_frame, text="TC: 0.0", font=("Arial", 12, "bold"), foreground="blue")
        self.tc_label.grid(row=0, column=1, pady=10)
        
        self.seen_label = ttk.Label(status_frame, text="Cards: 0")
        self.seen_label.grid(row=0, column=2, pady=10)
        
        self.decks_left_label = ttk.Label(status_frame, text="Decks Left: 6.00")
        self.decks_left_label.grid(row=0, column=3, pady=10)

        # Betting Advice Label
        self.bet_label = ttk.Label(status_frame, text="Bet: 1 Unit", font=("Arial", 12, "bold"), foreground="#d9534f")
        self.bet_label.grid(row=1, column=0, columnspan=4, pady=(0, 10))

        # --- Main Content Area ---
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # --- Card Input (Counting) ---
        card_frame = ttk.LabelFrame(content_frame, text="Add Seen Cards (Updates Count)")
        card_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        # Grid 4 columns
        for i, card in enumerate(cards):
            btn = ttk.Button(card_frame, text=card, width=4, command=lambda c=card: self.add_card(c))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="ew")
            
        # Undo button
        ttk.Button(card_frame, text="Undo Last", command=self.undo_last_card).grid(row=4, column=0, columnspan=4, pady=10, sticky="ew", padx=5)

        # --- Recommendation ---
        rec_frame = ttk.LabelFrame(content_frame, text="Get Recommendation")
        rec_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ttk.Label(rec_frame, text="Player Hand (e.g. 'A 6 2'):").pack(pady=(10, 2))
        self.p_hand_entry = ttk.Entry(rec_frame)
        self.p_hand_entry.pack(pady=2, padx=10, fill="x")
        
        ttk.Label(rec_frame, text="Dealer Upcard (e.g. '10'):").pack(pady=(10, 2))
        self.d_card_entry = ttk.Entry(rec_frame)
        self.d_card_entry.pack(pady=2, padx=10, fill="x")
        
        ttk.Button(rec_frame, text="Get Advice", command=self.get_advice).pack(pady=15)
        
        self.result_label = ttk.Label(rec_frame, text="", font=("Arial", 11, "bold"), wraplength=250, justify="center")
        self.result_label.pack(pady=5, padx=5)
        
        self.history = [] # To store history for undo

    def reset_session(self):
        try:
            self.num_decks = self.decks_var.get()
        except:
            self.num_decks = 8
            
        # Update rules
        self.rules['s17'] = not self.h17_var.get()
        self.rules['das'] = self.das_var.get()
        self.rules['surrender'] = self.surrender_var.get()
        
        self.running_count = 0
        self.cards_seen_total = 0
        self.history = []
        self.update_status()
        self.result_label.config(text="")

    def add_card(self, card_str):
        val = ba.get_hilo_value(card_str)
        self.running_count += val
        self.cards_seen_total += 1
        self.history.append(val)
        self.update_status()
        
    def undo_last_card(self):
        if not self.history:
            return
        val = self.history.pop()
        self.running_count -= val
        self.cards_seen_total -= 1
        self.update_status()

    def update_status(self):
        decks_remaining = self.num_decks - (self.cards_seen_total / 52.0)
        if decks_remaining < 0.5: decks_remaining = 0.5
        
        true_count = self.running_count / decks_remaining
        
        self.rc_label.config(text=f"RC: {self.running_count}")
        self.tc_label.config(text=f"TC: {true_count:.1f}")
        self.seen_label.config(text=f"Cards: {self.cards_seen_total}")
        self.decks_left_label.config(text=f"Decks Left: {decks_remaining:.2f}")
        
        # Betting Strategy (Standard Hi-Lo Ramp)
        # TC <= 1: 1 Unit (Min Bet)
        # TC increases -> Bet increases
        if true_count < 1.5:
            units = 1
        elif true_count < 2.5:
            units = 2
        elif true_count < 3.5:
            units = 3
        elif true_count < 4.5:
            units = 4
        else:
            units = 5
            
        self.bet_label.config(text=f"RECOMMENDED BET: {units} UNIT(S)")
        
        return true_count

    def get_advice(self):
        p_text = self.p_hand_entry.get()
        d_text = self.d_card_entry.get()
        
        p_hand = ba.parse_cards(p_text)
        d_card = ba.parse_cards(d_text)
        
        if len(p_hand) < 2:
            self.result_label.config(text="Error: Player needs at least 2 cards", foreground="red")
            return
        if len(d_card) != 1:
            self.result_label.config(text="Error: Dealer needs 1 card", foreground="red")
            return
            
        true_count = self.update_status() # Get current TC
        
        basic_action = ba.get_basic_strategy(p_hand, d_card[0], self.rules)
        final_action, reason = ba.apply_deviations(basic_action, p_hand, d_card[0], true_count, self.rules)
        
        # Insurance Check (Hi-Lo Index >= 3)
        if d_card[0] == 'A' and true_count >= 3:
            final_action += "\n[TAKE INSURANCE]"
            reason += " Insurance is profitable (TC >= 3)."

        color = "green"
        if "STAND" in final_action: color = "red"
        elif "DOUBLE" in final_action: color = "blue"
        elif "SPLIT" in final_action: color = "orange"
        
        self.result_label.config(text=f"{final_action}\n\n{reason}", foreground=color)

if __name__ == "__main__":
    root = tk.Tk()
    # Set theme if available
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass
    app = BlackjackAdvisorGUI(root)
    root.mainloop()
