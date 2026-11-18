#!/usr/bin/env python3
"""Select a fifth degree-sequence-distinct McKay seed with provenance."""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import combinations


def decode(line):
    assert ord(line[0]) - 63 == 42
    bits = [(ord(c) - 63 >> shift) & 1 for c in line[1:] for shift in range(5, -1, -1)]
    graph = [[0] * 42 for _ in range(42)]
    cursor = 0
    for i in range(1, 42):
        for j in range(i):
            graph[i][j] = graph[j][i] = bits[cursor]
            cursor += 1
    return graph


def rows(path):
    return [[int(bit) for bit in row.strip()] for row in open(path, encoding="ascii") if row.strip()]


def degrees(graph):
    return tuple(sorted(map(sum, graph)))


def complement(sequence):
    return tuple(sorted(41 - degree for degree in sequence))


def k5_free(graph):
    return not any(len({graph[i][j] for i, j in combinations(vertices, 2)}) == 1
                   for vertices in combinations(range(42), 5))


def main():
    source, output, evidence, *prior_paths = sys.argv[1:]
    prior = {path.rsplit("/", 1)[-1]: degrees(rows(path)) for path in prior_paths}
    forbidden = set(prior.values()) | {complement(sequence) for sequence in prior.values()}
    lines = [line.strip() for line in open(source, encoding="ascii") if line.strip()]
    for index, line in enumerate(lines):
        graph = decode(line)
        sequence = degrees(graph)
        if sequence in forbidden:
            continue
        assert k5_free(graph)
        with open(output, "w", encoding="ascii") as handle:
            handle.writelines("".join(map(str, row)) + "\n" for row in graph)
        result = {
            "source_sha256": hashlib.sha256(open(source, "rb").read()).hexdigest(),
            "graphs_in_source": len(lines), "selected_line": index, "selected_g6": line,
            "selected_degree_sequence": sequence, "prior_degree_sequences": prior,
            "color_swap_checked": True,
            "nonisomorphism_certificate": "selected degree sequence differs from all four prior seeds and all color-swapped complements",
            "k5_free": True,
        }
        with open(evidence, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(json.dumps(result, sort_keys=True))
        return
    raise RuntimeError("no color-swap-degree-distinct fifth seed found")


if __name__ == "__main__":
    main()
