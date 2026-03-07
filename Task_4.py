class QueenPuzzle:
    def __init__(self, board_size):
        self.size = board_size
        self.all_results = []

        self.taken_cols  = set()
        self.taken_diag_a = set()   
        self.taken_diag_b = set()   

    def find_solutions(self):
        self._recurse([], 0)
        return self.all_results

    def _recurse(self, placement, current_row):
        if current_row == self.size:
            self.all_results.append(placement[:])
            return

        for c in range(self.size):
            if c in self.taken_cols:
                continue
            if (current_row - c) in self.taken_diag_a:
                continue
            if (current_row + c) in self.taken_diag_b:
                continue

            self.taken_cols.add(c)
            self.taken_diag_a.add(current_row - c)
            self.taken_diag_b.add(current_row + c)
            placement.append(c)

            self._recurse(placement, current_row + 1)

            # Undo placement
            self.taken_cols.remove(c)
            self.taken_diag_a.remove(current_row - c)
            self.taken_diag_b.remove(current_row + c)
            placement.pop()

    def render_board(self, arrangement, label):
        divider = " +" + "---+" * self.size
        print(f"\nSolution {label}:")
        print(divider)
        for r, queen_col in enumerate(arrangement):
            row_str = " |"
            for c in range(self.size):
                row_str += " Q |" if c == queen_col else " . |"
            print(row_str)
            print(divider)
        col_numbers = "  " + "  ".join(str(i) for i in range(self.size))
        print(col_numbers)

    def display_all(self):
        print(f"\nBoard : {self.size} × {self.size}")
        print(f"Solutions found : {len(self.all_results)}")
        for num, sol in enumerate(self.all_results, start=1):
            self.rend
def trace_placement(arrangement, n):
    """Walk through a solution one step at a time."""
    print("\nStep-by-Step Queen Placement")
    grid = [['.' for _ in range(n)] for _ in range(n)]

    for step, queen_col in enumerate(arrangement):
        grid[step][queen_col] = 'Q'
        divider = " +" + "---+" * n
        print(f"\nStep {step + 1}  —  Row {step}, Col {queen_col}")
        print(divider)
        for r in range(n):
            row_line = " |" + "".join(f" {grid[r][c]} |" for c in range(n))
            print(row_line)
            print(divider)


if __name__ == "__main__":
    N = 6
    print(f"=== {N}-Queens Solver ===")

    puzzle = QueenPuzzle(N)
    results = puzzle.find_solutions()
    puzzle.display_all()

    if results:
        trace_placement(results[0], N)
