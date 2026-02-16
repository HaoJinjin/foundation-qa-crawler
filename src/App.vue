<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-left">
        <div class="logo">🌟 北太天元数据分析系统</div>
      </div>
      <div class="navbar-right">
        <div v-if="systemStatus" :class="['status', systemStatus.status === 'healthy' ? 'healthy' : 'error']">
          ● {{ systemStatus.status === 'healthy' ? '正常' : '异常' }}
        </div>
        <el-button link @click="refreshAll" :loading="isRefreshing">
          🔄 刷新全部
        </el-button>
      </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-wrapper">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="nav-menu">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            :class="['nav-item', { active: $route.path === item.path }]"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </nav>

        <!-- 爬虫控制面板 -->
        <div class="crawler-panel">
          <h3>🕷️ 爬虫控制</h3>
          <el-form :model="crawlerConfig" label-width="80px" size="small">
            <el-form-item label="最大页数">
              <el-input-number
                v-model="crawlerConfig.maxPages"
                :min="1"
                :max="50"
              />
            </el-form-item>
          </el-form>
          <el-button
            type="primary"
            @click="startCrawler"
            :loading="dataStore.crawlerState.isRunning"
            block
          >
            {{ dataStore.crawlerState.isRunning ? '爬虫运行中...' : '启动爬虫' }}
          </el-button>
          <el-button
            v-if="dataStore.crawlerState.isRunning"
            type="danger"
            @click="stopCrawler"
            block
          >
            停止爬虫
          </el-button>
        </div>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 进度条 -->
    <div v-if="dataStore.crawlerState.isRunning" class="progress-overlay">
      <div class="progress-card">
        <div class="progress-title">{{ dataStore.crawlerState.message }}</div>
        <el-progress :percentage="dataStore.crawlerState.progress" />
        <div class="progress-text">
          {{ dataStore.crawlerState.progress }}% 完成
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDataStore } from '@/stores/useDataStore'
import apiClient from '@/api/client'
import { ElMessage } from 'element-plus'

const dataStore = useDataStore()
const systemStatus = ref<any>(null)
const isRefreshing = ref(false)

const crawlerConfig = ref({
  maxPages: 10,
})

// 导航菜单项
const navItems = [
  { path: '/dashboard', label: '仪表板', icon: '📊' },
  { path: '/trends', label: '趋势分析', icon: '📈' },
  { path: '/users', label: '用户分析', icon: '👥' },
  { path: '/content', label: '内容分析', icon: '🏷️' },
  { path: '/data-table', label: '数据表', icon: '📋' },
]

// 获取系统状态
const getSystemStatus = async () => {
  try {
    const response = await apiClient.getSystemStatus()
    systemStatus.value = response.data.data
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

// 刷新全部数据
const refreshAll = async () => {
  isRefreshing.value = true
  try {
    await dataStore.refreshAllData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    isRefreshing.value = false
  }
}

// 启动爬虫
const startCrawler = async () => {
  dataStore.setCrawlerConfig({
    maxPages: crawlerConfig.value.maxPages,
  })
  await dataStore.startCrawler()
  if (dataStore.crawlerState.lastResult) {
    ElMessage.success('爬虫完成！')
  }
}

// 停止爬虫
const stopCrawler = async () => {
  await dataStore.stopCrawler()
  ElMessage.info('爬虫已停止')
}

// 组件挂载时获取系统状态
onMounted(() => {
  getSystemStatus()
  // 定期检查系统状态
  setInterval(getSystemStatus, 30000)
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ==================== 导航栏 ==================== */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background: linear-gradient(90deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border-bottom: 2px solid var(--primary-color);
  box-shadow: var(--shadow-glow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-left, .navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  color: var(--primary-color);
  font-size: 20px;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
  white-space: nowrap;
}

.status {
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  border: 1px solid;
}

.status.healthy {
  background: rgba(82, 196, 26, 0.2);
  color: var(--success-color);
  border-color: var(--success-color);
}

.status.error {
  background: rgba(255, 77, 79, 0.2);
  color: var(--danger-color);
  border-color: var(--danger-color);
}

/* ==================== 主包装器 ==================== */
.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ==================== 侧边栏 ==================== */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px 0;
}

.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-base);
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--primary-color);
  border-left-color: var(--primary-color);
}

.nav-item.active {
  background: rgba(0, 212, 255, 0.1);
  color: var(--primary-color);
  border-left-color: var(--primary-color);
  font-weight: 600;
}

.nav-icon {
  font-size: 18px;
}

.nav-label {
  flex: 1;
}

/* ==================== 爬虫控制面板 ==================== */
.crawler-panel {
  margin: 20px 10px 0;
  padding: 15px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.crawler-panel h3 {
  margin-bottom: 15px;
  font-size: 14px;
  color: var(--primary-color);
}

.crawler-panel :deep(.el-form) {
  margin-bottom: 15px;
}

.crawler-panel .el-button {
  margin-bottom: 8px;
}

/* ==================== 主内容区域 ==================== */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* ==================== 进度条覆盖 ==================== */
.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.progress-card {
  background: var(--bg-secondary);
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-lg);
  padding: 30px;
  min-width: 300px;
  box-shadow: var(--shadow-glow-strong);
}

.progress-title {
  color: var(--primary-color);
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
}

.progress-text {
  color: var(--text-secondary);
  font-size: 12px;
  text-align: center;
  margin-top: 10px;
}

/* ==================== 过渡动画 ==================== */
.fade-enter-active, .fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .main-wrapper {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    flex-direction: row;
    padding: 10px 0;
    max-height: none;
  }

  .nav-menu {
    flex-direction: row;
    overflow-x: auto;
  }

  .nav-item {
    white-space: nowrap;
  }

  .crawler-panel {
    display: none;
  }

  .main-content {
    padding: 10px;
  }
}
</style>
