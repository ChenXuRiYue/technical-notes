



# Go Test

## 概述  
`go test` 是 Go 内置的测试工具，用于运行单元测试和基准测试，确保代码质量。核心目标：快速验证功能，保持可靠性。

## 工作流  
1. **编写测试文件**  
   - 文件名以 `_test.go` 结尾，放在与被测代码相同的包中。  
   - 测试函数以 `Test` 开头（如 `TestFunc`），参数为 `*testing.T`。  
2. **运行测试**  
   - 命令：`go test`（当前包）或 `go test ./...`（所有包）。  
   - 输出：成功显示 `PASS`，失败显示错误详情。  
3. **可选参数**  
   - `-v`：详细输出。  
   - `-run`：运行特定测试（如 `go test -run TestFunc`）。  

## Demo  
假设有 `math.go`：  
```go
package math

func Add(a, b int) int {
    return a + b
}
```

对应测试文件 `math_test.go`：  
```go
package math

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}
```

运行：  
```bash
go test
```
输出：`ok   math    0.002s`（成功）。

---

**核心点**：  
- 测试文件命名和函数签名是关键。  
- `t.Errorf` 报告失败，简洁直观。  
- `go test` 集成度高，无需额外工具。