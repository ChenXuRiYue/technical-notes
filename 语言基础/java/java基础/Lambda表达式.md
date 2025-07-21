# Lambda 表达式

## 概述以及历史

初次接触 Lamba表达式 是C++ 。

1. **理论奠基（1930年代）**：阿隆佐·丘奇的 Lambda 演算提出匿名函数概念，与图灵机共同奠定计算理论基础，标志着函数式思想的起源。
2. **实践开端（1958年）**：Lisp 将 Lambda 引入编程，使函数成为一等公民，开创函数式编程先河，影响深远。
3. **理念深化（1970-1990年代）**：ML、Haskell 等语言发展出纯函数、不可变性等核心特性，推动函数式编程成为独立范式。
4. **主流融合（2000-2010年代）**：Python、C#、Java（2014年 Java 8）等语言引入 Lambda，标志着函数式思想融入主流，提升代码简洁性和并发能力。
5. **现代意义（至今）**：Lambda 表达式驱动大数据、响应式编程等领域的革新，成为现代软件开发的关键技术。

**历史意义**：从数学理论到编程实践，Lambda 思想推动了计算模型的建立、编程范式的演进，并在多核时代赋予语言新的生命力，深刻改变了软件开发的表达方式和效率。

## 基础语法

```java
(参数列表)->{
    
}

(参数列表) -> 单语句;
```

## 典例、使用优化

---

### 1. 集合排序（Comparator）
**场景**：对列表按自定义规则排序。
**传统方式**：
```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
        Collections.sort(names, new Comparator<String>() {
            @Override
            public int compare(String a, String b) {
                return a.length() - b.length(); // 按长度排序
            }
        });
        System.out.println(names); // 输出 [Bob, Alice, Charlie]
    }
}
```
**Lambda 方式**：
```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(Arrays.asList("Alice", "Bob", "Charlie"));
        Collections.sort(names, (a, b) -> a.length() - b.length());
        System.out.println(names); // 输出 [Bob, Alice, Charlie]
    }
}
```
- **优点**：
  - **简洁性**：从 8 行减少到 1 行，消除了匿名类的冗余。
  - **灵活性**：只需改动 `(a, b) ->` 后的逻辑即可快速调整排序规则。
- **历史意义**：这是 Java 8 中 Lambda 的典型应用，取代了繁琐的 Comparator 实现。

---

### 2. 集合操作（Stream API）
**场景**：从列表中筛选并转换数据。
**传统方式**：
```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        List<Integer> result = new ArrayList<>();
        for (int n : numbers) {
            if (n % 2 == 0) { // 筛选偶数
                result.add(n * 2); // 乘以 2
            }
        }
        System.out.println(result); // 输出 [4, 8]
    }
}
```
**Lambda 方式**：
```java
import java.util.*;
import java.util.stream.*;

public class Main {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        List<Integer> result = numbers.stream()
            .filter(n -> n % 2 == 0)  // 筛选偶数
            .map(n -> n * 2)         // 乘以 2
            .collect(Collectors.toList());
        System.out.println(result); // 输出 [4, 8]
    }
}
```
- **优点**：
  - **声明式编程**：描述“做什么”（筛选偶数、乘以 2），而不是“怎么做”（循环）。
  - **简洁性**：逻辑清晰，代码更紧凑。
  - **灵活性**：通过替换 Lambda，可以轻松调整筛选或转换规则。
- **应用场景**：大数据处理（如 Spark）中广泛使用类似模式。

---

### 3. 事件监听（Swing 或 JavaFX）
**场景**：为按钮添加点击事件。
**传统方式**：
```java
import javax.swing.*;

public class Main {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Demo");
        JButton button = new JButton("Click me");
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("Button clicked!");
            }
        });
        frame.add(button);
        frame.setSize(200, 200);
        frame.setVisible(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }
}
```
**Lambda 方式**：
```java
import javax.swing.*;

public class Main {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Demo");
        JButton button = new JButton("Click me");
        button.addActionListener(e -> System.out.println("Button clicked!"));
        frame.add(button);
        frame.setSize(200, 200);
        frame.setVisible(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }
}
```
- **优点**：
  - **简洁性**：从多行样板代码缩减为一行。
  - **可读性**：事件处理逻辑一目了然。
- **历史意义**：这是 Lambda 在 GUI 编程中的经典用法，简化了事件驱动模型。

---

### 4. 线程创建（Runnable）
**场景**：启动一个新线程。
**传统方式**：
```java
public class Main {
    public static void main(String[] args) {
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("Thread running!");
            }
        });
        thread.start();
    }
}
```
**Lambda 方式**：
```java
public class Main {
    public static void main(String[] args) {
        Thread thread = new Thread(() -> System.out.println("Thread running!"));
        thread.start();
    }
}
```
- **优点**：
  - **简洁性**：去掉冗长的匿名类，直接聚焦线程逻辑。
  - **灵活性**：可快速修改线程任务。
- **应用场景**：并发编程中常用，体现了 Lambda 对多线程的支持。

---

### 5. 函数组合（Function 接口）
**场景**：将多个操作组合成一个流程。
**代码**：
```java
import java.util.function.*;

public class Main {
    public static void main(String[] args) {
        Function<Integer, Integer> addOne = x -> x + 1;
        Function<Integer, Integer> doubleIt = x -> x * 2;

        // 组合：先加 1，再乘以 2
        Function<Integer, Integer> addThenDouble = addOne.andThen(doubleIt);

        System.out.println(addThenDouble.apply(3)); // 输出 8（(3 + 1) * 2）
    }
}
```
- **优点**：
  - **行为参数化**：通过 Lambda 定义独立的操作，再灵活组合。
  - **函数式思维**：体现了函数式编程中函数组合的优雅。
- **历史意义**：类似 Lisp 中函数组合的思想，展示了 Lambda 的数学根源。

---

### 总结：Lambda 的优点体现
1. **简洁性**：减少样板代码（如匿名类），让代码更紧凑。
2. **灵活性**：通过参数化行为，轻松调整逻辑。
3. **声明式**：关注结果而非过程，提升可读性。
4. **函数式特性**：支持高阶函数、组合等现代编程范式。

这些例子覆盖了排序、集合操作、事件处理、并发和函数组合等经典场景，充分展示了 Lambda 在 Java 中的实用价值。如果你想深入某个例子或尝试改写，我可以进一步协助！