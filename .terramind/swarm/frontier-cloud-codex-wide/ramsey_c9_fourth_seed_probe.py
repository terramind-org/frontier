#!/usr/bin/env python3
"""Select a fourth McKay seed with a color-swap-aware degree certificate."""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import combinations


def decode_g6(line):
    assert ord(line[0]) - 63 == 42
    bits = [(ord(char) - 63 >> shift) & 1 for char in line[1:] for shift in range(5, -1, -1)]
    graph = [[0] * 42 for _ in range(42)]
    cursor = 0
    for i in range(1, 42):
        for j in range(i):
            graph[i][j] = graph[j][i] = bits[cursor]
            cursor += 1
    return graph


def load_rows(path):
    return [[int(bit) for bit in row.strip()] for row in open(path, encoding="ascii") if row.strip()]


def degree_sequence(graph):
    return tuple(sorted(map(sum, graph)))


def complement_sequence(sequence):
    return tuple(sorted(41 - degree for degree in sequence))


def k5_free(graph):
    return not any(len({graph[i][j] for i, j in combinations(vertices, 2)}) == 1
                   for vertices in combinations(range(42), 5))


def main():
    exoo_path, alternate_path, third_path, source_path, output_path, evidence_path = sys.argv[1:]
    prior = {
        "exoo": degree_sequence(load_rows(exoo_path)),
        "alternate": degree_sequence(load_rows(alternate_path)),
        "third": degree_sequence(load_rows(third_path)),
    }
    forbidden = {sequence for sequence in prior.values()}
    forbidden |= {complement_sequence(sequence) for sequence in prior.values()}
    lines = [line.strip() for line in open(source_path, encoding="ascii") if line.strip()]
    for line_number, line in enumerate(lines):
        graph = decode_g6(line)
        sequence = degree_sequence(graph)
        if sequence not in forbidden:
            assert k5_free(graph)
            with open(output_path, "w", encoding="ascii") as handle:
                for row in graph:
                    handle.write("".join(map(str, row)) + "\n")
            evidence = {
                "source_sha256": hashlib.sha256(open(source_path, "rb").read()).hexdigest(),
                "graphs_in_source": len(lines), "selected_line": line_number,
                "selected_g6": line, "selected_degree_sequence": sequence,
                "prior_degree_sequences": prior, "color_swap_checked": True,
                "nonisomorphism_certificate": "selected degree sequence differs from all three prior seeds and all color-swapped complements",
                "k5_free": True,
            }
            with open(evidence_path, "w", encoding="utf-8") as handle:
                json.dump(evidence, handle, indent=2, sort_keys=True)
                handle.write("\n")
            print(json.dumps(evidence, sort_keys=True))
            return
    raise RuntimeError("no color-swap-degree-distinct fourth seed found")


if __name__ == "__main__":
    main()
