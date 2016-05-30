#!/usr/bin/env python3
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
    indent_count = 0
    for line in split_input[2:]:
        line = line.strip('·»')
        if line.startswith('NEXT') or line.startswith('ENDIF'):
            indent_count -= 1
        print(indent_count * indent + line)
        if line.startswith('FOR') or line.startswith('IF'):
            indent_count += 1 
