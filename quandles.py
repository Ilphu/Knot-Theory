# @author Garrett Rhoads, Emma Hirsch, Liam Casey, Miffy Wang
# @file quandles.py
# @date 9-17-26
# @brief Given a quandle operation table, proivdes useful tools for computing
#        things with them

import sys

def is_quandle(quandle):
    # NOTE: this only checks idempotency and right invertibility. right
    # distributivity is checked separately (see is_right_distributive_partial),
    # both in the -v mode and while generating in backtrack_partial.
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
    # too
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

def backtrack_partial(row, col, order, table, all_quandles):
    # fills the table in column by column. a cell that was already given in
    # the partial input (table[row][col] != -1) is kept as-is instead of being
    # searched over a fully blank table (apart from the diagonal) generates
    # every quandle of that order
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
            backtrack_partial(0, col+1, order, table, all_quandles)

    # diagonal -> move to the next row
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
    # same convention used everywhere else in this file. passing a table of
    # all -1s generates every quandle of that order.
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
            return []  # given diagonal value violates idempotency

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

def relabel(quandle, perm):
    # apply the relabeling i -> perm[i] to the whole table
    order = len(quandle)
    new = [[0] * order for _ in range(order)]
    for i in range(order):
        for j in range(order):
            new[perm[i]][perm[j]] = perm[quandle[i][j]]
    return new

def build_permutations(current, used, order, all_perms):
    # standard backtracking: extend `current` with every value not used yet
    if len(current) == order:
        all_perms.append(list(current))
    else:
        for val in range(order):
            if not used[val]:
                used[val] = True
                current.append(val)
                build_permutations(current, used, order, all_perms)
                current.pop()
                used[val] = False

def gen_all_permutations(order):
    # every ordering of 0..order-1, as a list of lists (order! of them)
    all_perms = []
    build_permutations([], [False] * order, order, all_perms)
    return all_perms

def canonical_form(quandle, perms=None):
    # smallest table over all n! relabelings; two quandles are isomorphic
    # exactly when their canonical forms are equal, basically if A is is the 
    # canonical form of B then A ~ B, thus if C has canonical form A, then A ~ C
    # so B ~ C
    order = len(quandle)
    if perms is None:
        perms = gen_all_permutations(order)
    best = None
    for perm in perms:
        candidate = tuple(tuple(row) for row in relabel(quandle, perm))
        if best is None or candidate < best:
            best = candidate
    return best

def up_to_isomorphism(quandles):
    # keeps one representative from each isomorphism class
    seen = set()
    representatives = []
    if len(quandles) == 0:
        return representatives
    # every quandle here has the same order, so build the permutations once
    perms = gen_all_permutations(len(quandles[0]))
    for q in quandles:
        key = canonical_form(q, perms)
        if key not in seen:
            seen.add(key)
            representatives.append(q)
    return representatives

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

def build_presentation(crossings):
    # each (a, b, c) represents a tri b = c
    arcs = set()
    relations = []

    for crossing in crossings:
        a, b, c = crossing
        arcs.update((a, b, c))
        relations.append((a, b, c))

    if len(arcs) == 0:
        arcs.add(0)

    return {"arcs": sorted(arcs), "relations": relations}

def is_knot_homomorphism(presentation, target, mapping):
    images = {}
    for i in range(len(presentation["arcs"])):
        images[presentation["arcs"][i]] = mapping[i]
    for a, b, c in presentation["relations"]:
        if target[images[a]][images[b]] != images[c]:
            return False
    return True

def count_knot_homomorphisms(presentation, target):
    m = len(presentation["arcs"])
    n = len(target)
    candidate_map = [0] * m
    all_maps = []

    for count in range(n ** m):
        remainder = count
        for i in range(m):
            candidate_map[i] = remainder % n
            remainder = remainder // n
        if is_knot_homomorphism(presentation, target, candidate_map):
            all_maps.append(list(candidate_map))
    return len(all_maps), all_maps

def compare_knot_counts(crossings1, crossings2, target):
    presentation1 = build_presentation(crossings1)
    presentation2 = build_presentation(crossings2)
    count1, map1 = count_knot_homomorphisms(presentation1, target)
    count2, map2 = count_knot_homomorphisms(presentation2, target)
    print(f"|Hom(Q(L1), T)| = {count1}")
    print(f"|Hom(Q(L2), T)| = {count2}")

    if count1 != count2:
        print(f"L1 and L2 are different knots/links.")
    else:
        print("The counts match; this target cannot distinguish them.")

    return count1, count2

def has_all_trivial_maps(presentation, target, maps):
    m = len(presentation["arcs"])
    for i in range(len(target)):
        constant_map = [i] * m
        if constant_map not in maps:
            return False
    return True

def read_quandle_table(order, allow_blank=False):
    if allow_blank:
        print(f"Enter the {order}x{order} table, one row at a time, "
              f"space-separated (use -1 for unknown cells):")
    else:
        print(f"Enter the {order}x{order} table, one row at a time, space-separated:")

    table = []
    for i in range(order):
        raw = input(f"Row {i}: ").split()
        table.append([int(x) for x in raw])
    return table

def read_fundemental_quandle(r):
    # reads r crossings, one per line, each as three space-separated arc
    # labels "a b c" meaning arc_a rhd arc_b = arc_c. the labels can be any
    # integers, build_presentation collects the arcs from the crossings.
    crossings = []
    for i in range(0, r):
        crossing = input(f"Crossing {i}: ").split()
        crossings.append([int(x) for x in crossing])
    return crossings

def read_subset(quandle_order, num_endo):
    endo_maps = {x: [] for x in range(quandle_order)}
    for i in range(num_endo):
        sub_endo = input(f"Enter Endomorphism Map {i+1}: ").split()
        for j in range(len(sub_endo)):
            endo_maps[j].append(int(sub_endo[j]))
    return endo_maps

def adj_matrix_builder(hom_set, endo_subset):
    k = len(hom_set)
    adj_matrix = [[0] * k for i in range(k)]
    for i in range(k):
        valid_hom = hom_set[i]
        for x in range(len(endo_subset[0])):
            phi_ci = []
            for val in valid_hom:
                phi_ci.append(endo_subset[val][x])
            for j in range(k):
                if phi_ci == hom_set[j]:
                    adj_matrix[i][j] += 1
    return adj_matrix

def write_quandles_to_file(quandles, filename):
    f = open(filename, "w")
    f.write(f"Number of quandles: {len(quandles)}\n")
    for i in range(len(quandles)):
        f.write(f"\nQuandle {i+1}\n")
        for row in quandles[i]:
            f.write(str(row) + "\n")
    f.close()

def write_results(quandles, keep_all):
    found = len(quandles)
    if not keep_all:
        quandles = up_to_isomorphism(quandles)
    write_quandles_to_file(quandles, "quandles-out.txt")
    if keep_all:
        print(f"Found {found} labelled quandles. All written to quandles-out.txt")
    else:
        print(f"Found {found} labelled quandles, {len(quandles)} up to isomorphism. "
              f"Written to quandles-out.txt")

def print_usage():
    print("Usage:")
    print("  python3 quandles.py -v n           Validate a quandle table of order n")
    print("  python3 quandles.py -g n [-a]      Generate all quandles of order n (up to isomorphism) -> quandles-out.txt")
    print("  python3 quandles.py -p n [-a]      Complete a partial quandle table of order n (up to isomorphism) -> quandles-out.txt")
    print("  python3 quandles.py -m n1 n2       List all homomorphisms/isomorphisms between two quandles")
    print("  python3 quandles.py -f r1 n2       List all homomorphisms from a fundamental quandle")
    print("                                     (r1 crossings, arcs inferred from them) to a quandle of order n2")
    print("  -a keeps every labelled quandle instead of one per isomorphism class")


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print_usage()
        return

    mode = args[0]
    keep_all = "-a" in args

    if mode == "-v":
        n = int(args[1])
        table = read_quandle_table(n)
        print(is_quandle(table) and is_right_distributive_partial(table, n, n - 1))

    elif mode == "-g":
        # generating everything is just completing a table of all unknowns
        n = int(args[1])
        blank = [[-1] * n for _ in range(n)]
        write_results(gen_all_quandles_from_partial(blank), keep_all)

    elif mode == "-p":
        n = int(args[1])
        partial = read_quandle_table(n, allow_blank=True)
        write_results(gen_all_quandles_from_partial(partial), keep_all)

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

    elif mode == "-f":
        r1 = int(args[1])
        n2 = int(args[2])

        print(f"-- Fundemental Quandle 1 ({r1} crossings) -- ")
        crossings = read_fundemental_quandle(r1)

        print(f"-- Quandle 2 (order {n2}) --")
        quandle_2 = read_quandle_table(n2)
        if not (is_quandle(quandle_2) and is_right_distributive_partial(quandle_2, n2, n2 - 1)):
            print(f"ERROR: Inputted quandle is invalid")
            return

        presentation = build_presentation(crossings)
        count, homomorphisms = count_knot_homomorphisms(presentation, quandle_2)

        print(f"\nArcs: {presentation['arcs']} (each map below gives the images of these arcs, in order)")
        print(f"Homomorphisms ({count}):")
        for mapping in homomorphisms:
            print(mapping)

    else:
        print(f"Unknown mode: {mode}")
        print_usage()
main()