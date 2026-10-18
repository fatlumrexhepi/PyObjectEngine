from types import FunctionType

#copy paste bc import conflicts

def find(mro, method_name): #extra mro argument, because can be called from dict_super
    for mro_class in mro:               #where the desired mro doesn't match the class mro
        func = mro_class.get(method_name)
        if (func):
            return func
    raise NotImplementedError("method could not be found") #error type could be changed



def MRO(classDict):
    parents = classDict["_parents"]

    return [classDict] + merge([*[parent["_mro"] for parent in parents], parents])



def merge(classLists):

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




def get_abstract_methods(classDict):
    parents = classDict["_parents"]
    own_abstract_methods = set(method_name for method_name, value in classDict.items() if value == "abstractmethod")
    candidate_set = set().union(*[parent["_abstractmethods"] for parent in parents], own_abstract_methods) 
    abc_methods_set = set()
    for candidate in candidate_set:
        func = find(classDict["_mro"], candidate)

        if func == "abstractmethod":
            abc_methods_set.add(candidate)
    return abc_methods_set


        

