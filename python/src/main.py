import json
from pathlib import Path
from argparse import ArgumentParser
from dimacs_parser import DimacsParser
from dpll import DPLL
from model_timer import Timer

def main(args):
    input_file = args.input_file
    
    if not input_file:
        print("Usage: python3 src/main.py <cnf file>")
        return

    path = Path(input_file)
    filename = path.name
    result = None
    
    timer = Timer()
    timer.start()
    
    try:
        instance = DimacsParser.parse_cnf_file(input_file)
        if instance:
            print(instance, end="")
            symbols = list(instance.vars)
            clauses = [list(clause) for clause in instance.clauses]
            solver = DPLL(clauses, symbols)

            result = solver.solve()
    except Exception as e:
        print(f"Error: {e}")
    
    timer.stop()

    printSol = {
        "Instance": filename,
        "Time": f"{timer.getTime():.2f}",
        "Result": "--"
    }

    if result is not None:
        printSol["Result"] = "SAT"
        printSol["Solution"] = ' '.join([f'{key} {val}' for key, val in result.items()])
    else:
        printSol["Result"] = "UNSAT"
    
    print(json.dumps(printSol))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)
