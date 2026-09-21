# @author Garrett Rhoads, Emma Hirsch, Liam Casey, Miffy Wang
# @file quandles.py
# @date 9-17-26
# @brief Given a quandle operation table, proivdes useful tools for computing
#        things with them

import sys

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

def backtrack_partial(row, col, order, table, all_quandles):
    # identical to backtrack, except a cell that was already given in the
    # partial input (table[row][col] != -1) is kept as-is instead of being
    # searched over
    if col == order:
        if is_quandle(table) == True:
            saved_quandle = []
            for rows in table:
                saved_row = []
                for val in rows:
                    saved_row.append(val)
                saved_quandle.append(saved_row)
            all_quandles.append(saved_quandle)

    elif row == order:
        if is_right_distributive_partial(table, order, col):
            backtrack_partial(0, col+1, order, table, all_quandles)

    elif row == col:
        backtrack_partial(row+1, col, order, table, all_quandles)

    elif table[row][col] != -1:
        # this cell was already given -> don't search it, just move on
        backtrack_partial(row+1, col, order, table, all_quandles)

    else:
        used_values = set()
        for row_idx in range(order):
            used_values.add(table[row_idx][col])
        for val in range(order):
            if val not in used_values:
                table[row][col] = val
                backtrack_partial(row+1, col, order, table, all_quandles)
                table[row][col] = -1

def gen_all_quandles_from_partial(partial_table):
    # partial_table should use -1 for any cell that isn't yet decided,
    # same convention used everywhere else in this file
    order = len(partial_table)

    # copy so we don't mutate whatever the caller passed in
    table = []
    for row in partial_table:
        new_row = []
        for val in row:
            new_row.append(val)
        table.append(new_row)

    # fill in / validate the diagonal
    for i in range(order):
        if table[i][i] == -1:
            table[i][i] = i
        elif table[i][i] != i:
            return []  

    # validate that no column already has a duplicate among its given values
    for col in range(order):
        seen = set()
        for row in range(order):
            val = table[row][col]
            if val == -1:
                continue
            if val in seen:
                return []  # two given cells in this column already clash
            seen.add(val)

    all_quandles = []
    backtrack_partial(0, 0, order, table, all_quandles)
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

def is_permutation(mapping, order):
    seen = set()
    for val in mapping:
        if val in seen:
            return False
        seen.add(val)
    return True

def gen_all_isomorphisms(quandle_1, quandle_2):
    order_1 = len(quandle_1)
    order_2 = len(quandle_2)

    if order_1 != order_2:
        return []  # can't have a bijection between different-sized sets

    all_homomorphisms = gen_all_homomorphisms(quandle_1, quandle_2)

    all_isomorphisms = []
    for mapping in all_homomorphisms:
        if is_permutation(mapping, order_1):
            all_isomorphisms.append(mapping)

    return all_isomorphisms

def read_quandle_table(order, allow_blank=False):
    # reads an order x order table from the user, one row at a time, as
    # space-separated integers. if allow_blank is True, -1 is accepted as
    # "unknown cell" (used for the -p partial-completion mode).
    if allow_blank:
        print(f"Enter the {order}x{order} table, one row at a time, "
              f"space-separated (use -1 for unknown cells):")
    else:
        print(f"Enter the {order}x{order} table, one row at a time, space-separated:")
 
    table = []
    for i in range(order):
        while True:
            raw = input(f"Row {i}: ").split()
            if len(raw) != order:
                print(f"Expected {order} values, got {len(raw)}. Try again.")
                continue
            row = [int(x) for x in raw]
            table.append(row)
            break
    return table
 
def write_quandles_to_file(quandles, filename):
    f = open(filename, "w")
    f.write(f"Number of quandles: {len(quandles)}\n")
    for i in range(len(quandles)):
        f.write(f"\nQuandle {i+1}\n")
        for row in quandles[i]:
            f.write(str(row) + "\n")
    f.close()
 
def print_usage():
    print("Usage:")
    print("  python3 quandles.py -v n        Validate a quandle table of order n")
    print("  python3 quandles.py -g n        Generate all quandles of order n -> quandles-out.txt")
    print("  python3 quandles.py -p n        Complete a partial quandle table of order n -> quandles-out.txt")
    print("  python3 quandles.py -m n1 n2    List all homomorphisms/isomorphisms between two quandles")
 
 
def main():
    args = sys.argv[1:]
 
    if len(args) == 0:
        print_usage()
        return
 
    mode = args[0]
 
    if mode == "-v":
        n = int(args[1])
        table = read_quandle_table(n)
        print(is_quandle(table))
 
    elif mode == "-g":
        n = int(args[1])
        all_quandles = gen_all_quandles(n)
        write_quandles_to_file(all_quandles, "quandles-out.txt")
        print(f"Found {len(all_quandles)} quandles of order {n}. Written to quandles-out.txt")
 
    elif mode == "-p":
        n = int(args[1])
        partial = read_quandle_table(n, allow_blank=True)
        completions = gen_all_quandles_from_partial(partial)
        write_quandles_to_file(completions, "quandles-out.txt")
        print(f"Found {len(completions)} completions. Written to quandles-out.txt")
 
    elif mode == "-m":
        n1 = int(args[1])
        n2 = int(args[2])
 
        print(f"-- Quandle 1 (order {n1}) --")
        quandle_1 = read_quandle_table(n1)
        print(f"-- Quandle 2 (order {n2}) --")
        quandle_2 = read_quandle_table(n2)
 
        homomorphisms = gen_all_homomorphisms(quandle_1, quandle_2)
        isomorphisms = gen_all_isomorphisms(quandle_1, quandle_2)
 
        print(f"\nHomomorphisms ({len(homomorphisms)}):")
        for mapping in homomorphisms:
            print(mapping)
 
        print(f"\nIsomorphisms ({len(isomorphisms)}):")
        for mapping in isomorphisms:
            print(mapping)
 
    else:
        print(f"Unknown mode: {mode}")
        print_usage()
 
main()
