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

def is_right_distributive_partial(table, order, filled_up_to):
    # checks (x rhd y) rhd z == (x rhd z) rhd (y rhd z) for every triple 
    # (x, y, z) whose required cells are already filled: y and z must be columns
    # 0..filled_up_to, and c = y rhd z must land in an already filled column 
    # too. Anything not yet decidable is skipped here and gets checked later, 
    # once its column fills in.
    for x in range(order):
        for y in range(filled_up_to + 1):
            for z in range(filled_up_to + 1):
                a = table[x][y]  # x rhd y
                b = table[x][z]  # x rhd z
                c = table[y][z]  # y rhd z

                if c > filled_up_to:
                    continue  # column c not filled yet, defer this triple

                lhs = table[a][z]  # (x rhd y) rhd z
                rhs = table[b][c]  # (x rhd z) rhd (y rhd z)

                if lhs != rhs:
                    return False
    return True

def backtrack(row, col, order, table, all_quandles):
    # when all the cols are filled -> save the quandle
    if col == order:
        if is_quandle(table) == True:
            saved_quandle = []
            for rows in table:
                saved_row = []
                for val in rows:
                    saved_row.append(val)
                saved_quandle.append(saved_row)
            all_quandles.append(saved_quandle)

    # when we finish the current col -> column `col` is fully filled, so
    # check right-distributivity for every triple that just became
    # decidable, and only move on to the next col if it holds
    elif row == order:
        if is_right_distributive_partial(table, order, col):
            backtrack(0, col+1, order, table, all_quandles)

    # diagonal -> move to the next row
    elif row == col:
        backtrack(row+1, col, order, table, all_quandles)

    # fill in regular rows & cols
    else:
        used_values = set()
        for row_idx in range(order):
            used_values.add(table[row_idx][col])
        for val in range(order):
            if val not in used_values:
                table[row][col] = val
                backtrack(row+1, col, order, table, all_quandles)
                table[row][col] = -1

def gen_all_quandles(order):
    all_quandles = []
    table = []
    for row in range(order):
        new_row = []
        for col in range(order):
            new_row.append(-1)
        table.append(new_row)
    for i in range(order):
        table[i][i] = i
    backtrack(0, 0, order, table, all_quandles)
    return all_quandles

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
    n = int(input("Enter the order of the quandle: "))
    all_quandles = gen_all_quandles(n)
    print()
    print(f"Number of quandles: {len(all_quandles)}")
    for i in range(len(all_quandles)):
        print()
        print(f"Quandle {i+1}")
        table = all_quandles[i]
        for row in range(n):
            print(table[row])
    # print(len(gen_all_quandles(4)))
    # print(len(gen_all_quandles_up_to_isomorphism(5)))
    # all_quandles = gen_all_quandles_from_partial(op_table)
    print(gen_all_homomorphisms(op_table1, op_table1))
    # for quandle in all_quandles:
    #     print_arr(quandle)
    #     print()

main()