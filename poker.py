import glob
import re
import pprint as pp

NAME_REGEX = r"player\s(\"\".*@.*\"\")"
VALUE_REGEX = r"stack of ([0-9]+)"
CHANGE_REGEX = r"stack from ([0-9]+) to ([0-9]+)"


g = {"BUY_IN_REGEX": "(participation|created)"}
QUIT_REGEX = "(quits)"
UPDATED_REGEX = "(updated)"
IGNORE_REGEX = r"(WARNING)"
ENTER = "enter"
EXIT = "exit"


def read_csv(file_name: str):
    results = {}
    with open(file_name, 'r', encoding='utf8') as f:
        log = f.readlines()[1:][::-1]
        for line in log:
            if ignore(line):
                continue

            if is_update(line):
                if name not in results:
                    results[name] = {ENTER: 0, EXIT: 0}

                name, value = process_name(line), process_change(line)
                results[name][ENTER] += value
            else:
                name, value = get_name_and_value(line)

                if name not in results:
                    results[name] = {ENTER: 0, EXIT: 0}

                if is_buy_in(line):
                    results[name][ENTER] += value

                if is_cash_out(line):
                    results[name][EXIT] += value

    s1 = 0
    for name in results:
        s1 += results[name][ENTER]
        s1 -= results[name][EXIT]
        print(name, (results[name][EXIT] - results[name][ENTER])/400)

    print("Buy Ins - Cash Outs", s1)

    print("Results")
    pp.PrettyPrinter().pprint(results)

def is_update(line):
    return re.search(UPDATED_REGEX, line) is not None


def is_buy_in(line):
    return re.search(g["BUY_IN_REGEX"], line) is not None


def is_cash_out(line):
    return re.search(QUIT_REGEX, line) is not None


def ignore(line: str) -> bool:
    return re.search(IGNORE_REGEX, line) is not None or re.search(NAME_REGEX, line) is None


def get_name_and_value(line: str) -> (str, int):
    name = process_name(line)
    value = process_value(line)
    return name, value


def process_name(line: str) -> str:
    name = re.search(NAME_REGEX, line)
    if name is None:
        return ""

    return name.groups()[0][2:-2]


def process_change(line: str) -> int:
    values = re.search(CHANGE_REGEX, line)
    return int(values.groups()[1]) - int(values.groups()[0])


def process_value(line: str) -> int:
    value = re.search(VALUE_REGEX, line)

    return int(value.groups()[0])


if __name__ == "__main__":
    for file in glob.glob("*.csv", recursive=True):
        read_csv(file)
