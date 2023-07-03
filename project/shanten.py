"""
Calculates the shanten of a hand in the format dict = { key=tile : value=occurence }

tileList = {'1s': 1,'2s': 2,'3s': 3,'4s': 4,'5s': 5,'6s': 6,'7s': 7,'8s': 8,'9s': 9,
            '1p':11,'2p':12,'3p':13,'4p':14,'5p':15,'6p':16,'7p':17,'8p':18,'9p':19,
            '1m':21,'2m':22,'3m':23,'4m':24,'5m':25,'6m':26,'7m':27,'8m':28,'9m':29,
            '1z':31,'2z':32,'3z':33,'4z':34,'5z':35,'6z':36,'7z':37} # ESWN-WGR
"""

# Global Variables
bestShanten = 8
completeSets = 0
partialSets = 0
pair = 0

def CalculateMinimumShanten(hand):
    global bestShanten
    global completeSets
    global partialSets
    global pair
    bestShanten = 8
    completeSets = 0
    partialSets = 0
    pair = 0
    
    chiitoiShanten = CalculateChiitoitsuShanten(hand)
    kokushiShanten = CalculateKokushiShanten(hand)
    #print(chiitoiShanten, kokushiShanten)
    if chiitoiShanten == -1 or kokushiShanten == -1: return -1
    bestShanten = min(chiitoiShanten, kokushiShanten)
    minShanten = CalculateStandardShanten(hand)
    return minShanten

def CalculateChiitoitsuShanten(hand):
    pairCount = 0
    for i in range(1, 38):
        if hand[i] >= 2: pairCount += 1
    shanten = 6 - pairCount
    return shanten

def CalculateKokushiShanten(hand):
    uniqueTiles = 0
    hasPair = 0
    for i in range(1, 38):
        if i in [1,9,11,19,21,29] or i > 30:
            if hand[i] != 0: uniqueTiles += 1
            if hand[i] >= 2: hasPair = 1
    shanten = 13 - uniqueTiles - hasPair
    return shanten

def CalculateStandardShanten(hand):
    global bestShanten
    global pair
    
    # Loop through the hand, removing all pair candidates and checking their shanten
    for i in range(1, 38):
        if hand[i] >= 2:
            pair += 1
            hand[i] -= 2
            #print('##########################################')
            #print('Checking Pair:', i, i)
            #print('##########################################')
            RemoveCompletedSets(hand)
            hand[i] += 2
            pair -= 1
    
    #print('##########################################')
    #print('No Pair In Hand')
    #print('##########################################')
    RemoveCompletedSets(hand)
    
    #print('##########################################')
    #print('End of Script. Best Shanten =', bestShanten)
    #print('##########################################')
    return bestShanten

def RemoveCompletedSets(hand, i=1):
    global bestShanten
    global completeSets
    global partialSets
    global pair
    if bestShanten <= -1: return
    
    # Skip to the next tile that exists in the hand.
    while i < 38 and hand[i] == 0: i += 1
    
    # Debugging
    #if i != 38: print('i=', i, ' hand[i]=', hand[i], sep='')
    
    # We've gone through the whole hand, now check for partial sets.  
    if i >= 38:
        #print('Gone through whole hand. Checking potential sets.')
        RemovePotentialSets(hand)
        return
    
    if hand[i] >= 3:
        #print('PON--------------------')
        completeSets += 1
        hand[i] -= 3
        RemovePotentialSets(hand)
        #print('--------------------PON')
        hand[i] += 3
        completeSets -= 1
    
    if i < 30 and hand[i+1] != 0 and hand[i+2] != 0:
        #print('CHI--------------------')
        completeSets += 1
        hand[i] -= 1
        hand[i+1] -= 1
        hand[i+2] -= 1
        RemovePotentialSets(hand)
        #print('--------------------CHI')
        hand[i] += 1
        hand[i+1] += 1
        hand[i+2] += 1
        completeSets -= 1
    
    # Check all alternative hand configurations
    RemoveCompletedSets(hand, i+1)

def RemovePotentialSets(hand, i=1):
    global bestShanten
    global completeSets
    global partialSets
    global pair
    if bestShanten <= -1: return
    
    # Skip to the next tile that exists in the hand.
    while i < 38 and hand[i] == 0: i += 1
    
    # Debugging
    #if i != 38: print('i=', i, ' hand[i]=', hand[i], sep='')
    
    # We've checked everything. See if this shanten is better than the current best.
    if i >= 38:
        #print('Checked all potential sets')
        currentShanten = 8 - (completeSets * 2) - partialSets - pair
        if currentShanten < bestShanten:
            bestShanten = currentShanten
        return
    
    # A standard hand will only ever have four groups plus a pair.
    if completeSets + partialSets < 4:
        # Pair
        if hand[i] == 2:
            partialSets += 1
            hand[i] -= 2
            RemovePotentialSets(hand)
            hand[i] += 2
            partialSets -= 1
        
        # Edge or Side wait protorun
        if i < 30 and hand[i + 1] != 0:
            partialSets += 1
            hand[i] -= 1
            hand[i + 1] -= 1
            RemovePotentialSets(hand)
            hand[i] += 1
            hand[i + 1] += 1
            partialSets -= 1
        
        # Closed wait protorun
        if i < 30 and i % 10 <= 8 and hand[i + 2] != 0:
            partialSets += 1
            hand[i] -= 1
            hand[i + 2] -= 1
            RemovePotentialSets(hand)
            hand[i] += 1
            hand[i + 2] += 1
            partialSets -= 1
    
    # Check all alternative hand configurations
    RemovePotentialSets(hand, i+1)