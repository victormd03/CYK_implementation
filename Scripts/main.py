from functions import CKY,CKYProb,read_grammar
from FNC import *


#Gr_1 = read_grammar("CYK_1.txt")
# Gr_1_prob = read_grammar("CYK_1_Prob.txt")
# Gr_2 = read_grammar("CYK_2.txt")
# Gr_0 = read_grammar("CYK_0.txt")
# Gr_3 = read_grammar("CYK_3.txt")
Gr = read_grammar("CYK_2_Prob.txt")
#Gr_z està resolt a https://courses.cs.washington.edu/courses/cse322/08au/lec14.pdf


# fnc = FNC_transformer(Gr_3)
# fnc_grammar = fnc.to_FNC()
# print(fnc_grammar[2])
alg = CKYProb(Gr)
print(alg.check_word("el nano eligio un coche rapido", phrase=True))
alg.show_tree("el nano eligio un coche rapido",phrase=True)


