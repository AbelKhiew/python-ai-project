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

def _is_valid(grid, row, col, number):
    if number in grid[row]:
        return False

    if any(grid[r][col] == number for r in range(9)):
        return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == number:
                return False

    return True


def _find_empty(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return row, col
    return None


def solve(puzzle, seed=1):
    del seed  # DFS is deterministic; kept only for a common interface.

    grid = [row[:] for row in puzzle]
    stats = {
        "expanded": 0,
        "max_stored": 1,
        "max_depth": 0,
    }

    # Keep only the successful DFS path.
    path = [[row[:] for row in grid]]
    path_notes = ["Original Sudoku puzzle"]

    start_time = time.perf_counter()

    def dfs(depth=0):
        stats["expanded"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        stats["max_stored"] = max(stats["max_stored"], depth + 1)

        empty = _find_empty(grid)

        if empty is None:
            return True

        row, col = empty

        for number in range(1, 10):
            if _is_valid(grid, row, col, number):
                grid[row][col] = number

                path.append([r[:] for r in grid])
                path_notes.append(
                    f"Place {number} at row {row + 1}, column {col + 1}"
                )

                if dfs(depth + 1):
                    return True

                # Dead end: remove this state from the successful path.
                path.pop()
                path_notes.pop()
                grid[row][col] = 0

        return False

    solved = dfs()
    elapsed = time.perf_counter() - start_time

    return {
        "solution": [row[:] for row in grid] if solved else None,
        "solved": solved,
        "time": elapsed,
        "expanded": stats["expanded"],
        "max_stored": stats["max_stored"],
        "detail": f"max_depth={stats['max_depth']}",
        "path": path if solved else [[row[:] for row in puzzle]],
        "path_notes": path_notes if solved else ["Original Sudoku puzzle"],
    }


# Change TEST_NUMBER (1-10) to run a different test scenario.
TEST_NUMBER = 1

# True pauses after each group of steps; False prints continuously.
PAUSE_BETWEEN_STEPS = False


if __name__ == "__main__":
    run_single_demo(
        solve,
        "Depth-First Search (DFS) - Uninformed Search",
        test_number=TEST_NUMBER,
        pause=PAUSE_BETWEEN_STEPS,
        seed=1001,
    )
