<template>
  <div class="content-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>🏷️ 内容分析</h1>
      <el-button type="primary" @click="refreshData" :loading="loading">
        🔄 刷新
      </el-button>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" :closable="false" />

    <!-- 两列布局 -->
    <div class="grid-container" v-if="!loading && tagsData">
      <!-- 标签词云 -->
      <div class="card">
        <h2>☁️ 标签词云</h2>
        <div class="tags-cloud">
          <div
            v-for="tag in tagsData.tags.slice(0, 30)"
            :key="tag.tag"
            class="tag-item"
            :style="getTagStyle(tag.count)"
          >
            {{ tag.tag }}
            <span class="tag-count">({{ tag.count }})</span>
          </div>
        </div>
      </div>

      <!-- 标签排行 -->
      <div class="card">
        <h2>🔝 热门标签排行 (Top 15)</h2>
        <div class="tag-ranking">
          <div
            v-for="(tag, index) in tagsData.tags.slice(0, 15)"
            :key="tag.tag"
            class="ranking-item"
          >
            <div class="ranking-header">
              <span class="ranking-badge">{{ index + 1 }}</span>
              <span class="ranking-name">{{ tag.tag }}</span>
            </div>
            <el-progress
              :percentage="(tag.count / maxTagCount) * 100"
              :color="getProgressColor"
              :show-text="false"
            />
            <div class="ranking-count">{{ tag.count }} 次</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签统计 -->
    <div class="card" id="tag-card" v-if="!loading && tagsData">
      <h2>📊 标签统计信息</h2>
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-label">总标签数</div>
          <div class="stat-value">{{ tagsData.total_tags }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">最热标签</div>
          <div class="stat-value">{{ tagsData.tags[0]?.tag || 'N/A' }}</div>
          <div class="stat-sub">{{ tagsData.tags[0]?.count || 0 }} 次</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">平均标签出现</div>
          <div class="stat-value">{{ (tagsData.tags.reduce((sum: number, t: any) => sum + t.count, 0) / tagsData.total_tags).toFixed(1) }}</div>
          <div class="stat-sub">次/标签</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()

const error = computed(() => dataStore.errors.tags)
const loading = computed(() => dataStore.loading.tags)
const tagsData = computed(() => dataStore.tagsData)

// 计算最大标签数
const maxTagCount = computed(() => {
  if (!tagsData.value || !tagsData.value.tags.length) return 1
  return Math.max(...tagsData.value.tags.map(t => t.count))
})

// 获取标签样式（用于词云大小）
const getTagStyle = (count: number) => {
  const min = 12
  const max = 32
  const minCount = Math.min(...(tagsData.value?.tags.map(t => t.count) || [1]))
  const maxCount = Math.max(...(tagsData.value?.tags.map(t => t.count) || [1]))
  const range = maxCount - minCount
  const ratio = range === 0 ? 0.5 : (count - minCount) / range
  const fontSize = min + ratio * (max - min)

  return {
    fontSize: fontSize + 'px',
    opacity: 0.6 + ratio * 0.4,
  }
}

// 进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage > 80) return '#52c41a'
  if (percentage > 60) return '#1890ff'
  if (percentage > 40) return '#faad14'
  return '#ff4d4f'
}

// 刷新数据
const refreshData = async () => {
  await dataStore.fetchTags()
  ElMessage.success('数据已刷新')
}

// 页面加载时获取数据
onMounted(async () => {
  if (!tagsData.value) {
    await dataStore.fetchTags()
  }
})
</script>

<style scoped>
.content-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 100px);
  overflow: hidden;
  padding: 20px;
}

/* ==================== 页面标题 ==================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border-color);
  flex-shrink: 0;
}

.page-header h1 {
  margin: 0;
}

/* ==================== 网格布局 ==================== */
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}

/* ==================== 卡片样式 ==================== */
.card {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-hover) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

#tag-card{
  height: 220px;
}

.card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-glow);
}

.card h2 {
  margin-bottom: 15px;
  flex-shrink: 0;
}

/* ==================== 标签词云 ==================== */
.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  align-items: flex-start;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px;
  border-radius: var(--radius-md);
}

.tag-item {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 20px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.tag-item:hover {
  background: rgba(0, 212, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
  transform: scale(1.1);
}

.tag-count {
  color: var(--text-secondary);
  font-size: 0.8em;
  margin-left: 4px;
}

/* ==================== 标签排行 ==================== */
.tag-ranking {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 5px;
}

.ranking-item {
  padding: 12px;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  transition: all var(--transition-base);
}

.ranking-item:hover {
  background: rgba(0, 212, 255, 0.05);
  border-color: var(--primary-color);
}

.ranking-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.ranking-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary-color);
  color: var(--bg-primary);
  font-weight: bold;
  font-size: 12px;
}

.ranking-name {
  color: var(--text-primary);
  font-weight: 600;
  flex: 1;
}

.ranking-count {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 6px;
  text-align: right;
}

/* ==================== 统计信息 ==================== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  /* max-height: 120px; */
  overflow-y: auto;
}

.stat-box {
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 15px;
  text-align: center;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.stat-value {
  color: var(--primary-color);
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.stat-sub {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 4px;
}

/* 统计卡片容器 */
.content-page > .card {
  flex-shrink: 0;
  /* max-height: 140px; */
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .content-page {
    padding: 15px;
    gap: 15px;
  }

  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    max-height: 100%;
  }
}
</style>
