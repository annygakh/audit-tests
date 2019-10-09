import sys
import csv

def process(filename, status, output_fname):
    output_file = open(output_fname, "w")
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) < 1:
                continue
            opt_status = row[4]
            debug_status = row[5]
            if (status == "opt" and opt_status == "skipped") \
                or (status == "debug" and debug_status == "skipped"):
                output_file.write(row[3] + "\n")

if __name__ == "__main__":
    usage = f"""
    Usage: {sys.argv[0]} [name of the csv file] [status - opt|debug] [name of the output file for paths of skipped tests]
    """
    if (len(sys.argv) < 4):
        print(usage)
        sys.exit(1)
    status = sys.argv[2]
    if status not in ["opt", "debug"]:
        print(f"status must be one of opt, debug, not '{status}'")
        sys.exit(1)
    process(sys.argv[1], status, sys.argv[3])
