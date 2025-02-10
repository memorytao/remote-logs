import re

text = ""
pattern = r'^[^:]+:(.*)'

match = re.match(pattern, text)
if match:
    result = match.group(1)
    print(result)
