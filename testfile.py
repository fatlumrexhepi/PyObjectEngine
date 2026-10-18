def print_sth(arg):
    print(arg)

dict = {
    "a": "a",
    "print": lambda x: print_sth(dict)
}

dict["print"]("a")