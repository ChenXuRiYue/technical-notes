# 树状数组

## C++

**模版**

```c++
using ll = long long;
class BIT {
public:
    vector<ll> c;
    int n;

    BIT(int n) {
        c = vector<ll>(n + 10, 0);
        this->n = n + 1;
    }
    
    ll query(int x) {
        ll res = 0;
        for (; x ; x -= x & (-x))
            res += c[x];
        return res;
    }
    void modify(int x, ll d) {
        assert(x != 0);
        for (; x <= n; x += x & (-x)) {
            c[x] += d;
        }
    }
};
```
**说明**

```C++
BIT bit = BIT(n);
bit.query(x);
bit.modify(x, -1);
```

