# 常用 Demo

## 学校背景

学校、班级、学生三表，查学生的平均成绩

```mysql
-- 创建学校表
CREATE TABLE schools (
    school_id INT AUTO_INCREMENT PRIMARY KEY,
    school_name VARCHAR(255) NOT NULL UNIQUE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_school_name (school_name)
);

-- 创建班级表
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL,
    school_id INT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (school_id, class_name),
    INDEX idx_school_id (school_id),
    INDEX idx_class_name (class_name)
);

-- 创建学生表
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    class_id INT NOT NULL,
    score DECIMAL(5, 2) NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON UPDATE CASCADE ON DELETE CASCADE, -- 修改为 ON DELETE CASCADE
    INDEX idx_class_id (class_id),
    INDEX idx_score (score)
);
```



**捏造一些数据：**

```mysql
-- 插入学校数据
INSERT INTO schools (school_name) VALUES 
('阳光中学'),
('育才中学'),
('光明中学');

-- 插入班级数据
INSERT INTO classes (class_name, school_id) VALUES 
('初一（1）班', 1),
('初一（2）班', 1),
('高一（1）班', 2),
('高二（2）班', 2),
('初三（1）班', 3);

-- 插入学生数据
INSERT INTO students (student_name, class_id, score) VALUES 
('李华', 1, 88.50),
('张明', 1, 92.00),
('王丽', 2, 76.80),
('赵刚', 2, 80.20),
('陈红', 3, 95.00),
('孙磊', 3, 87.30),
('周芳', 4, 79.60),
('吴俊', 4, 83.90),
('郑强', 5, 91.10),
('王敏', 5, 84.70);
```

### 更新数据

```mysql
UPDATE schools
SET school_name = '新阳光中学'
WHERE school_name = '阳光中学';
```



### 删除数据

```mysql
DELETE FROM schools
WHERE school_name = '光明中学';
```



### 为表添加字段

为班级添加班级口号：

```sql
ALTER TABLE classes
ADD COLUMN slogan VARCHAR(500) DEFAULT NULL COMMENT '班级口号';
```

同时加多个字段

```sql
ALTER TABLE classes
ADD COLUMN slogan VARCHAR(500) DEFAULT NULL COMMENT '班级口号',
ADD COLUMN homeroom_teacher VARCHAR(100) DEFAULT NULL COMMENT '班主任姓名';
```

### 删除表中的字段

```mysql
ALTER TABLE classes
DROP COLUMN slogan,
DROP COLUMN homeroom_teacher;
```

### 为表新增索引

```mysql
-- 示例：为已有表添加索引

-- 1. 为主键字段添加唯一索引（虽然冗余，但若用于演示语法，可注明）
-- 注意：实际中主键已隐式创建唯一索引，此操作通常不必要
ALTER TABLE schools 
ADD UNIQUE INDEX uidx_school_id (school_id);  -- 仅作语法示例

-- 2. 为包含 score 字段的表添加普通索引（修正表名）
ALTER TABLE students 
ADD INDEX idx_score (score);
```



### 为表修改字段

```mysql
示例 1：将 school_name 的长度从 255 改为 128，并添加注释
ALTER TABLE schools
MODIFY COLUMN school_name VARCHAR(128) NOT NULL UNIQUE COMMENT '学校名称';

示例 2：为 create_time 添加注释
ALTER TABLE schools
MODIFY COLUMN create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
```

