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

# Find states connected by lambduh
def follow_lambda(state_set, table, lambduh):

    states = []

    # loop through the set of states given
    for initial in state_set:
        # add it to the return set if not already in there
        if initial not in states:
            states.append(initial)
        
        child = table[initial] # list of nodes current node can transition to
        stack = []             # stack for while loop

        # this could be better optimized
        # will do later (maybe)
        for s in child:
            if s[1] == lambduh:
                for c in table[int(s[0])]:
                    stack.append(c)
                if int(s[0]) not in states:
                    states.append(int(s[0]))

        while stack:
            t = stack.pop()
            if t[1] == lambduh:
                if int(t[0]) not in states:
                    states.append(int(t[0]))
                for e in table[int(t[0])]:
                    if int(e[0]) not in states and e[1] == lambduh:
                        stack.append(e)
                        states.append(int(e[0]))

    return states

# Find states transition on a specific symbol
def follow_char(state_set, table, symbol): 

    states = [] # list of states that transition on the symbol

    # loop and check all transitions
    for initial in state_set:
        for s in table[initial]:
            # add state if it matches the transition symbol
            if s[1] == symbol:
                states.append(int(s[0]))
    
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
    # Loop through and generate sets for each alphabet symbol
    # Add all unique sets back into the stack
    # Continue until stack is empty
    while L:
        S = list(L.pop())
        
        # for each symbol, generate set of states that transition on this symbol
        for a in alphabet:
            # R is the set of states that transition on a symbol
            R = follow_lambda(follow_char(S, table, a), table, lambduh)
            R.sort() # sort R because R is a tuple and without sort the same state might get added into the stack

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

# Optimize DFA (Hot cross buns algorithm) (Hopcrofts)
def dfa_opt():
    return 0

# Handles forming the NFA table, accepting state list, lambda, and alphabet
def initialize_table(filename):
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
            print(line)

            # if state is accepting, add it to the list
            if line[0] == "+":
                accept.append(int(line[1]))
            
            if len(line) == 3:
                # this is a check for a node transitioning to nothing
                node = (line[2],None)
            else:
                node = (line[2],line[3]) 
            
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

    table,accept,lambduh,alphabet = initialize_table(inpoot_file)

    for a in table:
        print(a, table[a])

    print("-------------------------------------------------------")

    #print(follow_lambda([6], table, lambduh))
    #print(follow_char([2,3,5,7,10], table, 'P'))
    dfa_table, dfa_accept = nfa_to_dfa(table,accept,lambduh,alphabet)

    for d in dfa_table:
        print(d, dfa_table[d])

    print(dfa_accept)

    sys.exit(0)

    
if __name__ == '__main__':
    main(sys.argv)


