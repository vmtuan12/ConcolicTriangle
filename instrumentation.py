import re

def make_instrumentation_code(line, offset, statement):
    return f'mark("line-in-function${line}#offset${offset}#statement${statement}")'

def make_instrumentation_code_if(line, offset, statement):
    instrumentation_code = f'mark("line-in-function${line}#offset${offset}#statement${statement}#control−block$if")'
    return f'({instrumentation_code} and ({statement}))'

def space_count(string):
    count = 0
    for x in string:
        if x == ' ':
            count += 1
        else:
            break

    return count

def have_parenthesis(statement):
    stripped_statement = statement.strip()
    return stripped_statement[0] == '(' and stripped_statement[len(stripped_statement) - 1] == ')'

def offset_in_if_positions(line_without_space):
    or_positions = [m.start() for m in re.finditer('or', line_without_space)]
    and_positions = [m.start() for m in re.finditer('and', line_without_space)]

    if len(or_positions) == 0:
        return list(map(lambda x: x + 4, and_positions))
    elif len(and_positions) == 0:
        return list(map(lambda x: x + 3, or_positions))
    else:
        or_index = 0
        and_index = 0
        result_positions = []
        
        while (or_index < len(or_positions)) and (and_index < len(and_positions)):
            if or_positions[or_index] < and_positions[and_index]:
                result_positions.append(or_positions[or_index] + 3)
                or_index += 1
            else:
                result_positions.append(and_positions[and_index] + 4)
                and_index += 1
        
        for i in range(or_index, len(or_positions)):
            result_positions.append(or_positions[i] + 3)

        for i in range(and_index, len(and_positions)):
            result_positions.append(and_positions[i] + 4)

        return result_positions

sourceFile = open("test.py", "r")
code = sourceFile.read()

regex_def = r"^\s*def (\S+)\s*\(\s*\S+\s*(?:,\s*\S+)*\):$"
regex_if = r"^\s*(if|elif|else) *.*:$"
regex_single_else = r"^\s*else\s*:$"

code_by_line = code.split('\n')

code_dicts = []
for i in range(len(code_by_line)):
    addition = code_dicts[i - 1]["word_count"] if i > 0 else 0
    code_dicts.append(dict(line=(code_by_line[i] + '\n'), word_count=(len(code_by_line[i]) + addition)))

for index in range(len(code_dicts)):

    line = code_dicts[index]["line"]

    line_without_space = line.strip()

    spaces = space_count(line)
    offset = code_dicts[index - 1]["word_count"] if index > 0 else 0
    offset += spaces

    match_if = re.search(regex_if, line)
    match_def = re.search(regex_def, line)

    # handle if else
    if match_if:
        
        is_else_statement = re.search(regex_single_else, line_without_space)

        if is_else_statement == None:
            conditions_to_be_replaced = []
            
            first_space = line_without_space.find(' ')
            conditions = line_without_space[(first_space + 1):(len(line_without_space) - 1)]
            conditions = conditions.replace('(', '').replace(')', '').strip()

            condition_list = re.split('or|and', conditions)

            offset_list = offset_in_if_positions(line_without_space)
            offset_list.insert(0, line_without_space.find(condition_list[0]))

            for condition_index in range(len(condition_list)):
                stripped_condition = condition_list[condition_index].strip()
                condition_with_instrumentation = make_instrumentation_code_if(index + 1, offset_list[condition_index], stripped_condition)
                conditions_to_be_replaced.append(dict(condititon=stripped_condition, condition_with_instrumentation=condition_with_instrumentation))

            for item in conditions_to_be_replaced:
                line = line.replace(item['condititon'], item['condition_with_instrumentation'])

            code_dicts[index]["line"] = line
        else:
            print('else')

    # handle linear call
    if (match_if == None and match_def == None):

        instrumentation = make_instrumentation_code(index + 1, offset, line.strip())

        # if index > 0:
        #     code_dicts[index - 1]["word_count"] += len(instrumentation)
        
        instrumentation = instrumentation.rjust(spaces + len(instrumentation), ' ') + '\n'

        code_dicts[index]["line"] = instrumentation + line


result = ''
for x in code_dicts:
    result += x["line"]

# print(result)
f = open("demo.txt", "w", encoding="utf-8")
f.write(result)
f.close()

