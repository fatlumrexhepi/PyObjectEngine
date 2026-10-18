from helper_funcs import MRO, merge, get_abstract_methods
from types import FunctionType


#Class constructor
def new_class(name, parents, namespace):
    #the namespace dict is directly modified. 
    # It is the set which will be returned afterward.
    # This is to preserve self-referentiality in namespace methods
    class_dict = namespace
    class_dict["_classname"] = name
    class_dict["_parents"] = parents
    class_dict["_mro"] = MRO(class_dict)
    class_dict["_abstractmethods"] = get_abstract_methods(class_dict)
    return class_dict


# Methods (under the hood)
def make(class_dict, *args):
    if class_dict["_abstractmethods"]: #abstract classes should not be instantiated
         raise TypeError("abstract class cannot be instantiated") #error type could be changed
    object_dict = {"_class": class_dict} #class constructors only modify this inital object
    class_dict["_new"](object_dict, *args)
    return object_dict

def find(mro, method_name): #extra mro argument, because can be called from dict_super
    for mro_class in mro:               #where the desired mro doesn't match the class mro
        func = mro_class.get(method_name)
        if (func): return func
    raise NotImplementedError("Method could not be found") #error type could be changed

def call(object_class_dict, method_name, *args):
    #both objects and classes should be callable. They are identified by unique special attributes _class/_classname
    if (object_class_dict.get("_classname")): 
        mro = object_class_dict["_mro"]
        method = find(mro, method_name, *args)
        if isinstance(method, FunctionType): return method(*args) #object instance must be passed by args
        else: raise ValueError("cannot call abstract method")
        
    else:
        mro = object_class_dict["_class"]["_mro"]
        method = find(mro, method_name, *args)
        if isinstance(method, FunctionType): return method(object_class_dict, *args) #EVERY method must take an object as argument
        else: raise ValueError("cannot call abstract method")

def dict_super(object_dict, class_dict): #returns next up class
    mro = object_dict["_class"]["_mro"]
    print([dict["_classname"] for dict in mro])

    for (i, mro_class) in enumerate(mro):
        print(f"mro_class: {mro_class["_classname"]}, compare class: {class_dict["_classname"]}, {mro_class is class_dict}")
        if mro_class is class_dict: #find the matching class in obj's mro
            if (mro[i+1]): return mro[i+1] #return next class of mro
    raise NotImplementedError #next up class doesnt exist
        
    '''
#Object creator / Constructors
def new_puzzle(object_dict, name, difficulty):
    return {
    "name": name,
    "difficulty": difficulty,
    "solved": False,
    }
    
def new_Resettable():
    pass

def new_Riddle(name, difficulty, hints_used):
    if check_abstract(Riddle) != True:
        raise NotImplementedError("Method ## must be implemented")
    else:
        return {
        "name": name,
        "difficulty": difficulty,
        "hints_used": hints_used,
        "_class": Riddle
        }
    
def new_ElectronicPuzzle(name, difficulty, mistakes, resets_left):
    if check_abstract(ElectronicPuzzle) != True:
        raise NotImplementedError("Method ## must be implemented")
    else:
         return {
        "name": name,
        "difficulty": difficulty,
        "mistakes": mistakes, 
        "resets_left": resets_left,
        }


## Methods for "Puzzle"
def solve(obj): 
    obj["solved"] = True

##abstract methods

def abstract_score(self):
    pass

def abstract_describe(self):
    pass

###score

def score_riddle(self):
        return max(0, self.difficulty * 10 - self.hints_used * 2)

def score_ElectronicPuzzle(self):
        return max(0, self.difficulty * 15 - self.mistakes * 3)

###describe

def describe_riddle(self):
        state = "solved" if self.solved else "unsolved"
        return (
            f"{self.name} is a difficulty-{self.difficulty} riddle, "
            f"currently {state}, with {self.hints_used} hint(s) used."
        )

def describe_ElectronicPuzzle(self):
        state = "solved" if self.solved else "unsolved"
        return (
            f"{self.name} is a difficulty-{self.difficulty} electronic "
            f"puzzle, currently {state}, with {self.mistakes} mistake(s) "
            f"and {self.resets_left} reset(s) left."
        )



#Classes
ABC = {}

Puzzle = {
        "abstract_score": abstract_score,
        "abstract_describe": abstract_describe,
        "solve": solve,
        "_classname": "Puzzle",
        "_parent": ABC
}

Resettable = {
        "_classname": "Resettable",
        "_parent": None
}

Riddle = {
        "score": score_riddle,
        "describe": describe_riddle,
        "_classname": "Riddle",
        "_parent": [Puzzle]
}

ElectronicPuzzle = {
        "score": score_ElectronicPuzzle,
        "describe": describe_ElectronicPuzzle,
        "_classname": "ElectronicPuzzle",
        "_parent": [Puzzle, Resettable]
}
'''

#Testing CCS 

A = new_class("A", [], {})
B = new_class("B", [], {})

abstract_namespace = {
    "example_method": lambda x: print("hi"),
    "do_sth": lambda x: print("no")
}

Abstract = new_class("Abstract", [A, B], abstract_namespace)
RandClass = new_class("RandClass", [A,B], {})

def new_simple_obj(object_dict, name):
    object_dict["name"] = name

def do_sth(object_dict):
    dict_super(object_dict, simple_namespace)["do_sth"]("a")

simple_namespace = {
    "_new": new_simple_obj,
    "do_sth": do_sth
}

Simple = new_class("Simple", [Abstract, RandClass, B], simple_namespace)
simple_obj = make(Simple, "object")

print(simple_namespace is Simple)
call(simple_obj, "do_sth")

'''
def new_ultrasimple_obj(object_dict, name):
    object_dict["name"] = name

ultrasimple_namespace = {
    "_new": new_ultrasimple_obj,
    "do_sth": do_sth,
    "example_method": do_sth
}

Ultrasimple = new_class("Ultrasimple", [Simple], ultrasimple_namespace)
'''



