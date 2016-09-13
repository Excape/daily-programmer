#!/usr/bin/env python3
"""A primitve BASIC syntax checker with only IF and FOR"""

input_text = """12
····
VAR I
·FOR I=1 TO 31
»»»»IF !(I MOD 3) THEN
··PRINT "FIZZ"
··»»ENDIF
»»»»····IF !(I MOD 5) THEN
»»»»··PRINT "BUZZ"
··»»»»»»ENDIF
»»»»IF (I MOD 3) && (I MOD 5) THEN
······PRINT "FIZZBUZZ"
··»»ENDIF
»»»»·NEXT"""

if __name__ == "__main__":
    split_input = input_text.split('\n')
    no_lines = int(split_input[0])
    indent = split_input[1]
    level = 0
    stack = []
    for line in split_input[2:]:
        line = line.strip('·»')
        if line.startswith('NEXT'):
            if not stack.pop().startswith('FOR'):
                print('Error on line "' + line + '", no matching FOR')
                break
            level -= 1
        elif line.startswith('ENDIF'):
            if not stack.pop().startswith('IF'):
                print('Error on line "' + line + '", no matching IF')
                break
            level -= 1
        print(level * indent + line)
        if line.startswith('FOR') or line.startswith('IF'):
            stack.append(line)
            level += 1
    while not len(stack) == 0:
        print('Missing End-Statement for "' + stack.pop() + '"')
