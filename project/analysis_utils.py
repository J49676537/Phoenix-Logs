import math
import re
from collections import Counter

tenhou_tile_to_array_index_lookup = [
    1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,
    11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,
    21,21,21,21,22,22,22,22,23,23,23,23,24,24,24,24,25,25,25,25,26,26,26,26,27,27,27,27,28,28,28,28,29,29,29,29,
    31,31,31,31,32,32,32,32,33,33,33,33,34,34,34,34,35,35,35,35,36,36,36,36,37,37,37,37
]

yaku_names = [
    "Tsumo", "Riichi", "Ippatsu", "Chankan", "Rinshan", "Haitei", "Houtei", "Pinfu", "Tanyao", "Iipeikou",
    "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind",
    "Yakuhai Dragon", "Yakuhai Dragon", "Yakuhai Dragon", "Double Riichi", "Chiitoitsu", "Chanta", "Itsu", "Doujun", "Doukou",
    "Sankantsu", "Toitoi", "Sanankou", "Shousangen", "Honroutou", "Ryanpeikou", "Junchan", "Honitsu", "Chinitsu",
    "Renhou", "Tenhou", "Chihou", "Daisangen", "Suuankou", "Suuankou", "Tsuuiisou", "Ryuuiisou", "Chinroutou", "Chuuren", "Chuuren",
    "Kokushi", "Kokushi", "Daisuushi", "Shousuushi", "Suukantsu", "Dora", "Uradora", "Akadora"
]

discards = ['D', 'E', 'F', 'G']
draws = ['T', 'U', 'V', 'W']
suit_characters = ['m', 'p', 's', 'z']

def convertTile(tile):
    return tenhou_tile_to_array_index_lookup[int(tile)]

def convertHand(hand):
    return Counter(hand)

def convertHandToTenhouString(hand):
    handString = ""
    valuesInSuit = ""

    for suit in range(4):
        for i in range(suit * 10 + 1, suit * 10 + 10):
            if i > 37: continue
            value = i % 10

            if value == 5 and hand[i - 5] > 0:
                for j in range(hand[i - 5]):
                    valuesInSuit += 0

            for j in range(hand[i]):
                valuesInSuit += str(value)

        if valuesInSuit != "":
            handString += valuesInSuit + suit_characters[suit]
            valuesInSuit = ""

    return handString

def convertHai(hai):
    converted = list(map(convertTile, hai.split(',')))
    return convertHand(converted)

def getTilesFromCall(call):
    meldInt = int(call)
    meldBinary = format(meldInt, "016b")

    if meldBinary[-3] == '1':
        # Chii
        tile = meldBinary[0:6]
        tile = int(tile, 2)
        order = tile % 3
        tile = tile // 3
        tile = 9 * (tile // 7) + (tile % 7)
        tile = convertTile(tile * 4)

        if order == 0:
            return [tile, tile + 1, tile + 2]
        
        if order == 1:
            return [tile + 1, tile, tile + 2]

        return [tile + 2, tile, tile + 1]
    
    elif meldBinary[-4] == '1':
        # Pon
        tile = meldBinary[0:7]
        tile = int(tile, 2)
        tile = tile // 3
        tile = convertTile(tile * 4)

        return [tile, tile, tile]
    
    elif meldBinary[-5] == '1':
        # Added kan
        tile = meldBinary[0:7]
        tile = int(tile, 2)
        tile = tile // 3
        tile = convertTile(tile * 4)

        return [tile]
    
    elif meldBinary[-6] == '1':
        # Nuki
        return [34]
    
    else:
        # Kan
        tile = meldBinary[0:8]
        tile = int(tile, 2)
        tile = tile // 4
        tile = convertTile(tile * 4)
        return [tile, tile, tile, tile]

def GetWhoTileWasCalledFrom(call):
    meldInt = int(call.attrib["m"])
    meldBinary = format(meldInt, "016b")
    return int(meldBinary[-2:], 2)

round_names = [
    "East 1", "East 2", "East 3", "East 4",
    "South 1", "South 2", "South 3", "South 4",
    "West 1", "West 2", "West 3", "West 4"
]

def GetRoundName(init):
    seed = init.attrib["seed"].split(",")
    return "%s-%s" % (round_names[int(seed[0])], seed[1])

def GetRoundNameWithoutRepeats(init):
    seed = init.attrib["seed"].split(",")
    return round_names[int(seed[0])]

seats_by_oya = [
    [ "East", "South", "West", "North" ],
    [ "North", "East", "South", "West" ],
    [ "West", "North", "East", "South" ],
    [ "South", "West", "North", "East" ]
]

def CheckSeat(who, oya):
    return seats_by_oya[int(oya)][int(who)]

def GetPlacements(ten, starting_oya):
    points = list(map(int, ten.split(",")))
    # For tiebreaking
    points[0] -= (4 - starting_oya) % 4
    points[1] -= (5 - starting_oya) % 4
    points[2] -= (6 - starting_oya) % 4
    points[3] -= (7 - starting_oya) % 4
    ordered_points = points.copy()
    ordered_points.sort(reverse=True)

    return [
        ordered_points.index(points[0]),
        ordered_points.index(points[1]),
        ordered_points.index(points[2]),
        ordered_points.index(points[3])
    ]

def GetNextRealTag(element):
    next_element = element.getnext()

    while next_element is not None and (next_element.tag == "UN" or next_element.tag == "BYE"):
        next_element = next_element.getnext()
    
    return next_element

def GetPreviousRealTag(element):
    next_element = element.getprevious()

    while next_element is not None and (next_element.tag == "UN" or next_element.tag == "BYE"):
        next_element = next_element.getprevious()
    
    return next_element
    
def CheckIfWinIsClosed(agari):
    if "m" not in agari.attrib:
        return True

    calls = agari.attrib["m"].split(",")

    for call in calls:
        meldInt = int(call)
        meldBinary = format(meldInt, "016b")
        last_nums = meldBinary[-2:]

        if int(last_nums, 2) != 0:
            return False
    
    return True

def CheckIfWinWasRiichi(agari):
    if "yaku" in agari.attrib:
        yaku = agari.attrib["yaku"].split(",")[0::2]
        if "1" in yaku or "21" in yaku:
            return True
        else:
            return False
    
    winner = agari.attrib["who"]

    previous = agari.getprevious()

    while previous is not None:
        if previous.tag == "INIT":
            return False
        
        if previous.tag == "REACH" and previous.attrib["who"] == winner:
            return True
        
        previous = previous.getprevious()
    
    return False

def CheckIfWinWasDealer(agari):
    winner = agari.attrib["who"]
    previous = agari.getprevious()

    while previous is not None:
        if previous.tag == "INIT":
            return previous.attrib["oya"] == winner
        previous = previous.getprevious()
    
    return False # ???

def CheckDoubleRon(element):
    next_element = GetNextRealTag(element)

    if next_element is not None and next_element.tag == "AGARI":
        return True
    
    return False

def GetStartingHands(init, players = 4):
    hands = []
    for i in range(players):
        hands.append(convertHai(init.attrib["hai%d" % i]))
    return hands

dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]

def GetDora(indicator):
    return dora_indication[indicator]