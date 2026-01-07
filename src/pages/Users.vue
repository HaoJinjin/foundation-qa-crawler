<template>
  <div class="users-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>👥 用户分析</h1>
      <el-button type="primary" @click="refreshData" :loading="loading">
        🔄 刷新
      </el-button>
    </div>

    <!-- 用户统计概览 -->
    <div v-if="!loading && usersData" class="stats-overview">
      <div class="stat-item">
        <div class="stat-label">总用户数</div>
        <div class="stat-value">{{ usersData.total_users }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">平均提问数</div>
        <div class="stat-value">{{ usersData.avg_questions_per_user.toFixed(1) }}</div>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" :closable="false" />

    <!-- 用户排行表 -->
    <div class="card" v-if="!loading && usersData">
      <h2>🏆 用户排行榜 (Top 10)</h2>
      <el-table :data="usersData.users" max-height="600">
        <el-table-column prop="rank" label="排名" width="60" align="center">
          <template #default="scope">
            <span :class="['rank-badge', `rank-${scope.row.rank}`]">
              {{ scope.row.rank }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="用户名" min-width="150" />
        <el-table-column prop="question_count" label="提问数" width="100" align="right">
          <template #default="scope">
            <el-progress
              :percentage="(scope.row.question_count / maxQuestionCount) * 100"
              :color="getProgressColor"
              :show-text="false"
            />
          </template>
        </el-table-column>
        <el-table-column prop="total_views" label="总浏览" width="100" align="right" />
        <el-table-column prop="total_likes" label="总点赞" width="100" align="right" />
        <el-table-column prop="total_answers" label="总回答" width="100" align="right" />
        <el-table-column prop="reputation" label="声望值" width="100" align="right">
          <template #default="scope">
            <span class="reputation-badge">{{ scope.row.reputation }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()

const error = computed(() => dataStore.errors.users)
const loading = computed(() => dataStore.loading.users)
const usersData = computed(() => dataStore.usersData)

// 计算最大提问数用于进度条
const maxQuestionCount = computed(() => {
  if (!usersData.value || !usersData.value.users.length) return 1
  return Math.max(...usersData.value.users.map(u => u.question_count))
})

// 进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage > 80) return '#52c41a'
  if (percentage > 60) return '#1890ff'
  if (percentage > 40) return '#faad14'
  return '#ff4d4f'
}

// 刷新数据
const refreshData = async () => {
  await dataStore.fetchUsers()
  ElMessage.success('数据已刷新')
}

// 页面加载时获取数据
onMounted(async () => {
  if (!usersData.value) {
    await dataStore.fetchUsers()
  }
})
</script>

<style scoped>
.users-page {
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

/* ==================== 统计概览 ==================== */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-item {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-hover) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  text-align: center;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.stat-value {
  color: var(--primary-color);
  font-size: 32px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
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
}

/* ==================== 排名徽章 ==================== */
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #333;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e0a060);
  color: #fff;
}

.rank-1, .rank-2, .rank-3 {
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

/* ==================== 声望徽章 ==================== */
.reputation-badge {
  display: inline-block;
  background: rgba(0, 212, 255, 0.1);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid var(--primary-color);
  font-size: 12px;
  font-weight: bold;
}

/* ==================== 表格美化 ==================== */
.el-table {
  background-color: transparent !important;
  width: 100%;
}

.el-table__header th {
  background-color: var(--bg-hover) !important;
  color: var(--text-primary) !important;
  border-bottom: 1px solid var(--border-color) !important;
}

.el-table__body tr {
  background-color: transparent !important;
}

/* 移除斑马纹 */
.el-table__body tr.el-table__row--striped {
  background-color: transparent !important;
}

.el-table__body tr:hover > td {
  background-color: rgba(0, 212, 255, 0.08) !important;
}

.el-table__body td {
  color: var(--text-primary) !important;
  border-bottom: 1px solid rgba(42, 63, 95, 0.3) !important;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
