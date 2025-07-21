# Java 网络编程

## 原生语法体系

Java 原生提供了丰富的 **网络编程 API**，主要集中在 `java.net` 包中，支持 **TCP、UDP、HTTP** 等协议。以下是 Java 网络编程的核心语法：

### 1. **Socket 编程（TCP）**
TCP 是一种 **面向连接** 的协议，适用于可靠的数据传输：
```java
// 客户端
Socket socket = new Socket("127.0.0.1", 8080);
OutputStream output = socket.getOutputStream();
output.write("Hello Server".getBytes());
socket.close();

// 服务器端
ServerSocket serverSocket = new ServerSocket(8080);
Socket clientSocket = serverSocket.accept();
InputStream input = clientSocket.getInputStream();
byte[] buffer = new byte[1024];
input.read(buffer);
System.out.println(new String(buffer));
serverSocket.close();
```
👉 **`Socket`** 代表客户端连接，**`ServerSocket`** 监听端口并接受连接。

### 2. **DatagramSocket（UDP）**
UDP 是 **无连接** 的协议，适用于实时通信：
```java
// 发送端
DatagramSocket socket = new DatagramSocket();
byte[] data = "Hello UDP".getBytes();
DatagramPacket packet = new DatagramPacket(data, data.length, InetAddress.getByName("127.0.0.1"), 9090);
socket.send(packet);
socket.close();

// 接收端
DatagramSocket serverSocket = new DatagramSocket(9090);
byte[] buffer = new byte[1024];
DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
serverSocket.receive(receivePacket);
System.out.println(new String(receivePacket.getData()));
serverSocket.close();
```
👉 **`DatagramSocket`** 适用于 **视频流、在线游戏** 等场景。

### 3. **URL 处理（HTTP）**
Java 提供了 `URL` 类用于访问 Web 资源：
```java
URL url = new URL("https://www.example.com");
HttpURLConnection connection = (HttpURLConnection) url.openConnection();
connection.setRequestMethod("GET");
InputStream response = connection.getInputStream();
BufferedReader reader = new BufferedReader(new InputStreamReader(response));
String line;
while ((line = reader.readLine()) != null) {
    System.out.println(line);
}
reader.close();
```
👉 **`HttpURLConnection`** 适用于 **REST API 调用**。

### 4. **NIO（非阻塞 IO）**
Java NIO 提供了 **高性能网络编程**：
```java
Selector selector = Selector.open();
ServerSocketChannel serverChannel = ServerSocketChannel.open();
serverChannel.configureBlocking(false);
serverChannel.bind(new InetSocketAddress(8080));
serverChannel.register(selector, SelectionKey.OP_ACCEPT);
```
👉 **`Selector`** 允许 **单线程管理多个连接**，适用于 **高并发服务器**。



## Servlet

Servlet 是 Java EE（Jakarta EE）中的一个关键组件，专门用于处理 **HTTP 请求和响应**，使得 Java Web 应用能够动态生成网页内容。它运行在 **Servlet 容器**（如 Tomcat、Jetty）中，负责管理 Servlet 的生命周期，并与 Web 服务器协作。

### Servlet 的背景知识：
1. **Servlet 的起源**
   - Servlet 诞生于 **Java EE 规范**，用于替代传统的 **CGI（Common Gateway Interface）**，提高 Web 应用的性能。
   - 相比 CGI，Servlet **不需要为每个请求创建新进程**，而是采用 **多线程** 方式处理请求，提高了效率。

2. **Servlet 的核心功能**
   - **处理 HTTP 请求**（如 GET、POST）。
   - **与数据库交互**，动态生成网页内容。
   - **管理会话**（Session），支持用户身份识别。
   - **与 Web 服务器协作**，提供动态 Web 服务。

3. **Servlet 的生命周期**
   - **初始化（`init()`）**：Servlet 容器加载 Servlet 时调用。
   - **请求处理（`service()`）**：每次请求都会调用 `service()` 方法，通常会调用 `doGet()` 或 `doPost()`。
   - **销毁（`destroy()`）**：Servlet 容器关闭时调用，用于释放资源。

4. **Servlet 与 Spring MVC**
   - Spring MVC 依赖 **Servlet 规范**，其中 **DispatcherServlet** 继承自 `HttpServlet`，用于处理 Web 请求。
   - Spring MVC 通过 **HandlerMapping** 解析请求路径，找到对应的 **HandlerMethod**，最终调用 Controller 方法。



### Tomcat 

Tomcat 是一个 **开源的 Java Web 服务器和 Servlet 容器**，主要用于运行 Java Web 应用。它由 **Apache 软件基金会** 维护，支持 **Servlet、JSP** 等 Java EE 规范。

#### **Tomcat 的作用**
1. **处理 HTTP 请求**：Tomcat 充当 Web 服务器，监听 HTTP 端口（默认 8080），接收浏览器请求并返回响应。
2. **运行 Servlet 和 JSP**：它是一个 **Servlet 容器**，可以执行 Java Web 应用中的 Servlet 和 JSP 代码。
3. **支持 Spring MVC**：在 Spring MVC 处理 HTTP 请求时，Tomcat 负责解析请求数据，并找到对应的 **HandlerMethod**。
4. **轻量级、易部署**：相比 WebLogic、JBoss，Tomcat 更轻量级，适用于中小型 Web 应用。

#### **Tomcat 在 Spring MVC 中的作用**
在 Spring MVC 处理 HTTP 请求的过程中，Tomcat 负责：
- **解析 HTTP 请求**，并交给 `HttpServlet` 处理。
- **通过 `HandlerMapping` 找到对应的 `HandlerMethod`**，然后执行 Controller 方法。
- **管理请求生命周期**，包括拦截器、参数解析、异常处理等。

#### **Tomcat 的核心组件**
1. **Connector**：处理 HTTP 连接，解析请求数据。
2. **Container（容器）**：
   - **Engine**：管理多个虚拟主机（Host）。
   - **Host**：代表一个 Web 应用的运行环境。
   - **Context**：对应一个具体的 Web 应用。
   - **Wrapper**：封装具体的 Servlet。

#### **为什么选择 Tomcat？**
- **免费开源**，由 Apache 维护，企业和个人开发者都可以使用。
- **支持 Java EE 规范**，可以运行 Servlet、JSP、Spring MVC 应用。
- **轻量级**，适用于开发和生产环境，易于部署和管理
