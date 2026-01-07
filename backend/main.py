"""
天工开物问答站数据爬取与分析系统 - 后端服务
FastAPI + 异步爬虫 + 缓存系统
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import re
import time

# ==================== 配置设置 ====================

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'backendData', 'output')
INPUT_DIR = os.path.join(BASE_DIR, 'backendData', 'input')

# 创建必要的目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI应用
app = FastAPI(
    title="天工开物数据分析API",
    description="问答网站数据爬取与分析系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源，生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class CrawlerRequest(BaseModel):
    """爬虫请求模型"""
    max_pages: int = 10
    timeout: int = 30
    async_mode: bool = True


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    granularity: str = "monthly"  # daily, weekly, monthly


class ExportRequest(BaseModel):
    """导出请求模型"""
    format: str = "csv"  # csv, excel, json
    data_type: str = "questions"  # questions, users, tags, all


# ==================== 缓存管理 ====================

class CacheManager:
    """简单的内存缓存管理器"""
    def __init__(self):
        self.cache = {}
        self.expires = {}

    def get(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key not in self.cache:
            return None

        # 检查过期
        if key in self.expires and datetime.now() > self.expires[key]:
            del self.cache[key]
            del self.expires[key]
            return None

        return self.cache[key]

    def set(self, key: str, value: Dict, ttl: int = 3600):
        """设置缓存"""
        self.cache[key] = value
        self.expires[key] = datetime.now() + timedelta(seconds=ttl)
        logger.info(f"缓存已设置: {key}, TTL: {ttl}秒")

    def clear(self, key: Optional[str] = None):
        """清空缓存"""
        if key:
            if key in self.cache:
                del self.cache[key]
            if key in self.expires:
                del self.expires[key]
            logger.info(f"缓存已清空: {key}")
        else:
            self.cache.clear()
            self.expires.clear()
            logger.info("所有缓存已清空")

    def status(self) -> Dict:
        """获取缓存状态"""
        return {
            "cache_enabled": True,
            "cache_items": len(self.cache),
            "items": [
                {
                    "key": key,
                    "created_at": (datetime.now() - timedelta(seconds=300)).isoformat(),
                    "expires_at": self.expires[key].isoformat() if key in self.expires else None
                }
                for key in self.cache.keys()
            ]
        }


# 全局缓存实例
cache_manager = CacheManager()

# ==================== 任务管理 ====================

class TaskManager:
    """爬虫任务管理器"""
    def __init__(self):
        self.tasks = {}

    def create_task(self, task_id: str, max_pages: int):
        """创建任务"""
        self.tasks[task_id] = {
            "id": task_id,
            "status": "running",
            "progress": 0,
            "current_page": 0,
            "total_pages": max_pages,
            "message": "正在初始化...",
            "created_at": datetime.now().isoformat(),
            "result": None
        }
        logger.info(f"任务已创建: {task_id}")

    def update_progress(self, task_id: str, progress: int, message: str = "", current_page: int = 0):
        """更新任务进度"""
        if task_id in self.tasks:
            self.tasks[task_id]["progress"] = progress
            self.tasks[task_id]["message"] = message
            if current_page > 0:
                self.tasks[task_id]["current_page"] = current_page
            logger.info(f"任务进度: {task_id} - {progress}% - {message}")

    def complete_task(self, task_id: str, result: Dict):
        """完成任务"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["progress"] = 100
            self.tasks[task_id]["result"] = result
            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
            logger.info(f"任务已完成: {task_id}")

    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = error
            self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
            logger.error(f"任务失败: {task_id} - {error}")

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_id)

    def stop_task(self, task_id: str):
        """停止任务"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "stopped"
            logger.info(f"任务已停止: {task_id}")


# 全局任务管理器
task_manager = TaskManager()

# ==================== 爬虫模块 ====================

class AnswerSiteCrawler:
    """天工开物问答站爬虫"""

    BASE_URL = "https://answer.chancefoundation.org.cn"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    async def fetch_all_questions(self, max_pages: int = 10, task_id: str = None) -> List[Dict]:
        """异步爬取所有页面问题数据"""
        all_questions = []

        for page in range(1, max_pages + 1):
            try:
                # 更新进度
                if task_id:
                    task_manager.update_progress(
                        task_id,
                        int((page - 1) / max_pages * 100),
                        f"正在爬取第{page}页...",
                        page
                    )

                page_data = await self._fetch_single_page_async(page)

                if not page_data:
                    logger.info(f"第{page}页无数据，停止爬取")
                    break

                all_questions.extend(page_data)
                logger.info(f"第{page}页: 抓到{len(page_data)}个问题，累计{len(all_questions)}个")

                # 礼貌延迟
                await asyncio.sleep(1.5)

            except Exception as e:
                logger.error(f"第{page}页爬取失败: {e}")
                if task_id:
                    task_manager.fail_task(task_id, str(e))
                break

        if task_id:
            task_manager.update_progress(task_id, 100, "爬取完成，正在整理数据...")

        return all_questions

    async def _fetch_single_page_async(self, page_num: int) -> List[Dict]:
        """异步爬取单个页面"""
        # 在线程池中运行同步爬虫逻辑
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_single_page_sync, page_num)

    def _fetch_single_page_sync(self, page_num: int) -> List[Dict]:
        """同步爬取单个页面"""
        try:
            if page_num == 1:
                url = f"{self.BASE_URL}/questions"
            else:
                url = f"{self.BASE_URL}/questions?page={page_num}"

            logger.info(f"爬取: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            question_items = soup.find_all('div', class_='list-group-item')

            if not question_items:
                logger.warning(f"第{page_num}页未找到问题元素")
                return []

            page_questions = []
            for item in question_items:
                question_data = self._extract_question_data(item, page_num)
                if question_data:
                    page_questions.append(question_data)

            return page_questions

        except Exception as e:
            logger.error(f"爬取第{page_num}页失败: {e}")
            return []

    def _extract_question_data(self, question_item, page_num: int) -> Optional[Dict]:
        """提取问题数据"""
        try:
            title_elem = question_item.find('a', class_='link-dark')
            title = title_elem.text.strip() if title_elem else "未知标题"
            question_link = title_elem['href'] if title_elem else ""

            user_elem = question_item.find('a', href=re.compile(r'/users/'))
            user = user_elem.text.strip() if user_elem else "匿名用户"

            reputation_elem = question_item.find('span', title='Reputation')
            reputation = int(reputation_elem.text.strip()) if reputation_elem else 0

            time_elem = question_item.find('time')
            asked_time = time_elem.text.strip().replace('asked', '').strip() if time_elem else "未知时间"

            datetime_str = ""
            if time_elem and 'datetime' in time_elem.attrs:
                datetime_str = time_elem['datetime']

            likes = self._extract_stat(question_item, 'bi-hand-thumbs-up-fill')
            answers = self._extract_stat(question_item, 'bi-chat-square-text-fill')
            views = self._extract_stat(question_item, 'bi-eye-fill')

            tags = self._extract_tags(question_item)
            question_id = self._extract_question_id(question_link)

            full_question_url = f"{self.BASE_URL}{question_link}" if question_link else ""
            full_user_url = f"{self.BASE_URL}{user_elem['href']}" if user_elem else ""

            return {
                'id': question_id,
                'title': title,
                'user': user,
                'reputation': reputation,
                'asked_time': asked_time,
                'precise_time': datetime_str,
                'likes': likes,
                'answers': answers,
                'views': views,
                'tags': tags,
                'question_link': full_question_url,
                'user_link': full_user_url,
                'crawled_at': datetime.now().isoformat(),
                'source_page': page_num
            }

        except Exception as e:
            logger.error(f"提取问题数据失败: {e}")
            return None

    def _extract_stat(self, element, icon_class: str) -> int:
        """提取统计数字"""
        try:
            elem = element.find('i', class_=icon_class)
            if elem:
                stat_elem = elem.find_next('em')
                if stat_elem:
                    return int(stat_elem.text.strip())
        except:
            pass
        return 0

    def _extract_tags(self, element) -> List[str]:
        """提取标签"""
        tags = []
        try:
            tag_elems = element.find_all('a', class_='badge-tag')
            for tag_elem in tag_elems:
                span = tag_elem.find('span')
                if span:
                    tags.append(span.text.strip())
        except:
            pass
        return tags

    def _extract_question_id(self, question_link: str) -> str:
        """提取问题ID"""
        try:
            match = re.search(r'/questions/(\d+)', question_link)
            return match.group(1) if match else ""
        except:
            return ""


# ==================== 分析模块 ====================

class DataAnalyzer:
    """数据分析器"""

    @staticmethod
    def analyze_basic_stats(questions: List[Dict]) -> Dict:
        """基础统计分析"""
        if not questions:
            return {}

        df = pd.DataFrame(questions)

        return {
            "total_questions": len(df),
            "total_views": int(df['views'].sum()),
            "total_likes": int(df['likes'].sum()),
            "total_answers": int(df['answers'].sum()),
            "total_reputation": int(df['reputation'].sum()),
            "total_users": int(df['user'].nunique()),
            "avg_views": float(df['views'].mean()),
            "avg_likes": float(df['likes'].mean()),
            "avg_answers": float(df['answers'].mean()),
            "max_views": int(df['views'].max()),
            "min_views": int(df['views'].min()),
        }

    @staticmethod
    def get_top_questions(questions: List[Dict], limit: int = 10) -> List[Dict]:
        """获取最热门问题"""
        if not questions:
            return []

        df = pd.DataFrame(questions)
        top_df = df.nlargest(limit, 'views')[
            ['id', 'title', 'views', 'likes', 'answers', 'asked_time', 'question_link', 'user']
        ]

        return top_df.to_dict('records')

    @staticmethod
    def get_top_users(questions: List[Dict], limit: int = 5) -> List[Dict]:
        """获取最活跃用户"""
        if not questions:
            return []

        df = pd.DataFrame(questions)
        user_stats = df.groupby('user').agg({
            'views': 'sum',
            'likes': 'sum',
            'answers': 'sum',
            'title': 'count',
            'reputation': 'max'
        }).rename(columns={'title': 'question_count'}).sort_values('question_count', ascending=False)

        top_users = user_stats.head(limit).reset_index()
        return [
            {
                "user": row['user'],
                "question_count": int(row['question_count']),
                "total_views": int(row['views']),
                "total_likes": int(row['likes']),
                "total_answers": int(row['answers']),
                "reputation": int(row['reputation'])
            }
            for _, row in top_users.iterrows()
        ]

    @staticmethod
    def get_top_tags(questions: List[Dict], limit: int = 15) -> List[Dict]:
        """获取热门标签"""
        if not questions:
            return []

        all_tags = []
        for tags in [q.get('tags', []) for q in questions]:
            if isinstance(tags, list):
                all_tags.extend(tags)
            elif isinstance(tags, str):
                all_tags.extend([t.strip() for t in tags.split(',')])

        if not all_tags:
            return []

        tag_counts = Counter(all_tags)
        return [
            {"tag": tag, "count": count}
            for tag, count in tag_counts.most_common(limit)
        ]

    @staticmethod
    def get_trends(questions: List[Dict], granularity: str = "monthly") -> Dict:
        """获取趋势数据"""
        if not questions:
            return {}

        df = pd.DataFrame(questions)
        df['date'] = pd.to_datetime(df['precise_time'], errors='coerce')

        if granularity == "monthly":
            df['period'] = df['date'].dt.to_period('M')
        elif granularity == "weekly":
            df['period'] = df['date'].dt.to_period('W')
        else:  # daily
            df['period'] = df['date'].dt.to_period('D')

        trends = df.groupby('period').agg({
            'views': 'sum',
            'likes': 'sum',
            'answers': 'sum',
            'title': 'count'
        }).rename(columns={'title': 'question_count'})

        return {
            "granularity": granularity,
            "data": [
                {
                    "period": str(idx),
                    "question_count": int(row['question_count']),
                    "total_views": int(row['views']),
                    "total_likes": int(row['likes']),
                    "total_answers": int(row['answers'])
                }
                for idx, row in trends.iterrows()
            ]
        }

    @staticmethod
    def get_user_analysis(questions: List[Dict], limit: int = 10) -> Dict:
        """用户分析"""
        if not questions:
            return {}

        df = pd.DataFrame(questions)
        user_stats = df.groupby('user').agg({
            'views': 'sum',
            'likes': 'sum',
            'answers': 'sum',
            'title': 'count',
            'reputation': 'max'
        }).rename(columns={'title': 'question_count'}).sort_values('question_count', ascending=False)

        top_users = user_stats.head(limit).reset_index()

        return {
            "total_users": int(df['user'].nunique()),
            "avg_questions_per_user": float(user_stats['question_count'].mean()),
            "users": [
                {
                    "rank": i + 1,
                    "user": row['user'],
                    "question_count": int(row['question_count']),
                    "total_views": int(row['views']),
                    "total_likes": int(row['likes']),
                    "total_answers": int(row['answers']),
                    "reputation": int(row['reputation'])
                }
                for i, (_, row) in enumerate(top_users.iterrows())
            ]
        }


# ==================== API 路由 ====================

# 全局爬虫实例
crawler = AnswerSiteCrawler()

@app.get("/api/v1/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "code": 200,
        "message": "系统状态正常",
        "data": {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "cache_enabled": True,
            "tasks_running": sum(1 for t in task_manager.tasks.values() if t['status'] == 'running')
        }
    }


@app.post("/api/v1/crawler/start")
async def start_crawler(request: CrawlerRequest, background_tasks: BackgroundTasks):
    """启动爬虫"""
    import uuid

    try:
        # 验证参数
        if request.max_pages < 1 or request.max_pages > 50:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "message": "参数验证失败",
                    "error": {
                        "type": "ValidationError",
                        "details": "max_pages 必须在 1-50 之间"
                    }
                }
            )

        # 创建任务ID
        task_id = f"crawler_task_{uuid.uuid4().hex[:12]}"

        # 创建任务
        task_manager.create_task(task_id, request.max_pages)

        # 异步执行爬虫
        async def run_crawler():
            try:
                logger.info(f"开始执行爬虫任务: {task_id}")
                questions = await crawler.fetch_all_questions(request.max_pages, task_id)

                # 执行分析
                task_manager.update_progress(task_id, 100, "正在分析数据...")

                basic_stats = DataAnalyzer.analyze_basic_stats(questions)
                top_questions = DataAnalyzer.get_top_questions(questions, 10)
                top_users = DataAnalyzer.get_top_users(questions, 5)
                top_tags = DataAnalyzer.get_top_tags(questions, 15)

                result = {
                    "total_questions": len(questions),
                    "basic_stats": basic_stats,
                    "top_questions": top_questions,
                    "top_users": top_users,
                    "top_tags": top_tags,
                    "questions": questions,
                    "completed_at": datetime.now().isoformat()
                }

                # 保存到本地JSON
                json_file = os.path.join(OUTPUT_DIR, f'crawler_result_{task_id}.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"爬虫数据已保存: {json_file}")

                task_manager.complete_task(task_id, result)

            except Exception as e:
                logger.error(f"爬虫执行失败: {e}")
                task_manager.fail_task(task_id, str(e))

        if request.async_mode:
            # 异步模式：立即返回task_id，后台执行爬虫
            background_tasks.add_task(run_crawler)

            return JSONResponse(
                status_code=202,
                content={
                    "code": 202,
                    "message": "爬虫任务已提交",
                    "data": {
                        "task_id": task_id,
                        "status": "running",
                        "progress": 0,
                        "message": "爬虫正在初始化..."
                    }
                }
            )
        else:
            # 同步模式：等待爬虫完成
            await run_crawler()

            task = task_manager.get_task(task_id)

            if task['status'] == 'completed':
                return {
                    "code": 200,
                    "message": "爬虫执行成功",
                    "data": task['result']
                }
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "code": 500,
                        "message": "爬虫执行失败",
                        "error": task.get('error', '未知错误')
                    }
                )

    except Exception as e:
        logger.error(f"爬虫启动失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "服务器错误",
                "error": str(e)
            }
        )


@app.get("/api/v1/crawler/task/{task_id}")
async def get_crawler_task(task_id: str):
    """查询爬虫任务状态"""
    task = task_manager.get_task(task_id)

    if not task:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "任务不存在",
                "error": "指定的task_id未找到"
            }
        )

    response_data = {
        "task_id": task['id'],
        "status": task['status'],
        "progress": task['progress'],
        "message": task.get('message', ''),
        "current_page": task.get('current_page', 0),
        "total_pages": task['total_pages']
    }

    if task['status'] == 'completed':
        response_data['result'] = task['result']
    elif task['status'] == 'failed':
        response_data['error'] = task.get('error', '未知错误')

    return {
        "code": 200,
        "message": "任务信息获取成功",
        "data": response_data
    }


@app.post("/api/v1/crawler/stop/{task_id}")
async def stop_crawler_task(task_id: str):
    """停止爬虫任务"""
    task = task_manager.get_task(task_id)

    if not task:
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "任务不存在"
            }
        )

    task_manager.stop_task(task_id)

    return {
        "code": 200,
        "message": "任务已停止",
        "data": {
            "task_id": task_id,
            "status": "stopped"
        }
    }


@app.get("/api/v1/analysis/dashboard")
async def get_dashboard_data(
    use_cache: bool = Query(True),
    cache_ttl: int = Query(3600)
):
    """获取仪表板数据"""
    try:
        cache_key = "dashboard_data"

        # 尝试从缓存获取
        if use_cache:
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                logger.info("从缓存返回仪表板数据")
                return {
                    "code": 200,
                    "message": "仪表板数据获取成功（缓存）",
                    "data": cached_data
                }

        # 读取最新的爬虫数据文件
        json_files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.startswith('crawler_result_') and f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if not json_files:
            # 如果没有爬虫数据，返回空数据
            data = {
                "basic_stats": {},
                "top_questions": [],
                "top_users": [],
                "top_tags": []
            }
        else:
            # 读取最新的数据文件
            with open(os.path.join(OUTPUT_DIR, json_files[0]), 'r', encoding='utf-8') as f:
                crawler_result = json.load(f)

            data = {
                "basic_stats": crawler_result.get('basic_stats', {}),
                "top_questions": crawler_result.get('top_questions', []),
                "top_users": crawler_result.get('top_users', []),
                "top_tags": crawler_result.get('top_tags', [])
            }

        # 缓存数据
        cache_manager.set(cache_key, data, cache_ttl)

        return {
            "code": 200,
            "message": "仪表板数据获取成功",
            "data": data
        }

    except Exception as e:
        logger.error(f"获取仪表板数据失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取仪表板数据失败",
                "error": str(e)
            }
        )


@app.get("/api/v1/analysis/trends")
async def get_trends_data(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    granularity: str = Query("monthly"),
    use_cache: bool = Query(True),
    cache_ttl: int = Query(7200)
):
    """获取趋势数据"""
    try:
        cache_key = f"trends_{granularity}_{start_date}_{end_date}"

        if use_cache:
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return {
                    "code": 200,
                    "message": "趋势数据获取成功（缓存）",
                    "data": cached_data
                }

        # 读取最新的爬虫数据
        json_files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.startswith('crawler_result_') and f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if not json_files:
            return {
                "code": 200,
                "message": "暂无数据",
                "data": {"data": []}
            }

        with open(os.path.join(OUTPUT_DIR, json_files[0]), 'r', encoding='utf-8') as f:
            crawler_result = json.load(f)

        questions = crawler_result.get('questions', [])
        trends = DataAnalyzer.get_trends(questions, granularity)

        cache_manager.set(cache_key, trends, cache_ttl)

        return {
            "code": 200,
            "message": "趋势数据获取成功",
            "data": trends
        }

    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取趋势数据失败",
                "error": str(e)
            }
        )


@app.get("/api/v1/analysis/users")
async def get_users_analysis(
    limit: int = Query(10),
    sort_by: str = Query("question_count"),
    use_cache: bool = Query(True),
    cache_ttl: int = Query(3600)
):
    """获取用户分析"""
    try:
        cache_key = f"users_analysis_{limit}_{sort_by}"

        if use_cache:
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return {
                    "code": 200,
                    "message": "用户分析数据获取成功（缓存）",
                    "data": cached_data
                }

        json_files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.startswith('crawler_result_') and f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if not json_files:
            return {
                "code": 200,
                "message": "暂无数据",
                "data": {"users": []}
            }

        with open(os.path.join(OUTPUT_DIR, json_files[0]), 'r', encoding='utf-8') as f:
            crawler_result = json.load(f)

        questions = crawler_result.get('questions', [])
        user_analysis = DataAnalyzer.get_user_analysis(questions, limit)

        cache_manager.set(cache_key, user_analysis, cache_ttl)

        return {
            "code": 200,
            "message": "用户分析数据获取成功",
            "data": user_analysis
        }

    except Exception as e:
        logger.error(f"获取用户分析失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取用户分析失败",
                "error": str(e)
            }
        )


@app.get("/api/v1/analysis/tags")
async def get_tags_analysis(
    limit: int = Query(15),
    use_cache: bool = Query(True),
    cache_ttl: int = Query(7200)
):
    """获取标签分析"""
    try:
        cache_key = f"tags_analysis_{limit}"

        if use_cache:
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                return {
                    "code": 200,
                    "message": "标签分析数据获取成功（缓存）",
                    "data": cached_data
                }

        json_files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.startswith('crawler_result_') and f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if not json_files:
            return {
                "code": 200,
                "message": "暂无数据",
                "data": {"tags": []}
            }

        with open(os.path.join(OUTPUT_DIR, json_files[0]), 'r', encoding='utf-8') as f:
            crawler_result = json.load(f)

        questions = crawler_result.get('questions', [])
        tags = DataAnalyzer.get_top_tags(questions, limit)

        data = {
            "total_tags": len(tags),
            "tags": tags
        }

        cache_manager.set(cache_key, data, cache_ttl)

        return {
            "code": 200,
            "message": "标签分析数据获取成功",
            "data": data
        }

    except Exception as e:
        logger.error(f"获取标签分析失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取标签分析失败",
                "error": str(e)
            }
        )


@app.get("/api/v1/analysis/questions")
async def get_questions_list(
    page: int = Query(1),
    limit: int = Query(20),
    sort_by: str = Query("views"),
    order: str = Query("desc"),
    search: Optional[str] = Query(None)
):
    """获取问题列表"""
    try:
        json_files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.startswith('crawler_result_') and f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
            reverse=True
        )

        if not json_files:
            return {
                "code": 200,
                "message": "暂无数据",
                "data": {
                    "total": 0,
                    "page": page,
                    "limit": limit,
                    "pages": 0,
                    "questions": []
                }
            }

        with open(os.path.join(OUTPUT_DIR, json_files[0]), 'r', encoding='utf-8') as f:
            crawler_result = json.load(f)

        questions = crawler_result.get('questions', [])

        # 搜索过滤
        if search:
            questions = [q for q in questions if search.lower() in q.get('title', '').lower()]

        # 排序
        reverse = order.lower() == 'desc'
        questions = sorted(questions, key=lambda x: x.get(sort_by, 0), reverse=reverse)

        # 分页
        total = len(questions)
        pages = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit

        return {
            "code": 200,
            "message": "问题列表获取成功",
            "data": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": pages,
                "questions": questions[start:end]
            }
        }

    except Exception as e:
        logger.error(f"获取问题列表失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "获取问题列表失败",
                "error": str(e)
            }
        )


@app.get("/api/v1/system/cache-status")
async def get_cache_status():
    """获取缓存状态"""
    return {
        "code": 200,
        "message": "缓存状态获取成功",
        "data": cache_manager.status()
    }


@app.post("/api/v1/system/cache-clear")
async def clear_cache(cache_keys: Optional[List[str]] = None):
    """清空缓存"""
    if cache_keys:
        for key in cache_keys:
            cache_manager.clear(key)
        cleared_count = len(cache_keys)
    else:
        cache_manager.clear()
        cleared_count = len(cache_manager.cache)

    return {
        "code": 200,
        "message": "缓存已清空",
        "data": {
            "cleared_count": cleared_count
        }
    }


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "天工开物数据分析API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==================== 启动脚本 ====================

if __name__ == "__main__":
    import uvicorn

    logger.info("正在启动天工开物数据分析API服务...")
    logger.info("访问地址: http://localhost:5000")
    logger.info("API文档: http://localhost:5000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
