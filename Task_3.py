def jug_solver_dfs(jug1_max, jug2_max, goal):
    """
    Water Jug problem — solved with Depth First Search.
    jug1_max : total capacity of the first jug
    jug2_max : total capacity of the second jug
    goal     : how many litres we want in jug1
    """

    initial = (0, 0)
    seen = set()
    seen.add(initial)

    dfs_stack = [(initial, [(initial, "Start — both jugs empty")])]

    print("=" * 60)
    print("  Depth-First Search : Water Jug Problem")
    print(f"  Jug-1 holds up to : {jug1_max} L")
    print(f"  Jug-2 holds up to : {jug2_max} L")
    print(f"  We need           : {goal} L in Jug-1")
    print("=" * 60)

    while dfs_stack:
        curr_state, history = dfs_stack.pop()
        j1, j2 = curr_state

        if j1 == goal:
            print(">>> Solution found!\n")
            header = f"  {'#':<4} {'Jug-1':>7} {'Jug-2':>7}   Action"
            print(header)
            print("  " + "-" * 52)
            for idx, (s, action) in enumerate(history):
                print(f"  {idx:<4} {s[0]:>6}L {s[1]:>6}L   {action}")
            print(f"\n  Done — Jug-1 has exactly {goal} litres.")
            print("=" * 60)
            return

        candidates = []

        if j1 < jug1_max:
            candidates.append(((jug1_max, j2), "Action 1 : Fill Jug-1 to full"))

        if j2 < jug2_max:
            candidates.append(((j1, jug2_max), "Action 2 : Fill Jug-2 to full"))

        if j1 > 0:
            candidates.append(((0, j2), "Action 3 : Empty Jug-1"))

        if j2 > 0:
            candidates.append(((j1, 0), "Action 4 : Empty Jug-2"))

        if j1 > 0 and j2 < jug2_max:
            amt = min(j1, jug2_max - j2)
            candidates.append(((j1 - amt, j2 + amt),
                               f"Action 5 : Move {amt}L  Jug-1 → Jug-2"))

        if j2 > 0 and j1 < jug1_max:
            amt = min(j2, jug1_max - j1)
            candidates.append(((j1 + amt, j2 - amt),
                               f"Action 6 : Move {amt}L  Jug-2 → Jug-1"))

        for next_s, label in candidates:
            if next_s not in seen:
                seen.add(next_s)
                dfs_stack.append((next_s, history + [(next_s, label)]))

    print("No path to the target exists with these jug sizes.")
    print("=" * 60)


if __name__ == "__main__":
    jug_solver_dfs(jug1_max=4, jug2_max=3, goal=2)
