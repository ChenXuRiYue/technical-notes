# Global-leetcode

Leetcode 的通用模版

```c++
// 常用 STL
#include <iostream>
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <string>
#include <vector>
#include <list>
#include <set>
#include <map>
#include <queue>
#include <stack>
#include <deque>
#include <cmath>
#include <climits>
#include <cfloat>
#include <unordered_set>
#include <unordered_map>

// 常用宏和语法支持
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <sstream>

// 类型别名
typedef long long ll;
typedef unsigned long long ull;
typedef pair<int, int> pii;
typedef pair<long long, long long> pll;

// 常用宏
#define pb push_back
#define mp make_pair
#define fi first
#define se second
#define all(x) (x).begin(), (x).end()
#define sz(x) ((int)(x).size())
#define rep(i, a, b) for (int i = a; i < b; ++i)
#define per(i, a, b) for (int i = b - 1; i >= a; --i)

// Tuple
#include <tuple>  // 仅用于 std::tie（做字典序比较）
// === 极简 Tuple 实现 ===
template<class A, class B>
struct Tuple2 {
    A a; B b;
    Tuple2(A a_ = A(), B b_ = B()) : a(a_), b(b_) {}
    bool operator<(const Tuple2& x) const { return std::tie(a, b) < std::tie(x.a, x.b); }
    bool operator==(const Tuple2& x) const { return a == x.a && b == x.b; }
    bool operator!=(const Tuple2& x) const { return !(*this == x); }
    bool operator>(const Tuple2& x) const { return x < *this; }
    bool operator<=(const Tuple2& x) const { return !(*this > x); }
    bool operator>=(const Tuple2& x) const { return !(*this < x); }
};

template<class A, class B, class C>
struct Tuple3 {
    A a; B b; C c;
    Tuple3(A a_ = A(), B b_ = B(), C c_ = C()) : a(a_), b(b_), c(c_) {}
    bool operator<(const Tuple3& x) const { return std::tie(a, b, c) < std::tie(x.a, x.b, x.c); }
    bool operator==(const Tuple3& x) const { return a == x.a && b == x.b && c == x.c; }
    bool operator!=(const Tuple3& x) const { return !(*this == x); }
    bool operator>(const Tuple3& x) const { return x < *this; }
    bool operator<=(const Tuple3& x) const { return !(*this > x); }
    bool operator>=(const Tuple3& x) const { return !(*this < x); }
};

template<class A, class B, class C, class D>
struct Tuple4 {
    A a; B b; C c; D d;
    Tuple4(A a_ = A(), B b_ = B(), C c_ = C(), D d_ = D()) : a(a_), b(b_), c(c_), d(d_) {}
    bool operator<(const Tuple4& x) const { return std::tie(a, b, c, d) < std::tie(x.a, x.b, x.c, x.d); }
    bool operator==(const Tuple4& x) const { return a == x.a && b == x.b && c == x.c && d == x.d; }
    bool operator!=(const Tuple4& x) const { return !(*this == x); }
    bool operator>(const Tuple4& x) const { return x < *this; }
    bool operator<=(const Tuple4& x) const { return !(*this > x); }
    bool operator>=(const Tuple4& x) const { return !(*this < x); }
};

```

