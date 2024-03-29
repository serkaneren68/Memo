import regex as re


pat = r"[\| ]+\s*([a-zA-Z0-9_:]+)\s+[\|]"
line = "| 0x0        | asdf                                                                                                                                  | 1245 |"
line2 = "asdafa |asd| sad |"
pattern = re.compile(pat)


for match in pattern.finditer(line):
    # extract words
    print(match.group(1))
    # extract numbers
