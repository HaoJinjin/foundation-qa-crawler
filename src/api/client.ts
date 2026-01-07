/**
 * API 客户端 - 统一的后端通信层
 * 负责所有HTTP请求、错误处理、拦截等
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

// ==================== 类型定义 ====================

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
  error?: {
    type: string;
    details: string;
  };
  timestamp?: string;
}

export interface CrawlerStartResponse {
  task_id: string;
  status: string;
  progress: number;
  message?: string;
}

export interface CrawlerTaskResponse {
  task_id: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  progress: number;
  message: string;
  current_page: number;
  total_pages: number;
  result?: any;
  error?: string;
}

export interface DashboardData {
  basic_stats: {
    total_questions: number;
    total_views: number;
    total_likes: number;
    total_answers: number;
    total_reputation: number;
    total_users: number;
    avg_views: number;
    avg_likes: number;
    avg_answers: number;
    max_views: number;
    min_views: number;
  };
  top_questions: Array<any>;
  top_users: Array<any>;
  top_tags: Array<any>;
}

export interface TrendsData {
  granularity: string;
  data: Array<{
    period: string;
    question_count: number;
    total_views: number;
    total_likes: number;
    total_answers: number;
  }>;
}

export interface UsersData {
  total_users: number;
  avg_questions_per_user: number;
  users: Array<any>;
}

export interface TagsData {
  total_tags: number;
  tags: Array<{
    tag: string;
    count: number;
  }>;
}

export interface QuestionsListData {
  total: number;
  page: number;
  limit: number;
  pages: number;
  questions: Array<any>;
}

export interface SystemStatus {
  status: string;
  version: string;
  timestamp: string;
  cache_enabled: boolean;
  tasks_running: number;
}

// ==================== API客户端类 ====================

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:5000/api/v1') {
    this.baseURL = baseURL;

    // 创建axios实例
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // 可以在这里添加token等
        // config.headers.Authorization = `Bearer ${token}`;
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.status}`, response.data);
        return response;
      },
      (error: AxiosError<ApiResponse>) => {
        console.error('[API Response Error]', error);

        // 统一错误处理
        if (error.response) {
          const { status, data } = error.response;
          console.error(`API Error ${status}:`, data?.message || '未知错误');
        } else if (error.request) {
          console.error('没有收到响应:', error.request);
        } else {
          console.error('请求配置错误:', error.message);
        }

        return Promise.reject(error);
      }
    );
  }

  // ==================== 爬虫接口 ====================

  /**
   * 启动爬虫
   */
  async startCrawler(
    maxPages: number = 10,
    timeout: number = 30,
    asyncMode: boolean = true
  ): Promise<ApiResponse<CrawlerStartResponse>> {
    return this.client.post('/crawler/start', {
      max_pages: maxPages,
      timeout,
      async: asyncMode,
    });
  }

  /**
   * 查询爬虫任务状态
   */
  async getCrawlerTask(taskId: string): Promise<ApiResponse<CrawlerTaskResponse>> {
    return this.client.get(`/crawler/task/${taskId}`);
  }

  /**
   * 停止爬虫任务
   */
  async stopCrawlerTask(taskId: string): Promise<ApiResponse> {
    return this.client.post(`/crawler/stop/${taskId}`);
  }

  // ==================== 分析接口 ====================

  /**
   * 获取Dashboard数据
   */
  async getDashboard(
    useCache: boolean = true,
    cacheTtl: number = 3600
  ): Promise<ApiResponse<DashboardData>> {
    return this.client.get('/analysis/dashboard', {
      params: {
        use_cache: useCache,
        cache_ttl: cacheTtl,
      },
    });
  }

  /**
   * 获取趋势数据
   */
  async getTrends(
    granularity: string = 'monthly',
    startDate?: string,
    endDate?: string,
    useCache: boolean = true,
    cacheTtl: number = 7200
  ): Promise<ApiResponse<TrendsData>> {
    return this.client.get('/analysis/trends', {
      params: {
        start_date: startDate,
        end_date: endDate,
        granularity,
        use_cache: useCache,
        cache_ttl: cacheTtl,
      },
    });
  }

  /**
   * 获取用户分析数据
   */
  async getUsersAnalysis(
    limit: number = 10,
    sortBy: string = 'question_count',
    useCache: boolean = true,
    cacheTtl: number = 3600
  ): Promise<ApiResponse<UsersData>> {
    return this.client.get('/analysis/users', {
      params: {
        limit,
        sort_by: sortBy,
        use_cache: useCache,
        cache_ttl: cacheTtl,
      },
    });
  }

  /**
   * 获取标签分析数据
   */
  async getTagsAnalysis(
    limit: number = 15,
    useCache: boolean = true,
    cacheTtl: number = 7200
  ): Promise<ApiResponse<TagsData>> {
    return this.client.get('/analysis/tags', {
      params: {
        limit,
        use_cache: useCache,
        cache_ttl: cacheTtl,
      },
    });
  }

  /**
   * 获取问题列表
   */
  async getQuestionsList(
    page: number = 1,
    limit: number = 20,
    sortBy: string = 'views',
    order: string = 'desc',
    search?: string
  ): Promise<ApiResponse<QuestionsListData>> {
    return this.client.get('/analysis/questions', {
      params: {
        page,
        limit,
        sort_by: sortBy,
        order,
        search,
      },
    });
  }

  // ==================== 系统接口 ====================

  /**
   * 获取系统状态
   */
  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    return this.client.get('/system/status');
  }

  /**
   * 获取缓存状态
   */
  async getCacheStatus(): Promise<ApiResponse> {
    return this.client.get('/system/cache-status');
  }

  /**
   * 清空缓存
   */
  async clearCache(cacheKeys?: string[]): Promise<ApiResponse> {
    if (cacheKeys) {
      return this.client.post('/system/cache-clear', {
        cache_keys: cacheKeys,
      });
    }
    return this.client.post('/system/cache-clear');
  }

  // ==================== 工具方法 ====================

  /**
   * 轮询获取任务状态（用于异步爬虫）
   */
  async pollTaskStatus(
    taskId: string,
    maxAttempts: number = 120,
    intervalMs: number = 2000,
    onProgress?: (progress: number, message: string) => void
  ): Promise<CrawlerTaskResponse> {
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await this.getCrawlerTask(taskId);

        if (response.data) {
          const task = response.data;

          // 调用进度回调
          if (onProgress) {
            onProgress(task.progress, task.message);
          }

          // 任务完成或失败
          if (task.status === 'completed' || task.status === 'failed' || task.status === 'stopped') {
            return task;
          }
        }

        // 等待后再继续轮询
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
        attempts++;
      } catch (error) {
        console.error('轮询任务状态失败:', error);
        throw error;
      }
    }

    throw new Error('任务执行超时');
  }

  /**
   * 设置基础URL
   */
  setBaseURL(url: string): void {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }

  /**
   * 获取基础URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }
}

// 导出单例
export const apiClient = new ApiClient();

export default apiClient;
