import cProfile
import re
import bisect
class cell():
    def __init__(self, x, y, color):
        # Assigned parameters, not variable to change
        self.x = x
        self.y = y
        self.z = x-y
        self.color = color
        # States of the cell, variable to change
        # States in axes (open, closed, etc.)
        self.statex = 2
        self.statey = 2
        self.statez = 2
        # Limits for search
        self.posx = 6
        self.negx = -6
        self.posy = 6
        self.negy = -6
        self.posz = 6
        self.negz = -6
        # For detection of preemptives, and gaps in preemptives
        self.preemparrayx = []
        self.preemparrayy = []
        self.preemparrayz = []
        self.gapx = 0
        self.gapy = 0
        self.gapz = 0
        self.k = -7
        # Preemptives in axes
        self.preempx = 1
        self.preempy = 1
        self.preempz = 1
        self.preempstatex = 2
        self.preempstatey = 2
        self.preempstatez = 2
        # Win condition
        self.sixinarow = False
        # Evaluation
        self.eval = 0
        self.dirty = True
        # Checks its own color
        if self.color == "blue":
            self.enemy = "orange"
        elif self.color == "orange":
            self.enemy = "blue"
        else:
            self.enemy = "empty"
    # Raytracing function
    def checkcells(self, by_x, by_y, by_z):
        # Evaluation
        if self.dirty == False:
            pass
        else:
            self.preemparrayx = []
            self.preemparrayy = []
            self.preemparrayz = []
            self.preemparray = []
            self.preempx = 1
            self.preempy = 1
            self.preempz = 1
            # Y axis
            for c in by_x.get(self.x, []):  # replaces: if cellsplaced[i].x == self.x
                valy = c.y - self.y
                if c.color == self.enemy:
                    if valy < self.posy and valy > self.negy:
                        # Reduces vision
                        if valy < 0:
                            self.negy = valy
                        elif valy > 0:
                            self.posy = valy
                        # Checks if this hex is open, closed, or dead 
                        if self.posy < 3 or self.negy > -3:
                            self.statey = 1
                        if self.posy - self.negy < 6:
                            self.statey = 0 
                if c.color == self.color:
                    if valy < self.posy and valy > self.negy:
                        bisect.insort(self.preemparrayy, valy)
            # X axis
            for c in by_y.get(self.y, []):  # replaces: if cellsplaced[i].y == self.y
                valxz = c.x - self.x
                if c.color == self.enemy:
                    if valxz < self.posx and valxz > self.negx:
                        if valxz < 0:
                            self.negx = valxz
                        elif valxz > 0:
                            self.posx = valxz
                        if self.posx < 3 or self.negx > -3:
                            self.statex = 1
                        if self.posx - self.negx < 6:
                            self.statex = 0 
                if c.color == self.color:
                    if valxz < self.posx and valxz > self.negx:
                        bisect.insort(self.preemparrayx, valxz)
            # Z axis
            for c in by_z.get(self.z, []):  # replaces: if cellsplaced[i].z == self.z
                valxz = c.x - self.x
                if c.color == self.enemy:
                    if valxz < self.posz and valxz > self.negz:
                        if valxz < 0:
                            self.negz = valxz
                        elif valxz > 0:
                            self.posz = valxz
                        if self.posz < 3 or self.negz > -3:
                            self.statez = 1
                        if self.posz - self.negz < 6:
                            self.statez = 0
                if c.color == self.color:
                    if valxz < self.posz and valxz > self.negz:
                        bisect.insort(self.preemparrayz, valxz)
            # Detects preemptives, threats and wins
            self.threatcount = 0
            # X axis (new)
            for i in range(-5, 1): # Evaluates the 6 absolute windows overlapping this cell
                self.preemparray = []
                if i > self.negx and i + 6 <= self.posx:
                    left = bisect.bisect_left(self.preemparrayx, i)
                    right = bisect.bisect_left(self.preemparrayx, i + 6)
                    self.preemparray = self.preemparrayx[left:right]
                    k = len(self.preemparray)
                    
                    if k > 0:
                        # Recalculate gaps for the pieces in this specific window
                        self.gapx = 0
                        k_prev = -7
                        for j in self.preemparray:
                            if k_prev != -7:
                                self.gapx += j - k_prev - 1
                            k_prev = j
                            
                        # THE FIX: The threat level inherits the line's open/closed state
                        if self.gapx <= abs(4-k):
                            self.preempstatex = self.statex 
                        else:
                            self.preempstatex = 1

                        if k > self.preempx:
                            self.preempx = k
                            
            if self.preempx == 6:
                if self.gapx == 0:
                    self.sixinarow = True
                    self.preempstatex = 1000000
            
            # Y axis (new)
            for i in range(-5, 1): # Evaluates the 6 absolute windows overlapping this cell
                self.preemparray = []
                if i > self.negy and i + 6 <= self.posy:
                    left = bisect.bisect_left(self.preemparrayy, i)
                    right = bisect.bisect_left(self.preemparrayy, i + 6)
                    self.preemparray = self.preemparrayy[left:right]
                    k = len(self.preemparray)
                    
                    if k > 0:
                        # Recalculate gaps for the pieces in this specific window
                        self.gapy = 0
                        k_prev = -7
                        for j in self.preemparray:
                            if k_prev != -7:
                                self.gapy += j - k_prev - 1
                            k_prev = j
                            
                        # THE FIX: The threat level inherits the line's open/closed state
                        if self.gapy <= abs(4-k):
                            self.preempstatey = self.statey
                        else:
                            self.preempstatey = 1

                        if k > self.preempy:
                            self.preempy = k
                            
            if self.preempy == 6:
                if self.gapy == 0:
                    self.sixinarow = True
                    self.preempstatey = 1000000

            # Z axis (new)
            for i in range(-5, 1): # Evaluates the 6 absolute windows overlapping this cell
                self.preemparray = []
                if i > self.negz and i + 6 <= self.posz:
                    left = bisect.bisect_left(self.preemparrayz, i)
                    right = bisect.bisect_left(self.preemparrayz, i + 6)
                    self.preemparray = self.preemparrayz[left:right]
                    k = len(self.preemparray)
                    
                    if k > 0:
                        # Recalculate gaps for the pieces in this specific window
                        self.gapz = 0
                        k_prev = -7
                        for j in self.preemparray:
                            if k_prev != -7:
                                self.gapz += j - k_prev - 1
                            k_prev = j
                            
                        # THE FIX: The threat level inherits the line's open/closed state
                        if self.gapz <= abs(4-k):
                            self.preempstatez = self.statez 
                        else:
                            self.preempstatez = 1

                        if k > self.preempz:
                            self.preempz = k
                            
            if self.preempz == 6:
                if self.gapz == 0:
                    self.sixinarow = True
                    self.preempstatez = 1000000
            
            self.threatcount = (self.preempstatex if self.preempx >= 4 else 0) + (self.preempstatey if self.preempy >= 4 else 0) + (self.preempstatez if self.preempz >= 4 else 0)
            self.eval = ((self.statex*self.preempx*(self.preempstatex/2) + self.statey*self.preempy*(self.preempstatey/2) + self.statez*self.preempz*(self.preempstatez/2))/6)
            self.dirty = False
        return self.eval
color = ""
player = int(input("what player are you"))
if player == 1:
    color = "blue"
else:
    color = "orange"
# List of cells
cellsplaced = {"t01":cell(0, 0, "orange")}
# Turn functions
def add_to_index(bot, cell, key):
    bot.by_x.setdefault(cell.x, []).append(cell)
    bot.by_y.setdefault(cell.y, []).append(cell)
    bot.by_z.setdefault(cell.z, []).append(cell)
    bot.cell_to_key[id(cell)] = key
def remove_from_index(bot, cell):
    bot.by_x.setdefault(cell.x, []).remove(cell)
    bot.by_y.setdefault(cell.y, []).remove(cell)
    bot.by_z.setdefault(cell.z, []).remove(cell)
    del bot.cell_to_key[id(cell)]

def turn(x1, y1, x2, y2, turnNum,cellNum, bot):
    if player == 1:
        coloring = "orange" 
    else:
        coloring = "blue"
    notation = "t" + turnNum + cellNum
    c1 = cell(x1, y1, coloring)
    c2 = cell(x2, y2, coloring)
    cellsplaced.update({notation:c1})
    add_to_index(bot, c1, notation)
    cellNum = str(int(cellNum) + 1)
    notation = "t" + turnNum + cellNum
    cellsplaced.update({notation:c2})
    add_to_index(bot, c2, notation)
    mark_dirty_multiple(bot, [c1, c2], bot.by_x, bot.by_y, bot.by_z)
def mark_dirty_multiple(bot, cells, by_x, by_y, by_z):
    seen = set()
    for new_cell in cells:
        for c in by_x.get(new_cell.x, []):
            if id(c) not in seen:
                c.dirty = True
                seen.add(id(c))
        for c in by_y.get(new_cell.y, []):
            if id(c) not in seen:
                c.dirty = True
                seen.add(id(c))
        for c in by_z.get(new_cell.z, []):
            if id(c) not in seen:
                c.dirty = True
                seen.add(id(c))
# Bot
class Reina0():
    def __init__ (self, turnNum, cellNum, color, position, depth):
        self.turnNum = turnNum
        self.cellNum = cellNum
        self.hypocellsplaced = position
        self.by_x = {0:[position["t01"]]}  
        self.by_y = {0:[position["t01"]]}  
        self.by_z = {0:[position["t01"]]}  
        self.legalmoves = []
        self.color = color
        self.themove = []
        self.depth = {}
        self.movecheck = depth
        self.transposition_table = {}
        self.cell_to_key = {id(position["t01"]): "t01"}
    def legalMoves(self, color):
        self.legalmoves = []
        seen = set()
        occupied = {(c.x, c.y) for c in self.hypocellsplaced.values()}
        
        # 1. Hard cap: Start with only the last 8 pieces placed (4 turns)
        focus_cells = list(self.hypocellsplaced.values())[-8:]
        
        # 2. Threat awareness: Add ANY piece on the board that has a threatcount > 0
        # This guarantees we never go blind to an older threat.
        for c in self.hypocellsplaced.values():
            c.checkcells(self.by_x, self.by_y, self.by_z)
            if c.threatcount > 0 and c not in focus_cells:
                focus_cells.append(c)
                
        # 3. Generate the 5x5 box ONLY around these highly relevant pieces
        for c in focus_cells:
            for x in range(c.x - 2, c.x + 3):
                for y in range(c.y - 2, c.y + 3):
                    if (x, y) not in seen and (x, y) not in occupied:
                        self.legalmoves.append(cell(x, y, color))
                        seen.add((x, y))
    def affected_cells(self, i, j):
        affected = set()
        for cell in (i, j):
            for c in self.by_x.get(cell.x, []):
                if c is not i and c is not j and id(c) in self.cell_to_key:
                    affected.add(self.cell_to_key[id(c)])
            for c in self.by_y.get(cell.y, []):
                if c is not i and c is not j and id(c) in self.cell_to_key:
                    affected.add(self.cell_to_key[id(c)])
            for c in self.by_z.get(cell.z, []):
                if c is not i and c is not j and id(c) in self.cell_to_key:
                    affected.add(self.cell_to_key[id(c)])
        return affected
    def snapshots(self, board, affected):
        snapshot = {}
        for k in affected:
            c = board[k]
            snapshot[k] = (c.statex, c.statey, c.statez, c.posx, c.negx, c.posy, c.negy, c.posz, c.negz, c.eval, c.dirty, c.preempstatex, c.preempstatey, c.preempstatez, c.preempx, c.preempy, c.preempz, c.sixinarow, c.gapx, c.gapy, c.gapz, c.threatcount)
        return snapshot
    def retrieve_snapshot(self, board, snapshot):
        for k, state in snapshot.items():
            c = board[k]
            (c.statex, c.statey, c.statez, c.posx, c.negx, c.posy, c.negy, c.posz, c.negz, c.eval, c.dirty, c.preempstatex, c.preempstatey, c.preempstatez, c.preempx, c.preempy, c.preempz, c.sixinarow, c.gapx, c.gapy, c.gapz, c.threatcount) = state
    def prescore(self, i, j, board, base_eval, base_total, affected, maxplayer, base_threat_count):
        # Place i and j
        evaluation = base_total
        
        # 1. Update evaluations for affected cells
        for k in affected:
            evaluation -= base_eval.get(k, 0)
            board[k].checkcells(self.by_x, self.by_y, self.by_z)
            if board[k].color == self.color:
                evaluation += board[k].eval
            else:
                evaluation -= board[k].eval
                
        i.checkcells(self.by_x, self.by_y, self.by_z)
        j.checkcells(self.by_x, self.by_y, self.by_z)
        
        # 2. FIX: Check the entire board for remaining enemy threats
        global_threatcount = 0
        for c in board.values():
            if c.color != i.color: # Only check enemy cells for threats
                global_threatcount = max(global_threatcount, c.threatcount)

        # 3. Compare the global threat count to the base threat count
        threatcount = min(global_threatcount, base_threat_count)
        
        # If threatcount is 0, it means either there were no base threats to begin with, 
        # or we successfully neutralized the existing base threats.
        if threatcount == 0:
            if maxplayer:
                evaluation += i.eval + j.eval
            else:
                evaluation -= (i.eval + j.eval)
            return evaluation
        else:
            # The enemy still has an active threat, prune this move
            return None
    def tree(self, maxplayer, depth,  board, base_eval, base_threats):
        prescores = []
        seen_move_fingerprints = set()
        if self.color == "orange":
            playercolor = "blue"
        else:
            playercolor = "orange"
        if maxplayer:
            self.legalMoves(self.color)
        else:
            self.legalMoves(playercolor)
        base_total = sum(base_eval.values())
        for i in self.legalmoves:
            for j in self.legalmoves:
                if j.x != i.x or j.y != i.y:
                    j.color = i.color
                    fingerprint = tuple(sorted(((i.x, i.y), (j.x, j.y))))
                    if fingerprint in seen_move_fingerprints:
                        continue
                    else: 
                        affected = self.affected_cells(i, j)
                        snapshot = self.snapshots(board, affected)
                        board["hypo1"] = i
                        board["hypo2"] = j
                        add_to_index(self, i, "hypo1")
                        add_to_index(self, j, "hypo2")
                        mark_dirty_multiple(self, [i, j], self.by_x, self.by_y, self.by_z)
                        # Start from base, only re-evaluate affected cells
                        evaluation = self.prescore(i, j, board, base_eval, base_total, affected, maxplayer, base_threats)
                        if evaluation != None:
                            prescores.append((evaluation, [i, j]))
                        remove_from_index(self, i)
                        remove_from_index(self, j)
                        del board["hypo1"]
                        del board["hypo2"]
                        self.retrieve_snapshot(board, snapshot)
        priority = []
        normal = []
        threatsx = set()
        threatsy = set()
        threatsz = set()
        for k, c in board.items():
            if c.color != i.color:
                if c.preempx >= 2:
                    threatsx.add(c)
                elif c.preempy >= 2:
                    threatsy.add(c)
                elif c.preempz >= 2:
                    threatsz.add(c)
        for score, pair in prescores:
            i, j = pair
            # Check if this pair blocks a serious threat

            is_defensivex = any(t for t in threatsx if ((i.y == t.y and j.y == t.y) if (t.preempx >= 4 and t.statex == 2) else (i.y == t.y or j.y == t.y)))
            is_defensivey = any(t for t in threatsy if ((i.x == t.x and j.x == t.x) if (t.preempy >= 4 and t.statey == 2) else (i.x == t.x or j.x == t.x)))
            is_defensivez = any(t for t in threatsz if ((i.z == t.z and j.z == t.z) if (t.preempz >= 4 and t.statez == 2) else (i.z == t.z or j.z == t.z)))
            if is_defensivex or is_defensivey or is_defensivez:
                priority.append((score, pair))
            else:
                normal.append((score, pair))
        # Sort each group separately
        priority.sort(key=lambda x: x[0], reverse=maxplayer)
        normal.sort(key=lambda x: x[0], reverse=maxplayer)
    
        # Always include defensive moves, fill rest with normal moves
        top_moves = priority[:30] + normal[:max(0, 60 - len(priority[:30]))]
    
        for score, pair in top_moves:
            move_key = ((pair[0].x, pair[0].y), (pair[1].x, pair[1].y))
            depth[move_key] = (pair, score)
        return depth
    def alphabetaupdated(self, bot, depth, child, alpha, beta, on_pv=False):
        permanent = []
        full = []
        for k, c in self.hypocellsplaced.items():
            t = (c.x, c.y, c.color)
            full.append(t)
            if not k.startswith("hypo"):
                permanent.append(t)
        current_permanent = frozenset(permanent)
        full_hash = frozenset(full)
        state = (full_hash, bot)
        if state in self.transposition_table:
            stored = self.transposition_table[state]
            stored_depth, stored_result, stored_permanent = stored[0], stored[1], stored[2]
            if stored_depth >= depth and current_permanent.issubset(stored_permanent):
                if self.movecheck != depth:  # only use cache for non-root nodes
                    return stored_result
        print(depth)
        statictotaleval = 0
        Ordered = {}
        base_eval = {}
        base_threats = 0
        forced_win = None
        for i in self.hypocellsplaced:
            c = self.hypocellsplaced[i]
            c.checkcells(self.by_x, self.by_y, self.by_z)
            forced_win = None
            if c.sixinarow:
                print("Six-in-a-row encountered (should never happen if not forced win)")
                forced_win = 10000000 if self.color == c.color else -10000000
                break
            staticeval = c.eval
            staticthreats = c.threatcount
            if self.color == c.color:
                statictotaleval += staticeval
                base_eval[i] = staticeval
            else:
                statictotaleval -= staticeval
                base_eval[i] = -staticeval
            if bot:
                if c.color != self.color:
                    base_threats = max(base_threats, staticthreats)
            else:
                if c.color == self.color:
                    base_threats = max(base_threats, staticthreats)
        if forced_win is not None:
                self.transposition_table[(full_hash, bot)] = (depth, forced_win, current_permanent)
                return forced_win
        if depth == 0:
            self.transposition_table[(full_hash, bot)] = (depth, statictotaleval, current_permanent)
            return statictotaleval
        else:
            if self.hypocellsplaced == {"t01":cell(0, 0, "orange")}:
                childupdated = {((0, -1), (1, 1)):[[cell(0, -1, "blue"), cell(1, 1, "blue")], 0], ((-1, -1), (1, 1)):[[cell(-1, -1, "blue"), cell(1, 1, "blue")], 0], ((1, 1), (2, 2)):[[cell(1, 1, "blue"), cell(2, 2, "blue")], 0], ((-2, 0), (1, 1)):[[cell(-2, 0, "blue"), cell(1, 1, "blue")], 0], ((-1, 1), (1, -1)):[[cell(-1, 1, "blue"), cell(1, -1, "blue")], 0], ((0, -1), (1, 0)):[[cell(0, -1, "blue"), cell(1, 0, "blue")], 0], ((0, -1), (2, 1)):[[cell(0, -1, "blue"), cell(2, 1, "blue")], 0], ((1, 2), (2, 2)):[[cell(1, 2, "blue"), cell(2, 2, "blue")], 0], ((-1, 2), (0, 2)):[[cell(-1, 2, "blue"), cell(0, 2, "blue")], 0], ((2, 0), (2, 2)):[[cell(2, 0, "blue"), cell(2, 2, "blue")], 0], ((-2, 1), (-1, 2)):[[cell(-2, 1, "blue"), cell(-1, 2, "blue")], 0], ((-2, 2), (-1, 2)):[[cell(-2, 2, "blue"), cell(-1, 2, "blue")], 0], ((1, 1), (2, 1)):[[cell(1, 1, "blue"), cell(2, 1, "blue")], 0], ((2, 1), (3, 1)):[[cell(2, 1, "blue"), cell(3, 1, "blue")], 0], ((1, -1), (2, 1)):[[cell(1, -1, "blue"), cell(2, 1, "blue")], 0], ((-1, 1), (2, 1)):[[cell(-1, 1, "blue"), cell(2, 1, "blue")], 0], ((2, 1), (4, 2)):[[cell(2, 1, "blue"), cell(4, 2, "blue")], 0], ((8, 0), (8, 1)):[[cell(8, 0, "blue"), cell(8, 1, "blue")], 0], ((8, 0), (1, 1)):[[cell(8, 0, "blue"), cell(1, 1, "blue")], 0]}
            else:
                if bot:
                    childupdated = self.tree(True, child, self.hypocellsplaced, base_eval, base_threats)
                else:
                    childupdated = self.tree(False, child, self.hypocellsplaced, base_eval, base_threats)
            if childupdated != {}:
                if bot:
                    best_item = max(childupdated.keys(), key=lambda k: childupdated[k][1])
                else:
                    best_item = None
                for item in childupdated:
                    snapshot = self.snapshots(self.hypocellsplaced, self.affected_cells(childupdated[item][0][0], childupdated[item][0][1]))
                    string1 = "hypo1eval" + str(depth)
                    self.hypocellsplaced.update({string1:childupdated[item][0][0]})
                    add_to_index(self, childupdated[item][0][0], string1)
                    string2 = "hypo2eval" + str(depth)
                    self.hypocellsplaced.update({string2:childupdated[item][0][1]})
                    add_to_index(self, childupdated[item][0][1], string2)
                    mark_dirty_multiple(self, [childupdated[item][0][0], childupdated[item][0][1]], self.by_x, self.by_y, self.by_z)
                    should_cache = on_pv and (not bot or item == best_item)
                    if childupdated[item][0][0].color == self.color and childupdated[item][0][1].color == self.color:
                        returneval = self.alphabetaupdated(False, depth-1, {}, alpha, beta, on_pv=should_cache)
                        Ordered.update({returneval:childupdated[item]})
                        alpha = max(alpha, returneval)
                    else:
                        returneval = self.alphabetaupdated(True, depth-1, {}, alpha, beta, on_pv=should_cache)
                        Ordered.update({returneval:childupdated[item]})
                        beta = min(beta, returneval)

                    del self.hypocellsplaced[string1]
                    remove_from_index(self, childupdated[item][0][0])
                    del self.hypocellsplaced[string2]
                    remove_from_index(self, childupdated[item][0][1])
                    self.retrieve_snapshot(self.hypocellsplaced, snapshot)
                    if beta <= alpha:
                        print(beta, alpha)
                        break
            elif bot:
                print("Forced win detected!")
                statictotaleval = -5000000
                self.themove = None
                return statictotaleval
            else:
                print("You won!")
                statictotaleval = 5000000
                return statictotaleval
            if self.movecheck == depth:
                best_key = max(Ordered.keys())
                best_move = Ordered[best_key][0]
                print(best_key)
                self.transposition_table[(full_hash, bot)] = (depth, best_key, current_permanent, best_move)
                self.themove = best_move
                return self.themove
            else:
                if bot:
                    statictotaleval = max(Ordered.keys())
                    if on_pv:
                        self.transposition_table[(full_hash, bot)] = (depth, statictotaleval, current_permanent)
                    return statictotaleval  # this call was maximising
                else: 
                    statictotaleval = min(Ordered.keys())
                    if on_pv:
                        self.transposition_table[(full_hash, bot)] = (depth, statictotaleval, current_permanent)
                    return statictotaleval  # this call was minimising
                

    def boturn(self):
        print(self.themove)
        notation = "bot: " + self.turnNum + self.cellNum
        cellsplaced.update({notation:self.themove[0]})
        add_to_index(self, self.themove[0], notation)
        self.cellNum = str(int(self.cellNum) + 1)
        notation = "bot: " + self.turnNum + self.cellNum
        cellsplaced.update({notation:self.themove[1]})
        add_to_index(self, self.themove[1], notation)
        print(self.themove[0].x, self.themove[0].y, self.themove[1].x, self.themove[1].y, self.themove[0].color, self.themove[1].color)
        mark_dirty_multiple(self, [self.themove[0], self.themove[1]], self.by_x, self.by_y, self.by_z)
# Game function
def game():
    sixinarow = False
    turnNum = "0"
    cellNum = "0"
    reina = Reina0(turnNum, cellNum, color, cellsplaced, 3)
    while sixinarow == False:
        # Notation and human interaction with the bot
        cellNum = "1"
        turnNum = str(int(turnNum) + 1)
        reina.cellNum = cellNum
        reina.turnNum = turnNum
        if player == 1:
            reina.alphabetaupdated(True, 3, {}, float("-inf"), float("inf"))
            if reina.themove is None:
                print("Game Over! No further moves can be made.")
                break
            reina.boturn()
            x1 = int(input("x"))
            y1 = int(input("y"))
            x2 = int(input("x"))
            y2 = int(input("y"))
            turn(x1, y1, x2, y2, turnNum, cellNum, reina)
        else:
            x1 = int(input("x"))
            y1 = int(input("y"))
            x2 = int(input("x"))
            y2 = int(input("y"))
            turn(x1, y1, x2, y2, turnNum, cellNum, reina)
            reina.alphabetaupdated(True, 3, {}, float("-inf"), float("inf"))
            if reina.themove is None:
                print("Game Over! No further moves can be made.")
                break
            reina.boturn()
        for i in cellsplaced:
            cellsplaced[i].checkcells(reina.by_x, reina.by_y, reina.by_z)
            print(f"cell ({cellsplaced[i].x},{cellsplaced[i].y}) color:{cellsplaced[i].color}")
            if cellsplaced[i].sixinarow == True:
                sixinarow = True



game()