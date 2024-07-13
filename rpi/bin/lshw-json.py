#! /usr/bin/env python3

import json
import re


def parse_lshw_output(lshw_text):
    lines = lshw_text.splitlines()
    data = {}
    stack = [data]

    section_pattern = re.compile(r'\s*\*-([\w-]+)')
    kv_pattern = re.compile(r'\s*(\w+):\s*(.*)')

    for line in lines:
        section_match = section_pattern.match(line)
        kv_match = kv_pattern.match(line)

        if section_match:
            section_name = section_match.group(1)
            new_section = {}
            if isinstance(stack[-1], list):
                stack[-1].append({section_name: new_section})
            else:
                stack[-1][section_name] = new_section
            stack.append(new_section)

        elif kv_match:
            key, value = kv_match.groups()
            if isinstance(stack[-1], list):
                stack[-1][-1][key] = value
            else:
                stack[-1][key] = value

        elif line.startswith('    '):  # Handling nested sections
            if isinstance(stack[-1], dict):
                last_key = list(stack[-1].keys())[-1]
                if isinstance(stack[-1][last_key], dict):
                    stack.append(stack[-1][last_key])
                else:
                    stack[-1][last_key] = {}
                    stack.append(stack[-1][last_key])
            else:
                stack.append(stack[-1][-1])

        elif not line.strip():  # End of a section
            stack.pop()

    return data


with open('lshw.txt', 'r') as file:
    lshw_text = file.read()

parsed_data = parse_lshw_output(lshw_text)

with open('lshw.json', 'w') as json_file:
    json.dump(parsed_data, json_file, indent=4)

print("Converted lshw output to JSON and saved to lshw_output.json")
