#!/usr/bin/env python3


from helper_funcs import (
    new_class, make, call, call_super, 
    NameSpaceDict, ObjectDict, ClassDict)


# Object constructors
def new_Puzzle(obj: ObjectDict, name: str, difficulty: int) -> None:
    obj["name"] = name
    obj["difficulty"] = difficulty
    obj["solved"] = False
    
def new_Resettable(obj: ObjectDict, resets_left: int) -> None:
    obj["resets_left"] = resets_left

def new_Riddle(obj: ObjectDict, name: str, difficulty: int, hints_used: int) -> None:
    call_super(Riddle_namespace, obj, "_new", name, difficulty) #calls new_Puzzle; passes Riddle_namespace due to self-referentiality
    obj["hints_used"] = hints_used
    
def new_ElectronicPuzzle(obj: ObjectDict, name: str, difficulty: int, mistakes: int, resets_left: int) -> None:
    call(Puzzle, "_new", obj, name, difficulty)
    call(Resettable, "_new", obj, resets_left)
    obj["mistakes"] = mistakes
        

# Methods
def solve(obj: ObjectDict) -> bool:
    obj["solved"] = True


#   Score
def score_Riddle(obj: ObjectDict) -> int:
    return max(0, obj["difficulty"] * 10 - obj["hints_used"] * 2)

def score_ElectronicPuzzle(obj: ObjectDict) -> int:
    return max(0, obj["difficulty"] * 15 - obj["mistakes"] * 3)


#   Describe
def describe_Riddle(obj: ObjectDict) -> str:
    state = "solved" if obj["solved"] else "unsolved"
    return (
        f"{obj['name']} is a difficulty-{obj['difficulty']} riddle, "
        f"currently {state}, with {obj['hints_used']} hint(s) used."
    )

def describe_ElectronicPuzzle(obj: ObjectDict) -> str:
    state = "solved" if obj["solved"] else "unsolved"
    return (
        f"{obj['name']} is a difficulty-{obj['difficulty']} electronic "
        f"puzzle, currently {state}, with {obj['mistakes']} mistake(s) "
        f"and {obj['resets_left']} reset(s) left."
    )

#   Reset
def can_reset(obj: ObjectDict) -> bool:
    return obj["resets_left"] > 0


def reset(obj: ObjectDict) -> bool:
    if not call(obj, "can_reset"):
        return False

    obj["solved"] = False
    obj["resets_left"] -= 1
    return True

#Namespaces

Puzzle_namespace: NameSpaceDict = {
    "_new": new_Puzzle,
    "solve": solve,
    "score": "abstractmethod",
    "describe": "abstractmethod"
}

Resettable_namespace: NameSpaceDict = {
    "_new": new_Resettable,
    "reset": reset,
    "can_reset": can_reset
}

Riddle_namespace: NameSpaceDict = {
    "_new": new_Riddle,
    "score": score_Riddle,
    "describe": describe_Riddle
}

ElectronicPuzzle_namespace: NameSpaceDict = {
    "_new": new_ElectronicPuzzle,
    "score": score_ElectronicPuzzle,
    "describe": describe_ElectronicPuzzle
}

#Classes

Puzzle: ClassDict = new_class("Puzzle", [], Puzzle_namespace)
Resettable: ClassDict = new_class("Resettable", [], Resettable_namespace)
Riddle: ClassDict = new_class("Riddle", [Puzzle], Riddle_namespace)
ElectronicPuzzle: ClassDict = new_class("ElectronicPuzzle", [Puzzle, Resettable], ElectronicPuzzle_namespace)

