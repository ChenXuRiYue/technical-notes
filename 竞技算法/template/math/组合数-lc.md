# 组合数



```C++
int init_flag;
const int N_c = 3E3;
const int mod = 1E9 + 7;
int c[N_c][N_c];
void C_init() {
    for (int i = 1; i < N_c; ++i) {
        c[i][0] = c[i][i] = 1;
        for (int j = 1; j < i; ++j) {
            c[i][j] = (c[i - 1][j] + c[i - 1][j - 1]) % mod;
        }
    }
}

void init() {
  if(init_flag) return;
  init_flag = true;
  C_init();
}
```

