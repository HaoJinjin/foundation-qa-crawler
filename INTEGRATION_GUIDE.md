# 前后端通信集成指南

## 1. 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    前端应用 (Vue 3)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 视图层 (Pages)                                       │   │
│  │ ├─ Dashboard.vue      (首页仪表板)                   │   │
│  │ ├─ Trends.vue         (趋势分析页)                   │   │
│  │ ├─ Users.vue          (用户分析页)                   │   │
│  │ ├─ Content.vue        (内容分析页)                   │   │
│  │ └─ DataTable.vue      (数据表页)                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 状态管理层 (Pinia Store)                             │   │
│  │ useDataStore.ts                                     │   │
│  │ ├─ 管理所有应用状态                                  │   │
│  │ ├─ 处理数据加载和缓存                                │   │
│  │ ├─ 处理错误管理                                      │   │
│  │ └─ 坐标爬虫任务                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ API客户端层 (API Client)                             │   │
│  │ client.ts                                           │   │
│  │ ├─ 所有HTTP请求                                     │   │
│  │ ├─ 请求/响应拦截                                    │   │
│  │ ├─ 统一错误处理                                      │   │
│  │ └─ 异步任务轮询                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         HTTP/HTTPS (JSON)
         ↓
┌─────────────────────────────────────────────────────────────┐
│                  后端服务 (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ API路由层                                           │   │
│  │ ├─ /crawler/* (爬虫接口)                             │   │
│  │ ├─ /analysis/* (分析接口)                            │   │
│  │ └─ /system/* (系统接口)                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 业务逻辑层                                           │   │
│  │ ├─ AnswerSiteCrawler (爬虫)                          │   │
│  │ ├─ DataAnalyzer (分析)                              │   │
│  │ ├─ TaskManager (任务管理)                            │   │
│  │ └─ CacheManager (缓存)                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 数据层                                               │   │
│  │ ├─ 本地JSON文件 (缓存)                               │   │
│  │ ├─ 爬虫源数据                                        │   │
│  │ └─ 临时数据文件                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 后端服务安装与启动

### 2.1 安装依赖

```bash
cd backend
pip install fastapi uvicorn requests beautifulsoup4 pandas pydantic
```

### 2.2 启动服务

```bash
cd backend
python main.py
```

服务启动后，访问地址：
- **API服务**: http://localhost:5000
- **自动文档**: http://localhost:5000/docs (Swagger UI)
- **ReDoc文档**: http://localhost:5000/redoc

### 2.3 验证服务是否正常

```bash
# 检查系统状态
curl http://localhost:5000/api/v1/system/status
```

响应应该类似：
```json
{
  "code": 200,
  "message": "系统状态正常",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "cache_enabled": true
  }
}
```

---

## 3. 前端项目集成

### 3.1 项目结构

```
frontend/
├── api/
│   └── client.ts              # API客户端
├── stores/
│   └── useDataStore.ts        # Pinia数据存储
├── components/
│   ├── Dashboard/
│   │   ├── KPICards.vue      # KPI卡片
│   │   ├── TopQuestions.vue  # 热门问题排行
│   │   └── UserRanking.vue   # 用户排行
│   └── Charts/
│       ├── TrendLine.vue     # 趋势折线图
│       ├── WordCloud.vue     # 标签词云
│       └── UserScatter.vue   # 用户散点图
├── pages/
│   ├── Dashboard.vue          # 首页
│   ├── Trends.vue            # 趋势分析
│   ├── Users.vue             # 用户分析
│   ├── Content.vue           # 内容分析
│   └── DataTable.vue         # 数据表
├── App.vue
├── main.ts
└── vite.config.ts
```

### 3.2 安装前端依赖

```bash
cd frontend

# 创建Vite项目（如果还没有）
npm create vite@latest . -- --template vue-ts

# 安装依赖
npm install

# 安装额外包
npm install axios pinia echarts element-plus
```

### 3.3 配置main.ts

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(ElementPlus)

app.mount('#app')
```

### 3.4 配置API基础URL

在 `frontend/api/client.ts` 中，可以根据环境配置不同的URL：

```typescript
// 根据环境设置API URL
const baseURL = import.meta.env.DEV
  ? 'http://localhost:5000/api/v1'
  : 'https://api.example.com/api/v1'

const client = new ApiClient(baseURL)
```

---

## 4. 前端使用示例

### 4.1 在Vue组件中使用

#### 示例1：Dashboard页面

```vue
<template>
  <div class="dashboard">
    <!-- 标题和刷新按钮 -->
    <div class="header">
      <h1>数据仪表板</h1>
      <button @click="handleRefresh" :loading="store.loading.dashboard">
        刷新数据
      </button>
    </div>

    <!-- KPI卡片 -->
    <div class="kpi-cards" v-if="store.dashboardData">
      <KPICard
        title="总问题数"
        :value="store.dashboardData.basic_stats.total_questions"
      />
      <KPICard
        title="总浏览数"
        :value="store.dashboardData.basic_stats.total_views"
      />
      <KPICard
        title="总点赞数"
        :value="store.dashboardData.basic_stats.total_likes"
      />
      <KPICard
        title="总回答数"
        :value="store.dashboardData.basic_stats.total_answers"
      />
    </div>

    <!-- 热门问题排行 -->
    <TopQuestions
      :questions="store.dashboardData?.top_questions"
      :loading="store.loading.dashboard"
    />

    <!-- 用户排行 -->
    <UserRanking
      :users="store.dashboardData?.top_users"
      :loading="store.loading.dashboard"
    />

    <!-- 标签词云 -->
    <WordCloud
      :tags="store.dashboardData?.top_tags"
      :loading="store.loading.dashboard"
    />
  </div>
</template>

<script setup lang="ts">
import { useDataStore } from '@/stores/useDataStore'
import { onMounted } from 'vue'
import KPICard from '@/components/Dashboard/KPICard.vue'
import TopQuestions from '@/components/Dashboard/TopQuestions.vue'
import UserRanking from '@/components/Dashboard/UserRanking.vue'
import WordCloud from '@/components/Charts/WordCloud.vue'

const store = useDataStore()

// 组件挂载时加载数据
onMounted(() => {
  handleRefresh()
})

// 刷新数据
const handleRefresh = async () => {
  await store.fetchDashboard()
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
</style>
```

#### 示例2：启动爬虫页面

```vue
<template>
  <div class="crawler-panel">
    <h2>数据爬虫控制</h2>

    <!-- 爬虫配置 -->
    <div class="config-section">
      <el-form :model="crawlerConfig" label-width="120px">
        <el-form-item label="最大页数">
          <el-input-number
            v-model="crawlerConfig.maxPages"
            :min="1"
            :max="50"
          />
        </el-form-item>
        <el-form-item label="超时时间(秒)">
          <el-input-number
            v-model="crawlerConfig.timeout"
            :min="10"
            :max="300"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button
        type="primary"
        @click="handleStartCrawler"
        :loading="store.crawlerState.isRunning"
      >
        启动爬虫
      </el-button>

      <el-button
        v-if="store.crawlerState.isRunning"
        type="danger"
        @click="handleStopCrawler"
      >
        停止爬虫
      </el-button>

      <el-button
        v-if="!store.crawlerState.isRunning"
        @click="handleClearCache"
      >
        清空缓存
      </el-button>
    </div>

    <!-- 进度条 -->
    <div v-if="store.crawlerState.isRunning" class="progress-section">
      <p>{{ store.crawlerState.message }}</p>
      <el-progress :percentage="store.crawlerState.progress" />
    </div>

    <!-- 结果信息 -->
    <div v-if="store.crawlerState.lastResult" class="result-section">
      <el-alert
        title="爬虫完成"
        type="success"
        description="爬虫已完成，数据已刷新"
      />
    </div>

    <!-- 错误信息 -->
    <div v-if="store.errors.crawler" class="error-section">
      <el-alert
        title="错误"
        :description="store.errors.crawler"
        type="error"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDataStore } from '@/stores/useDataStore'
import { ElMessage } from 'element-plus'

const store = useDataStore()

const crawlerConfig = $ref({
  maxPages: store.crawlerConfig.maxPages,
  timeout: store.crawlerConfig.timeout,
})

const handleStartCrawler = async () => {
  // 更新配置
  store.setCrawlerConfig(crawlerConfig)

  // 启动爬虫
  await store.startCrawler()

  if (store.crawlerState.lastResult) {
    ElMessage.success('爬虫成功完成！')
  }
}

const handleStopCrawler = async () => {
  await store.stopCrawler()
  ElMessage.info('爬虫已停止')
}

const handleClearCache = async () => {
  await apiClient.clearCache()
  ElMessage.success('缓存已清空')
}
</script>

<style scoped>
.crawler-panel {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f9f9f9;
}

.config-section {
  margin-bottom: 20px;
}

.actions {
  margin-bottom: 20px;
}

.el-button {
  margin-right: 10px;
}

.progress-section {
  margin-bottom: 20px;
}

.result-section,
.error-section {
  margin-bottom: 20px;
}
</style>
```

#### 示例3：数据表页面

```vue
<template>
  <div class="data-table-page">
    <h2>问题数据表</h2>

    <!-- 搜索和筛选 -->
    <div class="controls">
      <el-input
        v-model="search"
        placeholder="搜索问题标题"
        @input="handleSearch"
        style="width: 300px"
      />
      <el-select
        v-model="sortBy"
        placeholder="排序方式"
        @change="handleSearch"
      >
        <el-option label="浏览数" value="views" />
        <el-option label="点赞数" value="likes" />
        <el-option label="回答数" value="answers" />
      </el-select>
    </div>

    <!-- 数据表 -->
    <el-table
      :data="store.questionsData?.questions"
      stripe
      :loading="store.loading.questions"
      style="width: 100%"
    >
      <el-table-column prop="title" label="标题" min-width="300" />
      <el-table-column prop="user" label="提问用户" width="150" />
      <el-table-column prop="views" label="浏览数" width="100" />
      <el-table-column prop="likes" label="点赞数" width="100" />
      <el-table-column prop="answers" label="回答数" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-link
            type="primary"
            target="_blank"
            :href="scope.row.question_link"
          >
            查看
          </el-link>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="store.questionsData?.total"
      @current-change="handlePageChange"
      @size-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { useDataStore } from '@/stores/useDataStore'
import { ref } from 'vue'

const store = useDataStore()
const search = ref('')
const sortBy = ref('views')
const currentPage = ref(1)
const pageSize = ref(20)

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const handlePageChange = () => {
  loadData()
}

const loadData = async () => {
  await store.fetchQuestions(
    currentPage.value,
    pageSize.value,
    sortBy.value,
    'desc',
    search.value || undefined
  )
}

// 初始加载
onMounted(() => {
  loadData()
})
</script>
```

### 4.2 数据流示例

#### 流程1：初始化加载Dashboard

```
用户打开应用
    ↓
Dashboard.vue mounted()
    ↓
store.fetchDashboard()
    ↓
apiClient.getDashboard()
    ↓
HTTP GET /api/v1/analysis/dashboard
    ↓
后端检查缓存
    ├─ 有缓存 → 返回缓存数据
    └─ 无缓存 → 读取JSON文件 → 返回数据
    ↓
前端接收JSON响应
    ↓
更新 dashboardData 状态
    ↓
设置 loading.dashboard = false
    ↓
Vue自动重新渲染 → 图表数据更新 → 用户看到图表
```

#### 流程2：执行爬虫任务

```
用户点击"启动爬虫"
    ↓
store.startCrawler()
    ↓
apiClient.startCrawler(maxPages=10, asyncMode=true)
    ↓
HTTP POST /api/v1/crawler/start
    ↓
后端创建后台任务 → 返回 task_id
    ↓
前端保存 task_id 到 crawlerState
    ↓
前端启动轮询：apiClient.pollTaskStatus(task_id)
    ├─ 每2秒查询一次任务状态
    ├─ HTTP GET /api/v1/crawler/task/{task_id}
    ├─ 更新 progress 和 message
    └─ 重复直到 status = 'completed'
    ↓
后台爬虫完成
    ↓
返回爬虫结果 + 分析数据
    ↓
前端收到完成信号
    ↓
store.refreshAllData()
    ├─ fetchDashboard()
    ├─ fetchTrends()
    ├─ fetchUsers()
    ├─ fetchTags()
    └─ fetchQuestions()
    ↓
所有页面数据自动更新
    ↓
用户看到最新数据
```

---

## 5. 关键技术点

### 5.1 异步任务处理

后端使用后台任务执行长时间爬虫，前端轮询查询进度：

```python
# 后端 (FastAPI)
@app.post("/api/v1/crawler/start")
async def start_crawler(request: CrawlerRequest, background_tasks: BackgroundTasks):
    # 立即返回task_id
    # 后台执行爬虫
    background_tasks.add_task(run_crawler)
    return {"task_id": task_id}
```

```typescript
// 前端 (Vue)
async function pollCrawler() {
  const finalTask = await apiClient.pollTaskStatus(
    taskId,
    maxAttempts,
    intervalMs,
    (progress, message) => {
      // 更新进度条
      crawlerState.value.progress = progress
    }
  )
}
```

### 5.2 缓存管理

后端支持自动缓存，减少重复计算：

```typescript
// 前端请求时指定缓存参数
const response = await apiClient.getDashboard(
  useCache = true,      // 使用缓存
  cacheTtl = 3600       // 3小时过期
)
```

### 5.3 错误处理

统一的错误处理链：

```typescript
// API客户端拦截错误
this.client.interceptors.response.use(
  (response) => response,
  (error) => {
    // 统一处理所有错误
    const message = error?.response?.data?.message
    // 显示错误提示
    return Promise.reject(error)
  }
)

// Store中catch错误
try {
  const response = await apiClient.getDashboard()
} catch (error) {
  errors.value.dashboard = error?.message
}
```

### 5.4 响应式数据绑定

使用Pinia+Vue3 Composition API实现完整的响应式：

```typescript
// Store中的ref自动响应
const dashboardData = ref<DashboardData | null>(null)
const loading = ref({ dashboard: false })

// 更新状态时，所有订阅的组件自动更新
dashboardData.value = newData  // 触发组件重新渲染
```

---

## 6. 环境配置

### 6.1 开发环境 (.env.development)

```
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_CRAWLER_TIMEOUT=60000
VITE_CACHE_ENABLED=true
```

### 6.2 生产环境 (.env.production)

```
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_CRAWLER_TIMEOUT=120000
VITE_CACHE_ENABLED=true
```

### 6.3 在代码中使用

```typescript
const baseURL = import.meta.env.VITE_API_BASE_URL
const timeout = import.meta.env.VITE_CRAWLER_TIMEOUT
```

---

## 7. 调试技巧

### 7.1 查看API请求日志

在浏览器DevTools中：

```javascript
// 在控制台输入
localStorage.debug = 'axios:*'

// 或者在API客户端中启用日志
console.log(`[API Request] ${method} ${url}`)
```

### 7.2 查看后端日志

```bash
# 后端服务会输出所有请求
[2025-01-07 10:30:45] - API Request: POST /api/v1/crawler/start
[2025-01-07 10:30:45] - Task created: crawler_task_abc123
[2025-01-07 10:30:47] - Crawler started for task_abc123
```

### 7.3 测试单个API接口

```bash
# 使用curl测试
curl -X GET "http://localhost:5000/api/v1/analysis/dashboard" \
  -H "Content-Type: application/json"

# 使用Python测试
import requests
response = requests.get('http://localhost:5000/api/v1/analysis/dashboard')
print(response.json())
```

---

## 8. 部署建议

### 8.1 后端部署（Docker）

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend/main.py"]
```

### 8.2 前端部署（Nginx）

```nginx
server {
    listen 80;
    server_name example.com;

    root /app/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
    }
}
```

### 8.3 Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## 总结

✅ **完整的前后端通信架构**包含：

1. **后端 (FastAPI)**
   - 完整的API接口规范
   - 异步爬虫任务管理
   - 缓存系统
   - 统一的响应格式

2. **前端 (Vue 3)**
   - API客户端层
   - 数据状态管理 (Pinia)
   - 错误处理和加载状态
   - 异步任务轮询

3. **数据流**
   - 用户操作 → Store → API客户端 → 后端 → 返回JSON → Store → 组件自动更新

4. **最佳实践**
   - 分层架构清晰
   - 错误处理完善
   - 缓存优化性能
   - 异步任务支持

现在已经准备好开始开发前端页面和组件了！

