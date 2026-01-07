<template>
  <div class="trends-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📈 趋势分析</h1>
      <div class="controls">
        <el-select v-model="granularity" placeholder="选择粒度" @change="refreshData">
          <el-option label="每日" value="daily" />
          <el-option label="每周" value="weekly" />
          <el-option label="每月" value="monthly" />
        </el-select>
        <el-button type="primary" @click="refreshData" :loading="loading">
          🔄 刷新
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 错误提示 -->
    <el-alert v-if="error" :title="error" type="error" :closable="false" />

    <!-- 趋势图表 -->
    <div class="card" v-if="!loading && trendsData">
      <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
    </div>

    <!-- 数据表格 -->
    <div class="card" v-if="!loading && trendsData">
      <h2>📊 月度数据统计</h2>
      <el-table :data="trendsData.data" max-height="400">
        <el-table-column prop="period" label="时期" min-width="120" />
        <el-table-column prop="question_count" label="问题数" min-width="120" align="right" />
        <el-table-column prop="total_views" label="总浏览" min-width="120" align="right" />
        <el-table-column prop="total_likes" label="总点赞" min-width="120" align="right" />
        <el-table-column prop="total_answers" label="总回答" min-width="120" align="right" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()
const granularity = ref('monthly')
const chartContainer = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const error = computed(() => dataStore.errors.trends)
const loading = computed(() => dataStore.loading.trends)
const trendsData = computed(() => dataStore.trendsData)

// 初始化图表
const initChart = async () => {
  // 等待 DOM 更新
  await nextTick()

  if (!chartContainer.value) {
    console.warn('图表容器未找到')
    return
  }

  if (!trendsData.value || !trendsData.value.data || trendsData.value.data.length === 0) {
    console.warn('趋势数据为空')
    return
  }

  if (!chart) {
    chart = echarts.init(chartContainer.value)
  }

  const data = trendsData.value.data
  const periods = data.map((item: any) => item.period)
  const questionCounts = data.map((item: any) => item.question_count)
  const totalViews = data.map((item: any) => item.total_views)
  const totalLikes = data.map((item: any) => item.total_likes)
  const totalAnswers = data.map((item: any) => item.total_answers)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 14, 39, 0.9)',
      borderColor: '#00d4ff',
      textStyle: {
        color: '#e0e0e0',
      },
    },
    legend: {
      data: ['问题数', '浏览数', '点赞数', '回答数'],
      textStyle: {
        color: '#a0a0a0',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: periods,
      axisLine: {
        lineStyle: {
          color: '#2a3f5f',
        },
      },
      axisLabel: {
        color: '#a0a0a0',
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#2a3f5f',
        },
      },
      axisLabel: {
        color: '#a0a0a0',
      },
      splitLine: {
        lineStyle: {
          color: '#2a3f5f',
        },
      },
    },
    series: [
      {
        name: '问题数',
        type: 'line',
        data: questionCounts,
        smooth: true,
        itemStyle: {
          color: '#00d4ff',
        },
        lineStyle: {
          color: '#00d4ff',
          width: 2,
        },
        areaStyle: {
          color: 'rgba(0, 212, 255, 0.1)',
        },
      },
      {
        name: '浏览数',
        type: 'line',
        data: totalViews,
        smooth: true,
        itemStyle: {
          color: '#1890ff',
        },
        lineStyle: {
          color: '#1890ff',
          width: 2,
        },
        areaStyle: {
          color: 'rgba(24, 144, 255, 0.1)',
        },
      },
      {
        name: '点赞数',
        type: 'line',
        data: totalLikes,
        smooth: true,
        itemStyle: {
          color: '#52c41a',
        },
        lineStyle: {
          color: '#52c41a',
          width: 2,
        },
        areaStyle: {
          color: 'rgba(82, 196, 26, 0.1)',
        },
      },
      {
        name: '回答数',
        type: 'line',
        data: totalAnswers,
        smooth: true,
        itemStyle: {
          color: '#faad14',
        },
        lineStyle: {
          color: '#faad14',
          width: 2,
        },
        areaStyle: {
          color: 'rgba(250, 173, 20, 0.1)',
        },
      },
    ],
  }

  chart.setOption(option)
}

// 刷新数据
const refreshData = async () => {
  await dataStore.fetchTrends(granularity.value)
  await initChart()
  ElMessage.success('数据已刷新')
}

// 监听趋势数据变化
watch(trendsData, async (newVal) => {
  if (newVal && newVal.data && newVal.data.length > 0) {
    await initChart()
  }
}, { deep: true })

// 监听窗口大小变化
const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

// 页面加载时获取数据
onMounted(async () => {
  if (!trendsData.value) {
    await dataStore.fetchTrends(granularity.value)
  } else {
    // 如果已有数据，直接初始化图表
    await initChart()
  }
  window.addEventListener('resize', handleResize)
})

// 清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.trends-page {
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

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.controls .el-select {
  min-width: 120px;
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
</style>
