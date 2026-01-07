# 前端项目启动指南

## 📋 项目结构

```
frontend/
├── index.html                     # HTML入口
├── package.json                   # 依赖配置
├── vite.config.ts                # Vite配置
├── tsconfig.json                 # TypeScript配置
├── tsconfig.node.json            # Node TypeScript配置
├── .gitignore                    # Git忽略
│
└── src/
    ├── main.ts                   # Vue应用入口
    ├── App.vue                   # 主应用文件（导航 + 布局）
    │
    ├── api/
    │   └── client.ts             # API客户端
    │
    ├── stores/
    │   └── useDataStore.ts       # Pinia数据存储
    │
    ├── router/
    │   └── index.ts              # Vue Router配置
    │
    ├── pages/
    │   ├── Dashboard.vue         # 仪表板首页
    │   ├── Trends.vue            # 趋势分析页面
    │   ├── Users.vue             # 用户分析页面
    │   ├── Content.vue           # 内容分析页面
    │   └── DataTable.vue         # 数据表页面
    │
    └── styles/
        └── theme.css             # 暗色科技主题样式
```

## 🚀 快速启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

或使用yarn:
```bash
yarn install
```

### 2. 启动开发服务器

```bash
npm run dev
```

输出应该显示：
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### 3. 访问应用

在浏览器中打开：http://localhost:5173

## 📦 依赖说明

| 包 | 版本 | 用途 |
|---|------|------|
| vue | ^3.3.4 | 前端框架 |
| axios | ^1.6.0 | HTTP客户端 |
| pinia | ^2.1.6 | 状态管理 |
| element-plus | ^2.4.2 | UI组件库 |
| echarts | ^5.4.3 | 图表库 |
| vite | ^5.0.0 | 构建工具 |
| typescript | ^5.2.2 | 类型系统 |
| vue-tsc | ^1.8.19 | Vue类型检查 |

## 🛠️ 可用的npm命令

```bash
# 开发模式（热更新）
npm run dev

# 类型检查
npm run type-check

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

## 🎨 应用特性

### 暗色科技主题
- 深蓝色背景 (#0a0e27)
- 霓虹青色强调 (#00d4ff)
- 平滑过渡动画
- 响应式设计

### 完整的页面
- **Dashboard** - 仪表板首页，展示KPI和热门数据
- **Trends** - 趋势分析，多指标折线图
- **Users** - 用户分析，排行榜和统计
- **Content** - 内容分析，标签词云和排行
- **DataTable** - 问题数据表，支持搜索和分页

### 智能功能
- 实时进度反馈
- 异步数据加载
- 错误处理和提示
- 缓存优化
- 响应式布局

## 📊 页面详解

### Dashboard (仪表板)
- 5个KPI卡片（总问题数、总浏览、总点赞、总回答、活跃用户）
- 热门问题表格（Top 10）
- 活跃用户排行（Top 5）
- 热门标签展示

### Trends (趋势分析)
- 时间粒度选择（日/周/月）
- 多指标折线图（问题数、浏览数、点赞数、回答数）
- 月度数据对比表格
- 实时图表交互

### Users (用户分析)
- 用户统计概览
- 用户排行榜表格（Top 10）
- 进度条显示贡献度
- 排名徽章和声望值展示

### Content (内容分析)
- 标签词云（大小根据出现次数）
- 热门标签排行（Top 15）
- 标签统计信息
- 交互式标签浏览

### DataTable (数据表)
- 完整的问题数据表
- 搜索功能
- 排序选项
- 分页功能（每页10/20/50/100条）
- 标签展示
- 直达问题链接

## 🔌 API连接

### 后端连接配置

前端会自动连接到后端API：
```
http://localhost:5000/api/v1
```

确保后端服务运行在 `localhost:5000`

### 代理配置

Vite配置中已自动配置API代理：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
    rewrite: (path) => path,
  },
}
```

## 📱 响应式设计

应用支持多种屏幕尺寸：
- **桌面** (≥1024px) - 完整三列布局
- **平板** (768px-1024px) - 两列布局
- **手机** (<768px) - 单列堆叠

## 🎯 使用流程

### 第一次访问

1. 打开 http://localhost:5173
2. 查看Dashboard首页
3. 数据会自动从后端加载
4. 如果没有数据，可点击左侧"启动爬虫"获取数据

### 启动爬虫

1. 在左侧爬虫控制面板设置页数
2. 点击"启动爬虫"按钮
3. 查看进度条实时更新
4. 爬虫完成后，所有页面数据自动更新

### 浏览数据

1. **Dashboard** - 快速浏览关键数据
2. **Trends** - 分析数据趋势
3. **Users** - 查看用户贡献
4. **Content** - 浏览热门标签
5. **DataTable** - 搜索和筛选具体问题

## 🔧 调试技巧

### 查看网络请求

1. 打开浏览器DevTools (F12)
2. 切换到Network标签
3. 刷新页面
4. 观察API请求和响应

### 查看应用状态

1. 打开浏览器DevTools
2. 切换到Console标签
3. 输入以下代码查看状态：

```javascript
import { useDataStore } from '@/stores/useDataStore'
const store = useDataStore()
console.log(store.dashboardData)
console.log(store.crawlerState)
```

### 常见问题排查

**Q: 页面显示为空**
- 检查后端是否启动在 localhost:5000
- 查看DevTools Console是否有错误
- 在控制面板点击"启动爬虫"获取数据

**Q: 数据加载缓慢**
- 检查网络连接
- 查看后端是否在处理其他请求
- 尝试清空浏览器缓存

**Q: 图表不显示**
- 确保ECharts已正确安装
- 检查浏览器DevTools是否有报错
- 尝试刷新页面

## 📦 构建和部署

### 生产构建

```bash
npm run build
```

生成的文件在 `dist/` 目录中

### 部署到Nginx

```nginx
server {
    listen 80;
    server_name example.com;

    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
    }
}
```

## 🚀 性能优化

### 已实施的优化
- ✅ 代码分割（路由懒加载）
- ✅ 缓存策略（智能缓存管理）
- ✅ 图表按需加载
- ✅ 响应式图片

### 可进一步优化
- [ ] CDN加速
- [ ] Gzip压缩
- [ ] 图片优化
- [ ] 字体优化

## 🎓 学习资源

- [Vue 3文档](https://vuejs.org/)
- [Vite文档](https://vitejs.dev/)
- [Element Plus](https://element-plus.org/)
- [ECharts](https://echarts.apache.org/)
- [Pinia](https://pinia.vuejs.org/)

## 📞 获取帮助

### 查看文件结构
```bash
cd frontend
npm run type-check  # 检查类型错误
```

### 查看日志
- 浏览器DevTools Console - 前端错误
- 后端终端输出 - 后端日志

### 常用快捷键
- **F12** - 打开DevTools
- **Ctrl+Shift+I** - 打开DevTools (Firefox)
- **Cmd+Option+I** - 打开DevTools (Mac)

---

**现在就开始开发吧！** 🚀

所有的基础结构都已准备完毕，所有的页面都已实现，所有的样式都已美化。现在只需要启动应用并查看效果！

