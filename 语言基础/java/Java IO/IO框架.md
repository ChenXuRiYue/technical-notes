# IO 框架

Java 的 I/O（输入/输出）框架是 Java 标准库中用于处理输入和输出操作的一组类和接口。它提供了丰富的功能，用于读取和写入文件、网络通信、内存数据处理等。Java 的 I/O 框架主要分为以下几类：

### 1\. 传统的 I/O 框架（基于阻塞 I/O）
传统的 Java I/O 是基于阻塞 I/O 的，主要包含在 `java.io` 包中。它提供了文件和数据流的读写操作，以及字符和字节的处理。

#### 1.1 字节流
- **输入流**：`InputStream` 是所有字节输入流的父类，例如 `FileInputStream` 用于从文件读取字节。
- **输出流**：`OutputStream` 是所有字节输出流的父类，例如 `FileOutputStream` 用于向文件写入字节。

#### 1.2 字符流
- **输入流**：`Reader` 是所有字符输入流的父类，例如 `FileReader` 用于从文件读取字符。
- **输出流**：`Writer` 是所有字符输出流的父类，例如 `FileWriter` 用于向文件写入字符。

#### 1.3 示例代码
```java
import java.io.*;

public class TraditionalIOExample {
    public static void main(String[] args) {
        // 字节流：从文件读取字节
        try (FileInputStream fis = new FileInputStream("input.txt");
             FileOutputStream fos = new FileOutputStream("output.txt")) {
            int byteRead;
            while ((byteRead = fis.read()) != -1) {
                fos.write(byteRead);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        // 字符流：从文件读取字符
        try (FileReader fr = new FileReader("input.txt");
             FileWriter fw = new FileWriter("output.txt")) {
            int charRead;
            while ((charRead = fr.read()) != -1) {
                fw.write(charRead);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 2\. NIO（New I/O）框架（基于非阻塞 I/O）
Java NIO 是 Java 1.4 引入的非阻塞 I/O 框架，主要包含在 `java.nio` 包中。它提供了更高效的 I/O 操作，支持多路复用和内存映射文件 I/O。

#### 2.1 核心组件
- **缓冲区（Buffer）**：用于存储数据的容器，例如 `ByteBuffer`、`CharBuffer` 等。
- **通道（Channel）**：用于读写数据的通道，例如 `FileChannel`、`DatagramChannel` 等。
- **选择器（Selector）**：用于多路复用 I/O 操作，可以同时管理多个通道。

#### 2.2 示例代码
```java
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class NIOExample {
    public static void main(String[] args) {
        try (FileChannel inChannel = FileChannel.open(Paths.get("input.txt"), StandardOpenOption.READ);
             FileChannel outChannel = FileChannel.open(Paths.get("output.txt"), StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            while (inChannel.read(buffer) != -1) {
                buffer.flip();
                outChannel.write(buffer);
                buffer.clear();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 3\. NIO.2（Java 7 引入的文件系统增强）
Java 7 引入了 NIO.2，进一步增强了文件系统的操作能力，主要包含在 `java.nio.file` 包中。

#### 3.1 核心组件
- **`Path`**：表示文件路径。
- **`Paths`**：用于创建 `Path` 对象。
- **`Files`**：提供了一系列静态方法，用于文件和目录的操作。

#### 3.2 示例代码
```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class NIO2Example {
    public static void main(String[] args) {
        Path sourcePath = Paths.get("input.txt");
        Path targetPath = Paths.get("output.txt");

        try {
            // 复制文件
            Files.copy(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING);
            // 读取文件内容
            String content = new String(Files.readAllBytes(sourcePath));
            System.out.println(content);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 4\. Java I/O 框架的总结
- **传统 I/O**：基于阻塞 I/O，适合简单的文件读写操作
- **NIO**：基于非阻塞 I/O，适合高性能的 I/O 操作，如网络编程和内存映射文件
- **NIO.2**：提供了更强大的文件系统操作能力，适合复杂的文件管理任务
