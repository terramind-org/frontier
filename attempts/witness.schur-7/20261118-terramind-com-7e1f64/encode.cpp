#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

using Mask = unsigned;
int main(int argc, char** argv) {
    if (argc != 3) return 2;
    std::ifstream input(argv[1]);
    int n, k, mirrors, restrictions;
    if (!(input >> n >> k >> mirrors >> restrictions) || n < 1 || k < 1 || k > 7) return 2;
    std::vector<int> rep(n + 1);
    std::vector<Mask> allowed(n + 1, (1u << k) - 1);
    for (int x = 1; x <= n; ++x) rep[x] = x;
    for (int i = 0; i < mirrors; ++i) {
        int x, y;
        if (!(input >> x >> y) || x < 1 || y < 1 || x > n || y > n) return 2;
        int a = rep[x], b = rep[y];
        if (a != b) for (int& r : rep) if (r == b) r = a;
    }
    for (int i = 0; i < restrictions; ++i) {
        int x;
        Mask mask;
        if (!(input >> x >> mask) || x < 1 || x > n || mask >= (1u << k)) return 2;
        allowed[rep[x]] &= mask;
    }
    FILE* out = std::fopen(argv[2], "w+");
    if (!out) return 3;
    std::setvbuf(out, nullptr, _IOFBF, 1024 * 1024);
    auto variable = [k](int x, int c) { return (x - 1) * k + c + 1; };
    int clauses = 0;
    std::fprintf(out, "%-50s\n", "");
    auto end_clause = [&] { std::fputs("0\n", out); ++clauses; };
    for (int x = 1; x <= n; ++x) {
        if (rep[x] != x) continue;
        for (int c = 0; c < k; ++c) {
            if (allowed[x] & (1u << c)) std::fprintf(out, "%d ", variable(x,c));
        }
        end_clause();
        for (int c = 0; c < k; ++c) {
            if (!(allowed[x] & (1u << c))) {
                std::fprintf(out, "%d ", -variable(x,c));
                end_clause();
            }
        }
        for (int c = 0; c < k; ++c) {
            if (!(allowed[x] & (1u << c))) continue;
            for (int d = c + 1; d < k; ++d) {
                if (!(allowed[x] & (1u << d))) continue;
                std::fprintf(out, "%d %d ", -variable(x,c), -variable(x,d));
                end_clause();
            }
        }
    }
    // A triple and its reflected companions are interchangeable. Only identical
    // representative sets are duplicates, including pairs from x == y.
    std::vector<std::array<int,3>> triples;
    triples.reserve(static_cast<size_t>(n) * n / 4);
    for (int x = 1; 2*x <= n; ++x) {
        for (int y = x; x + y <= n; ++y) {
            std::array<int,3> rs{rep[x], rep[y], rep[x+y]};
            if (!(allowed[rs[0]] & allowed[rs[1]] & allowed[rs[2]])) continue;
            std::sort(rs.begin(), rs.end());
            triples.push_back(rs);
        }
    }
    std::sort(triples.begin(), triples.end());
    triples.erase(std::unique(triples.begin(), triples.end()), triples.end());
    for (const auto& rs : triples) {
        Mask shared = allowed[rs[0]] & allowed[rs[1]] & allowed[rs[2]];
        for (int c = 0; c < k; ++c) {
            Mask bit = 1u << c;
            if (!(shared & bit)) continue;
            int last = 0;
            for (int r : rs) {
                if (r != last && allowed[r] != bit) std::fprintf(out, "%d ", -variable(r,c));
                last = r;
            }
            end_clause();
        }
    }
    if (std::fflush(out) || std::fseek(out, 0, SEEK_SET) ||
        std::fprintf(out, "p cnf %d %d", n*k, clauses) < 0 || std::fclose(out)) return 3;
    return 0;
}
