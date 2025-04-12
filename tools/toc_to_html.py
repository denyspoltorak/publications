#! /usr/bin/env python3

import sys


INPUT_SPACES_PER_LEVEL = 4
OUTPUT_SPACES_PER_LEVEL = 2


class Node:
    def __init__(self, name, level):
        self.name = name
        self.level = level


def parse(text):
    nodes = []

    for l in text:
        # Read
        stripped = l.lstrip(" ")

        # Get level
        num_spaces = len(l) - len(stripped)
        assert(not (num_spaces % INPUT_SPACES_PER_LEVEL))
        level = num_spaces // INPUT_SPACES_PER_LEVEL

        nodes. append(Node(stripped.strip(), level))

    return nodes


def dump(html, nodes, level, begin, end):
    i = begin
    assert(nodes[i].level == level)
    prefix = ' ' * OUTPUT_SPACES_PER_LEVEL * level

    while i < end:
        # Add the current node
        html.append(prefix + '<li>')
        html.append(prefix + nodes[i].name)
        # Check if the next node is a child
        i += 1
        if i < end:
            if nodes[i].level > level:
                # Generate a sublist
                html.append(prefix + '<ul>')
                i = dump(html, nodes, nodes[i].level, i, end)
                html.append(prefix + '</ul>')
        # i could have changed, reevaluate
        if i < end:
            assert(nodes[i].level <= level)
            if nodes[i].level < level:
                # Jump up the ToC
                html.append(prefix + '</li>')
                break
        html.append(prefix + '</li>')

    return i

def convert(text):
    nodes = parse(text)
    html = []

    # header
    html.append('<ul class="toc no-parts">')

    # ToC
    dump(html, nodes, 0, 0, len(nodes))

    # footer
    html.append('</ul>')

    return html


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} input_file output_file")
        return 1

    text = open(sys.argv[1]).readlines()

    html = convert(text)

    open(sys.argv[2], "w").writelines("\n".join(html))


if __name__ == "__main__":
    main()
