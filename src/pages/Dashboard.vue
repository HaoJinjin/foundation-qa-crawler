<template>
  <div class="dashboard-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📊 数据仪表板</h1>
      <el-button type="primary" @click="refreshData" :loading="loading">
        🔄 刷新
      </el-button>
    </div>

    <!-- KPI卡片区域 -->
    <div v-if="!loading && dashboardData" class="kpi-section">
      <div class="kpi-card">
        <div class="kpi-label">总问题数</div>
        <div class="kpi-value">{{ dashboardData.basic_stats.total_questions }}</div>
        <div class="kpi-change">平均浏览数: {{ dashboardData.basic_stats.avg_views.toFixed(1) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">总浏览数</div>
        <div class="kpi-value">{{ formatNumber(dashboardData.basic_stats.total_views) }}</div>
        <div class="kpi-change">最大: {{ dashboardData.basic_stats.max_views }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">总点赞数</div>
        <div class="kpi-value">{{ formatNumber(dashboardData.basic_stats.total_likes) }}</div>
        <div class="kpi-change">平均: {{ dashboardData.basic_stats.avg_likes.toFixed(1) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">总回答数</div>
        <div class="kpi-value">{{ formatNumber(dashboardData.basic_stats.total_answers) }}</div>
        <div class="kpi-change">平均: {{ dashboardData.basic_stats.avg_answers.toFixed(1) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">总活跃用户</div>
        <div class="kpi-value">{{ dashboardData.basic_stats.total_users }}</div>
        <div class="kpi-change">声望值: {{ dashboardData.basic_stats.total_reputation }}</div>
      </div>
    </div>

    <!-- 加载骨架屏 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" :closable="false" />

    <!-- 两列布局 -->
    <div class="grid-container" v-if="!loading && dashboardData">
      <!-- 热门问题排行 -->
      <div class="card">
        <h2>🔥 热门问题 (Top 10)</h2>
        <el-table :data="dashboardData.top_questions" stripe max-height="400">
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="views" label="浏览" width="80" align="right" />
          <el-table-column prop="likes" label="点赞" width="80" align="right" />
          <el-table-column prop="answers" label="回答" width="80" align="right" />
          <el-table-column label="操作" width="80" align="center">
            <template #default="scope">
              <el-link
                type="primary"
                target="_blank"
                :href="scope.row.question_link"
                :underline="false"
              >
                查看
              </el-link>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 活跃用户排行 -->
      <div class="card">
        <h2>👥 活跃用户 (Top 5)</h2>
        <div class="user-list">
          <div
            v-for="(user, index) in dashboardData.top_users"
            :key="index"
            class="user-item"
          >
            <div class="user-rank">{{ index + 1 }}</div>
            <div class="user-info">
              <div class="user-name">{{ user.user }}</div>
              <div class="user-stats">
                提问: {{ user.question_count }} | 浏览: {{ user.total_views }} | 点赞: {{ user.total_likes }}
              </div>
            </div>
            <div class="user-reputation">
              <span class="reputation-value">{{ user.reputation }}</span>
              <span class="reputation-label">声望</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 热门标签 -->
    <div class="card" v-if="!loading && dashboardData">
      <h2>🏷️ 热门标签</h2>
      <div class="tags-container">
        <el-tag
          v-for="tag in dashboardData.top_tags.slice(0, 15)"
          :key="tag.tag"
          :style="{ fontSize: Math.min(20, 12 + tag.count / 5) + 'px' }"
          effect="light"
          class="tag-item"
        >
          {{ tag.tag }}: {{ tag.count }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()
const error = computed(() => dataStore.errors.dashboard)
const loading = computed(() => dataStore.loading.dashboard)
const dashboardData = computed(() => dataStore.dashboardData)

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// 刷新数据
const refreshData = async () => {
  await dataStore.fetchDashboard()
  ElMessage.success('数据已刷新')
}

// 页面加载时获取数据
onMounted(async () => {
  if (!dashboardData.value) {
    await dataStore.fetchDashboard()
  }
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ==================== 页面标题 ==================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border-color);
}

.page-header h1 {
  margin: 0;
}

/* ==================== KPI卡片区域 ==================== */
.kpi-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.kpi-card {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-hover) 100%);
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-glow);
  text-align: center;
  transition: all var(--transition-base);
}

.kpi-card:hover {
  box-shadow: var(--shadow-glow-strong);
  transform: translateY(-5px);
  border-color: var(--primary-light);
}

.kpi-label {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.kpi-value {
  color: var(--primary-color);
  font-size: 32px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
  margin-bottom: 5px;
}

.kpi-change {
  color: var(--text-secondary);
  font-size: 12px;
}

/* ==================== 卡片样式 ==================== */
.card {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-hover) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
}

.card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-glow);
}

.card h2 {
  margin-bottom: 15px;
  font-size: 18px;
}

/* ==================== 网格布局 ==================== */
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* ==================== 用户列表 ==================== */
.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  transition: all var(--transition-base);
}

.user-item:hover {
  background: rgba(0, 212, 255, 0.05);
  border-color: var(--primary-color);
}

.user-rank {
  color: var(--primary-color);
  font-size: 20px;
  font-weight: bold;
  min-width: 30px;
  text-align: center;
}

.user-info {
  flex: 1;
}

.user-name {
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 4px;
}

.user-stats {
  color: var(--text-secondary);
  font-size: 12px;
}

.user-reputation {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-sm);
}

.reputation-value {
  color: var(--primary-color);
  font-size: 18px;
  font-weight: bold;
}

.reputation-label {
  color: var(--text-secondary);
  font-size: 11px;
  text-transform: uppercase;
}

/* ==================== 标签云 ==================== */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-item {
  cursor: pointer;
  transition: all var(--transition-base);
}

.tag-item:hover {
  transform: scale(1.1);
}

/* ==================== 表格美化 ==================== */
.el-table {
  background-color: transparent !important;
}

.el-table__header th {
  background-color: var(--bg-hover) !important;
  color: var(--text-primary) !important;
}

.el-table__body tr {
  background-color: transparent !important;
}

.el-table__body tr:hover > td {
  background-color: rgba(0, 212, 255, 0.05) !important;
}

.el-table__body td {
  color: var(--text-primary) !important;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .kpi-section {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .grid-container {
    grid-template-columns: 1fr;
  }

  .kpi-value {
    font-size: 28px;
  }
}

@media (max-width: 768px) {
  .kpi-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .kpi-card {
    padding: 15px;
  }

  .kpi-value {
    font-size: 24px;
  }
}
</style>
