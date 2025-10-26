# Battery History Viewer

设备电量历史查询系统

## 简介

Battery History Viewer 是一个基于Web的设备电量监控系统，用于查询和可视化设备的电池电量历史数据。系统采用前后端分离架构，前端使用HTML/CSS/JavaScript + Chart.js，后端使用Python Flask框架。

## 功能特性

- 📊 实时电量历史数据可视化
- 🔍 按设备和日期查询历史记录
- 📱 响应式设计，支持移动端访问
- 🎨 美观的图表展示
- ⚡ 高效的数据查询和渲染

## 技术栈

### 前端技术
- HTML5 + CSS3
- JavaScript (ES6+)
- Chart.js 4.4.0 - 数据可视化库
- 响应式设计

### 后端技术
- Python 3.x
- Flask - Web框架
- MySQL - 数据库存储
- RESTful API

## 系统架构

```
battery/
├── app.py              # Flask主应用
├── templates/
│   └── view.html       # 前端页面
└── requirements.txt    # 依赖包
```

## 使用说明

### 前端界面

1. **设备查询**：
   - 输入8位设备名（字母和数字组合，至少包含一个字母和数字）
   - 选择查询日期
   - 点击"查询"按钮

2. **图表展示**：
   - 实时显示电量变化趋势
   - Y轴默认范围：可选动态范围
   - 显示最新数据时间和电量百分比
   - 显示查询结果总数

### 数据验证

- 设备名必须为8位字符
- 必须包含至少一个字母和一个数字
- 日期为必选项

## API接口

### 获取电量历史数据
```
GET /api/data?table=<device_name>&date=<query_date>
```

响应格式：
```json
{
  "data": [
    {"time": "08:30", "battery": 95},
    {"time": "09:00", "battery": 94},
    ...
  ],
  "min_battery": 70,
  "max_battery": 100
}
```

## 部署说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 访问地址：`http://localhost:5000`

