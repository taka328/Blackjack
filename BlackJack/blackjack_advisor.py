import math

def get_card_value(card_str):
    """
    Returns the numeric value of a card string for hand totaling.
    Returns 11 for Ace (handling soft/hard logic elsewhere).
    Returns 10 for face cards.
    """
    card_str = card_str.upper()
    if card_str in ['J', 'Q', 'K', '10']:
        return 10
    elif card_str == 'A':
        return 11
    elif card_str.isdigit():
        val = int(card_str)
        if 2 <= val <= 9:
            return val
    return None

def get_hilo_value(card_str):
    """
    Returns the Hi-Lo count value for a card.
    2-6: +1
    7-9: 0
    10, J, Q, K, A: -1
    """
    card_str = card_str.upper()
    if card_str in ['2', '3', '4', '5', '6']:
        return 1
    elif card_str in ['7', '8', '9']:
        return 0
    elif card_str in ['10', 'J', 'Q', 'K', 'A']:
        return -1
    return 0

def parse_cards(input_str):
    """
    Parses a string of cards separated by spaces.
    Returns a list of valid card strings.
    """
    tokens = input_str.strip().split()
    valid_cards = []
    for token in tokens:
        token = token.upper()
        if token in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
            valid_cards.append(token)
        else:
            print(f"Warning: Ignored invalid token '{token}'")
    return valid_cards

def calculate_hand(cards):
    """
    Calculates the total, whether it's soft, and if it's a pair.
    Returns (total, is_soft, is_pair)
    """
    if not cards:
        return 0, False, False
    
    total = 0
    aces = 0
    for card in cards:
        val = get_card_value(card)
        total += val
        if val == 11:
            aces += 1
            
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
        
    is_soft = (aces > 0)
    is_pair = (len(cards) == 2 and get_card_value(cards[0]) == get_card_value(cards[1]))
    
    return total, is_soft, is_pair

def get_basic_strategy(player_hand, dealer_upcard, rules):
    """
    Determines the Basic Strategy move.
    Returns: Action string (HIT, STAND, DOUBLE, SPLIT, SURRENDER)
    """
    p_total, is_soft, is_pair = calculate_hand(player_hand)
    d_val = get_card_value(dealer_upcard)
    
    # Unpack rules
    # rules = {'s17': True/False, 'das': True/False, 'surrender': True/False}
    
    # SURRENDER LOGIC (Simplified common rules)
    if rules.get('surrender', False) and len(player_hand) == 2:
        if p_total == 16 and d_val in [9, 10, 11]:
            return "SURRENDER"
        if p_total == 15 and d_val == 10:
            return "SURRENDER"

    # PAIR SPLITTING
    if is_pair:
        card_val = get_card_value(player_hand[0])
        # Always split Aces and 8s
        if card_val == 11: return "SPLIT"
        if card_val == 8: return "SPLIT"
        
        # Never split 10s, 5s
        if card_val == 10: return "STAND"
        if card_val == 5: 
            # Treat 5s as hard 10
            pass # Fall through to hard totals
        
        elif card_val == 9: # 9,9 vs 2-6, 8, 9 -> Split. Stand vs 7, 10, A
            if d_val in [2,3,4,5,6,8,9]: return "SPLIT"
            else: return "STAND"
            
        elif card_val == 7: # 7,7 vs 2-7 -> Split
            if d_val <= 7: return "SPLIT"
            else: return "HIT"
            
        elif card_val == 6: # 6,6 vs 2-6 -> Split
            if d_val <= 6: return "SPLIT"
            else: return "HIT"
            
        elif card_val == 4: # 4,4 vs 5,6 (sometimes only if DAS)
            if rules.get('das', True) and d_val in [5,6]: return "SPLIT"
            else: return "HIT"
            
        elif card_val in [2, 3]: # 2,2 or 3,3 vs 2-7 (if DAS for 2,3 vs 2,3)
            # Simplified: Split vs 2-7
            if d_val <= 7: return "SPLIT"
            else: return "HIT"
            
        if card_val == 5:
             pass # Handled below as Hard 10

    # SOFT TOTALS
    can_double = (len(player_hand) == 2)
    
    if is_soft:
        if p_total >= 20: # A,9+
            return "STAND"
        elif p_total == 19: # A,8
            # Double vs 6 if H17 (Dealer hits soft 17)
            if d_val == 6 and not rules.get('s17', True): 
                return "DOUBLE" if can_double else "STAND"
            return "STAND"
        elif p_total == 18: # A,7
            if d_val in [2,3,4,5,6]: return "DOUBLE" if can_double else "STAND"
            if d_val in [9,10,11]: return "HIT"
            return "STAND" # vs 7, 8
        elif p_total == 17: # A,6
            if d_val in [3,4,5,6]: return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif p_total in [15, 16]: # A,4 / A,5
            if d_val in [4,5,6]: return "DOUBLE" if can_double else "HIT"
            return "HIT"
        elif p_total in [13, 14]: # A,2 / A,3
            if d_val in [5,6]: return "DOUBLE" if can_double else "HIT"
            return "HIT"
            
    # HARD TOTALS
    if p_total >= 17:
        return "STAND"
    if p_total == 16:
        if d_val in [2,3,4,5,6]: return "STAND"
        return "HIT"
    if p_total == 15:
        if d_val in [2,3,4,5,6]: return "STAND"
        return "HIT"
    if p_total in [13, 14]:
        if d_val in [2,3,4,5,6]: return "STAND"
        return "HIT"
    if p_total == 12:
        if d_val in [4,5,6]: return "STAND"
        return "HIT"
    if p_total == 11:
        return "DOUBLE" if can_double else "HIT"
    if p_total == 10:
        if d_val in [2,3,4,5,6,7,8,9]: return "DOUBLE" if can_double else "HIT"
        return "HIT"
    if p_total == 9:
        if d_val in [3,4,5,6]: return "DOUBLE" if can_double else "HIT"
        return "HIT"
    if p_total <= 8:
        return "HIT"
        
    return "HIT" # Fallback

def apply_deviations(basic_action, player_hand, dealer_upcard, true_count, rules):
    """
    Checks for specific True Count deviations and overrides Basic Strategy.
    Returns (Final Action, Explanation)
    """
    p_total, is_soft, is_pair = calculate_hand(player_hand)
    d_val = get_card_value(dealer_upcard)
    
    explanation = f"Basic strategy says {basic_action}."
    final_action = basic_action
    
    # Deviation: 16 vs 10 -> Stand if TC >= 0
    if p_total == 16 and not is_soft and d_val == 10:
        if true_count >= 0:
            if basic_action == "HIT":
                final_action = "STAND"
                explanation += f" Deviation applies (16 vs 10, TC {true_count:.1f} >= 0) -> STAND."
        else:
            if basic_action == "STAND": # Should be HIT by basic
                pass 
    
    # Deviation: 15 vs 10 -> Stand if TC >= 4
    elif p_total == 15 and not is_soft and d_val == 10:
        if true_count >= 4:
            if basic_action == "HIT":
                final_action = "STAND"
                explanation += f" Deviation applies (15 vs 10, TC {true_count:.1f} >= 4) -> STAND."

    # Deviation: 12 vs 3 -> Stand if TC >= 2
    elif p_total == 12 and not is_soft and d_val == 3:
        if true_count >= 2:
            final_action = "STAND"
            explanation += f" Deviation applies (12 vs 3, TC {true_count:.1f} >= 2) -> STAND."

    # Deviation: 12 vs 2 -> Stand if TC >= 3
    elif p_total == 12 and not is_soft and d_val == 2:
        if true_count >= 3:
            final_action = "STAND"
            explanation += f" Deviation applies (12 vs 2, TC {true_count:.1f} >= 3) -> STAND."

    # Deviation: 10 vs 10 -> Double if TC >= 4
    elif p_total == 10 and not is_soft and d_val == 10:
        if true_count >= 4:
            final_action = "DOUBLE"
            explanation += f" Deviation applies (10 vs 10, TC {true_count:.1f} >= 4) -> DOUBLE."

    # Deviation: 11 vs A -> Double if TC >= 1 (assuming H17/S17 common index)
    elif p_total == 11 and not is_soft and d_val == 11:
        if true_count >= 1:
            final_action = "DOUBLE"
            explanation += f" Deviation applies (11 vs A, TC {true_count:.1f} >= 1) -> DOUBLE."
            
    # Fab 4 Surrender Deviations (Optional but good for "Advanced")
    # 15 vs 10 Surrender if TC >= 0? Usually 16 vs 10 is TC >= 0, 15 vs 10 is TC >= 3 or 4.
    # Keeping it simple to the requested list.
    
    if final_action == basic_action:
        explanation += " No deviation applies."
        
    return final_action, explanation

def print_separator():
    print("-" * 60)

def print_header():
    print_separator()
    print("             BLACKJACK ADVISOR (Hi-Lo System)")
    print_separator()

def print_status(running_count, cards_seen_total, decks_remaining, true_count):
    print("\n" + "="*60)
    print(f" STATUS REPORT")
    print(f" {'Running Count (RC)':<20}: {running_count}")
    print(f" {'True Count (TC)':<20}: {true_count:.1f}")
    print(f" {'Cards Seen':<20}: {cards_seen_total}")
    print(f" {'Decks Remaining':<20}: {decks_remaining:.2f}")
    print("="*60)

def main():
    print_header()
    
    # 1. Setup
    print("STEP 1: TABLE CONFIGURATION")
    try:
        num_decks = int(input("  Enter number of decks in shoe (default 6): ") or "6")
    except ValueError:
        num_decks = 6
        print("  Invalid input, using 6 decks.")
        
    # Rules setup
    print("\nSTEP 2: RULES CONFIGURATION (Press Enter for defaults)")
    rules = {
        's17': True, # Dealer stands on soft 17
        'das': True, # Double after split allowed
        'surrender': True # Late surrender allowed
    }
    
    r_in = input("  Dealer hits soft 17? (y/N): ").lower()
    if r_in == 'y': rules['s17'] = False # H17
    
    r_in = input("  Double after split allowed? (Y/n): ").lower()
    if r_in == 'n': rules['das'] = False
    
    r_in = input("  Surrender allowed? (Y/n): ").lower()
    if r_in == 'n': rules['surrender'] = False
    
    running_count = 0
    cards_seen_total = 0
    
    print("\n" + "*"*60)
    print(" SESSION STARTED")
    print(" Instructions:")
    print("  - Enter cards seen (e.g., '10 A 5') to update count.")
    print("  - Type 'rec' to get a move recommendation.")
    print("  - Type 'reset' when the shoe is shuffled.")
    print("  - Type 'quit' to exit.")
    print("*"*60)
    
    while True:
        # Calculate True Count
        decks_remaining = num_decks - (cards_seen_total / 52.0)
        if decks_remaining < 0.5: decks_remaining = 0.5 # Avoid division by zero/negative
        
        true_count = running_count / decks_remaining
        
        print_status(running_count, cards_seen_total, decks_remaining, true_count)
        
        user_input = input("\nAction (Cards / 'rec' / 'reset' / 'quit'): ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'reset':
            running_count = 0
            cards_seen_total = 0
            print("\n[!] Shoe reset. Counts cleared.")
            continue
        elif user_input.lower() == 'rec':
            # Recommendation Mode
            print("\n--- GET RECOMMENDATION ---")
            p_hand_str = input("  Your Hand (e.g. 'A 6' or 'A 6 2'): ")
            p_hand = parse_cards(p_hand_str)
            if len(p_hand) < 2:
                print("  [!] Invalid hand. Need at least 2 cards.")
                continue
                
            d_card_str = input("  Dealer Upcard (e.g. '10'): ")
            d_card = parse_cards(d_card_str)
            if len(d_card) != 1:
                print("  [!] Invalid upcard.")
                continue
                
            basic_action = get_basic_strategy(p_hand, d_card[0], rules)
            final_action, reason = apply_deviations(basic_action, p_hand, d_card[0], true_count, rules)
            
            print(f"\n  >>> RECOMMENDATION: {final_action}")
            print(f"  >>> Reason: {reason}")
            input("\n  Press Enter to continue...")
            continue
            
        # Card Input Mode
        cards = parse_cards(user_input)
        if not cards:
            continue
            
        for card in cards:
            val = get_hilo_value(card)
            running_count += val
            cards_seen_total += 1
            
        print(f"  -> Processed {len(cards)} cards.")

if __name__ == "__main__":
    main()
