from log_hand_analyzer import LogHandAnalyzer
from analysis_utils import GetDora, convertTile, yaku_names, GetNextRealTag
from collections import defaultdict, Counter
import tenpai_waits

class DiscardTenpaiInfo(LogHandAnalyzer):
    def __init__(self):
        super().__init__()
        self.tsumogiri = [0,0,0,0]
        self.first_discards = [0,0,0,0]
        self.dora = []
        self.dora_discarded = [0,0,0,0]
        self.discards_at_riichi = [[],[],[],[]]
        self.counts = defaultdict(Counter)
        self.data = []

    def RoundStarted(self, init):
        super().RoundStarted(init)
        self.tsumogiri = [0,0,0,0]
        self.first_discards = [0,0,0,0]
        self.dora_discarded = [0,0,0,0]
        self.discards_at_riichi = [[],[],[],[]]
        self.dora = [GetDora(convertTile(init.attrib["seed"].split(",")[5]))]

    def DoraRevealed(self, hai, element):
        super().DoraRevealed(hai, element)
        #self.dora.append(GetDora(convertTile(hai)))

    def RiichiCalled(self, who, step, element):
        super().RiichiCalled(who, step, element)
        if step == 2: return

        self.discards_at_riichi[who] = self.discards[who].copy()

        ### Record the game state each time Riichi is called on the 9th turn or later
        if len(self.discards_at_riichi[who]) > 8:

            # finding the tenpai wait
            discard_element = GetNextRealTag(element)
            discard = convertTile(discard_element.tag[1:])
            self.hands[who][discard] -= 1

            remaining_tiles = [4]*38
            for i in range(38):
                remaining_tiles[i-1] -= self.hands[who][i]

            riichi_wait = tenpai_waits.calculateWaits(self.hands[who], remaining_tiles)

            ### Reducing wait to just the 4 main categories

            # iterate backwards and break on HONORS and TERMINALS
            for i in range(1, len(riichi_wait)+1):
                if riichi_wait[-i] >= 31:
                    riichi_wait = 0
                    break
                if riichi_wait[-i] in [1,9,11,19,21,29]:
                    riichi_wait = 1
                    break

            # iterate again to check for NEIGHBOURS (maybe better way to do this, but can't be bothered)
            if riichi_wait not in [ 0,1 ]:
                for i in range(1, len(riichi_wait)+1):
                    if riichi_wait[-i] in [2,8,12,18,22,28]:
                        riichi_wait = 2
                        break

            # otherwise it is a middle wait
            if riichi_wait not in [ 0,1,2 ]:
                riichi_wait = 3

            # append data to list
            entry_to_add = [0]*35
            entry_to_add[0] = riichi_wait

            for j in range(len(self.discards_at_riichi[who])):
                if self.discards_at_riichi[who][j] < 10:
                    entry_to_add[self.discards_at_riichi[who][j]-0] = 1
                elif self.discards_at_riichi[who][j] < 20:
                    entry_to_add[self.discards_at_riichi[who][j]-1] = 1
                elif self.discards_at_riichi[who][j] < 30:
                    entry_to_add[self.discards_at_riichi[who][j]-2] = 1
                elif self.discards_at_riichi[who][j] < 40:
                    entry_to_add[self.discards_at_riichi[who][j]-3] = 1

            self.data += [entry_to_add]

    def PrintResults(self):
        with open("./results/RiichiWaits.csv", "w", encoding="utf8") as f:
            f.write("Wait,1s,2s,3s,4s,5s,6s,7s,8s,9s,1p,2p,3p,4p,5p,6p,7p,8p,9p,1m,2m,3m,4m,5m,6m,7m,8m,9m,Ew,Sw,Ww,Nw,Wd,Gd,Rd")
            f.write("\n")
            for i in range(len(self.data)):
                row = self.data[i]
                for j in range(len(row)):
                    f.write(str(row[j]))
                    f.write(",")
                f.write("\n")