# rl/utils.py
import itertools

# squares: 0..63 (row*8 + col)
def rc_to_sq(r,c): return r*8+c
def sq_to_rc(s): return divmod(s,8)

# Promotion types: 0=no, 1=queen,2=rook,3=bishop,4=knight
PROM_TYPES = [0,1,2,3,4]

# Build action mapping: (from_sq, to_sq, promo) -> index
ACTION_LIST = []
for fr in range(64):
    for to in range(64):
        # allow promo flags even if not used always
        for promo in PROM_TYPES:
            ACTION_LIST.append((fr,to,promo))
ACTION_TO_INDEX = {a:i for i,a in enumerate(ACTION_LIST)}
INDEX_TO_ACTION = {i:a for a,i in ACTION_TO_INDEX.items()}
ACTION_SIZE = len(ACTION_LIST)  # 64*64*5 = 20480

# helpers
def action_to_index(fr, to, promo=0):
    return ACTION_TO_INDEX[(fr,to,promo)]

def index_to_action(idx):
    return INDEX_TO_ACTION[idx]
