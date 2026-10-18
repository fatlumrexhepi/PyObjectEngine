Here the class constructor system shall be elaborated (this md can be deleted or included idk)

The point of the constructor class system is to mimic the way Python deals with classes under the hood. When a class is defined in Python, what happens (roughly) is that an instance of a _metaclass_ is created, which is a class whose instances are classes. Doing this, other attributes, not set originally in the namespace (the body of the class which contains "custom attributes"), are computed based off of the arguments (name, parents, namespace, among others) passed to the metaclass (normal class syntax is translated into metaclass instantiation) and assigned to the class instance. These "computed attributes" (I will use this name from hereon) include "mro" and "abstractmethods" (named differently with real Python classes). Python uses computed attributes to ensure correct behaviour of instances, e.g. following the correct order when checking classes and their ancestry for methods, or throwing an error if an object is instatiated from a class which does not implement an inherited abstract method.

These computed attributes are needed to make possible some behaviour specified for the task. In the class we had been manually creating classes, but if we wanted to add to add these "computed attributes", we would have to do the computation ourselves and "hardcode" it for each class, which defeats the purpose of creating a class system using dictionaries.

MRO means method resolution order. It is relevant if a class can inherit multiple parents: in that case, there needs to be clear rules for the order in which classes are checked for methods. Each class has its associated MRO, and it is based off of their parents' MRO's (which in turn base their MRO's on their parents, and so on). The MRO is computed with the C3 linearization algorithm, which assures that each MRO follows 3 rules: 1. children are checked before parents; 2. parent order is preserved (e.g. for class C(A,B), A is checked before B; for class D(B,A) the reverse is true) and 3. parents' MRO is preserved (e.g. for class C(A,B), if B has MRO [B, X, Y], then for class C, B must be checked before X before Y, not matter what MRO A has. However, only the _relative order_ is preserved, which means other classes checked _before_, _after_, and _between_ B,X,Y is fine - what's not allowed is that B,X,Y be swapped around. So for example MRO(C) = [C,A,B,D,X,Y] is fine, but MRO(C) = [C,A,B,D,Y,X] would be false). If a child inherits parents with conflicting MRO's, a TypeError is thrown at class creation.

Abstract classes add complication to instantiation behaviour. When an abstract class defines abstract methods, these must be implemented among its descendants before a descendant can be instantiated. This can also happen "gradually": a direct subclass may implement one of the abstract methods and leave the other unimplemented, becoming thereby an abstract class itself. The best way to keep track of the abstract methods to be implemented by descendants is that each class has an "\_abstractmethods" attribute which holds the abstract methods it has inherited, but not yet implemented. Multiple inheritance adds additional complication: a child can inherit two sets of abstract methods, which would be merged for the child's abstract methods set. Additionally, an abstract method which it inherits from a parent could be implemented in another part of the ancestry, which means that each candidate abstract method from the abstract methods set has to be looked up via MRO to check whether it still needs implementation.

Both MRO and the set of abstract methods yet to be implemented could theoretically be computed recursively for each when needed, without classes having to store them as an attribute. However, that would be needlessly complex and add unnecessary computation. In a certain way, one could think of classes storing both attributes as a memoization technique.

Another difference between how Python works under the hood, and how our dictionary object system was implemented in class, is how object constructor methods in classes work. In python, "init" take as argument the calling object (self), and modifies it *in place*, it does not return a new object to be the object instance. Under the hood, is it another dunder function "new" which creates the actual object instance in memory, which then gets passed to the constructor functions. This is extremely useful because it makes calling super() inside of constructor functions easier, with no merging of dictionaries needed. We decided to implement this as well. 


Now the concrete implementation of these ideas in our system, using dictionaries, shall be defined.
First of all, "blueprint" or types shall be named, which are model patterns which the dictionaries must follow to
mimic real Python objects/classes.

type Object = {
    "{attribute_name}": any,
    [...],
    "_class": Class,
}

Here, the [...] refers to the fact that the normal "attribute" key value pair, provided by class constructor functions, can repeat an arbitrary number of times. The "_class" special attribute is set inside of make() upon creation of the object instance - the class constructor functions only modify it. 

type Class = {
    "method_name": FunctionType | "abstractmethod",
    [...],
    "_new": FunctionType,
    "_classname": string,
    "_mro": Class[],
    "_abstractmethods": set(string)
}

type Namespace = {
    "method_name": FunctionType | "abstractmethod",
    [...],
    "_new": FunctionType,
}

The methods and "_new" special method are defined in the namespace. All other special attributes are added inside of new_class. Due to problems with self-refentiality (a class potentially needs to pass an instance of itself to dict_super) the dictionary passed as namespace is the dict in memory which will get turned into the class dict - so if one wants to access the class itself inside of a method, the namespace dict needs to access itself inside of a method. 

A normal method inside of namespace can be of type FunctionType or just the string "abstractmethod". The latter is the representation of using the @abstractmethod marker. Since in most applications, the function body of an abstractmethod will not be needed (this is their whole purpose), in our system it will not be represented (though it should be noted that in Python, the function body of a abstract method can still be accessed through super()). It is "_abstractmethods" which decide whether a class is abstract, there is no representation of the inherited ABC class. This is because based on the assignment, it seems that the requirements dictate that a classes abstractness should be decided by its abstract methods. Also there is no representation of class attributes which are not methods, since they do not appear in our task and are less common.


OPEN QUESTIONS:

should "call" take classes, objects, or mro as input
should dict_super also call a method (to preserve calling object's mro), or otherwise how can functions called on dict_super be searched according to calling objects mro (which is how super() works in Python) or how should it work
correct error types