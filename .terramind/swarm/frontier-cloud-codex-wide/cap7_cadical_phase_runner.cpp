// Model-producing CaDiCaL runner with documented Solver::phase preferences.
// It never calls assume() and never adds clauses: the DIMACS input is the
// production formula verbatim.  Hints affect only branching polarity.
#include "cadical.hpp"

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

int main(int argc, char **argv) {
  if (argc != 4) {
    std::cerr << "usage: cap7_cadical_phase_runner CNF HINTS MODEL\n";
    return 2;
  }
  const char *cnf = argv[1];
  const char *hints = argv[2];
  const char *model = argv[3];
  CaDiCaL::Solver solver;
  int vars = 0;
  if (const char *error = solver.read_dimacs(cnf, vars)) {
    std::cerr << "DIMACS_ERROR " << error << "\n";
    return 2;
  }
  std::ifstream in(hints);
  int lit = 0, hinted = 0;
  while (in >> lit) {
    if (!lit || std::abs(lit) > 713) {
      std::cerr << "HINT_ERROR " << lit << "\n";
      return 2;
    }
    solver.phase(lit);  // CaDiCaL public API: default decision polarity.
    ++hinted;
  }
  if (hinted != 713) {
    std::cerr << "HINT_COUNT_ERROR " << hinted << "\n";
    return 2;
  }
  std::cout << "c phase_api=CaDiCaL::Solver::phase selection_hints=" << hinted
            << " assumptions=0 added_clauses=0 proof_logging=0\n";
  int result = solver.solve();
  if (result == 10) {
    std::ofstream out(model);
    for (int i = 1; i <= vars; ++i) {
      if ((i - 1) % 16 == 0) out << "v ";
      const int value = solver.val(i);
      out << (value > 0 ? i : -i) << ((i % 16 == 0) ? "\n" : " ");
    }
    out << "\n";
    std::cout << "s SATISFIABLE\n";
    std::cout << "c model_file=" << model << " variables=" << vars << "\n";
    return 10;
  }
  if (result == 20) {
    std::cout << "s UNSATISFIABLE\n";
    return 20;
  }
  std::cout << "s UNKNOWN\n";
  return 0;
}
