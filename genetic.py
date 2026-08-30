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

def _validate_clues(puzzle):
    for row in range(9):
        values = [value for value in puzzle[row] if value != 0]
        if len(values) != len(set(values)):
            return False

    for col in range(9):
        values = [
            puzzle[row][col]
            for row in range(9)
            if puzzle[row][col] != 0
        ]
        if len(values) != len(set(values)):
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = [
                puzzle[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
                if puzzle[row][col] != 0
            ]
            if len(values) != len(set(values)):
                return False

    return True


def _mutable_columns(puzzle):
    return [
        [col for col in range(9) if puzzle[row][col] == 0]
        for row in range(9)
    ]


def _random_individual(puzzle, mutable_columns, rng):
    board = [row[:] for row in puzzle]

    for row in range(9):
        missing = [
            number
            for number in range(1, 10)
            if number not in board[row]
        ]

        rng.shuffle(missing)

        for col, number in zip(mutable_columns[row], missing):
            board[row][col] = number

    return board


def _conflicts(board):
    score = 0

    for col in range(9):
        score += 9 - len({board[row][col] for row in range(9)})

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = [
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            score += 9 - len(set(values))

    return score


def _copy(board):
    return [row[:] for row in board]


def _tournament(scored_population, rng, size=4):
    contestants = rng.sample(
        scored_population,
        min(size, len(scored_population)),
    )
    return min(contestants, key=lambda item: item[0])[1]


def _crossover(parent1, parent2, rng):
    # Row-wise crossover keeps every row valid and keeps original clues.
    child = []

    for row in range(9):
        if rng.random() < 0.5:
            child.append(parent1[row][:])
        else:
            child.append(parent2[row][:])

    return child


def _mutate(board, mutable_columns, rng):
    possible_rows = [
        row
        for row in range(9)
        if len(mutable_columns[row]) >= 2
    ]

    if not possible_rows:
        return

    row = rng.choice(possible_rows)
    columns = mutable_columns[row]

    # Sometimes use a random swap to keep population diversity.
    if rng.random() < 0.20:
        col1, col2 = rng.sample(columns, 2)
        board[row][col1], board[row][col2] = (
            board[row][col2],
            board[row][col1],
        )
        return

    # Otherwise choose the best swap in this row.
    current_score = _conflicts(board)
    best_score = current_score
    best_pairs = []

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]

            board[row][col1], board[row][col2] = (
                board[row][col2],
                board[row][col1],
            )

            score = _conflicts(board)

            board[row][col1], board[row][col2] = (
                board[row][col2],
                board[row][col1],
            )

            if score < best_score:
                best_score = score
                best_pairs = [(col1, col2)]
            elif score == best_score:
                best_pairs.append((col1, col2))

    if best_pairs:
        col1, col2 = rng.choice(best_pairs)
    else:
        col1, col2 = rng.sample(columns, 2)

    board[row][col1], board[row][col2] = (
        board[row][col2],
        board[row][col1],
    )


def solve(
    puzzle,
    seed=4001,
    population_size=160,
    max_generations=1600,
    mutation_rate=0.40,
    elite_size=12,
    max_path_steps=30,
):
    start_time = time.perf_counter()

    if not _validate_clues(puzzle):
        return {
            "solution": None,
            "solved": False,
            "time": 0.0,
            "expanded": 0,
            "max_stored": 0,
            "detail": "invalid puzzle",
            "path": [[row[:] for row in puzzle]],
            "path_notes": ["Original Sudoku puzzle"],
        }

    rng = random.Random(seed)
    mutable_columns = _mutable_columns(puzzle)

    population = [
        _random_individual(puzzle, mutable_columns, rng)
        for _ in range(population_size)
    ]

    evaluations = 0
    best_score = 10**9
    best_board = None
    stagnant = 0

    # For GA, a "step" means a new best individual. Recording is capped at
    # max_path_steps so a puzzle with hundreds of improving generations
    # does not produce an excessively long work-through printout.
    path = [[row[:] for row in puzzle]]
    path_notes = ["Original Sudoku puzzle"]

    for generation in range(max_generations + 1):
        scored = []

        for individual in population:
            score = _conflicts(individual)
            evaluations += 1
            scored.append((score, individual))

        scored.sort(key=lambda item: item[0])
        current_score, current_best = scored[0]

        if current_score < best_score:
            best_score = current_score
            best_board = _copy(current_best)
            stagnant = 0

            if current_score == 0 or len(path) <= max_path_steps:
                path.append(_copy(best_board))
                path_notes.append(
                    f"Generation {generation}: new best individual; "
                    f"conflicts={best_score}"
                )
        else:
            stagnant += 1

        if current_score == 0:
            elapsed = time.perf_counter() - start_time

            return {
                "solution": _copy(current_best),
                "solved": True,
                "time": elapsed,
                "expanded": evaluations,
                "max_stored": population_size,
                "detail": (
                    f"generations={generation}, conflicts=0, "
                    f"population={population_size}"
                ),
                "path": path,
                "path_notes": path_notes,
            }

        if generation == max_generations:
            break

        effective_mutation = mutation_rate

        if stagnant > 60:
            effective_mutation = min(0.80, mutation_rate + 0.20)

        next_population = [
            _copy(individual)
            for _, individual in scored[:elite_size]
        ]

        while len(next_population) < population_size:
            parent1 = _tournament(scored, rng)
            parent2 = _tournament(scored, rng)

            child = _crossover(parent1, parent2, rng)

            if rng.random() < effective_mutation:
                _mutate(child, mutable_columns, rng)

            next_population.append(child)

        # Random immigrants restore diversity after long stagnation.
        if stagnant > 120:
            immigrant_count = max(1, population_size // 10)

            for index in range(immigrant_count):
                next_population[-1 - index] = _random_individual(
                    puzzle,
                    mutable_columns,
                    rng,
                )

            stagnant = 0

        population = next_population

    elapsed = time.perf_counter() - start_time

    # Always show the last-known best board, even if it was skipped
    # earlier because the path cap had already been reached.
    if best_board is not None and path[-1] != best_board:
        path.append(_copy(best_board))
        path_notes.append(f"Best individual found; conflicts={best_score}")

    return {
        "solution": best_board if best_score == 0 else None,
        "solved": best_score == 0,
        "time": elapsed,
        "expanded": evaluations,
        "max_stored": population_size,
        "detail": (
            f"generations={generation}, "
            f"best_conflicts={best_score}, population={population_size}"
        ),
        "path": path,
        "path_notes": path_notes,
    }


# Change TEST_NUMBER (1-10) to run a different test scenario.
TEST_NUMBER = 1

# True pauses after each group of steps; False prints continuously.
PAUSE_BETWEEN_STEPS = False


if __name__ == "__main__":
    run_single_demo(
        solve,
        "Genetic Algorithm - Local Search",
        test_number=TEST_NUMBER,
        pause=PAUSE_BETWEEN_STEPS,
        seed=4001 + TEST_NUMBER,
    )
