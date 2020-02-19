##########################################################################################
#
# CSCI498: NFAMATCH
# CODE BY JESSY LIAO
#
# TODO:
#   - CHECK FOR A NODE POINTING TO NOWHERE BUT ALSO ISNT ACCEPTING
#   - DFA OPTIMIZE (HOT CROSS BUNS ALGORITHM) (HOPCROFTS)
#
##########################################################################################

import sys
import copy

#########################################################################################
# NFA TO DFA
#   - Follow Lambda
#   - Follow Char
#########################################################################################

# Follow Lambda: Helper method for NFA to DFA
#   Returns set of states from following the lambdas
def follow_lambda(start_set, table, lambduh):

    return_states = copy.deepcopy(start_set)

    L = [] # Let L be the empty stack 

    for t in start_set:
        L.append(t)

    # loop and check all states in L and follow the lambdas
    while L:
        t = L.pop()
        for l in table[t]:
            if l[1] == lambduh and l[0] not in return_states:
                return_states.append(l[0]) # add state if it follows in lambda
                L.append(l[0])

    return return_states

# Follow Char: Helper method for NFA to DFA
#   Return set of states that transition on a given symbol
def follow_char(start_set, table, symbol): 

    states = [] # list of states that transition on the symbol

    # loop and check all transitions
    for initial in start_set:
        for s in table[initial]:
            if s[1] == symbol:
                states.append(int(s[0])) # add state if it matches the transition symbol
    
    return states

# Convert NFA to DFA
def nfa_to_dfa(table,accept,lambduh,alphabet): 

    # Step 1:
    #   L = empty stack
    #   A = set of accepting states for N
    #   i = starting state of N

    L = []
    A = accept
    i = [0]

    B = tuple(follow_lambda(i,table,lambduh))

    dfa_accept = []
    dfa_table = {}
    dfa_table[B] = []

    L.append(B)
    
    # Step 2:
    #   Loop through and generate sets for each alphabet symbol
    #   Add all unique sets back into the stack
    #   Continue until stack is empty

    while L:
        S = list(L.pop())
        
        # for each symbol, generate set of states that transition on this symbol
        for a in alphabet:
            # R is the set of states that transition on a symbol
            R = follow_lambda(follow_char(S, table, a), table, lambduh)
            R.sort() # sort R because R is a tuple and without sort the same 
                     # state might get added into the stack

            if R != []:
                # check whether the state exists in the DFA table
                if tuple(S) in dfa_table:
                    value = dfa_table[tuple(S)]
                else: 
                    value = []

                # add value into DFA table
                new_state = (tuple(R),a)
                if new_state not in value:
                    value.append(new_state)
                dfa_table[tuple(S)] = value

                # if R is a new state and its not empty, add to the stack
                if tuple(R) not in dfa_table and R != []:
                    L.append(R)

            # checks if R is an accept state
            if set(R).intersection(set(accept)) != set() and tuple(R) not in dfa_accept:
                dfa_accept.append(tuple(R))
        
        # if S has no outgoing transitions, but is accepting, needs tobe in table
        if set(S).intersection(set(accept)) and tuple(S) not in dfa_table:
            dfa_table[tuple(S)] = []

    return dfa_table, dfa_accept

#########################################################################################
# DFA Optimization
#   - Simplify States
#   - Create Table
#########################################################################################

# Simplify States
#   My implementatiion of the DFA is a dictionary with states represented as tuples
#   This function is used to simplify the tuples into readable ints
def simplify_states(dfa_table, dfa_accept):

    simple_table = {}
    simple_accept = []
    index_table = {}

    count = 0
    for d in dfa_table:
        index_table[d] = count
        count = count + 1

    for d in dfa_table:
        if dfa_table[d] == []:
            simple_table[index_table[d]] = []
        for l in dfa_table[d]:
            if index_table[d] in simple_table:
                value = simple_table[index_table[d]]
                value.append((index_table[l[0]], l[1]))
                simple_table[index_table[d]] = value
            else:
                simple_table[index_table[d]] = [(index_table[l[0]], l[1])]
        
    for a in dfa_accept:
        simple_accept.append(index_table[a])

    return simple_table, simple_accept

def create_transition_table(dfa_table, dfa_accept, alphabet):

    transition_table = [['E' for x in range(len(alphabet)+2)] for y in range(len(dfa_table))] 

    count = 0
    for d in dfa_table:
        transition_table[count][1] = d
        if d in dfa_accept: 
            transition_table[count][0] = '+'
        else:
            transition_table[count][0] = '-'
        count = count + 1

    alphabet = list(alphabet)

    for row in transition_table:
        for d in dfa_table[row[1]]:
            row[alphabet.index(d[1])+2] = d[0]

    return transition_table

def print_pretty(matrix):
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))


# Optimize DFA (Hot cross buns algorithm) (Hopcrofts)
def dfa_opt(dfa_table, dfa_accept, alphabet):

    # Step 0:
    #   Simplify dfa_table and dfa_accept

    dfa_table, dfa_accept = simplify_states(dfa_table, dfa_accept)

    # Step 1: 
    #   M = empty set 
    #   L = empty set
    #   Populate accepting states and alphabet into L
    #   Populate non-accepting states and alphabet into L
    M = []
    L = []

    acc = set(dfa_accept)  # populate accepting state
    dfa = set(dfa_table)    
    for c in acc:
        dfa.remove(c)      # populate all states, remove accepting, leaving non-accepting

    L.append((acc, alphabet))
    L.append((dfa, alphabet))

    # Step 2:
    #   While L is not empty
    #   S, C = pop L (Set, Alphabet)
    #   remove one symbol from alphabet
    #   segregate state s by T[S][C]a
    while L: 
        current_set = L.pop()
        S = current_set[0]    # set of states
        C = list(current_set[1])    # alphabet list

        c = C.pop(0)
        segregate = set()

        diff_sets = {}
        
        for s in S:
            count = 0
            for c_tuples in dfa_table[s]:
                if c == c_tuples[1]:
                    count = 1
                    if c_tuples[0] in diff_sets:
                        value = diff_sets[c_tuples[0]]
                        value.append(s)
                        diff_sets[c_tuples[0]] = value
                    else: 
                        diff_sets[c_tuples[0]] = [s]
        if not C:
            M.append(S)
        else:
            for diff in diff_sets:
                if len(diff_sets[diff]) != 1:
                    L.append((set(diff_sets[diff]),C))

    transition_table = create_transition_table(dfa_table, dfa_accept, alphabet)

    # Step 3:
    #   Merge States
    for m in M: 
        m = list(m)
        combine = m[0]
        merge = m[1:]
        for a in range(len(transition_table)):
            for b in range(len(transition_table[0])):
                if transition_table[a][b] in merge:
                    transition_table[a][b] = combine

    unique_table = set()

    for t in range(len(transition_table)):
        unique_table.add(tuple(transition_table[t]))

    for u in unique_table:
        print(u)

    return unique_table

#########################################################################################
# MAIN/PREPROCESS
#   - create_nfa_table
#   - main function
#########################################################################################

# Handles forming the NFA table, accepting state list, lambda, and alphabet
def create_nfa_table(filename):
    # Check if file is empty
    # Doesnt exist
    with open(filename) as file_input: 
        first_line = next(file_input).split()
        
        # check if file is empty
        if first_line == "":
            sys.exit(1)
        
        # initialize number of states, lambda, and alphabet
        num_states = first_line[0]
        lambduh = first_line[1]
        alphabet_list = first_line[2:]
        
        # alphabet is a dict (may or may not be useful when implementing optimize DFA)
        alphabet = {}
        for index,a in enumerate(alphabet_list):
            alphabet[a] = index
        
        table = {}
        accept = []

        # initialize NFA table to empty lists (representation of NFA diagram)
        for table_size in range(int(num_states)):
            table[table_size] = []

        # go through and add states to the proper table entry
        for line in file_input:
            line = line.split()

            # if state is accepting, add it to the list
            if line[0] == "+":
                accept.append(int(line[1]))
            
            if len(line) == 3:
                # this is a check for a node transitioning to nothing
                node = (int(line[2]),None)
            else:
                node = (int(line[2]),line[3]) 
            
            value = table[int(line[1])]
            value.append(node)
            
            table[int(line[1])] = value

    return table, accept, lambduh, alphabet

def main(argv): 

    if len(argv) < 3: 
        print('Usage: [nfa_file] [output_file] [tokens(optional)]')
        sys.exit(1)
    elif len(argv) == 3: 
        inpoot_file = argv[1]
        output_file = argv[2]

    else:
        inpoot_file = argv[1]
        output_file = argv[2]
        tokens = argv[3:]

    table,accept,lambduh,alphabet = create_nfa_table(inpoot_file)

    for t in table:
        print(t, table[t])
    print("--------------------------------")

    dfa_table, dfa_accept = nfa_to_dfa(table,accept,lambduh,alphabet)
    
    dfa_opt(dfa_table, dfa_accept, alphabet)

    sys.exit(0)

    
if __name__ == '__main__':
    main(sys.argv)


