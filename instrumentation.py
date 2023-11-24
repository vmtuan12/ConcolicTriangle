import re

# instrumentation code for linear call
def make_instrumentation_code(line, offset, statement):
    return f'mark("line-in-function${line}#offset${offset}#statement${statement}")'

# instrumentation code for condition in if statement
def make_instrumentation_code_if(line, offset, statement):
    instrumentation_code = f'mark("line-in-function${line}#offset${offset}#statement${statement}#control−block$if")'
    return f'({instrumentation_code} and ({statement}))'

# instrumentation code opening and closing of if/elif/else block
def make_instrumentation_blockin_function(line, statement, space):
    result = f'mark("statement${statement}#line-of-blockin-function${line}")\n'
    return result.rjust(space + len(result), ' ')

# beginning whitespace count in a line
def space_count(string):
    count = 0
    for x in string:
        if x == ' ':
            count += 1
        else:
            break

    return count

# check whether the statement being considered has parenthesis or not
def have_parenthesis(statement):
    stripped_statement = statement.strip()
    return stripped_statement[0] == '(' and stripped_statement[len(stripped_statement) - 1] == ')'

# list of offset in an if/elif line
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

# read file
sourceFile = open("test.py", "r")
code = sourceFile.read()

# regex
regex_def = r"^\s*def (\S+)\s*\(\s*\S+\s*(?:,\s*\S+)*\):$"
regex_if = r"^\s*(if|elif|else) *.*:$"
regex_single_else = r"^\s*else\s*:$"

# split lines of code into single elements in a list
code_by_line = code.split('\n')

if_space_dict = dict()
if_line_dict = dict()
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

    pre_line = None
    if if_space_dict.get(spaces) == True:
        current_line = code_dicts[index]["line"]
        pre_line = make_instrumentation_blockin_function(if_line_dict[spaces], 'block-end', spaces + 4)
        if_space_dict[spaces] = False

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
            offset_list.insert(0, line_without_space.find(condition_list[0].strip()))

            for condition_index in range(len(condition_list)):
                stripped_condition = condition_list[condition_index].strip()
                condition_with_instrumentation = make_instrumentation_code_if(index + 1, offset_list[condition_index] + offset, stripped_condition)
                conditions_to_be_replaced.append(dict(condititon=stripped_condition, condition_with_instrumentation=condition_with_instrumentation))

            for item in conditions_to_be_replaced:
                line = line.replace(item['condititon'], item['condition_with_instrumentation'])

            code_dicts[index]["line"] = line
        
        line_after_transforming = code_dicts[index]["line"]
        if if_space_dict.get(spaces) == None or if_space_dict.get(spaces) == False:
            if_space_dict[spaces] = True
            if_line_dict[spaces] = index + 2
            line_after_transforming += make_instrumentation_blockin_function(if_line_dict[spaces], 'block-start', spaces + 4)
            code_dicts[index]["line"] = line_after_transforming

    # handle linear call
    if (match_if == None and match_def == None):

        instrumentation = make_instrumentation_code(index + 1, offset, line.strip())
        instrumentation = instrumentation.rjust(spaces + len(instrumentation), ' ') + '\n'

        code_dicts[index]["line"] = instrumentation + line

    if pre_line != None:
        code_dicts[index]["line"] = pre_line + code_dicts[index]["line"]


result = ''
for x in code_dicts:
    result += x["line"]

for item in reversed(sorted(if_space_dict.keys())):
    if if_space_dict[item] == True:
        result += make_instrumentation_blockin_function(if_line_dict[item], 'block-end', item + 4)

# print(result)
f = open("demo.txt", "w", encoding="utf-8")
f.write(result)
f.close()

