// Clause-weighting (breakout) local search for a K-colour Schur partition of 1..N.
// Constraints: for each x <= y with x + y <= N, the triple {x, y, x+y} (a pair when x = y) must not be
// monochromatic. Each triple has a weight (start 1). A move recolours one integer; its cost is the change in the
// weighted number of monochromatic triples. At a local minimum (no improving move) all currently violated
// triples gain weight 1 (breakout). Random-walk moves with probability p.
// usage: breakout N K start.json(or -) seed seconds out.json p
// start.json is {"colors": [...]} of any length; integers beyond it start random. Prints UTC-stamped progress.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <chrono>
#include <random>
#include <string>
#include <vector>
#include <array>
using namespace std;
static string utc() { time_t t = time(nullptr); char b[32]; strftime(b, 32, "%Y-%m-%dT%H:%M:%SZ", gmtime(&t)); return b; }
int main(int argc, char** argv) {
  if (argc < 8) { fprintf(stderr, "usage\n"); return 2; }
  int N = atoi(argv[1]), K = atoi(argv[2]); unsigned seed = atoi(argv[4]); double secs = atof(argv[5]); double p = atof(argv[7]);
  mt19937_64 rng(seed);
  vector<int> col(N + 1);
  for (int i = 1; i <= N; i++) col[i] = rng() % K;
  if (strcmp(argv[3], "-")) {
    FILE* f = fopen(argv[3], "r"); string s; int ch; while ((ch = fgetc(f)) != EOF) s += (char)ch; fclose(f);
    size_t a = s.find('['); int i = 1; const char* q = s.c_str() + a + 1;
    while (*q && *q != ']' && i <= N) { while (*q == ' ' || *q == ',' || *q == '\n') q++; if (*q == ']') break; col[i++] = strtol(q, (char**)&q, 10); }
  }
  // triples
  vector<array<int, 3>> T; vector<vector<int>> occ(N + 1);
  for (int x = 1; x <= N / 2; x++) for (int y = x; x + y <= N; y++) {
    int id = T.size(); T.push_back({x, y, x + y}); occ[x].push_back(id); if (y != x) occ[y].push_back(id); occ[x + y].push_back(id);
  }
  int M = T.size(); vector<long> w(M, 1);
  auto mono = [&](int t, int skip, int c) {  // is triple t monochromatic in colour c if integer `skip` had colour c
    for (int j = 0; j < 3; j++) { int v = T[t][j]; int cv = (v == skip) ? c : col[v]; if (cv != c) return false; }
    return true;
  };
  auto violated = [&](int t) { return col[T[t][0]] == col[T[t][1]] && col[T[t][1]] == col[T[t][2]]; };
  vector<int> vpos(M, -1), vset;
  auto refresh = [&](int u) { bool v = violated(u);
    if (v && vpos[u] < 0) { vpos[u] = vset.size(); vset.push_back(u); }
    else if (!v && vpos[u] >= 0) { int last = vset.back(); vset[vpos[u]] = last; vpos[last] = vpos[u]; vset.pop_back(); vpos[u] = -1; } };
  for (int t = 0; t < M; t++) refresh(t);
  long nviol = vset.size();
  long best = nviol; vector<int> bestc = col; auto t0 = chrono::steady_clock::now();
  printf("%s START N %d K %d seed %u triples %d viol %ld p %.3f\n", utc().c_str(), N, K, seed, M, nviol, p); fflush(stdout);
  long steps = 0, breakouts = 0;
  while (true) {
    if (nviol == 0) break;
    if ((steps & 1023) == 0) {
      double el = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
      if (el > secs) break;
      if ((steps & ((1 << 20) - 1)) == 0) { printf("%s step %ld viol %ld best %ld breakouts %ld\n", utc().c_str(), steps, nviol, best, breakouts); fflush(stdout); }
    }
    steps++;
    // pick a violated triple at random (reservoir over a sample)
    int t = vset[rng() % vset.size()];
    int bv = -1, bc = -1; long bd = 0;
    if ((double)(rng() % 1000000) / 1e6 < p) { bv = T[t][rng() % 3]; bc = rng() % K; if (bc == col[bv]) bc = (bc + 1) % K; }
    else {
      for (int j = 0; j < 3; j++) {
        int v = T[t][j];
        for (int c = 0; c < K; c++) if (c != col[v]) {
          long d = 0;
          for (int u : occ[v]) { if (violated(u)) d -= w[u]; if (mono(u, v, c)) d += w[u]; }
          if (bv < 0 || d < bd || (d == bd && rng() % 2)) { bd = d; bv = v; bc = c; }
        }
      }
      if (bd >= 0) {  // local minimum: breakout
        for (int u : vset) w[u]++;
        breakouts++;
        if (bd > 0) continue;
      }
    }
    col[bv] = bc;
    for (int u : occ[bv]) refresh(u);
    nviol = vset.size();
    if (nviol < best) { best = nviol; bestc = col; }
  }
  double el = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
  FILE* o = fopen(argv[6], "w"); fprintf(o, "{\"colors\": ["); for (int i = 1; i <= N; i++) fprintf(o, "%s%d", i > 1 ? ", " : "", bestc[i]); fprintf(o, "]}\n"); fclose(o);
  printf("%s END steps %ld breakouts %ld best %ld seconds %.1f\n", utc().c_str(), steps, breakouts, best, el);
  return 0;
}
