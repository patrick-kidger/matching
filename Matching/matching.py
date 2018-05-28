# An algorithm for iterating through the maximal number of disjoint perfect 
# matchings of a complete graph.
# For all vertex pairs, there exists precisely one matching such that pair of 
# vertices is in the matching.
#
# Can be used to read a list of names from a file, to pair people up.
#
# Usage:
# For normal usage, that is loading a list of names from the the 
# newline-separated names.txt, which should be within the same folder as this
# script, just run 'python matching.py'
# For testing that it works, run either 'python matching.py test' to check all
# even complete graphs up to and including 98 vertices, or 
# 'python matching.py test <max>' to check from complete graphs with vertices 
# from 2 up to <max>, or 'python matching.py test <min> <max>' to check 
# complete graphs with vertices from <min> up to <max>.


# What the extra fake person is called to bring an odd number of people up to 
# an even number of people.
SPACER = ''
# How many characters of space should be allowed for printing names. Not really
# a problem if a name is longer than this, it'll just make that line's 
# formatting look a little strange. (But still perfectly intelligible)
PADDING = 25


import itertools
import math
import sys


# Save ourselves some hassle
class _modulolist(list):
    def __getitem__(self, item):
        item = item % len(self)
        return super(_modulolist, self).__getitem__(item)
    

# When the graph has twice an odd number of vertices, then the matchings that 
# link up a vertex with the vertices an even number of vertices away from it
# take a special format. In order to make this work, we also need to reserve
# the matching to the vertex opposite.
# (With 'opposite' and 'two away' being in terms of going around the circle
# of vertices in a depiction of a complete graph.)
def _twice_an_odd_handling(elements):
    # We take a list of elements as an input, rather than just a number like in
    # disjoint_matchings, for ease with how this is used below.
    assert len(elements) % 2 == 0
    halflen = len(elements) // 2
    elements = _modulolist(elements)
    
    for index in range(halflen):
        yieldval = [(elements[index], elements[index + halflen])]
        for ind in range(1, halflen):
            yieldval.append((elements[index + ind], elements[index - ind]))
        yield yieldval
    
    
# Finds the number of factors of two that the inputted number has.
def _two_factors(n):
    if n == 0:
        raise ValueError('_two_factors input cannot be zero.')
    count = 0
    while n % 2 == 0:
        n = n / 2
        count += 1
    return count
    

# A generator for the matchings we're seeking.
def disjoint_matchings(n):
    twofactor = _two_factors(n)
    if twofactor == 0:
        raise ValueError('The input number must be even.')
    reducedtwofactorpower = 2 ** (twofactor - 1)
    twofactorpower = 2 * reducedtwofactorpower
    halfn = n // 2
    
    # Handle the non-special-cases first: for these, we are essentially taking
    # every other edge of an even cycle in the graph. In the case of i and n 
    # being coprime, it will a Hamiltonian cycle, for group-theoretic reasons.
    for i in range(1, n):  # i is the offset between vertices in the matching
        # Skip special cases
        if i % twofactorpower == 0:
            continue
        if i == n / 2:
            continue
            
        yieldval = []
        gcd = math.gcd(n, i)
        for k in range(gcd):
            yieldval.extend([((k + j * i) % n, (k + (j + 1) * i) % n) 
                             for j in range(0, n // gcd, 2)])
        yield yieldval
        
    # Split the graph up into reducedtwofactorpower subgraphs to handle the 
    # special cases
    subgraph_generators = []
    for subgraph_index in range(reducedtwofactorpower):
        subgraph = [i % n for i in range(subgraph_index, 
                                         subgraph_index + n, 
                                         reducedtwofactorpower)]
        subgraph_generators.append(_twice_an_odd_handling(subgraph))
    for subgraph_matchings in zip(*subgraph_generators):
        yield list(itertools.chain.from_iterable(subgraph_matchings))
        
        
# Test that our algorithm actually works: that every vertex pair does indeed 
# appear in precisely one matching.
_sentinel = object()
def test(min_test=_sentinel, max_test=_sentinel):
    if min_test == _sentinel:
        min_test = 100
    if max_test == _sentinel:
        max_test = min_test
        min_test = 2
        
    for n in range(min_test, max_test, 2):
        data = [set() for _ in range(n)]
        for matching in disjoint_matchings(n):
            for index_one, index_two in matching:
                if index_one in data[index_two]:
                    raise Exception('{} in {}'.format(index_one, index_two))
                if index_two in data[index_one]:
                    raise Exception('{} in {}'.format(index_two, index_one))
                data[index_one].add(index_two)
                data[index_two].add(index_one)
        for vertex, edges in enumerate(data):
            if len(edges) != n - 1:
                raise Exception('Vertex {} has only {} edges, expected {}'
                                ''.format(vertex, len(edges), n - 1))
        print('{} vertices passed'.format(n))
    print('Test complete: vertices from {} to {} tested.'
          ''.format(min_test, max_test))

    
# Wrapper around disjoint_matchings to read input from a file and provide other
# user-friendly features.
def main():
    try:
        input('Usage: Run this script in the same location as the file '
              '\'names.txt\', which should be a file with a list of names in,'
              ' each name on a new line, with blank lines are ignored.\nPress '
              'Control-C (or Command-C on a Mac) at any time to quit. Press '
              'enter to continue.')
        try:
            with open('names.txt', 'r') as f:
                name_list = f.read().split()
        except FileNotFoundError:
            print('Could not find the names file - is the file \'names.txt\' '
                  'in the same directory as this script?')
        except IOError:
            print('There was a problem with opening the file. The problem was '
                  '_not_ that the file was in the wrong location. There is a different error message for that!')
            
        if len(name_list) == 0:
            print('The file names.txt contains only blank lines. Terminating '
                  'process. Press enter to quit.')
            input()
            sys.exit()
            
        # Make sure we have an even number of people.
        if len(name_list) % 2 != 0:
            name_list.append(SPACER)

        start_again = True
        while start_again:
            for i, matching in enumerate(disjoint_matchings(len(name_list))):
                input('Press enter for the next matching.')
                print('Matching {}:'.format(i + 1))
                for index_one, index_two in matching:                    
                    print('{name_one:>{PADDING}} --- {name_two}'
                          ''.format(PADDING=PADDING, 
                                    name_one=name_list[index_one], 
                                    name_two=name_list[index_two]))
                print('\n')
            
            while True:
                start_again_inp = input('All matchings complete. Start again? '
                                        'Y/N: ').lower()
                if start_again_inp == 'y':
                    start_again = True
                    break
                elif start_again_inp == 'n':
                    start_again = False
                    break

            if start_again:
                print('Starting again!')
                print('.\n.\n.\n')
    except KeyboardInterrupt:
        sys.exit()
        
if __name__ == '__main__':
    argv_len = len(sys.argv)
    if argv_len >= 2 and sys.argv[1] == 'test':
        if argv_len == 2:
            test()
        elif argv_len == 3:
            test(int(sys.argv[2]))
        elif argv_len == 4:
            test(int(sys.argv[2]), int(sys.argv[3]))
    else:
        main()
