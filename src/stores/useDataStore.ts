/**
 * 数据存储 - Pinia Store
 * 负责管理所有应用状态和数据
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '../api/client';
import type {
  DashboardData,
  TrendsData,
  UsersData,
  TagsData,
  QuestionsListData,
  CrawlerTaskResponse,
} from '../api/client';

// ==================== 状态类型 ====================

export interface LoadingState {
  dashboard: boolean;
  trends: boolean;
  users: boolean;
  tags: boolean;
  questions: boolean;
  crawler: boolean;
}

export interface ErrorState {
  dashboard: string | null;
  trends: string | null;
  users: string | null;
  tags: string | null;
  questions: string | null;
  crawler: string | null;
}

export interface CrawlerState {
  isRunning: boolean;
  currentTaskId: string | null;
  progress: number;
  message: string;
  lastResult?: any;
}

// ==================== Store定义 ====================

export const useDataStore = defineStore('data', () => {
  // ==================== 状态 ====================

  // 数据
  const dashboardData = ref<DashboardData | null>(null);
  const trendsData = ref<TrendsData | null>(null);
  const usersData = ref<UsersData | null>(null);
  const tagsData = ref<TagsData | null>(null);
  const questionsData = ref<QuestionsListData | null>(null);

  // 加载状态
  const loading = ref<LoadingState>({
    dashboard: false,
    trends: false,
    users: false,
    tags: false,
    questions: false,
    crawler: false,
  });

  // 错误状态
  const errors = ref<ErrorState>({
    dashboard: null,
    trends: null,
    users: null,
    tags: null,
    questions: null,
    crawler: null,
  });

  // 爬虫状态
  const crawlerState = ref<CrawlerState>({
    isRunning: false,
    currentTaskId: null,
    progress: 0,
    message: '',
  });

  // 配置
  const crawlerConfig = ref({
    maxPages: 10,
    timeout: 30,
    asyncMode: true,
  });

  // ==================== 计算属性 ====================

  /**
   * 是否有任何数据加载中
   */
  const isLoading = computed(() => {
    return Object.values(loading.value).some((v) => v);
  });

  /**
   * 是否有任何错误
   */
  const hasErrors = computed(() => {
    return Object.values(errors.value).some((v) => v !== null);
  });

  /**
   * Dashboard是否有数据
   */
  const hasDashboardData = computed(() => {
    return dashboardData.value !== null;
  });

  /**
   * 获取所有未读错误信息
   */
  const getAllErrors = computed(() => {
    return Object.entries(errors.value)
      .filter(([_, error]) => error !== null)
      .map(([key, error]) => `${key}: ${error}`);
  });

  // ==================== 方法 ====================

  /**
   * 获取Dashboard数据
   */
  async function fetchDashboard() {
    loading.value.dashboard = true;
    errors.value.dashboard = null;

    try {
      const response = await apiClient.getDashboard();

      if (response.data) {
        dashboardData.value = response.data;
        console.log('Dashboard数据加载成功', response.data);
      } else {
        throw new Error(response.message || '获取Dashboard数据失败');
      }
    } catch (error: any) {
      errors.value.dashboard = error?.response?.data?.message || error?.message || '未知错误';
      console.error('获取Dashboard数据失败:', errors.value.dashboard);
    } finally {
      loading.value.dashboard = false;
    }
  }

  /**
   * 获取趋势数据
   */
  async function fetchTrends(
    granularity: string = 'monthly',
    startDate?: string,
    endDate?: string
  ) {
    loading.value.trends = true;
    errors.value.trends = null;

    try {
      const response = await apiClient.getTrends(granularity, startDate, endDate);

      if (response.data) {
        trendsData.value = response.data;
        console.log('趋势数据加载成功', response.data);
      } else {
        throw new Error(response.message || '获取趋势数据失败');
      }
    } catch (error: any) {
      errors.value.trends = error?.response?.data?.message || error?.message || '未知错误';
      console.error('获取趋势数据失败:', errors.value.trends);
    } finally {
      loading.value.trends = false;
    }
  }

  /**
   * 获取用户分析数据
   */
  async function fetchUsers(limit: number = 10, sortBy: string = 'question_count') {
    loading.value.users = true;
    errors.value.users = null;

    try {
      const response = await apiClient.getUsersAnalysis(limit, sortBy);

      if (response.data) {
        usersData.value = response.data;
        console.log('用户数据加载成功', response.data);
      } else {
        throw new Error(response.message || '获取用户数据失败');
      }
    } catch (error: any) {
      errors.value.users = error?.response?.data?.message || error?.message || '未知错误';
      console.error('获取用户数据失败:', errors.value.users);
    } finally {
      loading.value.users = false;
    }
  }

  /**
   * 获取标签分析数据
   */
  async function fetchTags(limit: number = 15) {
    loading.value.tags = true;
    errors.value.tags = null;

    try {
      const response = await apiClient.getTagsAnalysis(limit);

      if (response.data) {
        tagsData.value = response.data;
        console.log('标签数据加载成功', response.data);
      } else {
        throw new Error(response.message || '获取标签数据失败');
      }
    } catch (error: any) {
      errors.value.tags = error?.response?.data?.message || error?.message || '未知错误';
      console.error('获取标签数据失败:', errors.value.tags);
    } finally {
      loading.value.tags = false;
    }
  }

  /**
   * 获取问题列表
   */
  async function fetchQuestions(
    page: number = 1,
    limit: number = 20,
    sortBy: string = 'views',
    order: string = 'desc',
    search?: string
  ) {
    loading.value.questions = true;
    errors.value.questions = null;

    try {
      const response = await apiClient.getQuestionsList(page, limit, sortBy, order, search);

      if (response.data) {
        questionsData.value = response.data;
        console.log('问题列表加载成功', response.data);
      } else {
        throw new Error(response.message || '获取问题列表失败');
      }
    } catch (error: any) {
      errors.value.questions = error?.response?.data?.message || error?.message || '未知错误';
      console.error('获取问题列表失败:', errors.value.questions);
    } finally {
      loading.value.questions = false;
    }
  }

  /**
   * 启动爬虫
   */
  async function startCrawler() {
    loading.value.crawler = true;
    errors.value.crawler = null;
    crawlerState.value.isRunning = true;
    crawlerState.value.progress = 0;
    crawlerState.value.message = '准备启动爬虫...';

    try {
      const response = await apiClient.startCrawler(
        crawlerConfig.value.maxPages,
        crawlerConfig.value.timeout,
        crawlerConfig.value.asyncMode
      );

      if (response.data && response.data.task_id) {
        crawlerState.value.currentTaskId = response.data.task_id;
        console.log('爬虫任务已提交，TaskID:', response.data.task_id);

        // 如果是异步模式，开始轮询
        if (crawlerConfig.value.asyncMode) {
          await pollCrawler();
        }
      } else {
        throw new Error(response.message || '启动爬虫失败');
      }
    } catch (error: any) {
      errors.value.crawler = error?.response?.data?.message || error?.message || '未知错误';
      crawlerState.value.isRunning = false;
      console.error('启动爬虫失败:', errors.value.crawler);
    } finally {
      loading.value.crawler = false;
    }
  }

  /**
   * 轮询爬虫任务状态
   */
  async function pollCrawler() {
    if (!crawlerState.value.currentTaskId) {
      console.error('没有有效的任务ID');
      return;
    }

    try {
      const finalTask = await apiClient.pollTaskStatus(
        crawlerState.value.currentTaskId,
        120,
        2000,
        (progress: number, message: string) => {
          crawlerState.value.progress = progress;
          crawlerState.value.message = message;
          console.log(`爬虫进度: ${progress}% - ${message}`);
        }
      );

      if (finalTask.status === 'completed') {
        crawlerState.value.lastResult = finalTask.result;
        console.log('爬虫完成，数据已保存');

        // 重新加载所有数据
        await refreshAllData();
      } else if (finalTask.status === 'failed') {
        throw new Error(`爬虫执行失败: ${finalTask.error || '未知错误'}`);
      } else if (finalTask.status === 'stopped') {
        console.log('爬虫已停止');
      }
    } catch (error: any) {
      errors.value.crawler = error?.message || '爬虫轮询失败';
      console.error('爬虫轮询失败:', error);
    } finally {
      crawlerState.value.isRunning = false;
    }
  }

  /**
   * 停止爬虫
   */
  async function stopCrawler() {
    if (!crawlerState.value.currentTaskId) {
      console.error('没有运行中的任务');
      return;
    }

    try {
      await apiClient.stopCrawlerTask(crawlerState.value.currentTaskId);
      console.log('爬虫已停止');
      crawlerState.value.isRunning = false;
    } catch (error: any) {
      errors.value.crawler = error?.message || '停止爬虫失败';
      console.error('停止爬虫失败:', error);
    }
  }

  /**
   * 刷新所有数据
   */
  async function refreshAllData() {
    console.log('刷新所有数据...');
    const promises = [
      fetchDashboard(),
      fetchTrends(),
      fetchUsers(),
      fetchTags(),
      fetchQuestions(),
    ];

    await Promise.all(promises);
    console.log('所有数据刷新完成');
  }

  /**
   * 设置爬虫配置
   */
  function setCrawlerConfig(config: Partial<typeof crawlerConfig.value>) {
    crawlerConfig.value = { ...crawlerConfig.value, ...config };
  }

  /**
   * 清空所有数据
   */
  function clearAllData() {
    dashboardData.value = null;
    trendsData.value = null;
    usersData.value = null;
    tagsData.value = null;
    questionsData.value = null;
  }

  /**
   * 清空所有错误
   */
  function clearAllErrors() {
    errors.value = {
      dashboard: null,
      trends: null,
      users: null,
      tags: null,
      questions: null,
      crawler: null,
    };
  }

  // ==================== 返回接口 ====================

  return {
    // 状态
    dashboardData,
    trendsData,
    usersData,
    tagsData,
    questionsData,
    loading,
    errors,
    crawlerState,
    crawlerConfig,

    // 计算属性
    isLoading,
    hasErrors,
    hasDashboardData,
    getAllErrors,

    // 方法
    fetchDashboard,
    fetchTrends,
    fetchUsers,
    fetchTags,
    fetchQuestions,
    startCrawler,
    stopCrawler,
    pollCrawler,
    refreshAllData,
    setCrawlerConfig,
    clearAllData,
    clearAllErrors,
  };
});
