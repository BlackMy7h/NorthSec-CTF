# python3 solver.py
import copy

MASK_64 = 0xFFFFFFFFFFFFFFFF

class State:
    def __init__(self):
        self.rng = 0x9e3779b97f4a7c15
        self.mask = 0xA5A5F00DCAFEBEEF
        self.ops = 0
        self.rounds = 0
        self.hits = 0
        self.busts = 0
        self.path = ""

    def next_rng(self):
        x = self.rng
        x ^= (x >> 12) & MASK_64
        x ^= (x << 25) & MASK_64
        x ^= (x >> 27) & MASK_64
        self.rng = x
        return ((x * 0x2545F4914F6CDD1D) & MASK_64) >> 32

    def deal(self):
        return (self.next_rng() % 10) + 12

    def draw(self):
        return (self.next_rng() % 10) + 1

    def push_history(self, v):
        self.ops += 1
        self.mask ^= (v << (self.ops % 57)) & MASK_64
        self.mask = (self.mask * 0x9E3779B97F4A7C15) & MASK_64

    def finalize_history(self):
        x = self.mask ^ (self.ops * 0x1337)
        x ^= (x >> 33)
        x = (x * 0xff51afd7ed558ccd) & MASK_64
        x ^= (x >> 33)
        x ^= (x >> 33)
        x = (x * 0xff51afd7ed558ccd) & MASK_64
        x ^= (x >> 33)
        return x

def solve():
    initial_state = State()
    queue = [initial_state]

    # BFS/DFS to find the trigger state
    while queue:
        st = queue.pop(0)
        
        # Check winning condition
        if st.rounds > 6 and st.busts >= 3 and (st.finalize_history() & 0xFF) == 0x42:
            print(f"[+] Found winning path! Send this: {st.path}")
            return st.path
        
        # Prevent infinite loops (cap at 15 rounds)
        if st.rounds > 15:
            continue

        # Simulate a round
        player = st.deal()
        dealer = st.deal()

        # Branch 1: Player Stands immediately
        st_stand = copy.deepcopy(st)
        st_stand.push_history(0)
        st_stand.rounds += 1
        st_stand.path += "s\n"
        queue.append(st_stand)

        # Branch 2: Player Hits (we can hit multiple times, but let's just simulate 1 hit per round for simplicity, 
        # or expand this loop to allow multiple hits until bust)
        st_hit = copy.deepcopy(st)
        st_hit.push_history(1)
        st_hit.hits += 1
        st_hit.path += "h\n"
        player += st_hit.draw()
        
        if player > 21:
            st_hit.push_history(0)
            st_hit.busts += 1
            st_hit.rounds += 1
            st_hit.path += "s\n" # assuming automatic stand/end of round on bust
        else:
            # If not busted, player eventually has to stand to end the round
            st_hit.push_history(0)
            st_hit.rounds += 1
            st_hit.path += "s\n"
        
        queue.append(st_hit)

solve()
