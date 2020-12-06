class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf
        #print(self.children)
        #print(self.leaf)

    #def __repr__(self, level=0):
    #    ret = "\t" * level + repr(self.type) + "\n"
    #    if self.children:
    #        if self.leaf:
    #            for l in self.leaf:
    #                ret += self.type + "\t" + l

    #        for child in self.children:
    #            ret += child.__repr__(level + 1)

    #   else:
    #        if self.leaf:
    #            for l in self.leaf:
    #                ret += self.type + "\t" + l


     #   return ret

    #def __repr__(self):
    #    return '<tree node representation>'

    def other_name(self, level=0):
        if self.children:
            if type(self.type) == Node:
                print('\t' * level + repr(self.type.type))
            else:
                print('\t' * level + repr(self.type))
            if self.type == "stmt list":
                i = len(self.children)
                tmp = self.children
                #print(len(self.children))
                while(i >= 1):
                    self.children = tmp[i - 1]
                    i -= 1

                    if type(self.children)== Node:
                        self.children.other_name(level + 1)

                    elif type(self.children)== list:
                        for child in self.children:
                            if child and type(child) == Node:
                                child.other_name(level + 1)
                            elif child and type(child) != list:
                                print('\t' * level + str(child))

            #else:
            #    print('\t' * level + repr(self.type))
            else:
                if type(self.children) == Node:
                    self.children.other_name(level + 1)

                elif type(self.children) == list:
                    for child in self.children:
                        if child and type(child) == Node:
                            child.other_name(level + 1)
                        elif child and type(child) != list:
                            print('\t' * level + str(child))

        #else:
            #if type(self.leaf) == list:
                #for l in self.leaf:
                 #  if l:
                 #       print('\t' * level +" " + l)

            #elif type(self.leaf) == Node:
                #self.leaf.other_name(level + 1)

            #else:
                #print('\t' * level + repr(self.type)+"\t" + self.leaf)


class SkipStmt:
    def __init__(self, lines):
        self.lines = lines
        self.type = "Skip"
        self.__typecorrect = True

    def printout(self):
        print("Skip")

    def typecheck(self):
        return self.__typecorrect

    def has_return(self):
        return 0