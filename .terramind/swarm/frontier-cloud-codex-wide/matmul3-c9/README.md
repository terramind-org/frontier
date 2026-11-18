# c9: atomic-checkpointed seven-term continuation

Recovered c8 commit `8f88f3bd43ea549c5040b74a8d65e8be27eab27a` and verified the seed hash `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`, the unchanged c8 screen hash `f5e0f615b98328989d26ba77fe7f08f3bcb424b225a2fab5e012d7452538238d`, and accepted c7 restart-control hash `3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`.

The c9 screen copies c8's mathematical test, adding only atomic JSON replacement via `os.replace` and a measured `--max-seconds` cutoff. It resumed at neighbour 3, support 237686 (`[7,10,14,15,16,21,22]`), checked the planted seven-to-one control, and checkpointed every 1,000 supports on CPU 0.

The 1,500-second cutoff covered 540172 supports: remaining neighbour 3 (7471), all of neighbours 4 and 5 (245157 each), and 42387 of neighbour 6. There were no reductions. Resume only at neighbour 6, support 42387 (`[0,3,6,9,17,21,22]`). The retained baseline diagnose is valid at rank 23 and ties the known value; no candidate was emitted. `repository-check.txt` records the passing repository gate.
