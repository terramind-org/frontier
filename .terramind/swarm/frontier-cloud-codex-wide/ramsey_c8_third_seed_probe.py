#!/usr/bin/env python3
"""Select a K5-free McKay seed inequivalent to two prior seeds, even after color swap."""
import hashlib
import json
import sys
from itertools import combinations


def decode_g6(line):
    n = ord(line[0]) - 63
    assert n == 42
    bits = [(ord(char) - 63 >> shift) & 1 for char in line[1:] for shift in range(5, -1, -1)]
    graph = [[0] * n for _ in range(n)]
    cursor = 0
    for i in range(1, n):
        for j in range(i):
            graph[i][j] = graph[j][i] = bits[cursor]
            cursor += 1
    return graph


def load_rows(path):
    return [[int(bit) for bit in row.strip()] for row in open(path, encoding="ascii") if row.strip()]


def degree_sequence(graph):
    return sorted(map(sum, graph))


def complement_sequence(sequence):
    return sorted(41 - degree for degree in sequence)


def k5_free(graph):
    return not any(
        len({graph[i][j] for i, j in combinations(vertices, 2)}) == 1
        for vertices in combinations(range(42), 5)
    )


def write_rows(path, graph):
    with open(path, "w", encoding="ascii") as handle:
        for row in graph:
            handle.write("".join(map(str, row)) + "\n")


def main():
    exoo = load_rows(sys.argv[1])
    alternate = load_rows(sys.argv[2])
    source_path, output_path, evidence_path = sys.argv[3:]
    lines = [line.strip() for line in open(source_path, encoding="ascii") if line.strip()]
    exoo_seq, alternate_seq = degree_sequence(exoo), degree_sequence(alternate)
    forbidden = {tuple(exoo_seq), tuple(complement_sequence(exoo_seq)), tuple(alternate_seq), tuple(complement_sequence(alternate_seq))}
    for line_number, line in enumerate(lines):
        graph = decode_g6(line)
        sequence = degree_sequence(graph)
        if tuple(sequence) not in forbidden:
            assert k5_free(graph)
            write_rows(output_path, graph)
            evidence = {
                "source_sha256": hashlib.sha256(open(source_path, "rb").read()).hexdigest(),
                "graphs_in_source": len(lines), "selected_line": line_number,
                "selected_g6": line, "selected_degree_sequence": sequence,
                "exoo_degree_sequence": exoo_seq,
                "alternate_degree_sequence": alternate_seq,
                "color_swap_checked": True,
                "nonisomorphism_certificate": "selected degree sequence differs from each prior seed and each color-swapped complement degree sequence",
                "k5_free": True,
            }
            with open(evidence_path, "w", encoding="utf-8") as handle:
                json.dump(evidence, handle, indent=2, sort_keys=True)
                handle.write("\n")
            print(json.dumps(evidence, sort_keys=True))
            return
    raise RuntimeError("no color-swap-degree-distinct seed found")


if __name__ == "__main__":
    main()
