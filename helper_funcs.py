
from types import FunctionType
from typing import Any, Literal

type ClassDict = dict[str, str | list[ClassDict] | FunctionType]
type ObjectDict = dict[str, str | ClassDict | FunctionType]
type NameSpaceDict = dict[str, str | FunctionType]

#Class constructor
def new_class(name: str, parents: list[ClassDict], namespace: NameSpaceDict) -> ClassDict:
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
def make(class_dict: ClassDict, *args: any) -> ObjectDict:
    if class_dict["_abstractmethods"]: 
         raise TypeError("abstract class cannot be instantiated") 
    
    object_dict = {"_class": class_dict} #class constructors only modify this inital object
    class_dict["_new"](object_dict, *args)
    return object_dict


def find(mro: list[ClassDict], method_name: str) -> FunctionType | Literal["abstractmethod"]:
    for mro_class in mro:             
        func = mro_class.get(method_name)
        if (func): return func
    raise NotImplementedError("Method could not be found") 


def call(entity_dict: ClassDict | ObjectDict, method_name: str, *args) ->Any:
    #both objects and classes should be callable. They are identified by unique special attributes _class/_classname
    if (entity_dict.get("_classname")): 
        mro = entity_dict["_mro"]
        method = find(mro, method_name)
        if isinstance(method, FunctionType): return method(*args) #object instance must be passed by args as first arg
        else: raise ValueError("cannot call abstract method")
        
    else:
        mro = entity_dict["_class"]["_mro"]
        method = find(mro, method_name)
        if isinstance(method, FunctionType): return method(entity_dict, *args) #EVERY method must take an object as argument
        else: raise ValueError("cannot call abstract method")


def call_super(class_dict: ClassDict, object_dict: ObjectDict, method_name: str, *args: Any) -> Any: #returns next up class
    mro = object_dict["_class"]["_mro"] #mro to loop through is object's mro
    for (i, mro_class) in enumerate(mro):
        
        if mro_class is class_dict: 
            if (mro[i+1:]): 
                func = find(mro[i+1:], method_name)
                if isinstance(func, FunctionType): return func(object_dict, *args)

    raise ValueError("method could not be called with super()") 


#class constructor helper funcs

def MRO(class_dict: ClassDict) -> list[ClassDict]:
    parents = class_dict["_parents"]  

    return [class_dict] + merge([*[parent["_mro"] for parent in parents], parents]) 


def merge(classLists: list[list[ClassDict]]) -> list[ClassDict]: 

    classLists = [list(classList) for classList in classLists] #copy classList to avoid side effects

    retList = []
    i = 0
    while i < len(classLists): #terminating condition: either all classLists empty (success) or mro contradiction (failure) 
        currList = classLists[i]
        if len(currList) == 0: 
            i += 1
            continue 
        head = currList[0]
        conflict = False

        for classList in classLists: #check whether head is in any tail 
            if len(classList) < 2: continue 
            if any(head is class_dict for class_dict in classList[1:]): 
                conflict = True #appending the head would violate another MRO
                break

        if conflict: #cannot add any el of classList without violating other mro
            i += 1
        else:
            for classList in classLists: #delete all matching heads
                if len(classList) == 0: continue
                if classList[0] is head:
                    del classList[0]
            retList.append(head)

            i = 0 #restart with each success to process newly revealed classes
    if all(len(classList)== 0 for classList in classLists): #all lists empty -> success
        return retList
    else: 
        raise ValueError("MRO not resolvable")



def get_abstract_methods(class_dict: ClassDict) -> list[ClassDict]:
    parents = class_dict["_parents"] 
    own_abstract_methods = set(method_name for method_name, value in class_dict.items() if value == "abstractmethod") 
   
    candidate_set = set().union(*[parent["_abstractmethods"] for parent in parents], own_abstract_methods) 
    
    abc_methods_set = set()
    for candidate in candidate_set:
        func = find(class_dict["_mro"], candidate) 

        if func == "abstractmethod":
            abc_methods_set.add(candidate)
    return abc_methods_set


        

