# global-improve

练习过程中，总结需求总结一些模版。最终归并到 _global-lc 等总模版文件中。

## 类型





## Tuple

支持定义不同类型的元组，支持以下一些性质：

1. 大多C++版本支持
2. 支持 2 ～ 4 维，最好合并成一个类，也允许拆开成若干个类型简化语法复杂度
3. 支持排序：可以无缝河 STL 中的相关类集成
4. 支持深拷贝

```c++
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

**demo**

```cpp
// tuple_test.cpp - 极简 Tuple2/3/4 实现与测试
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>


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

// === 测试代码 ===
int main() {
    std::cout << "=== Tuple2 测试 ===\n";
    // Tuple2: 二维点
    std::vector<Tuple2<int, int>> pts = {
        {3, 5}, {1, 2}, {3, 1}, {2, 8}
    };
    std::sort(pts.begin(), pts.end());
    std::cout << "排序后: ";
    for (auto& p : pts)
        std::cout << "(" << p.a << "," << p.b << ") ";
    std::cout << "\n";

    std::cout << "\n=== Tuple3 测试 ===\n";
    // Tuple3: (年龄, 分数, ID)
    std::vector<Tuple3<int, double, std::string>> students;
    students.push_back({20, 85.5, "Alice"});
    students.push_back({19, 90.0, "Bob"});
    students.push_back({20, 80.0, "Charlie"});
    students.push_back({19, 85.5, "David"});

    std::sort(students.begin(), students.end());
    std::cout << "排序后:\n";
    for (auto& s : students)
        std::cout << "年龄:" << s.a << " 分数:" << s.b << " ID:" << s.c << "\n";

    std::cout << "\n=== Tuple4 测试 ===\n";
    // Tuple4: 自定义数据
    std::vector<Tuple4<int, int, int, int>> data = {
        {1, 2, 3, 4},
        {1, 2, 2, 9},
        {2, 1, 1, 1},
        {1, 2, 3, 3}
    };
    std::sort(data.begin(), data.end());
    std::cout << "排序后: ";
    for (auto& d : data) {
        std::cout << "(" << d.a << "," << d.b << "," << d.c << "," << d.d << ") ";
    }
    std::cout << "\n";

    std::cout << "\n=== 深拷贝测试 ===\n";
    Tuple2<int, std::string> original(42, "Hello");
    Tuple2<int, std::string> copy = original;  // 深拷贝
    copy.b = "World";
    std::cout << "原始: (" << original.a << "," << original.b << ")\n";
    std::cout << "拷贝: (" << copy.a << "," << copy.b << ")\n";

    std::cout << "\n=== 比较操作测试 ===\n";
    Tuple2<int, int> t1(1, 2), t2(1, 3), t3(1, 2);
    std::cout << "t1 < t2: " << (t1 < t2) << "\n";  // 1 (true)
    std::cout << "t1 == t3: " << (t1 == t3) << "\n"; // 1 (true)
    std::cout << "t1 != t2: " << (t1 != t2) << "\n"; // 1 (true)

    return 0;
}
```

