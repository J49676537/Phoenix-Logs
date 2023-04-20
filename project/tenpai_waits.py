def calculateWaits(hand, remainingTiles):
    value = 0
    tiles = []

    has_manzu = False
    has_souzu = False
    has_pinzu = False

    for i in range(10):
        if hand[i] > 0:
            has_manzu = True
        if hand[i+10] > 0:
            has_pinzu = True
        if hand[i+20] > 0:
            has_souzu = True

    # Check adding every tile to see if it improves the shanten
    for i in range(1, 38):
        if i % 10 == 0:
            continue
        if i < 10:
            if not has_manzu: continue
        elif i < 20:
            if not has_pinzu: continue
        elif i < 30:
            if not has_souzu: continue

        hand[i] += 1
        #print(hand)
        #this function works correctly and checks the hand with one extra of each tile to calculate shanten

        if _calculateMinimumShanten(hand, -1) == -1:
            # Improves shanten. Add the number of remaining tiles to the ukeire count
            value += remainingTiles[i]
            tiles.append(i)

        hand[i] -= 1

    return tiles

hand = []
completeSets = 0
pair = 0
partialSets = 0
bestShanten = 0
mininumShanten = 0

def _calculateMinimumShanten(handToCheck, mininumShanten = -1):
    chiitoiShanten = calculateChiitoitsuShanten(handToCheck)
    kokushiShanten = calculateKokushiShanten(handToCheck)
    if chiitoiShanten == -1 or kokushiShanten == -1:
        return -1

    standardShanten = calculateStandardShanten(handToCheck, mininumShanten)
    #print("Returning Standard Shanten...", standardShanten)
    return standardShanten

    # Useless?
    #return min(standardShanten, chiitoiShanten, kokushiShanten)

def calculateChiitoitsuShanten(handToCheck):
    hand = handToCheck
    pairCount = 0
    uniqueTiles = 0

    for i in range(1, 38):
        if hand[i] == 0:
            continue

        uniqueTiles += 1

        if hand[i] >= 2:
            pairCount += 1
        
    shanten = 6 - pairCount

    if uniqueTiles < 7:
        shanten += 7 - uniqueTiles
    
    return shanten

def calculateKokushiShanten(handToCheck):
    uniqueTiles = 0
    hasPair = 0

    for i in range(1, 38):
        if i % 10 == 1 or i % 10 == 9 or i > 30:
            if handToCheck[i] != 0:
                uniqueTiles += 1

                if handToCheck[i] >= 2:
                    hasPair = 1
               
    return 13 - uniqueTiles - hasPair


# Each hand already has 14 tiles. We just want to chek if it is completed or not. If so we return the tile that completed this hand.

def calculateStandardShanten(handToCheck, mininumShanten_ = -1):
    global hand
    global mininumShanten
    global completeSets
    global pair
    global partialSets
    global bestShanten

    hand = handToCheck
    mininumShanten = mininumShanten_

    # Initialize variables
    completeSets = 0
    pair = 0
    partialSets = 0
    bestShanten = 8

    # Loop through hand, removing all pair candidates and checking their shanten
    for i in range(1, 38):
        if hand[i] >= 2:
            pair += 1
            hand[i] -= 2
            #print("##########################################")
            #print("Checking Pair:", i)
            #print("##########################################")
            removeCompletedSets(1)
            hand[i] += 2
            pair -= 1

    # Check shanten when there's nothing used as a pair
    #print("##########################################")
    #print("No Pair In Hand")
    #print("##########################################")
    removeCompletedSets(1)

    #print("##########################################")
    #print("End of Script. Best Shanten =", bestShanten)
    #print("##########################################")
    return bestShanten

def removeCompletedSets(i):
    global hand
    global mininumShanten
    global completeSets
    global pair
    global partialSets
    global bestShanten

    # breaks the loop
    if bestShanten <= mininumShanten:
        #print("BREAK")
        return
    # Skip to the next tile that exists in the hand.
    while i < 38 and hand[i] == 0: i += 1

    # Debugging purposes
    #if i != 38:
        #print("i=", i, "hand[i]=", hand[i])

    if i >= 38:
        # We've gone through the whole hand, now check for partial sets.
        #print("Gone through whole hand")
        removePotentialSets(1)
        return

    # Pung
    if hand[i] >= 3:
        #print("PON--------------------")
        completeSets += 1
        hand[i] -= 3
        removeCompletedSets(i)
        #print("-----------------------")
        hand[i] += 3
        completeSets -= 1

    # Chow
    if i < 30 and hand[i + 1] != 0 and hand[i + 2] != 0:
        #print("CHI--------------------")
        completeSets += 1
        hand[i] -= 1
        hand[i + 1] -= 1
        hand[i + 2] -= 1
        removeCompletedSets(i)
        #print("-----------------------")
        hand[i] += 1
        hand[i + 1] += 1
        hand[i + 2] += 1
        completeSets -= 1

    # Check all alternative hand configurations
    removeCompletedSets(i + 1)

def removePotentialSets(i):
    global hand
    global mininumShanten
    global completeSets
    global pair
    global partialSets
    global bestShanten

    if bestShanten <= mininumShanten:
        #print("bestShanten <= minShanten")
        return
    if completeSets < 3:
        #print("Not enough completed sets")
        return

    # Skip to the next tile that exists in the hand
    while i < len(hand) and hand[i] == 0: i += 1

    if i >= len(hand):
        # We've checked everything. See if this shanten is better than the current best.
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
            removePotentialSets(i)
            hand[i] += 2
            partialSets -= 1
        
        # Edge or Side wait protorun
        if i < 30 and hand[i + 1] != 0:
            partialSets += 1
            hand[i] -= 1
            hand[i + 1] -= 1
            removePotentialSets(i)
            hand[i] += 1
            hand[i + 1] += 1
            partialSets -= 1
        
        # Closed wait protorun
        if i < 30 and i % 10 <= 8 and hand[i + 2] != 0:
            partialSets += 1
            hand[i] -= 1
            hand[i + 2] -= 1
            removePotentialSets(i)
            hand[i] += 1
            hand[i + 2] += 1
            partialSets -= 1

    # Check all alternative hand configurations
    removePotentialSets(i + 1)