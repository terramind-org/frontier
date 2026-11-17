#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using Bits = uint64_t;
using Counts = std::array<int, 2>;
using Clock = std::chrono::steady_clock;

std::ostream& timestamp() {
    const auto now = std::time(nullptr);
    return std::cout << std::put_time(std::gmtime(&now), "%FT%TZ") << ' ';
}

struct Graph {
    using Neighbors = std::array<Bits, 64>;
    int n;
    std::array<Neighbors, 2> adj{};

    explicit Graph(int n) : n(n) {
        if (n < 1 || n >= 64) throw std::runtime_error("vertex count");
        for (int i = 0; i < n; ++i) adj[0][i] = ((Bits{1} << n)-1) ^ (Bits{1} << i);
    }

    bool edge(int i, int j) const { return adj[1][i] & (Bits{1} << j); }

    void flip(int i, int j) {
        for (auto& color : adj) {
            color[i] ^= Bits{1} << j;
            color[j] ^= Bits{1} << i;
        }
    }

    static int cliques(const Neighbors& color, Bits remaining, int size) {
        if (size == 0) return 1;
        if (size == 1) return std::popcount(remaining);
        int total = 0;
        while (std::popcount(remaining) >= size) {
            int v = std::countr_zero(remaining);
            remaining &= remaining - 1;
            total += cliques(color, remaining & color[v], size - 1);
        }
        return total;
    }

    Counts counts(const Counts& forbidden) const {
        Bits all = (Bits{1} << n)-1;
        return {cliques(adj[0], all, forbidden[0]), cliques(adj[1], all, forbidden[1])};
    }

    Counts delta(int i, int j, const Counts& forbidden) const {
        int existing = edge(i, j);
        Counts result{};
        for (int c = 0; c < 2; ++c) {
            result[c] = (c == existing ? -1 : 1) *
                cliques(adj[c], adj[c][i] & adj[c][j], forbidden[c]-2);
        }
        return result;
    }

    // Only four-vertex sets containing both endpoints can change induced P4 status.
    int p4_delta(int i, int j) const {
        int result = 0;
        for (int a = 0; a < n; ++a) {
            if (a == i || a == j) continue;
            for (int b = a+1; b < n; ++b) {
                if (b == i || b == j) continue;
                int ia = edge(i,a), ib = edge(i,b), ja = edge(j,a), jb = edge(j,b), ab = edge(a,b);
                int without = ia+ib+ja+jb+ab;
                int da = ia+ja+ab, db = ib+jb+ab;
                if (da < 1 || da > 2 || db < 1 || db > 2) continue;
                if (without == 3 && ia+ib >= 1 && ia+ib <= 2 && ja+jb >= 1 && ja+jb <= 2)
                    result += edge(i,j) ? 1 : -1;
                if (without == 2 && ia+ib <= 1 && ja+jb <= 1)
                    result += edge(i,j) ? -1 : 1;
            }
        }
        return result;
    }

    std::vector<size_t> conflict_edges(const Counts& forbidden) const {
        std::vector<size_t> result;
        std::array<int, 6> vertices{};
        for (int c = 0; c < 2; ++c) {
            auto visit = [&](auto&& self, Bits remaining, int used) -> void {
                if (used == forbidden[c]) {
                    for (int a = 0; a < used; ++a) {
                        int i = vertices[a];
                        for (int b = a+1; b < used; ++b)
                            result.push_back(i*(2*n-i-1)/2 + vertices[b]-i-1);
                    }
                    return;
                }
                while (std::popcount(remaining) >= forbidden[c]-used && result.size() < 8192) {
                    int v = std::countr_zero(remaining);
                    remaining &= remaining - 1;
                    vertices[used] = v;
                    self(self,remaining & adj[c][v],used+1);
                }
            };
            visit(visit,(Bits{1} << n)-1,0);
        }
        return result;
    }

    // Parse the simple JSON format emitted by save(), retaining only binary row strings.
    static Graph read(const std::string& path, int n) {
        std::ifstream in(path);
        if (!in) throw std::runtime_error("cannot read " + path);
        Graph graph(n);
        std::string token;
        std::vector<std::string> rows;
        while (std::getline(in, token, '"')) {
            if (token.size() == static_cast<size_t>(n) && token.find_first_not_of("01") == std::string::npos)
                rows.push_back(token);
        }
        if (rows.size() != static_cast<size_t>(n)) throw std::runtime_error("row count " + path);
        for (int i = 0; i < n; ++i) {
            if (rows[i][i] != '0') throw std::runtime_error("diagonal");
            for (int j = i+1; j < n; ++j) {
                if (rows[i][j] != rows[j][i]) throw std::runtime_error("asymmetry");
                if (rows[i][j] == '1') graph.flip(i,j);
            }
        }
        return graph;
    }

    void save(const std::string& path) const {
        const auto temporary = path + ".tmp";
        std::ofstream out(temporary);
        if (!out) throw std::runtime_error("cannot write " + path);
        out << "{\"n\":" << n << ",\"adjacency\":[";
        for (int i = 0; i < n; ++i) {
            if (i) out << ',';
            out << '"';
            for (int j = 0; j < n; ++j) out << edge(i,j);
            out << '"';
        }
        out << "]}\n";
        out.close();
        if (!out) throw std::runtime_error("incomplete write " + temporary);
        std::filesystem::rename(temporary,path);
    }

    int distance(const Graph& other) const {
        int differing = 0;
        for (int i = 0; i < n; ++i) differing += std::popcount(adj[1][i] ^ other.adj[1][i]);
        return differing/2;
    }
};

struct Fingerprint {
    Bits lo{}, hi{};
    bool operator==(const Fingerprint&) const = default;
    void toggle(Fingerprint other) { lo ^= other.lo; hi ^= other.hi; }
};
struct FingerprintHash {
    size_t operator()(Fingerprint key) const { return key.lo ^ std::rotl(key.hi, 23); }
};

std::vector<std::pair<int,int>> all_edges(int n) {
    std::vector<std::pair<int,int>> edges;
    for (int i = 0; i < n; ++i)
        for (int j = i+1; j < n; ++j) edges.emplace_back(i,j);
    return edges;
}

using Orbit = std::vector<std::pair<int,int>>;

struct OrbitTable {
    std::vector<Orbit> orbits;
    std::vector<std::pair<int,int>> vertex_reps;  // (representative, orbit size)
};

OrbitTable read_orbits(int n, const std::string& path) {
    const auto edges = all_edges(n);
    OrbitTable table;
    if (path == "-") {
        for (auto edge : edges) table.orbits.push_back({edge});
        return table;
    }
    std::ifstream in(path);
    int variables, reps;
    if (!(in >> variables >> reps) || variables < 1 || variables > int(edges.size()) || reps < 1 || reps > n)
        throw std::runtime_error("invalid orbit table");
    int vertex_total = 0;
    for (int r = 0; r < reps; ++r) {
        int v, weight;
        if (!(in >> v >> weight) || v < 0 || v >= n || weight < 1 || weight > n)
            throw std::runtime_error("invalid vertex orbit");
        table.vertex_reps.emplace_back(v,weight);
        vertex_total += weight;
    }
    if (vertex_total != n) throw std::runtime_error("vertex orbit sizes do not sum to n");
    table.orbits.resize(variables);
    for (auto e : edges) {
        int v;
        if (!(in >> v) || v < -1 || v >= variables) throw std::runtime_error("invalid edge orbit");
        if (v >= 0) table.orbits[v].push_back(e);
    }
    for (const auto& orbit : table.orbits)
        if (orbit.empty()) throw std::runtime_error("empty edge orbit");
    return table;
}

void anneal(int n, Counts forbidden, uint64_t seed, int steps, int restarts,
            double weight, double p4, const std::string& input, const std::string& prefix, const std::string& map,
            double high_override = 0, double low = 0.12, double focus = 0, double pair_rate = 0) {
    if ((focus > 0 || pair_rate > 0) && (map != "-" || forbidden[0] > 6 || forbidden[1] > 6))
        throw std::runtime_error("conflict and paired proposals require unrestricted edges and clique sizes <= 6");
    const auto orbits = read_orbits(n,map).orbits;
    size_t variable_edges = 0;
    for (const auto& orbit : orbits) variable_edges += orbit.size();
    const double orbit_scale = std::sqrt(double(variable_edges) / orbits.size());
    std::mt19937_64 rng(seed), hashes(837203);
    std::vector<Fingerprint> keys;
    for (size_t i = 0; i < orbits.size(); ++i) keys.push_back({hashes(), hashes()});
    std::uniform_real_distribution<double> uniform(0,1);
    std::uniform_int_distribution<size_t> pick(0,orbits.size()-1);
    std::unordered_set<Fingerprint, FingerprintHash> distinct;
    int best = std::numeric_limits<int>::max();
    timestamp() << "anneal n=" << n << " seed=" << seed << " steps=" << steps
                << " restarts=" << restarts << " weight1=" << weight << " p4=" << p4 << " start=" << input << " map=" << map << " high_override=" << high_override << " low=" << low << " focus=" << focus << " pair_rate=" << pair_rate << std::endl;

    for (int restart = 0; restart < restarts; ++restart) {
        Graph graph(n);
        if (input == "-") {
            double density = forbidden[0] == forbidden[1] ? 0.5 : 0.56 + 0.08*uniform(rng);
            for (const auto& orbit : orbits)
                if (uniform(rng) < density) for (auto [i,j] : orbit) graph.flip(i,j);
        } else {
            graph = Graph::read(high_override > 0 && restart > 0 ? prefix + ".json" : input,n);
        }
        Graph start = graph;
        Fingerprint state;
        for (size_t k = 0; k < orbits.size(); ++k)
            if (graph.edge(orbits[k].front().first, orbits[k].front().second)) state.toggle(keys[k]);
        Counts counts = graph.counts(forbidden);
        int accepted = 0;
        auto observe = [&](int step) {
            distinct.insert(state);
            int score = counts[0] + counts[1];
            if (score >= best) return;
            if (counts != graph.counts(forbidden)) throw std::runtime_error("delta disagrees with recount");
            best = score;
            graph.save(prefix + ".json");
            timestamp() << "best restart=" << restart << " step=" << step << " zero=" << counts[0]
                        << " one=" << counts[1] << " distance=" << graph.distance(start)
                        << " distinct=" << distinct.size() << std::endl;
        };
        observe(0);
        // Each restart cools from the same temperature. The seeded first pass is colder.
        double high = orbit_scale * (input != "-" && restart == 0 ? 1.1 : 2.6 + uniform(rng));
        if (high_override > 0) high = high_override * (0.9 + 0.2*uniform(rng));
        double decay = std::pow(low/high, 1.0/steps);
        double temperature = high;
        int tried = 0;
        std::vector<size_t> conflicts;
        while (tried < steps && best > 0) {
            ++tried;
            temperature *= decay;
            size_t k = pick(rng);
            if (focus > 0) {
                if ((tried-1) % 128 == 0) conflicts = graph.conflict_edges(forbidden);
                if (!conflicts.empty() && uniform(rng) < focus) {
                    std::uniform_int_distribution<size_t> pick_conflict(0,conflicts.size()-1);
                    k = conflicts[pick_conflict(rng)];
                }
            }
            size_t second = orbits.size();
            if (pair_rate > 0 && uniform(rng) < pair_rate) {
                auto [i,j] = orbits[k].front();
                const int pivot = (rng() & 1) ? i : j;
                Bits choices = graph.adj[!graph.edge(i,j)][pivot];
                if (choices) {
                    std::uniform_int_distribution<int> rank(0,std::popcount(choices)-1);
                    for (int skip = rank(rng); skip > 0; --skip) choices &= choices-1;
                    const int target = std::countr_zero(choices);
                    const int a = std::min(pivot,target), b = std::max(pivot,target);
                    second = a*(2*n-a-1)/2 + b-a-1;
                }
            }
            Counts diff{};
            int change_p4 = 0;
            auto apply = [&](const Orbit& orbit) {
                for (auto [i,j] : orbit) {
                    Counts edge_diff = graph.delta(i,j,forbidden);
                    diff[0] += edge_diff[0];
                    diff[1] += edge_diff[1];
                    if (p4 != 0) change_p4 += graph.p4_delta(i,j);
                    graph.flip(i,j);
                }
            };
            apply(orbits[k]);
            if (second < orbits.size()) apply(orbits[second]);
            double energy = diff[0] + weight*diff[1] - p4*change_p4;
            if (energy > 0 && uniform(rng) >= std::exp(-energy/temperature)) {
                for (auto [i,j] : orbits[k]) graph.flip(i,j);
                if (second < orbits.size()) for (auto [i,j] : orbits[second]) graph.flip(i,j);
                continue;
            }
            ++accepted;
            counts[0] += diff[0];
            counts[1] += diff[1];
            state.toggle(keys[k]);
            if (second < orbits.size()) state.toggle(keys[second]);
            observe(tried);
        }
        if (counts != graph.counts(forbidden)) throw std::runtime_error("final counts disagree with recount");
        timestamp() << "end restart=" << restart << " tried=" << tried << " accepted=" << accepted
                    << " distinct=" << distinct.size() << " best_total=" << best
                    << " final_zero=" << counts[0] << " final_one=" << counts[1] << std::endl;
        if (best == 0) break;
    }
}

void enumerate(int n, Counts forbidden, const std::string& table, const std::string& prefix) {
    auto [orbits, vertex_reps] = read_orbits(n,table);
    const int variables = int(orbits.size());
    if (variables > 28 || vertex_reps.empty()) throw std::runtime_error("enumeration needs at most 28 variables");
    Graph graph(n);
    int best = std::numeric_limits<int>::max();
    const uint64_t candidates = Bits{1} << variables;
    timestamp() << "enumerate candidates=" << candidates << " variables=" << variables << std::endl;
    for (uint64_t index = 0; index < candidates; ++index) {
        if (index != 0 && (index & ((Bits{1} << 20) - 1)) == 0)
            timestamp() << "progress visited=" << index << " best_total=" << best << std::endl;
        if (index != 0)
            for (auto [i,j] : orbits[std::countr_zero(index)]) graph.flip(i,j);
        Counts counts{};
        for (int c = 0; c < 2; ++c) {
            int rooted_sum = 0;
            for (auto [v, orbit_size] : vertex_reps)
                rooted_sum += orbit_size * Graph::cliques(graph.adj[c], graph.adj[c][v],forbidden[c]-1);
            if (rooted_sum % forbidden[c]) throw std::runtime_error("nonintegral rooted clique count");
            counts[c] = rooted_sum / forbidden[c];
        }
        int score = counts[0] + counts[1];
        if (score >= best) continue;
        if (counts != graph.counts(forbidden)) throw std::runtime_error("rooted count mismatch");
        best = score;
        graph.save(prefix + ".json");
        timestamp() << "best visited=" << index+1 << " zero=" << counts[0] << " one=" << counts[1] << std::endl;
    }
    timestamp() << "end visited=" << candidates << " minimum_total=" << best << std::endl;
}

void check_deltas(Graph graph, Counts forbidden, int seed, int steps) {
    std::mt19937 rng(seed);
    const auto edges = all_edges(graph.n);
    std::uniform_int_distribution<size_t> pick(0,edges.size()-1);
    Counts counts = graph.counts(forbidden);
    timestamp() << "check zero=" << counts[0] << " one=" << counts[1] << std::endl;
    auto p4_count = [](const Graph& g) {
        int total = 0;
        for (int a=0; a<g.n; ++a) for (int b=a+1; b<g.n; ++b)
            for (int c=b+1; c<g.n; ++c) for (int d=c+1; d<g.n; ++d) {
                std::array<int,4> vertices{a,b,c,d};
                std::array<int,4> degree{};
                for (int i=0; i<4; ++i) for (int j=i+1; j<4; ++j)
                    if (g.edge(vertices[i],vertices[j])) { ++degree[i]; ++degree[j]; }
                std::sort(degree.begin(),degree.end());
                total += (degree == std::array<int,4>{1,1,2,2});
            }
        return total;
    };
    int p4 = p4_count(graph);
    for (int trial = 0; trial < steps; ++trial) {
        auto [i,j] = edges[pick(rng)];
        auto diff = graph.delta(i,j,forbidden);
        p4 += graph.p4_delta(i,j);
        graph.flip(i,j);
        for (int c=0; c<2; ++c) counts[c] += diff[c];
        if (graph.counts(forbidden) != counts || p4_count(graph) != p4)
            throw std::runtime_error("incremental control failed");
    }
    timestamp() << "checked_flips=" << steps << " seed=" << seed << std::endl;
}

#include "star.inc"

int main(int argc, char** argv) {
    if (argc < 5) throw std::runtime_error("expected MODE N ZERO ONE and mode arguments");
    std::string mode = argv[1];
    int n = std::stoi(argv[2]);
    Counts sizes{std::stoi(argv[3]), std::stoi(argv[4])};
    if (mode == "check" && argc == 8) {
        check_deltas(Graph::read(argv[5],n), sizes, std::stoi(argv[6]), std::stoi(argv[7]));
    } else if (mode == "exact-star" && argc == 8) {
        StarOptimizer(Graph::read(argv[5],n),sizes,argv[6],argv[7]).run();
    } else if (mode == "enumerate" && argc == 7) {
        enumerate(n,sizes,argv[5],argv[6]);
    } else if (mode == "anneal" && (argc == 12 || argc == 13 || argc == 15 || argc == 16 || argc == 17)) {
        anneal(n,sizes,std::stoull(argv[5]),std::stoi(argv[6]),std::stoi(argv[7]),
               std::stod(argv[8]),std::stod(argv[9]),argv[10],argv[11],argc >= 13 ? argv[12] : "-",
               argc >= 15 ? std::stod(argv[13]) : 0, argc >= 15 ? std::stod(argv[14]) : 0.12,
               argc >= 16 ? std::stod(argv[15]) : 0, argc == 17 ? std::stod(argv[16]) : 0);
    } else {
        throw std::runtime_error("invalid arguments");
    }
}
