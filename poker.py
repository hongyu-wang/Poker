import glob
import re
import pprint as pp
import sys
import copy

NAME_REGEX = r"player\s(\"\".*@.*\"\")"
VALUE_REGEX = r"stack of ([0-9]+)"
CHANGE_REGEX = r"stack from ([0-9]+) to ([0-9]+)"
STAND_UP_REGEX = "(stand)"
BUY_IN_REGEX = "(participation|created)"
QUIT_REGEX = "(quits)"
UPDATED_REGEX = "(updated)"
IGNORE_REGEX = r"(WARNING|seat|passed)"
ENTER = "enter"
EXIT = "exit"
STAND_UP = "stand up"
DID_QUIT = "did quit"
OLD_DATA = "old"
NAME = "name"


def process_csv(file_name: str):
    results = {}
    with open(file_name, 'r', encoding='utf8') as f:
        log = f.readlines()[1:][::-1]
        for line in log:
            if ignore(line):
                continue
            if is_update(line):
                if name not in results:
                    results[name] = create_player()

                name, value = process_name(line), process_change(line)
                results[name][ENTER] += value
            else:
                name, value = get_name_and_value(line)

                if name not in results:
                    results[name] = create_player()

                if is_buy_in(line):
                    results[name][ENTER] += value

                if is_cash_out(line):
                    results[name][EXIT] += value

                if is_stand(line):
                    results[name][STAND_UP] = value
    output_results(consolidate_same_ids(results))


def output_results(results: dict):
    print("======= Tentative Results ===========")
    s1 = 0
    for unique_id in results:
        s1 += results[unique_id][ENTER]
        s1 -= results[unique_id][EXIT]
        print(results[unique_id][NAME], (results[unique_id][EXIT] - results[unique_id][ENTER]) / 1000)

    print("Buy Ins - Cash Outs", s1)

    print("======= Results JSON ===========")
    pp.PrettyPrinter().pprint(results)


def consolidate_same_ids(results: dict) -> dict:
    consolidated_results = {}
    for name in results:
        unique_hash = name.split(" ")[-1]
        data = results[name]

        if unique_hash in consolidated_results:
            consolidated_results[unique_hash][ENTER] += data[ENTER]
            consolidated_results[unique_hash][EXIT] += data[EXIT]
            consolidated_results[unique_hash][OLD_DATA] += [{name: data}]
        else:
            consolidated_results[unique_hash] = copy.deepcopy(data)
            consolidated_results[unique_hash][NAME] = name
            consolidated_results[unique_hash][OLD_DATA] = [{name: data}]

    return consolidated_results


def create_player() -> dict:
    return {ENTER: 0, EXIT: 0, STAND_UP: 0}


def is_stand(line):
    return re.search(STAND_UP_REGEX, line) is not None


def is_update(line):
    return re.search(UPDATED_REGEX, line) is not None


def is_buy_in(line):
    return re.search(BUY_IN_REGEX, line) is not None


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
    if len(sys.argv) > 1:
        process_csv(sys.argv[0])
    else:
        for file in glob.glob("*.csv", recursive=True):
            process_csv(file)
