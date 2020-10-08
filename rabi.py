
class Rabi:

    RATE_ERROR = '**Subs:** atk / def / hp / speed / critc / critd / eff / res\n\n'\
                 '**Usage:** `rabi rate [level] [colour] [value1] [stat1] ... [value4] [stat4]`\n'\
                 '> *eg. rabi rate +15 red 9% critc 17% atk 4 spd 80 atk*'

    REACTIONS = {
        "fucking ssb users": ["ssb", "seaside bellona"],
        "fucking arby users": ["avild", "avildred", "a. vildred", "a. vild", "a.vildred", "a.vild", "arby"],
        "fucking basar users": ["basar"],
        "fucking dcorvus users": ["dark corvus", "dcorvus", "d corvus"],
        "fucking riolet users": ["riolet"],
        "i love gw": ["gw", "gvg", "guild war", "guildwar", "guild wars", "guildwars"],
        "https://saucer.s-ul.eu/yGF94EzV.jpg": ["+15"]
        }

    COMMANDS = ['hi rabi', 'kill rabi', 'hit rabi', 'ssbuser?', 'rabi rate', 'rabi gw', 'rabi time']

    RABI = {
        "<:rabi:646666830651326464><:arabi:648411271334461449>": ['double ravi', 'double rabi', 'rabis', 'ravis'],
        "<:rabi:646666830651326464>": ['ravi', 'rabi'],
        "<:arabi:648411271334461449>": ['mlravi', 'ml ravi', 'ml rabi', 'mlrabi', 'aravi', 'arabi', 'a.rabi', 'a.ravi']
        }

    SUBSTATS = {
        "atk%": [4, 8],
        "atk": [35, 46],
        "def%": [4, 8],
        "def": [25, 40],
        "hp%": [4, 8],
        "hp": [150, 190],
        "speed": [1, 4],
        "critc%": [3, 5],
        "critd%": [3, 7],
        "eff%": [4, 8],
        "res%": [4, 8]
        }

    COLOURS = {
        "blue": 2,
        "purple": 3,
        "red": 4
        }

    REFORGE = {
        "atk%": [1, 3, 4, 5, 7, 8],
        "atk": [],
        "def%": [1, 3, 4, 5, 7, 8],
        "def": [],
        "hp%": [1, 3, 4, 5, 7, 8],
        "hp": [],
        "speed": [0, 1, 2, 3, 4, 4],
        "critc%": [1,  2, 3, 4, 5, 6],
        "critd%": [1, 2, 3, 4, 6, 7],
        "eff%": [1, 3, 4, 5, 7, 8],
        "res%": [1, 3, 4, 5, 7, 8]
        }

    RATINGS = ["Your poor units...",
               "It could be better...",
               "This should get the job done",
               "<:rabigoodgood:656875318191194124>",
               "Rabi wants that gear",
               "<:ban:663121335190552576>"]
