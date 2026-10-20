#!/usr/bin/env python3


import sys
import time

from escape_room import (
    Puzzle,
    Riddle,
    ElectronicPuzzle,
    new_class,
    make,
    call,
    call_super

)


#helper function
def assert_raises(exception, function, *args):
    try:
        function(*args)
    except exception:
        return
    raise AssertionError(f"{exception.__name__} wasn't raised")




def test_puzzle_is_abstract():
    """Puzzle cannot be instantiated directly."""
    assert_raises(TypeError, make, Puzzle, "Test Puzzle", 1)


def test_incomplete_subclass_is_abstract():
    """
    A subclass that implements only one of Puzzle's abstract methods
    must remain abstract.
    """
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
    
    IncompletePuzzle = new_class("IncompletePuzzle", [Puzzle], {"score": lambda obj: 0})
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

        # describe() is intentionally not implemented.
    assert_raises(TypeError, make, IncompletePuzzle, "Incomplete Puzzle", 1)


def test_riddle_score():
    """Riddle.score() computes the expected score."""
    riddle = make(Riddle, "Mirror Words", 4, 3)

    assert call(riddle, "score") == 34


def test_riddle_inherits_solve():
    """Riddle inherits solve() from Puzzle."""
    riddle = make(Riddle, "Mirror Words", 4, 3)

    assert not riddle["solved"]

    call(riddle, "solve")

    assert riddle["solved"]


def test_electronic_puzzle_score():
    """ElectronicPuzzle.score() computes the expected score."""
    puzzle = make(ElectronicPuzzle, 
        "Circuit Lock",
        3,
        2,
        1,
    )

    assert call(puzzle, "score") == 39


def test_electronic_puzzle_uses_both_parents():
    """
    ElectronicPuzzle uses behavior inherited from both Puzzle
    and Resettable.
    """
    puzzle = make(ElectronicPuzzle,
        "Circuit Lock",
        3,
        2,
        2,
    )

    initial_resets = puzzle["resets_left"]

    # solve() comes from Puzzle.
    call(puzzle, "solve")

    assert puzzle["solved"]

    # reset() comes from Resettable.
    result = call(puzzle, "reset")

    assert result
    assert not puzzle["solved"]
    assert puzzle["resets_left"] == initial_resets - 1


def test_reset_exhaustion():
    """
    reset() succeeds while a reset is available and fails once
    all resets have been used.
    """
    puzzle = make(ElectronicPuzzle,
        "Circuit Lock",
        3,
        2,
        1,
    )

    call(puzzle, "solve")

    first_reset = call(puzzle, "reset")

    assert first_reset
    assert puzzle["resets_left"] == 0
    assert not call(puzzle, "can_reset")

    second_reset = call(puzzle, "reset")

    assert not second_reset
    assert puzzle["resets_left"] == 0
    assert not call(puzzle, "can_reset")


def test_descriptions():
    """describe() produces the exact expected descriptions."""
    riddle = make(Riddle,
        "Mirror Words",
        4,
        3,
    )

    expected_riddle = (
        "Mirror Words is a difficulty-4 riddle, "
        "currently unsolved, with 3 hint(s) used."
    )

    assert call(riddle, "describe") == expected_riddle

    electronic_puzzle = make(ElectronicPuzzle,
        "Circuit Lock",
        3,
        2,
        1,
    )

    expected_electronic = (
        "Circuit Lock is a difficulty-3 electronic "
        "puzzle, currently unsolved, with 2 mistake(s) "
        "and 1 reset(s) left."
    )

    assert call(electronic_puzzle, "describe") == expected_electronic


def test_instance_state_is_independent():
    """
    Modifying one ElectronicPuzzle must not change another
    ElectronicPuzzle instance.
    """
    first = make(ElectronicPuzzle,
        "Circuit Lock",
        3,
        2,
        2,
    )

    second = make(ElectronicPuzzle,
        "Laser Grid",
        5,
        1,
        3,
    )

    # Store the complete state of the second object before
    # modifying the first one.
    second_state_before = dict(second)

    call(first, "solve")
    call(first, "reset")

    assert second == second_state_before


def test_multiple_inheritance_lookup_order():
    """
    When two parents provide the same method, the left-most
    parent is searched first.
    """
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

    LeftParent = new_class("LeftParent", [], {
        "identify": lambda obj: "left"
    })

    RightParent = new_class("RightParent", [], {
        "identify": lambda obj: "right"
    })

    Child = new_class("Child", [LeftParent, RightParent], {"_new": lambda obj: obj})
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
    child = make(Child)

    assert call(child, "identify") == "left"


def test_mutliple_inheritance_initialization_order():
    """Cooperative constructors run in the parents' MRO order."""
    calls = []
#---------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

    def new_FirstParent(obj): 
        calls.append("FirstParent")
        call_super(FirstParent_namespace, obj, "_new")
        
    FirstParent_namespace = {"_new": new_FirstParent}

    FirstParent = new_class("FirstParent", [], FirstParent_namespace)

    def new_SecondParent(obj): 
        calls.append("SecondParent")

    SecondParent = new_class("SecondParent", [], {"_new": new_SecondParent})

    def new_Child(obj):
        call_super(Child_namespace, obj, "_new")

    Child_namespace = {
        "_new": new_Child
    }
    Child = new_class("Child", [FirstParent, SecondParent], Child_namespace)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

    c = make(Child)

    assert calls == ["FirstParent", "SecondParent"]



def run_test(test):
    start = time.perf_counter()
    try:
        test()
        status = "PASS"
    except AssertionError:
        status = "FAIL"
    except Exception:
        status = "ERROR"
    return status, time.perf_counter() - start


def find_tests(pattern=None):
    tests = []
    for name, obj in globals().items():
        if name.startswith("test_") and callable(obj):
            if pattern is None or pattern in name:
                tests.append(obj)
    return tests


def run_tests(pattern=None):
    results = {"PASS": 0, "FAIL": 0, "ERROR": 0}
    for test in find_tests(pattern):
        status, duration = run_test(test)
        results[status] += 1
        print(f"{status:<5} {test.__name__} {duration:.6f}s")
 
    print()
    print(f"pass:  {results['PASS']}")
    print(f"fail:  {results['FAIL']}")
    print(f"error: {results['ERROR']}")
    return results


def parse_select(argv):
    if "--select" in argv:
        index = argv.index("--select")
        if index + 1 >= len(argv):
            print("Usage: python test_escape_room.py [--select PATTERN]")
            sys.exit(2)
        return argv[index + 1]
    return None


if __name__ == "__main__":
    run_tests(parse_select(sys.argv[1:]))
