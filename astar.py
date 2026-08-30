import random
import time

TEST_SEED = 2104

# Number of Sudoku steps shown side-by-side in the terminal.
# Change to 4 if your terminal is wide enough.
STEPS_PER_ROW = 3

# Same 10 randomly generated Sudoku start states are reproduced every run.
# A fixed seed keeps the experiment fair and repeatable for all group members.
TEST_PLAN = [
    ("T1", "Easy", 24),
    ("T2", "Easy", 26),
    ("T3", "Easy", 28),
    ("T4", "Medium", 30),
    ("T5", "Medium", 32),
    ("T6", "Medium", 34),
    ("T7", "Medium", 36),
    ("T8", "Hard", 38),
    ("T9", "Hard", 40),
    ("T10", "Hard", 42),
]


def _pattern(row, col):
    return (3 * (row % 3) + row // 3 + col) % 9


def _shuffled(items, rng):
    items = list(items)
    rng.shuffle(items)
    return items


def generate_solved_sudoku(rng):
    rows = [
        group * 3 + row
        for group in _shuffled(range(3), rng)
        for row in _shuffled(range(3), rng)
    ]
    cols = [
        group * 3 + col
        for group in _shuffled(range(3), rng)
        for col in _shuffled(range(3), rng)
    ]
    numbers = _shuffled(range(1, 10), rng)

    return [
        [numbers[_pattern(row, col)] for col in cols]
        for row in rows
    ]


def create_puzzle(solution, blanks, rng):
    puzzle = [row[:] for row in solution]
    for position in rng.sample(range(81), blanks):
        row = position // 9
        col = position % 9
        puzzle[row][col] = 0
    return puzzle


def grid_to_text(grid):
    return "".join(str(value) for row in grid for value in row)


def generate_tests(seed=TEST_SEED):
    rng = random.Random(seed)
    tests = []
    used = set()

    for test_name, difficulty, blanks in TEST_PLAN:
        while True:
            goal = generate_solved_sudoku(rng)
            puzzle = create_puzzle(goal, blanks, rng)
            key = grid_to_text(puzzle)

            if key not in used:
                used.add(key)
                tests.append((test_name, difficulty, puzzle, goal))
                break

    return tests


def _grid_lines(grid):
    """Return one Sudoku board as printable text lines."""
    if grid is None:
        return ["No board available."]

    def _cell_text(value):
        return str(value) if value != 0 else " "

    lines = []
    for row in range(9):
        if row > 0 and row % 3 == 0:
            lines.append("------+-------+------")

        lines.append(
            " ".join(_cell_text(v) for v in grid[row][0:3])
            + " | "
            + " ".join(_cell_text(v) for v in grid[row][3:6])
            + " | "
            + " ".join(_cell_text(v) for v in grid[row][6:9])
        )
    return lines


def print_grid(grid):
    for line in _grid_lines(grid):
        print(line)


def valid_solution(grid, puzzle):
    if grid is None:
        return False

    target = set(range(1, 10))

    for row in range(9):
        if set(grid[row]) != target:
            return False

    for col in range(9):
        if {grid[row][col] for row in range(9)} != target:
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = {
                grid[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            }
            if values != target:
                return False

    for row in range(9):
        for col in range(9):
            if puzzle[row][col] != 0 and grid[row][col] != puzzle[row][col]:
                return False

    return True


def _compact_note(note):
    """Shorten long notes so several steps can fit on one terminal row."""
    if not note:
        return ""

    note = note.replace("Original Sudoku puzzle", "Start")
    note = note.replace(" at row ", " @ r")
    note = note.replace(", column ", " c")
    note = note.replace("new best state; ", "best; ")
    return note


def print_workthrough(result, pause=False, steps_per_row=STEPS_PER_ROW):
    """Print the solution path with 3 (or 4) Sudoku steps side-by-side."""
    path = result.get("path", [])
    notes = result.get("path_notes", [])

    if not path:
        print("\nNo work-through path was produced.")
        return

    print("\n" + "=" * 70)
    print("STEP-BY-STEP WORK-THROUGH")
    print("=" * 70)

    column_width = 36

    for start in range(0, len(path), steps_per_row):
        indexes = list(range(start, min(start + steps_per_row, len(path))))

        labels = []
        actions = []
        boards = []

        for index in indexes:
            step_number = index + 1

            if index == 0:
                label = f"Step {step_number} (Start)"
            elif result.get("solved") and index == len(path) - 1:
                label = f"Step {step_number} (Goal)"
            else:
                label = f"Step {step_number}"

            labels.append(label)
            note = notes[index] if index < len(notes) else ""
            actions.append(_compact_note(note))
            boards.append(_grid_lines(path[index]))

        print("\n" + "".join(label.ljust(column_width) for label in labels))
        print("".join(action[:column_width - 2].ljust(column_width) for action in actions))

        max_lines = max(len(board) for board in boards)
        for line_index in range(max_lines):
            row_text = []
            for board in boards:
                line = board[line_index] if line_index < len(board) else ""
                row_text.append(line.ljust(column_width))
            print("".join(row_text).rstrip())

        if pause and start + steps_per_row < len(path):
            input("\nPress Enter for the next group of steps...")


def run_single_demo(solver, algorithm_name, test_number=1, pause=False, seed=1):
    tests = generate_tests()

    if test_number < 1 or test_number > len(tests):
        raise ValueError("test_number must be from 1 to 10")

    test_name, difficulty, puzzle, _ = tests[test_number - 1]
    blanks = sum(value == 0 for row in puzzle for value in row)

    print("\n" + "=" * 70)
    print(algorithm_name)
    print("=" * 70)
    print(f"{test_name} | {difficulty} | blanks={blanks}")

    result = solver([row[:] for row in puzzle], seed=seed)
    correct = result["solved"] and valid_solution(result["solution"], puzzle)

    print_workthrough(result, pause=pause)

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print("Solved      :", "YES" if correct else "NO")
    print("Time        :", f"{result['time']:.6f} seconds")
    print("Expanded    :", result["expanded"])
    print("Max stored  :", result["max_stored"])
    print("Detail      :", result["detail"])

import heapq
import itertools


def _candidates(state, row, col):
    used = set(state[row])
    used.update(state[r][col] for r in range(9))

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    used.update(
        state[r][c]
        for r in range(box_row, box_row + 3)
        for c in range(box_col, box_col + 3)
    )

    return [number for number in range(1, 10) if number not in used]


def _select_mrv(state):
    best_cell = None
    best_candidates = None

    for row in range(9):
        for col in range(9):
            if state[row][col] == 0:
                candidates = _candidates(state, row, col)

                if not candidates:
                    return row, col, []

                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

                    if len(candidates) == 1:
                        return row, col, candidates

    if best_cell is None:
        return None

    return best_cell[0], best_cell[1], best_candidates


def _heuristic(state):
    # Lower heuristic = less uncertainty remaining.
    score = 0

    for row in range(9):
        for col in range(9):
            if state[row][col] == 0:
                candidates = _candidates(state, row, col)

                if not candidates:
                    return 10**9

                score += len(candidates)

    return score


def _reconstruct_path(goal_state, parent, move_note):
    states = []
    notes = []
    current = goal_state

    while current is not None:
        states.append([list(row) for row in current])
        notes.append(move_note.get(current, "Original Sudoku puzzle"))
        current = parent.get(current)

    states.reverse()
    notes.reverse()

    if notes:
        notes[0] = "Original Sudoku puzzle"

    return states, notes


def solve(puzzle, seed=1, max_expanded=250000):
    del seed  # A* is deterministic here; kept for a common interface.

    start_time = time.perf_counter()
    start_state = tuple(tuple(row) for row in puzzle)

    counter = itertools.count()
    open_heap = []
    start_h = _heuristic(start_state)

    heapq.heappush(
        open_heap,
        (start_h, 0, next(counter), start_state)
    )

    best_g = {start_state: 0}
    parent = {start_state: None}
    move_note = {start_state: "Original Sudoku puzzle"}

    expanded = 0
    max_stored = 1

    while open_heap and expanded < max_expanded:
        f_score, g_score, _, state = heapq.heappop(open_heap)

        if g_score != best_g.get(state):
            continue

        expanded += 1
        choice = _select_mrv(state)

        if choice is None:
            elapsed = time.perf_counter() - start_time
            path, notes = _reconstruct_path(state, parent, move_note)

            return {
                "solution": [list(row) for row in state],
                "solved": True,
                "time": elapsed,
                "expanded": expanded,
                "max_stored": max_stored,
                "detail": f"frontier_peak={max_stored}",
                "path": path,
                "path_notes": notes,
            }

        row, col, candidates = choice

        if not candidates:
            continue

        for number in candidates:
            child = [list(r) for r in state]
            child[row][col] = number
            child_state = tuple(tuple(r) for r in child)

            new_g = g_score + 1

            if new_g < best_g.get(child_state, 10**18):
                h_score = _heuristic(child_state)

                if h_score >= 10**9:
                    continue

                best_g[child_state] = new_g
                parent[child_state] = state
                move_note[child_state] = (
                    f"Place {number} at row {row + 1}, column {col + 1}; "
                    f"g={new_g}, h={h_score}, f={new_g + h_score}"
                )

                heapq.heappush(
                    open_heap,
                    (
                        new_g + h_score,
                        new_g,
                        next(counter),
                        child_state,
                    ),
                )

        max_stored = max(max_stored, len(open_heap))

    elapsed = time.perf_counter() - start_time

    return {
        "solution": None,
        "solved": False,
        "time": elapsed,
        "expanded": expanded,
        "max_stored": max_stored,
        "detail": (
            "search limit reached"
            if expanded >= max_expanded
            else "no solution"
        ),
        "path": [[row[:] for row in puzzle]],
        "path_notes": ["Original Sudoku puzzle"],
    }


# Change TEST_NUMBER (1-10) to run a different test scenario.
TEST_NUMBER = 5

# True pauses after each group of steps; False prints continuously.
PAUSE_BETWEEN_STEPS = False


if __name__ == "__main__":
    run_single_demo(
        solve,
        "A* Search - Informed Search",
        test_number=TEST_NUMBER,
        pause=PAUSE_BETWEEN_STEPS,
        seed=2001,
    )
