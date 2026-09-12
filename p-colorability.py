# @author Garrett Rhoads, Emma Hirsch, Liam Casey
# @file p-colorability.py
# @date 9-7-26
# @brief assign variables to each arc label all crossings positive or negative 
#        and encode in n-ples starting from over arc counter clockwise over 
#        strand * 2 - under strands = 0

import typing

def check_coloring(knot, coloring, p):
    # returns 1 if 'coloring' satisfies every crossing relation, else 0
    num_crossings = len(knot)
    for i in range(num_crossings):
        over = knot[i][1]
        u1 = knot[i][2]
        u2 = knot[i][3]

        lhs = (2 * coloring[over] - coloring[u1] - coloring[u2]) % p

        if lhs != 0:
            return 0

    return 1


def compute_colorings(knot, p):
    # knot: list of crossings, each (sign, over, under_1, under_2)
    # p:    modulus (Z/pZ)
    # number of arcs = number of crossings = len(knot)
    n = len(knot)

    valid_colorings = []
    coloring = [0] * n

    total = p ** n

    # walk through every base-p string of length n
    for count in range(total):
        remainder = count
        for i in range(0, n):
            coloring[i] = remainder % p
            remainder = remainder // p
        
        if check_coloring(knot, coloring, p) == 1:
            valid_colorings.append(list(coloring))
            
    return valid_colorings

def sort_trivial(colorings):
    trivial_colorings = []
    nontrivial_colorings = []
    for i in range(0, len(colorings)):
        c = colorings[i][0]
        trivial = True
        for j in range(0, len(colorings[i])):
            if c != colorings[i][j]:
                trivial = False
        if trivial:
            trivial_colorings.append(list(colorings[i]))
        else:
            nontrivial_colorings.append(list(colorings[i]))

    return (trivial_colorings, nontrivial_colorings)


def main():
    sol = sort_trivial(compute_colorings([(1, 0, 2, 1), (1, 1, 0, 2), (1, 2, 1, 0)], 5))
    print(f"trivial colorings = {sol[0]}\nnon-trivial colorings = {sol[1]}")

if __name__ == "__main__":
    main()
