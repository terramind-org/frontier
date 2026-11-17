// Marker 'satisfied_by' records the depth where an assigned literal first satisfied a clause.
struct StarClause {
    Bits variables;
    int satisfying_color;
    int remaining;
    int satisfied_by = -1;
};

class StarOptimizer {
    const Graph seed;
    const Counts forbidden;
    const std::string prefix;
    int variables;
    std::vector<StarClause> clauses;
    std::vector<std::vector<size_t>> occurrences;
    std::vector<Counts> units;
    int forced = 0;
    int unit_bound = 0;
    int incumbent;
    uint64_t nodes = 0;
    uint64_t covered = 0;

    void update_unit(const StarClause& clause, Bits assigned, int delta) {
        Bits unassigned = clause.variables & ~assigned;
        if (std::popcount(unassigned) != 1) throw std::runtime_error("not a unit clause");
        auto& counts = units[std::countr_zero(unassigned)];
        unit_bound -= std::min(counts[0],counts[1]);
        counts[clause.satisfying_color] += delta;
        unit_bound += std::min(counts[0],counts[1]);
    }

    void apply(int v, int value, Bits assigned, Bits after, int depth) {
        for (size_t id : occurrences[v]) {
            auto& clause = clauses[id];
            if (clause.satisfied_by >= 0) continue;
            if (clause.remaining == 1) update_unit(clause,assigned,-1);
            if (value == clause.satisfying_color) {
                clause.satisfied_by = depth;
            } else {
                --clause.remaining;
                if (clause.remaining == 0) ++forced;
                if (clause.remaining == 1) update_unit(clause,after,1);
            }
        }
    }

    void undo(int v, Bits assigned, Bits after, int depth) {
        for (size_t id : occurrences[v]) {
            auto& clause = clauses[id];
            if (clause.satisfied_by >= 0 && clause.satisfied_by < depth) continue;
            if (clause.satisfied_by == depth) {
                clause.satisfied_by = -1;
            } else {
                if (clause.remaining == 1) update_unit(clause,after,-1);
                if (clause.remaining == 0) --forced;
                ++clause.remaining;
            }
            if (clause.remaining == 1) update_unit(clause,assigned,1);
        }
    }

    Graph decode(Bits assignment) const {
        Graph graph = seed;
        for (int v = 0; v < variables; ++v) {
            if (graph.edge(v,variables) != bool(assignment & (Bits{1} << v))) graph.flip(v,variables);
        }
        return graph;
    }

    int violations(Bits assignment) const {
        int total = 0;
        for (const auto& clause : clauses)
            total += !(clause.variables & (clause.satisfying_color ? assignment : ~assignment));
        return total;
    }

    void visit(Bits assigned, Bits assignment, int depth) {
        ++nodes;
        if ((nodes & ((Bits{1} << 20)-1)) == 0)
            timestamp() << "progress nodes=" << nodes << " covered=" << covered << " incumbent=" << incumbent << std::endl;
        // Every violated clause is already fixed. For each unassigned variable,
        // the cheaper setting still violates at least min(positive,negative) unit clauses.
        if (forced + unit_bound >= incumbent) {
            covered += Bits{1} << (variables-depth);
            return;
        }
        if (depth == variables) {
            Graph graph = decode(assignment);
            Counts counts = graph.counts(forbidden);
            if (counts[0] + counts[1] != forced || violations(assignment) != forced)
                throw std::runtime_error("star bound or decode disagrees with full counter");
            incumbent = forced;
            graph.save(prefix+".json");
            ++covered;
            timestamp() << "best nodes=" << nodes << " covered=" << covered << " zero=" << counts[0]
                        << " one=" << counts[1] << " distance=" << graph.distance(seed) << std::endl;
            return;
        }
        int chosen = -1;
        size_t rank = 0;
        for (int v = 0; v < variables; ++v) {
            if (assigned & (Bits{1} << v)) continue;
            size_t candidate = occurrences[v].size() + 16*(units[v][0]+units[v][1]);
            if (chosen == -1 || candidate > rank) {
                chosen = v;
                rank = candidate;
            }
        }
        Bits bit = Bits{1} << chosen;
        Bits after = assigned | bit;
        int first = units[chosen][1] == units[chosen][0] ?
            seed.edge(chosen,variables) : units[chosen][1] > units[chosen][0];
        for (int value : {first,1-first}) {
            apply(chosen,value,assigned,after,depth);
            visit(after,assignment | (value ? bit : 0),depth+1);
            undo(chosen,assigned,after,depth);
        }
    }

public:
    StarOptimizer(Graph graph, Counts sizes, const std::string& path, std::string output)
        : seed(graph), forbidden(sizes), prefix(output), variables(graph.n-1),
          occurrences(variables), units(variables) {
        std::ifstream in(path);
        Bits mask;
        int color;
        while (in >> mask >> color) {
            if (mask == 0 || mask >> variables || color < 0 || color > 1)
                throw std::runtime_error("invalid star clause");
            const auto id = clauses.size();
            clauses.push_back({mask,color,std::popcount(mask),-1});
            for (int v = 0; v < variables; ++v)
                if (mask & (Bits{1} << v)) occurrences[v].push_back(id);
        }
        if (!in.eof() || clauses.empty()) throw std::runtime_error("missing star clauses");
        Bits assignment = seed.adj[1][variables];
        incumbent = violations(assignment);
        Counts counts = seed.counts(forbidden);
        if (counts[0] + counts[1] != incumbent) throw std::runtime_error("star seed and formula disagree");
        for (const auto& clause : clauses) if (clause.remaining == 1) update_unit(clause,0,1);
        seed.save(prefix+".json");
        timestamp() << "initial clauses=" << clauses.size() << " zero=" << counts[0]
                    << " one=" << counts[1] << " incumbent=" << incumbent << std::endl;
    }

    void run() {
        visit(0,0,0);
        if (covered != (Bits{1} << variables)) throw std::runtime_error("star traversal did not cover full space");
        timestamp() << "end nodes=" << nodes << " covered=" << covered << " optimum=" << incumbent << std::endl;
    }
};
