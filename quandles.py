# @author Garrett Rhoads, Emma Hirsch, Liam Casey, Miffy Wang
# @file quandles.py
# @date 9-17-26
# @brief Given a quandle operation table, proivdes useful tools for computing
#        things with them


def is_quandle(quandle):
    order = len(quandle)

    # check itempotency
    for i in range(order):
            if quandle[i][i] != i:
                return False

    # Check right invetablility
    for i in range(order):
        seen = set()
        for j in range(order):
            if quandle[j][i] in seen:
                return False
            seen.add(quandle[j][i])

    return True

def is_homomorphism(quandle_1, quandle_2, mapping):
    order_1 = len(quandle_1)
    order_2 = len(quandle_2)
    for i in range(order_1):
        for j in range(order_1):
            if (mapping[quandle_1[i][j]] != quandle_2[mapping[i]][mapping[j]]):
                return False
    return True

def gen_all_homomorphisms(quandle_1, quandle_2):
    all_homomorphisms = []
    order_1 = len(quandle_1)
    order_2 = len(quandle_2)

    candidate_map = [0] * order_1
    total = order_2 ** order_1
    for count in range(total):
        remainder = count
        for i in range(0, order_1):
            candidate_map[i] = remainder % order_2
            remainder = remainder // order_2

        if is_homomorphism(quandle_1, quandle_2, candidate_map):
            all_homomorphisms.append(list(candidate_map))

    return all_homomorphisms

def main():
    op_table1 = [[0, 2, 1], 
                 [2, 1, 0], 
                 [1, 0, 2]]

    op_table2 = [[0, 0, 1], 
                 [2, 1, 0], 
                 [1, 2, 2]]
    
    # print(is_quandle(op_table))
    # print(len(gen_all_quandles(4)))
    # print(len(gen_all_quandles_up_to_isomorphism(5)))
    # all_quandles = gen_all_quandles_from_partial(op_table)
    print(gen_all_homomorphisms(op_table1, op_table1))
    # for quandle in all_quandles:
    #     print_arr(quandle)
    #     print()

main()