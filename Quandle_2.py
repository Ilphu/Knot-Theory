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

# crossings = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
unknot = []
print(build_presentation(unknot))

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

presentation = build_presentation([(0, 1, 0), (1, 0, 1)])
trefoil = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
R3 = [[0, 2, 1], [2, 1, 0], [1, 0, 2]]
print(count_knot_homomorphisms(build_presentation(trefoil), R3))

target = [[0, 2, 1], [2, 1, 0], [1, 0, 2]]

print(count_knot_homomorphisms(presentation, target))

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

unknot = [(0, 0, 0)]
trefoil = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
R3 = [[0, 2, 1], [2, 1, 0], [1, 0, 2]]

compare_knot_counts(unknot, trefoil, R3)

def has_all_trivial_maps(presentation, target, maps):
    m = len(presentation["arcs"])
    for i in range(len(target)):
        constant_map = [i] * m
        if constant_map not in maps:
            return False
    return True

a1, b1 = count_knot_homomorphisms(presentation, target)
print(has_all_trivial_maps(presentation, target, b1))


trefoil = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
hopf = [(0, 1, 0), (1, 0, 1)]

R3 = [[0, 2, 1], [2, 1, 0], [1, 0, 2]]
R4 = [[0, 2, 0, 2], [3, 1, 3, 1], [2, 0, 2, 0], [1, 3, 1, 3]]

for target_name, target in [("R3", R3), ("R4", R4)]:
    for knot_name, crossings in [("Unknot", unknot), ("Trefoil", trefoil), ("Hopf link", hopf)]:
        presentation = build_presentation(crossings)
        count, maps = count_knot_homomorphisms(presentation, target)
        print(target_name, knot_name, count)