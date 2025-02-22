# JVM - GC

解决学习过程中，重复遇到的困惑

## 1. 关于 GC Root

### 1.1 GC Root 的定义
GC Root 是垃圾回收的起点，用于可达性分析，判断对象是否存活。任何从 GC Root 可达的对象不会被回收。

### 1.2 常见的 GC Root 类型
1. **虚拟机栈的局部变量**  
   - 方法栈帧中局部变量引用的对象。  
   - 样例：`Object obj = new Object();` 方法执行时，`obj` 是 GC Root。
2. **方法区的静态变量**  
   - 类中 `static` 变量引用的对象。  
   - 样例：`static Object staticObj = new Object();` 类未卸载时，`staticObj` 是 GC Root。
3. **方法区的常量**  
   - 常量池中引用的对象，如字符串常量。  
   - 样例：`String s = "hello";` 常量池中的 `"hello"` 可能是 GC Root。
4. **本地方法栈的 JNI 引用**  
   - 本地方法（JNI）中引用的 Java 对象。  
   - 样例：C 代码调用 Java 对象，对象被标记为 GC Root。
5. **活跃线程**  
   - 运行中线程及其栈中的引用。  
   - 样例：主线程中 `Thread t = new Thread();`，`t` 是 GC Root。
6. **类加载器及其他元数据**  
   - 类加载器（如自定义 ClassLoader）或 `Class` 对象。  
   - 样例：`ClassLoader cl = new CustomClassLoader();`，`cl` 可能是 GC Root。

### 1.3 GC Root 是否永远不会被回收？
- **纠正与补充**：  
  - GC Root 本身是引用位置，不是对象，其“回收”指失去 GC Root 身份。GC Root 引用的对象若失去所有引用，走普通回收流程。
  - GC Root 身份是相对的，与生命周期相关：
    - 临时性：如局部变量，随方法结束失去 GC Root 身份。
    - 持久性：如静态变量，除非置空或类卸载，否则一直是 GC Root。
  - 在三色标记算法中：
    - GC Root 初始为灰色，扫描后变黑色（存活）。
    - 失去 GC Root 身份的对象若不可达，标记为白色（回收）。

- **样例**：
  ```java
  class Test {
      static Object staticObj = new Object(); // 持久 GC Root
      void method() {
          Object localObj = new Object(); // 临时 GC Root
          localObj = null; // 失去 GC Root 身份，可能变白色
      }
  }
  ```
  - `staticObj`：除非置空或类卸载，一直是黑色。
  - `localObj`：方法结束或置空后，若无其他引用，变白色被回收。

### 1.4 GC Root 与普通对象的回收区别
- **相同点**：  
  - 回收机制一致：基于可达性分析和 GC 算法（如标记-清除）。
  - 样例：`Object o = new Object(); o = null;` 若无引用，和普通对象一样回收。
- **不同点**：  
  - GC Root 是存活起点，其身份由上下文决定；普通对象依赖引用。
  - 样例：`static List<Object> list = new ArrayList<>();` 置空前，`list` 保护对象不被回收。

---

### 备注
- **概念说明**：
  - **可达性分析**：从 GC Root 遍历引用链，标记存活对象。
  - **三色标记**：白色（未访问/垃圾）、灰色（待扫描）、黑色（存活）。
- **体系完善**：涵盖定义、类型、生命周期、回收机制，逻辑清晰。
- **精简性**：每点直击核心，避免冗长描述。

如果有其他需求，可以进一步调整！