<template>
  <div class="data-table-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📋 问题数据表</h1>
      <div class="controls">
        <el-input
          v-model="searchText"
          placeholder="搜索问题标题"
          clearable
          @input="handleSearch"
          style="width: 300px"
        />
        <el-select v-model="sortBy" placeholder="排序方式" @change="handleSearch">
          <el-option label="浏览数" value="views" />
          <el-option label="点赞数" value="likes" />
          <el-option label="回答数" value="answers" />
        </el-select>
        <el-button type="primary" @click="handleSearch" :loading="loading">
          🔍 搜索
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" :closable="false" />

    <!-- 数据表 -->
    <div class="card" v-if="!loading && questionsData">
      <el-table :data="questionsData.questions" style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <el-link :href="scope.row.question_link" target="_blank" :underline="false">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="提问用户" width="120" />
        <el-table-column prop="views" label="浏览数" width="80" align="right" sortable />
        <el-table-column prop="likes" label="点赞数" width="80" align="right" sortable />
        <el-table-column prop="answers" label="回答数" width="80" align="right" sortable />
        <el-table-column prop="reputation" label="声望值" width="80" align="right">
          <template #default="scope">
            <span class="reputation-badge">{{ scope.row.reputation }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="asked_time" label="提问时间" width="120" />
        <el-table-column label="标签" min-width="150">
          <template #default="scope">
            <div class="tags">
              <el-tag
                v-for="tag in scope.row.tags.slice(0, 3)"
                :key="tag"
                size="small"
                effect="light"
              >
                {{ tag }}
              </el-tag>
              <el-tag v-if="scope.row.tags.length > 3" size="small" effect="light">
                +{{ scope.row.tags.length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="questionsData.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()

const searchText = ref('')
const sortBy = ref('views')
const currentPage = ref(1)
const pageSize = ref(20)

const error = computed(() => dataStore.errors.questions)
const loading = computed(() => dataStore.loading.questions)
const questionsData = computed(() => dataStore.questionsData)

// 搜索或排序
const handleSearch = async () => {
  currentPage.value = 1
  await loadData()
}

// 分页变化
const handlePageChange = async () => {
  await loadData()
}

// 加载数据
const loadData = async () => {
  await dataStore.fetchQuestions(
    currentPage.value,
    pageSize.value,
    sortBy.value,
    'desc',
    searchText.value || undefined
  )
}

// 页面加载时获取数据
onMounted(async () => {
  await loadData()
})
</script>

<style scoped>
.data-table-page {
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
  flex-wrap: wrap;
  gap: 10px;
}

.page-header h1 {
  margin: 0;
}

.controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* ==================== 卡片样式 ==================== */
.card {
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-hover) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  overflow: auto;
}

.card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-glow);
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

/* ==================== 标签容器 ==================== */
.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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

/* ==================== 分页容器 ==================== */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.el-pagination {
  --el-text-color-regular: var(--text-primary);
}

.el-pager li {
  color: var(--text-primary) !important;
  background-color: transparent !important;
}

.el-pager li:hover {
  color: var(--primary-color) !important;
}

.el-pager li.active {
  color: var(--primary-color) !important;
  font-weight: bold;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls {
    width: 100%;
  }

  .el-table__body tr {
    font-size: 12px;
  }
}

@media (max-width: 768px) {
  .controls {
    width: 100%;
  }

  .controls .el-input {
    width: 100% !important;
  }

  .card {
    overflow-x: auto;
  }
}
</style>
