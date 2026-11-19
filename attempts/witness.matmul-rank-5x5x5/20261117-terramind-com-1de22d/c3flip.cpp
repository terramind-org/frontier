// C3-symmetric flip-graph descent over GF(2) for n x n matrix multiplication (n <= 6).
//
// Convention (trace form): the target tensor is sum_{i,j,k} E_ij (x) E_jk (x) E_ki, a factor is an n*n bitmask with
// bit i*n+j = entry (i,j). The cyclic action is (a,b,c) -> (b,c,a). A C3-invariant scheme is stored as
//   fixed terms X (x) X (x) X  (never moved, as in the paper), and
//   orbits {(a,b,c),(b,c,a),(c,a,b)} stored by one representative.
// rank = 3 * #orbits + #fixed.
//
// Moves (Moosbauer and Poole, arXiv:2502.04514, Theorem 4 and Algorithm 1):
//   orbit flip: two distinct orbits whose representatives, after rotation, share the first factor X:
//     (X,b,c) + (X,b',c') -> (X,b,c+c') + (X,b'+b,c')   (over GF(2))
//   a factor that becomes 0 removes its orbit (this is how reductions happen, as in the paper);
//   orbit plus-transition: (a,b,c) + (a',b',c') -> (a+a',b,c) + (a',b,c+c') + (a',b+b',c').
// Search (Algorithm 1): random orbit flips; a plus-transition after M flips with no rank change; stop the descent
// after L flips with no new minimum rank for that descent. Optional greedy reduction scan after each flip.
//
// The tensor identity of the state is re-checked exactly every 2^20 flips, at every new descent minimum, and on
// every saved scheme.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <unordered_set>
#include <vector>

typedef uint32_t M32;
static int N = 5, NN = 25;

static inline uint64_t splitmix(uint64_t &x) {
  uint64_t z = (x += 0x9E3779B97F4A7C15ULL);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}
struct Rng {
  uint64_t s[2];
  explicit Rng(uint64_t seed) { uint64_t x = seed; s[0] = splitmix(x); s[1] = splitmix(x); }
  inline uint64_t next() {
    uint64_t s1 = s[0]; const uint64_t s0 = s[1];
    s[0] = s0; s1 ^= s1 << 23; s[1] = s1 ^ s0 ^ (s1 >> 17) ^ (s0 >> 26);
    return s[1] + s0;
  }
  inline uint32_t below(uint32_t m) { return (uint32_t)(((next() >> 32) * (uint64_t)m) >> 32); }
};

static std::string utcnow() {
  char buf[32]; time_t t = time(nullptr); struct tm g; gmtime_r(&t, &g);
  strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", &g); return buf;
}

static inline uint64_t mix3(M32 a, M32 b, M32 c) {
  uint64_t x = ((uint64_t)a << 32) ^ ((uint64_t)b * 0x9E3779B97F4A7C15ULL) ^ ((uint64_t)c * 0xC2B2AE3D27D4EB4FULL);
  x ^= x >> 31; x *= 0xD6E8FEB86659FD93ULL; x ^= x >> 29; x *= 0x9FB21C651E98DF25ULL; x ^= x >> 32;
  return x;
}
static inline uint64_t orbitHash(M32 a, M32 b, M32 c) {
  uint64_t h1 = mix3(a, b, c), h2 = mix3(b, c, a), h3 = mix3(c, a, b);
  return std::min(h1, std::min(h2, h3));
}
static inline uint64_t fixedHash(M32 x) { return mix3(x, x, x) * 3ULL + 0x1234567ULL; }

// ---------------- factor index: value -> occurrences (orbit*3+pos) ----------------
static const int TBITS = 13, TSIZE = 1 << TBITS, TMASK = TSIZE - 1, MAXOCC = 120;
struct Slot { M32 key; int32_t mpos; uint16_t cnt; uint16_t occ[MAXOCC]; };

struct State {
  std::vector<M32> f;      // 3 per orbit
  std::vector<uint64_t> oh; // orbit hash
  std::vector<M32> fixedT;
  uint64_t H = 0;
  std::vector<Slot> tab;
  std::vector<M32> multi;  // keys whose slot has cnt >= 2
  bool overflow = false;

  State() : tab(TSIZE) { for (auto &s : tab) { s.key = 0; s.cnt = 0; s.mpos = -1; } }
  int orbits() const { return (int)f.size() / 3; }
  int rank() const { return 3 * orbits() + (int)fixedT.size(); }

  static inline uint32_t home(M32 k) { return (uint32_t)((k * 0x9E3779B1u) >> (32 - TBITS)); }
  inline int find(M32 k) const {
    uint32_t i = home(k);
    while (tab[i].key != 0) { if (tab[i].key == k) return (int)i; i = (i + 1) & TMASK; }
    return -1;
  }
  void multiAdd(M32 k, int si) { tab[si].mpos = (int)multi.size(); multi.push_back(k); }
  void multiDel(int si) {
    int p = tab[si].mpos; M32 last = multi.back(); multi[p] = last; multi.pop_back();
    if (last != tab[si].key) { int sj = find(last); tab[sj].mpos = p; }
    tab[si].mpos = -1;
  }
  void addOcc(M32 k, uint16_t id) {
    uint32_t i = home(k);
    while (tab[i].key != 0 && tab[i].key != k) i = (i + 1) & TMASK;
    Slot &s = tab[i];
    if (s.key == 0) { s.key = k; s.cnt = 0; s.mpos = -1; }
    if (s.cnt >= MAXOCC) { overflow = true; return; }
    s.occ[s.cnt++] = id;
    if (s.cnt == 2) multiAdd(k, (int)i);
  }
  void delSlot(uint32_t i) {
    uint32_t j = i;
    for (;;) {
      j = (j + 1) & TMASK;
      if (tab[j].key == 0) break;
      uint32_t h = home(tab[j].key);
      bool inRange = (i <= j) ? (i < h && h <= j) : (i < h || h <= j);
      if (!inRange) { tab[i] = tab[j]; i = j; }
    }
    tab[i].key = 0; tab[i].cnt = 0; tab[i].mpos = -1;
  }
  void delOcc(M32 k, uint16_t id) {
    int si = find(k);
    if (si < 0 && overflow) return; // index already inconsistent after an overflow; the descent ends after this move
    if (si < 0) { fprintf(stderr, "delOcc: missing key overflow=%d orbits=%d\n", (int)overflow, orbits()); abort(); }
    Slot &s = tab[si];
    int p = -1; for (int t = 0; t < s.cnt; t++) if (s.occ[t] == id) { p = t; break; }
    if (p < 0 && overflow) return;
    if (p < 0) { fprintf(stderr, "delOcc: missing id overflow=%d orbits=%d\n", (int)overflow, orbits()); abort(); }
    s.occ[p] = s.occ[--s.cnt];
    if (s.cnt == 1) multiDel(si);
    if (s.cnt == 0) delSlot((uint32_t)si);
  }
  void renameOcc(M32 k, uint16_t from, uint16_t to) {
    int si = find(k); Slot &s = tab[si];
    for (int t = 0; t < s.cnt; t++) if (s.occ[t] == from) { s.occ[t] = to; return; }
    fprintf(stderr, "renameOcc: missing\n"); abort();
  }
  void toggleFixed(M32 x) {
    for (size_t t = 0; t < fixedT.size(); t++)
      if (fixedT[t] == x) { fixedT[t] = fixedT.back(); fixedT.pop_back(); H -= fixedHash(x); return; }
    fixedT.push_back(x); H += fixedHash(x);
  }
  void addOrbit(M32 a, M32 b, M32 c) {
    if (a == 0 || b == 0 || c == 0) return;
    if (a == b && b == c) { toggleFixed(a); return; } // orbit sum of a fixed tensor is 3x = x over GF(2)
    int o = orbits();
    f.push_back(a); f.push_back(b); f.push_back(c);
    uint64_t h = orbitHash(a, b, c); oh.push_back(h); H += h;
    addOcc(a, (uint16_t)(3 * o)); addOcc(b, (uint16_t)(3 * o + 1)); addOcc(c, (uint16_t)(3 * o + 2));
  }
  void removeOrbit(int o) {
    for (int p = 0; p < 3; p++) if (f[3 * o + p]) delOcc(f[3 * o + p], (uint16_t)(3 * o + p));
    H -= oh[o];
    int last = orbits() - 1;
    if (o != last) {
      for (int p = 0; p < 3; p++) {
        f[3 * o + p] = f[3 * last + p];
        if (f[3 * o + p]) renameOcc(f[3 * o + p], (uint16_t)(3 * last + p), (uint16_t)(3 * o + p));
      }
      oh[o] = oh[last];
    }
    f.resize(3 * last); oh.resize(last);
  }
  // set factor (o,p) to v; does not remove zero orbits (caller does), keeps hash current when orbit stays nonzero
  void setFactor(int o, int p, M32 v) {
    M32 old = f[3 * o + p];
    if (old) delOcc(old, (uint16_t)(3 * o + p));
    f[3 * o + p] = v;
    if (v) addOcc(v, (uint16_t)(3 * o + p));
  }
  void rehash(int o) {
    H -= oh[o];
    M32 a = f[3 * o], b = f[3 * o + 1], c = f[3 * o + 2];
    oh[o] = (a && b && c) ? orbitHash(a, b, c) : 0; H += oh[o];
  }
  // after modifying orbits in `touched`, drop zero orbits and convert fixed ones; process high index first
  void cleanup(int *touched, int nt) {
    std::sort(touched, touched + nt, [](int x, int y) { return x > y; });
    for (int t = 0; t < nt; t++) {
      int o = touched[t];
      if (t > 0 && touched[t] == touched[t - 1]) continue;
      M32 a = f[3 * o], b = f[3 * o + 1], c = f[3 * o + 2];
      if (a == 0 || b == 0 || c == 0) { removeOrbit(o); continue; }
      if (a == b && b == c) { removeOrbit(o); toggleFixed(a); continue; }
      rehash(o);
    }
  }
  void rebuildFrom(const std::vector<M32> &orb, const std::vector<M32> &fx) {
    f.clear(); oh.clear(); fixedT.clear(); multi.clear(); H = 0; overflow = false;
    for (auto &s : tab) { s.key = 0; s.cnt = 0; s.mpos = -1; }
    for (M32 x : fx) toggleFixed(x);
    for (size_t t = 0; t + 2 < orb.size(); t += 3) addOrbit(orb[t], orb[t + 1], orb[t + 2]);
  }
};

// ---------------- exact tensor check over GF(2) ----------------
static std::vector<M32> targetT;
static void buildTarget() {
  targetT.assign(NN * NN, 0);
  for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) for (int k = 0; k < N; k++)
    targetT[(i * N + j) * NN + (j * N + k)] ^= (M32)1 << (k * N + i);
}
static void addTerm(std::vector<M32> &T, M32 a, M32 b, M32 c) {
  for (int p = 0; p < NN; p++) if (a >> p & 1) for (int q = 0; q < NN; q++) if (b >> q & 1) T[p * NN + q] ^= c;
}
static bool checkState(const State &S) {
  std::vector<M32> T(NN * NN, 0);
  for (int o = 0; o < S.orbits(); o++) {
    M32 a = S.f[3 * o], b = S.f[3 * o + 1], c = S.f[3 * o + 2];
    addTerm(T, a, b, c); addTerm(T, b, c, a); addTerm(T, c, a, b);
  }
  for (M32 x : S.fixedT) addTerm(T, x, x, x);
  return T == targetT;
}
// check that the stored index matches the factor list (debug / self-test)
static bool checkIndex(const State &S) {
  size_t occ = 0;
  for (auto &s : S.tab) if (s.key) {
    occ += s.cnt;
    for (int t = 0; t < s.cnt; t++) if (S.f[s.occ[t]] != s.key) return false;
    if ((s.cnt >= 2) != (s.mpos >= 0)) return false;
  }
  size_t nz = 0; for (M32 v : S.f) if (v) nz++;
  return occ == nz;
}

// ---------------- starting point for a diagonal partition (Definition 6) ----------------
static void startingPoint(const std::vector<std::vector<int>> &P, std::vector<M32> &orb, std::vector<M32> &fx) {
  auto E = [](int i, int j) { return (M32)1 << (i * N + j); };
  orb.clear(); fx.clear();
  std::vector<int> blk(N, -1);
  for (size_t b = 0; b < P.size(); b++) for (int i : P[b]) blk[i] = (int)b;
  for (auto &B : P) { M32 x = 0; for (int i : B) x |= E(i, i); fx.push_back(x); }
  // standard basis terms a_ij b_jk c_ki, i=j=k excluded, one representative per rotation class (i,j,k)->(j,k,i)
  for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) for (int k = 0; k < N; k++) {
    if (i == j && j == k) continue;
    int key = (i * N + j) * N + k, k2 = (j * N + k) * N + i, k3 = (k * N + i) * N + j;
    if (key > k2 || key > k3) continue;
    orb.push_back(E(i, j)); orb.push_back(E(j, k)); orb.push_back(E(k, i));
  }
  // correction terms a_ii b_jj c_kk for i,j,k in one block, not all equal
  for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) for (int k = 0; k < N; k++) {
    if (i == j && j == k) continue;
    if (blk[i] != blk[j] || blk[j] != blk[k]) continue;
    int key = (i * N + j) * N + k, k2 = (j * N + k) * N + i, k3 = (k * N + i) * N + j;
    if (key > k2 || key > k3) continue;
    orb.push_back(E(i, i)); orb.push_back(E(j, j)); orb.push_back(E(k, k));
  }
}
static std::vector<std::vector<int>> parsePartition(const std::string &s) {
  std::vector<std::vector<int>> P(1);
  for (char ch : s) { if (ch == '|') P.emplace_back(); else P.back().push_back(ch - '1'); }
  std::vector<int> seen(N, 0);
  for (auto &B : P) for (int i : B) { if (i < 0 || i >= N || seen[i]++) { fprintf(stderr, "bad partition\n"); exit(2); } }
  for (int i = 0; i < N; i++) if (!seen[i]) { fprintf(stderr, "partition misses %d\n", i + 1); exit(2); }
  return P;
}

// file format: "C3SCHEME n rank orbits fixed" then fixed lines "X" then orbit lines "a b c"
static void writeScheme(const char *path, const State &S) {
  FILE *fp = fopen(path, "w"); if (!fp) { perror(path); return; }
  fprintf(fp, "C3SCHEME %d %d %d %d\n", N, S.rank(), S.orbits(), (int)S.fixedT.size());
  for (M32 x : S.fixedT) fprintf(fp, "%u\n", x);
  for (int o = 0; o < S.orbits(); o++) fprintf(fp, "%u %u %u\n", S.f[3 * o], S.f[3 * o + 1], S.f[3 * o + 2]);
  fclose(fp);
}
static bool readScheme(const char *path, std::vector<M32> &orb, std::vector<M32> &fx) {
  FILE *fp = fopen(path, "r"); if (!fp) return false;
  int n, r, no, nf; if (fscanf(fp, "C3SCHEME %d %d %d %d", &n, &r, &no, &nf) != 4 || n != N) { fclose(fp); return false; }
  orb.clear(); fx.clear();
  for (int t = 0; t < nf; t++) { unsigned x; if (fscanf(fp, "%u", &x) != 1) return false; fx.push_back(x); }
  for (int t = 0; t < 3 * no; t++) { unsigned x; if (fscanf(fp, "%u", &x) != 1) return false; orb.push_back(x); }
  fclose(fp); return true;
}

// ---------------- the search ----------------
struct Params {
  int n = 5; std::string partition = "15|24|3"; std::string startFile; std::string poolFile; int kicks = 0;
  double L = 1e8, M = 5e4; uint64_t seed = 1; long descents = 1; double seconds = 1e18;
  int target = 0; int plusCap = 30; int saveAt = 0; std::string outDir = "out"; std::string tag = "run";
  bool greedy = false; int sampleShift = 7; bool selftest = false; bool paperPlus = false;
};

static double now() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }

// one random orbit flip. returns 1 if a flip was made, 0 if no flip available.
static int randomFlip(State &S, Rng &R) {
  for (int attempt = 0; attempt < 64; attempt++) {
    if (S.multi.empty()) return 0;
    M32 X = S.multi[R.below((uint32_t)S.multi.size())];
    const Slot &s = S.tab[S.find(X)];
    uint16_t u = s.occ[R.below(s.cnt)], v = s.occ[R.below(s.cnt)];
    int i = u / 3, j = v / 3;
    if (i == j) {
      // try to find a partner in another orbit
      int start = (int)R.below(s.cnt), found = -1;
      for (int t = 0; t < s.cnt; t++) { int w = s.occ[(start + t) % s.cnt]; if (w / 3 != i) { found = w; break; } }
      if (found < 0) continue;
      v = (uint16_t)found; j = v / 3;
    }
    int p = u % 3, q = v % 3;
    // orbit i rotated: (X, f[(p+1)%3], f[(p+2)%3]); orbit j likewise
    int ib = 3 * i + (p + 1) % 3, ic = 3 * i + (p + 2) % 3;
    int jb = 3 * j + (q + 1) % 3, jc = 3 * j + (q + 2) % 3;
    M32 newCi = S.f[ic] ^ S.f[jc];
    M32 newBj = S.f[jb] ^ S.f[ib];
    S.setFactor(i, (p + 2) % 3, newCi);
    S.setFactor(j, (q + 1) % 3, newBj);
    int touched[2] = {i, j};
    S.cleanup(touched, 2);
    return 1;
  }
  return 0;
}
static bool plusTransition(State &S, Rng &R) {
  int k = S.orbits(); if (k < 2) return false;
  for (int attempt = 0; attempt < 64; attempt++) {
    int i = (int)R.below(k), j = (int)R.below(k); if (i == j) continue;
    int ri = (int)R.below(3), rj = (int)R.below(3);
    M32 a = S.f[3 * i + ri], b = S.f[3 * i + (ri + 1) % 3], c = S.f[3 * i + (ri + 2) % 3];
    M32 a2 = S.f[3 * j + rj], b2 = S.f[3 * j + (rj + 1) % 3], c2 = S.f[3 * j + (rj + 2) % 3];
    if (a == a2 || b == b2 || c == c2) continue;
    // (a,b,c)+(a2,b2,c2) = (a+a2,b,c) + (a2,b,c+c2) + (a2,b+b2,c2)
    S.setFactor(i, ri, a ^ a2);
    S.setFactor(j, (rj + 1) % 3, b2 ^ b);
    int touched[2] = {i, j};
    S.cleanup(touched, 2);
    S.addOrbit(a2, b, c ^ c2);
    return true;
  }
  return false;
}
// greedy reduction: any two orbits whose rotations agree in two positions -> merge. Returns true if one was applied.
static bool greedyReduce(State &S) {
  int k = S.orbits();
  for (int i = 0; i < k; i++) for (int p = 0; p < 3; p++) {
    M32 X = S.f[3 * i + p];
    int si = S.find(X); if (si < 0 || S.tab[si].cnt < 2) continue;
    const Slot &s = S.tab[si];
    M32 Y = S.f[3 * i + (p + 1) % 3];
    for (int t = 0; t < s.cnt; t++) {
      int w = s.occ[t], j = w / 3, q = w % 3; if (j == i) continue;
      if (S.f[3 * j + (q + 1) % 3] == Y) {
        // (X,Y,c)+(X,Y,c') -> (X,Y,c+c')
        int ic = 3 * i + (p + 2) % 3, jc = 3 * j + (q + 2) % 3;
        M32 nc = S.f[ic] ^ S.f[jc];
        S.setFactor(i, (p + 2) % 3, nc);
        S.setFactor(j, (q + 2) % 3, 0);
        int touched[2] = {i, j};
        S.cleanup(touched, 2);
        return true;
      }
    }
  }
  return false;
}

int main(int argc, char **argv) {
  Params P;
  for (int a = 1; a < argc; a++) {
    std::string k = argv[a]; auto v = [&]() { return std::string(argv[++a]); };
    if (k == "--n") P.n = std::stoi(v());
    else if (k == "--partition") P.partition = v();
    else if (k == "--start") P.startFile = v();
    else if (k == "--kicks") P.kicks = std::stoi(v()); // on a stall, restart this many times from the descent's best state
    else if (k == "--pool") P.poolFile = v(); // file listing C3SCHEME paths; descent d restarts from entry d mod size
    else if (k == "--L") P.L = std::stod(v());
    else if (k == "--M") P.M = std::stod(v());
    else if (k == "--seed") P.seed = std::stoull(v());
    else if (k == "--descents") P.descents = std::stol(v());
    else if (k == "--seconds") P.seconds = std::stod(v());
    else if (k == "--target") P.target = std::stoi(v());
    else if (k == "--plus-cap") P.plusCap = std::stoi(v());
    else if (k == "--save-at") P.saveAt = std::stoi(v());
    else if (k == "--out") P.outDir = v();
    else if (k == "--tag") P.tag = v();
    else if (k == "--greedy") P.greedy = true;
    else if (k == "--paper-plus") P.paperPlus = true; // Algorithm 1 as printed: plus-transition every M flips unless a new minimum resets the counter
    else if (k == "--selftest") P.selftest = true;
    else { fprintf(stderr, "unknown arg %s\n", k.c_str()); return 2; }
  }
  N = P.n; NN = N * N;
  if (N > 6) { fprintf(stderr, "n <= 6\n"); return 2; }
  buildTarget();
  std::vector<M32> orb0, fx0;
  if (!P.startFile.empty()) { if (!readScheme(P.startFile.c_str(), orb0, fx0)) { fprintf(stderr, "cannot read start\n"); return 2; } }
  else startingPoint(parsePartition(P.partition), orb0, fx0);
  State S; S.rebuildFrom(orb0, fx0);
  bool ok0 = checkState(S) && checkIndex(S);
  printf("%s START tag=%s n=%d partition=%s start=%s rank=%d orbits=%d fixed=%d valid=%d L=%.0f M=%.0f seed=%llu greedy=%d plusCap=%d paperPlus=%d\n",
         utcnow().c_str(), P.tag.c_str(), N, P.startFile.empty() ? P.partition.c_str() : "-", P.startFile.empty() ? "-" : P.startFile.c_str(),
         S.rank(), S.orbits(), (int)S.fixedT.size(), ok0, P.L, P.M, (unsigned long long)P.seed, P.greedy, P.plusCap, P.paperPlus);
  fflush(stdout);
  if (!ok0) { printf("ERROR start scheme invalid\n"); return 3; }

  if (P.selftest) {
    // random moves with full index and tensor checks after each
    Rng R(P.seed); long bad = 0, flips = 0, plus = 0;
    for (int t = 0; t < 20000; t++) {
      if (t % 50 == 49) { if (plusTransition(S, R)) plus++; } else flips += randomFlip(S, R);
      if (P.greedy) greedyReduce(S);
      if (!checkState(S) || !checkIndex(S) || S.overflow) { bad++; break; }
    }
    // a broken copy must be rejected
    State B; B.rebuildFrom(orb0, fx0); B.f[0] ^= 1; bool brokenRejected = !checkState(B);
    printf("%s SELFTEST moves=20000 flips=%ld plus=%ld failures=%ld final_rank=%d broken_copy_rejected=%d\n",
           utcnow().c_str(), flips, plus, bad, S.rank(), brokenRejected);
    return bad == 0 && brokenRejected ? 0 : 4;
  }

  Rng R(P.seed);
  double t0 = now();
  int globalBest = 1 << 30;
  std::unordered_set<uint64_t> savedHashes;
  long totalFlips = 0;
  std::vector<std::string> pool;
  if (!P.poolFile.empty()) {
    FILE *pf = fopen(P.poolFile.c_str(), "r"); char line[1024];
    while (pf && fgets(line, sizeof line, pf)) { std::string t(line); while (!t.empty() && (t.back() == '\n' || t.back() == ' ')) t.pop_back(); if (!t.empty()) pool.push_back(t); }
    if (pf) fclose(pf);
    printf("%s POOL size=%zu\n", utcnow().c_str(), pool.size());
  }
  for (long d = 0; d < P.descents && now() - t0 < P.seconds; d++) {
    if (!pool.empty()) {
      const std::string &ps = pool[d % pool.size()];
      if (!readScheme(ps.c_str(), orb0, fx0)) { printf("ERROR cannot read pool entry %s\n", ps.c_str()); return 2; }
      printf("%s POOLSTART d=%ld file=%s\n", utcnow().c_str(), d, ps.c_str());
    }
    S.rebuildFrom(orb0, fx0);
    if (!checkState(S)) { printf("ERROR start invalid\n"); return 3; }
    int best = S.rank(); std::vector<M32> bestOrb = S.f, bestFx = S.fixedT; uint64_t bestH = S.H;
    double ell = 0, since = 0; long flips = 0, plusN = 0, reductions = 0, stuck = 0, overflowEnd = 0;
    std::unordered_set<uint64_t> sampled; long samples = 0;
    double td = now();
    bool timeUp = false; int kicksUsed = 0;
    for (;;) {
      if (ell >= P.L) {
        if (kicksUsed >= P.kicks) break;
        kicksUsed++; S.rebuildFrom(bestOrb, bestFx); ell = 0; since = 0;
        printf("%s KICK tag=%s d=%ld kick=%d best=%d\n", utcnow().c_str(), P.tag.c_str(), d, kicksUsed, best); fflush(stdout);
      }
      int r0 = S.rank();
      if (!randomFlip(S, R)) { stuck = 1; break; }
      flips++; ell += 1; since += 1;
      if (S.overflow || S.orbits() > 1500) { overflowEnd = 1; break; } // index list full: end this descent cleanly
      if (P.greedy) while (greedyReduce(S)) {}
      int r1 = S.rank();
      if (r1 < r0) {
        reductions++; if (!P.paperPlus) since = 0;
        if (r1 < best) {
          best = r1; ell = 0; since = 0; bestOrb = S.f; bestFx = S.fixedT; bestH = S.H;
          if (!checkState(S)) { printf("ERROR invalid state at new best\n"); return 5; }
        }
      }
      if (since >= P.M) {
        if (S.orbits() < (best - (int)S.fixedT.size()) / 3 + P.plusCap) { if (plusTransition(S, R)) plusN++; }
        since = 0;
      }
      if ((flips & ((1L << P.sampleShift) - 1)) == 0) { samples++; if (sampled.size() < 4000000) sampled.insert(S.H); }
      if ((flips & ((1L << 20) - 1)) == 0) {
        if (!checkState(S)) { printf("ERROR invalid state at periodic check overflow=%d\n", S.overflow); return 5; }
        if ((flips & ((1L << 26) - 1)) == 0)
          printf("%s PROGRESS tag=%s d=%ld flips=%ld rank=%d best=%d plus=%ld reductions=%ld\n", utcnow().c_str(), P.tag.c_str(), d, flips, S.rank(), best, plusN, reductions), fflush(stdout);
        if (now() - t0 >= P.seconds) { timeUp = true; break; }
      }
    }
    totalFlips += flips;
    // verify and save the best state of this descent
    State B; B.rebuildFrom(bestOrb, bestFx);
    bool valid = checkState(B);
    char fname[512] = "";
    bool isNew = savedHashes.insert(bestH).second;
    if (valid && best <= P.saveAt && isNew) {
      snprintf(fname, sizeof fname, "%s/%s-r%d-%016llx.c3", P.outDir.c_str(), P.tag.c_str(), best, (unsigned long long)bestH);
      writeScheme(fname, B);
    }
    if (best < globalBest) globalBest = best;
    printf("%s DESCENT tag=%s d=%ld best=%d orbits=%d fixed=%d valid=%d flips=%ld plus=%ld reductions=%ld kicks=%d stuck=%ld overflow=%ld timeup=%d secs=%.1f sampled=%ld distinct_sampled=%zu best_hash=%016llx new_best_scheme=%d saved=%s global_best=%d\n",
           utcnow().c_str(), P.tag.c_str(), d, best, (best - (int)bestFx.size()) / 3, (int)bestFx.size(), valid, flips, plusN, reductions, kicksUsed, stuck, overflowEnd,
           (int)timeUp, now() - td, samples, sampled.size(), (unsigned long long)bestH, (int)isNew, fname[0] ? fname : "-", globalBest);
    fflush(stdout);
    if (!valid) return 5;
    if (P.target && best <= P.target) printf("%s TARGET_REACHED rank=%d\n", utcnow().c_str(), best);
  }
  printf("%s FINISH tag=%s total_flips=%ld secs=%.1f global_best=%d distinct_best_schemes=%zu\n", utcnow().c_str(), P.tag.c_str(),
         totalFlips, now() - t0, globalBest, savedHashes.size());
  return 0;
}
