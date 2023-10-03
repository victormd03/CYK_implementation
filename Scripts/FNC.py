from functions import CKY,CKYProb
import random
from itertools import product

class FNC_transformer:

    """
    This class is a grammar transformer, from a simple CFG/PCFG to another one in FNC, which generates the same language as the original.
    It implements all the necessary methods to do so.
    Input: CFG/PCFG tuple which contains: (noterminals -> set() ,terminals -> set() ,rules -> Dict() ,start -> string).
           The dict of rules has the following structure:
           keys: different noterminals
           values: list(list(right-side of the rule)). If we have probabilities, the last position of the innermost list is the probability.
    Output: CFG/PCFG in FNC with the same structure as the input.
    """

    def __init__(self, Grammar):

        """
        Initialize the grammar variables for the class instance. Check if the grammar is not probabilistic.
        """

        self.n_t = Grammar[0]
        self.t = Grammar[1]
        self.r = Grammar[2]
        self.s = Grammar[3]

        try:                    #Probabilistic
            float(self.r[self.s][0][-1])  
            self._k = 1
        except ValueError:      #Non-Probabilistic
            self._k = 0


    def to_FNC(self):

        """
        This method is the responsible of directing the whole process of the grammar transformation by calling 
        all the necessary methods in the correct order. To transform a given grammar this function ought to be 
        called.

        Input: Self variables.
        Output: Transformed Self variables representing the new grammar.
        """
        
        self._START()
        self._DEL()
        self._TERM()
        self._BIN()
        self._UNIT()

        return self.n_t,self.t,self.r,self.s


    def _START(self):

        """
        This method is the one responsible of all the START transformations.
        The START transformations affect those rules which have the start (S) symbol on the Right Hand Side (RHS) of the rule.
        If those rules exist, we create a new start symbol "So", and the rule "So --> S", so that the start is not at RHS.
        """
        n_r = self.r.copy()                      #We don't want to modify the iterable that we are iterating.
        for key,value in self.r.items():         #Iterate over whole dict of rules: HEAD -> ANT
            for c in range(len(value)):     #And for all possible ANT given a certain HEAD.
                ant = value[c]
                if (self.s in ant):         #If START in RHS
                    if self._k:             #If PCFG
                        n_r["So"] = [[self.s,"1.0"]]
                    else:
                        n_r["So"] = [[self.s]]
                    self.n_t.add("So")
                    self.s = "So"
        self.r = n_r.copy()                 #Modify Self variable at the end of iteration.

    def _TERM(self):

        """
        This method is the one responsible of all the TERM transformations.
        The TERM transformations affect those rules  with nonsolitary terminal (t) terms at RHS.
        If those rules exist (i.e T --> A t), we create a new non-terminal (N) and a rule N --> t for each t that is nonsolitary.
        The old rules are replaced for the new ones: (i.e T --> A N)
        """
        n_r = self.r.copy()
        new_symbols = {}                         #Avoid creation of excessive new symbols if same terminal has to be replaced several times
        for key,value in self.r.items():         #Iterate over whole dict of rules: HEAD -> ANT
            for c in range(len(value)):     #And for all possible ANT given a certain HEAD.
                ant = n_r[key][c]
                if (len(ant)>(1+self._k)):     #Eliminate rules with nonsolitary terminal terms at RHS.
                    for i in range(len(ant)-self._k):
                        if (ant[i] in self.t):
                            if ant[i] not in new_symbols:
                                n = chr(random.randint(ord('A'), ord('Z')))   #Create new non-terminal symbol
                                while n in self.n_t:
                                    n = chr(random.randint(ord('A'), ord('Z')))    #ensure symbol not already in use
                                new_symbols[ant[i]] = n                        #Assign new symbol to replaced non-terminal.
                            else:                                             #If non-terminal already substituted by a single terminal symbol, use that one.
                                n = new_symbols[ant[i]]
                            if self._k:        
                                    n_r[n] = [[ant[i],"1.0"]]                      #Create new rule...
                            else:
                                n_r[n] = [[ant[i]]]
                            ant[i] = n; self.n_t.add(n)                        #and modify original rule
        self.r = n_r.copy()

    def _BIN(self):
        """
        This method is the responsible of all the BIN transformations.
        The BIN transformations include those rules with n non-terminal terms at RHS, with n > 2.
        If those rules exist (i.e T --> A B C) we create a new non-terminal (N) and a new rule (N --> B C)
        and we modify the original rule to end having T --> A N.
        """
        n_r = self.r.copy()
        for key,value in self.r.items():         #Iterate over whole dict of rules: HEAD -> ANT
            for c in range(len(value)):     #And for all possible ANT given a certain HEAD.
                ant = n_r[key][c]
                if (len(ant)>(1+self._k)):                       #At this point, all the rules with more than 2 symbols 
                    while not len(ant)==(2+self._k):                                 #at the RHS contain only Non-terminal symbols. We loop until binarized.
                        n = chr(random.randint(ord('A'), ord('Z')))   
                        while n in self.n_t:
                            n = chr(random.randint(ord('A'), ord('Z')))
                        if self._k:
                            n_r[n],ant[-3:-1] = [ant[-3:-1]+["1.0"]],n          #ant[-3:-1] is a list of the two last terms of ANT without the PROB and
                        else:                                                   #ant[-2:] is a list of the two last elements when its CFG. We merge this
                            n_r[n],ant[-2:] = [ant[-2:]],n                      #two symbols into a single one in a new rule: n -> ant[-2:], and
                        self.n_t.add(n)                                         #replace it.
        self.r = n_r.copy()

    def _UNIT(self):

        """
        This method is the responsible of all the UNIT transformations.
        The UNIT transformations include those rules with n non-terminal terms at RHS, with n = 1.
        If those rules exist (i.e T --> A, A --> a | b | c), we replace the original rule by adding the new one
        T --> a | b | c.
        There may be cases where a new UNIT transformation is required after a previous one, that's why we have to have
        a container of all the remaining UNIT transformations and loop until it's empty. If the new required transformation
        has already been trasnformed or is the one to be transformed, don't add the rule.
        """
        n_r = self.r.copy()
        unit = []                             #Container with all the remaining UNIT transformations
        removed = []                          #Container with all repeated to avoid infinite cycles.
        for key,value in n_r.items():         #Iterate over whole dict of rules: HEAD -> ANT
            for c in range(len(value)):     #And for all possible ANT given a certain HEAD.
                ant = n_r[key][c]
                if (len(ant) == (1+self._k)) and (ant[0] in self.n_t):   #If UNIT required, add to container.
                    unit.append((key,ant))                               #We add the list containing RHS

        while len(unit)>0:                   #Loop until container is empty
            key,rhs = unit.pop(0)            #Get remaining UNIT transformation as a rule
            removed.append((key,rhs))                #Add to removed
            n_r[key].remove(rhs)          #Pop original RHS of the rule to be transformed
            if rhs[0] != key:        #The case when the UNIT rule is A --> A can be deleted with no consequences.                             
                for a in n_r[rhs[0]]:      #Iterate over all rules with original RHS as LHS and create all the new rules.
                    if (key,a) not in removed:       #We just add the new rule if it is not being or has been removed before, thus avoiding cycles.
                        a_new = a.copy()                                        
                        if self._k:
                            a_new[-1] = str(round(float(a_new[-1])*float(rhs[-1]),3))    #New proba = Old_rule_proba * old_RHS --> X proba
                        n_r[key].append(a_new)                                             #Add new rule
                        if (len(a) == (1+self._k)) and (a[0] in self.n_t):                 #If new UNIT transf. required after transforming, add to container.
                            unit.append((key,a_new)) 
        self.r = n_r.copy()

    def _DEL(self):
        """
        This method is the responsible of all the DEL transformations.
        The DEL transformations include those rules of the type: A --> #, where # is the empty word.
        To do such transformations, we delete these rules, and for each rule where A is present ath RHS
        create all the rules such that some A is deleted.
        As in the UNIT transformations, when creating the new rules another DEL transformation may be required (if not previously transformed).
        This leads to the creation of a container of all the remaining DEL transformations ans another one for the already transformed.
        """
        n_r = self.r.copy()
        eps_rules = set();removed=set()          #Container of remaining rules to be transformed and one for already transformed. 
        for key,value in self.r.items():         #Iterate over whole dict of rules: HEAD -> ANT
            for c in range(len(value)):          #And for all possible ANT given a certain HEAD.
                ant = n_r[key][c]
                if len(ant)==(1+self._k) and (ant[0] == "#"):  #If rule is A --> #
                    if self._k:
                        eps_rules.add((key,ant[-1]))   #we also add the associated rule probability
                    else:
                        eps_rules.add((key))
        
        while len(eps_rules)>0:                      #Loop until no transformations required
            if self._k:
                key,prob = eps_rules.pop()   #Get key and prob of rule to be transformed
            else:
                key = eps_rules.pop()        #Get key of rule to be transformed
            
            if ["#"] in n_r[key]:                        #May not be added but needs to be treated
                n_r[key].remove(["#"])                   #Delete the rule
            removed.add(key)                       #Add to removed.

            n_r_2 = n_r.copy()               #Need a copy to avoid iterating and modifying the same iterable
                                
            for clau,valor in n_r_2.items():
                for c in range(len(valor)):
                    if self._k:
                        ant = n_r[clau][c][:-1]           #Get ANT of rule from which we'll produce all the combinations with some appearance of key removed.
                        prob_ant = n_r[clau][c][-1]       #Also prob if PCFG
                    else:
                        ant = n_r[clau][c]
                    if key in ant:
                        l =  list(product(range(2),repeat=len(ant)))[1:]     #List of all possible combinations of terms to be removed as a tuple of 0 (not remove) and 1 (remove)
                        for cmb in l:   #For each possible combination
                            new_rule = []  
                            for x in range(len(cmb)):
                                if cmb[x] == 0:  #If 0 (don't remove) add term to new_rule
                                    new_rule.append(ant[x])
                                elif (cmb[x] == 1) and (ant[x] != key):   #Those selected to be deleted but not key remain in the rule.
                                    new_rule.append(ant[x])

                            if (new_rule == []):   #If no terms added, it's the empty word.
                                new_rule.append("#")

                            if self._k:
                                new_rule.append(str(round(float(prob[-1])*float(prob_ant[-1]),3)))  #We add the respective probability.

                            if (new_rule[0] == "#"):                            #If empty word derived and not previously transformed, add to transform. Avoid infinite loop.  
                                if clau not in removed:                         #Unnecessary to create new rule R --> # because will be deleted. We only reference to it
                                    if self._k:                                 #as if it was created, detected and deleted.          
                                        eps_rules.add((clau,new_rule[-1]))
                                    else:
                                        eps_rules.add((clau))
                                    removed.add(clau)
                            
                            elif new_rule not in n_r[clau]:                    #If new rule not empty word and not already derived
                                n_r[clau].append(new_rule)                     #Add to set of rules

        self.r = n_r.copy()










 