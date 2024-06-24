def parse_python_code(response):
    response = response.strip()
    result_code = None
    current_code = []
    code_block = False

    for line in response.split("\n"):
        if line.startswith("```py"):
            code_block = not code_block
        elif line.startswith("```"):
            code_block = not code_block
        else:
            if code_block:
                current_code.append(line)

    if current_code:
        result_code = "\n".join(current_code)

    return result_code