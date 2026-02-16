#!/usr/bin/env python
# coding: utf-8
import os
import sys

# 获取脚本所在目录的父目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'backendData', 'output')
INPUT_DIR = os.path.join(BASE_DIR, 'backendData', 'input')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# In[6]:


#解析页面结构
import requests

url = "http://localhost:3000/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)

# 保存原始响应
with open(os.path.join(OUTPUT_DIR, 'debug_output.txt'), 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"状态码: {response.status_code}")
print(f"内容大小: {len(response.text)} 字符")

# 查找关键信息
lines = response.text.split('\n')
print("\n包含'回答于'的行:")
for i, line in enumerate(lines):
    if '回答于' in line:
        print(f"行 {i}: {line.strip()[:100]}")

print("\n请将 debug_output.txt 文件的前1000字符发给我")


# In[7]:


# 尝试爬取第一页数据
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def fetch_all_questions(base_url, max_pages=10):
    """
    抓取所有页面问题数据
    """
    all_questions = []
    page = 1
    
    while page <= max_pages:
        # 构建页面URL
        if page == 1:
            url = base_url + "questions"
        else:
            url = f"{base_url}questions?page={page}"
        
        print(f"正在抓取第 {page} 页: {url}")
        
        try:
            # 发送请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"第 {page} 页请求失败: {response.status_code}")
                break
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找问题列表
            question_items = soup.find_all('div', class_='list-group-item')
            
            if not question_items:
                print(f"第 {page} 页没有找到问题")
                break
            
            print(f"第 {page} 页找到 {len(question_items)} 个问题")
            
            # 提取每个问题的数据
            for item in question_items:
                question_data = extract_question_data(item)
                if question_data:
                    all_questions.append(question_data)
            
            # 检查是否有下一页
            next_page = soup.find('a', string='Next')
            if not next_page or page >= max_pages:
                break
            
            page += 1
            time.sleep(1)  # 礼貌等待
            
        except Exception as e:
            print(f"抓取第 {page} 页时出错: {e}")
            break
    
    return all_questions

def extract_question_data(question_item):
    """
    从单个问题元素中提取数据
    """
    try:
        # 提取问题标题
        title_elem = question_item.find('a', class_='link-dark')
        title = title_elem.text.strip() if title_elem else "未知标题"
        
        # 提取问题链接
        question_link = title_elem['href'] if title_elem else ""
        
        # 提取用户信息
        user_elem = question_item.find('a', href=re.compile(r'/users/'))
        user = user_elem.text.strip() if user_elem else "匿名用户"
        
        # 提取声望值
        reputation_elem = question_item.find('span', title='Reputation')
        reputation = int(reputation_elem.text.strip()) if reputation_elem else 0
        
        # 提取提问时间 - 查找time标签
        time_elem = question_item.find('time')
        asked_time = time_elem.text.strip().replace('asked', '').strip() if time_elem else "未知时间"
        
        # 提取点赞数 - 查找包含hand-thumbs-up的i标签
        likes_elem = question_item.find('i', class_='bi-hand-thumbs-up-fill')
        if likes_elem:
            likes = int(likes_elem.find_next('em').text.strip())
        else:
            likes = 0
        
        # 提取回答数
        answers_elem = question_item.find('i', class_='bi-chat-square-text-fill')
        if answers_elem:
            answers = int(answers_elem.find_next('em').text.strip())
        else:
            answers = 0
        
        # 提取浏览数
        views_elem = question_item.find('i', class_='bi-eye-fill')
        if views_elem:
            views = int(views_elem.find_next('em').text.strip())
        else:
            views = 0
        
        # 提取标签
        tags = []
        tag_elems = question_item.find_all('a', class_='badge-tag')
        for tag_elem in tag_elems:
            tag_text = tag_elem.find('span').text.strip()
            tags.append(tag_text)
        
        # 提取datetime属性中的精确时间
        datetime_str = ""
        if time_elem and 'datetime' in time_elem.attrs:
            datetime_str = time_elem['datetime']
        
        # 提取问题ID
        question_id = ""
        if question_link:
            match = re.search(r'/questions/(\d+)', question_link)
            if match:
                question_id = match.group(1)
        
        return {
            '问题ID': question_id,
            '标题': title,
            '提问用户': user,
            '用户声望': reputation,
            '提问时间': asked_time,
            '精确时间': datetime_str,
            '点赞数': likes,
            '回答数': answers,
            '浏览数': views,
            '标签': ', '.join(tags),
            '问题链接': f"https://answer.chancefoundation.org.cn{question_link}" if question_link else "",
            '用户链接': f"https://answer.chancefoundation.org.cn{user_elem['href']}" if user_elem else ""
        }
        
    except Exception as e:
        print(f"提取问题数据时出错: {e}")
        return None

def analyze_questions_data(questions):
    """
    分析问题数据
    """
    if not questions:
        print("没有数据可分析")
        return None
    
    # 转换为DataFrame
    df = pd.DataFrame(questions)
    
    print(f"\n{'='*70}")
    print("数据分析报告")
    print(f"{'='*70}")
    
    print(f"✅ 成功抓取 {len(df)} 个问题")
    
    # 基础统计
    print(f"\n📊 基础统计:")
    print(f"  总浏览数: {df['浏览数'].sum():,}")
    print(f"  总点赞数: {df['点赞数'].sum():,}")
    print(f"  总回答数: {df['回答数'].sum():,}")
    print(f"  总用户声望: {df['用户声望'].sum():,}")
    
    # 平均值
    print(f"\n📈 平均值:")
    print(f"  平均浏览数: {df['浏览数'].mean():.1f}")
    print(f"  平均点赞数: {df['点赞数'].mean():.1f}")
    print(f"  平均回答数: {df['回答数'].mean():.1f}")
    
    # 最受欢迎的问题
    if len(df) > 0:
        top_views = df.nlargest(5, '浏览数')[['标题', '浏览数', '点赞数', '提问时间']]
        print(f"\n🔥 最受欢迎的问题（按浏览数）:")
        for i, (_, row) in enumerate(top_views.iterrows(), 1):
            print(f"  {i}. {row['标题'][:50]}...")
            print(f"     浏览: {row['浏览数']}次, 点赞: {row['点赞数']}个, 时间: {row['提问时间']}")
    
    # 用户分析
    if '提问用户' in df.columns:
        user_stats = df.groupby('提问用户').agg({
            '浏览数': 'sum',
            '点赞数': 'sum',
            '回答数': 'sum',
            '标题': 'count'
        }).rename(columns={'标题': '提问数'}).sort_values('提问数', ascending=False)
        
        print(f"\n👥 用户贡献统计:")
        print(user_stats.head(10).to_string())
    
    # 标签分析
    if '标签' in df.columns:
        # 展开标签数据
        all_tags = []
        for tags_str in df['标签']:
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split(',')]
                all_tags.extend(tags)
        
        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            
            print(f"\n🏷️ 热门标签:")
            for tag, count in tag_counts.most_common(10):
                print(f"  {tag}: {count}次")
    
    # 时间分析（如果可能）
    if '提问时间' in df.columns:
        # 提取月份信息
        try:
            df['月份'] = df['提问时间'].apply(extract_month)
            monthly_stats = df.groupby('月份').agg({
                '浏览数': 'sum',
                '点赞数': 'sum',
                '标题': 'count'
            }).rename(columns={'标题': '提问数'}).sort_index(ascending=False)
            
            print(f"\n📅 月度统计:")
            print(monthly_stats.to_string())
        except:
            pass
    
    return df

def extract_month(time_str):
    """从时间字符串中提取月份"""
    try:
        # 匹配 "Dec 2, 2025" 或类似格式
        match = re.search(r'(\w+)\s+\d+,\s+(\d{4})', time_str)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        
        # 匹配中文格式
        match = re.search(r'(\d{4})年(\d{1,2})月', time_str)
        if match:
            months_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_num = int(match.group(2))
            if 1 <= month_num <= 12:
                return f"{months_en[month_num-1]} {match.group(1)}"
        
        return time_str[:7]
    except:
        return "未知月份"

def save_data(df, output_path):
    """
    保存数据到文件
    """
    if df is None or df.empty:
        print("没有数据可保存")
        return
    
    # 保存为CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 数据已保存到 CSV: {output_path}")
    
    # 保存为Excel
    try:
        excel_path = output_path.replace('.csv', '.xlsx')
        df.to_excel(excel_path, index=False)
        print(f"💾 数据已保存到 Excel: {excel_path}")
    except Exception as e:
        print(f"Excel保存失败: {e}")
    
    # 生成详细报告
    report_path = output_path.replace('.csv', '_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("天工开物问答站数据分析报告\n")
        f.write("="*60 + "\n")
        f.write(f"生成时间: {pd.Timestamp.now()}\n")
        f.write(f"数据来源: http://localhost:3000/\n")
        f.write(f"总问题数: {len(df)}\n")
        f.write(f"总浏览数: {df['浏览数'].sum()}\n")
        f.write(f"总点赞数: {df['点赞数'].sum()}\n")
        f.write(f"总回答数: {df['回答数'].sum()}\n")
        
        # 热门问题
        f.write("\n热门问题:\n")
        top_5 = df.nlargest(5, '浏览数')
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            f.write(f"{i}. {row['标题']}\n")
            f.write(f"   浏览: {row['浏览数']}, 点赞: {row['点赞数']}, 回答: {row['回答数']}, 时间: {row['提问时间']}\n")
        
        # 详细数据
        f.write("\n详细数据:\n")
        f.write(df.to_string(index=False))
    
    print(f"📄 分析报告已保存到: {report_path}")

def main():
    """
    主函数
    """
    print(f"{'='*70}")
    print("天工开物问答站数据抓取工具")
    print(f"{'='*70}")
    
    base_url = "http://localhost:3000/"
    output_path = os.path.join(OUTPUT_DIR, 'questions_data.csv')
    
    print(f"目标网站: {base_url}")
    print(f"输出路径: {output_path}")
    
    # 抓取数据
    print("\n开始抓取数据...")
    questions = fetch_all_questions(base_url, max_pages=4)
    
    if questions:
        # 分析数据
        df = analyze_questions_data(questions)
        
        if df is not None and not df.empty:
            # 保存数据
            save_data(df, output_path)
            
            # 显示数据预览
            print(f"\n📋 数据预览（前10条）:")
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 50)
            print(df.head(10).to_string(index=False))
            
            print(f"\n✅ 任务完成！")
            print(f"   共抓取 {len(df)} 个问题")
            print(f"   数据已保存到指定路径")
        else:
            print("\n❌ 数据提取失败")
    else:
        print("\n❌ 没有抓到任何数据")

def quick_test():
    """
    快速测试函数 - 抓取第一页数据
    """
    print("快速测试 - 抓取第一页数据...")
    
    url = "http://localhost:3000/questions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找问题列表
            question_items = soup.find_all('div', class_='list-group-item')
            print(f"找到 {len(question_items)} 个问题")
            
            # 提取前3个问题作为示例
            for i, item in enumerate(question_items[:3], 1):
                data = extract_question_data(item)
                if data:
                    print(f"\n问题 {i}:")
                    print(f"  标题: {data['标题'][:50]}...")
                    print(f"  用户: {data['提问用户']}")
                    print(f"  时间: {data['提问时间']}")
                    print(f"  浏览: {data['浏览数']}, 点赞: {data['点赞数']}, 回答: {data['回答数']}")
            
            return True
        else:
            print(f"请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    return False

if __name__ == "__main__":
    # 设置pandas显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    # 首先运行快速测试
    print("运行快速测试...")
    if quick_test():
        print("\n快速测试成功，开始完整抓取...")
        main()
    else:
        print("\n快速测试失败，请检查网络或网站访问")


# In[8]:


#尝试爬取所有问答数据
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import json
from datetime import datetime
import os
from typing import List, Dict, Optional

class AnswerSiteCrawler:
    """天工开物问答站完整数据抓取器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def fetch_all_questions(self, max_pages: int = 20) -> List[Dict]:
        """
        抓取所有页面问题数据
        
        Args:
            max_pages: 最大抓取页数
            
        Returns:
            问题数据列表
        """
        all_questions = []
        page = 1
        
        print(f"开始抓取数据，最多 {max_pages} 页...")
        print("-" * 60)
        
        while page <= max_pages:
            page_data = self._fetch_single_page(page)
            
            if not page_data:
                print(f"第 {page} 页没有数据，停止抓取")
                break
            
            all_questions.extend(page_data)
            print(f"第 {page} 页: 抓到 {len(page_data)} 个问题，累计 {len(all_questions)} 个")
            
            # 检查是否有下一页
            if not self._has_next_page(page_data, page):
                print("没有下一页了，抓取完成")
                break
            
            page += 1
            time.sleep(1.5)  # 礼貌等待，避免给服务器压力
        
        print(f"\n抓取完成！共抓取 {len(all_questions)} 个问题")
        return all_questions
    
    def _fetch_single_page(self, page_num: int) -> List[Dict]:
        """
        抓取单个页面
        
        Args:
            page_num: 页码
            
        Returns:
            当前页问题数据列表
        """
        try:
            # 构建URL
            if page_num == 1:
                url = f"{self.base_url}/questions"
            else:
                url = f"{self.base_url}/questions?page={page_num}"
            
            print(f"抓取第 {page_num} 页: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 保存页面内容用于调试
            if page_num == 1:
                self._save_page_content(response.text, 'first_page.html')
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找问题列表
            question_items = soup.find_all('div', class_='list-group-item')
            
            if not question_items:
                print(f"警告: 第 {page_num} 页没有找到问题元素")
                return []
            
            # 提取问题数据
            page_questions = []
            for item in question_items:
                question_data = self._extract_question_data(item)
                if question_data:
                    question_data['来源页码'] = page_num
                    page_questions.append(question_data)
            
            return page_questions
            
        except requests.RequestException as e:
            print(f"第 {page_num} 页请求失败: {e}")
            return []
        except Exception as e:
            print(f"第 {page_num} 页解析失败: {e}")
            return []
    
    def _extract_question_data(self, question_item) -> Optional[Dict]:
        """
        从单个问题元素中提取数据
        """
        try:
            # 提取问题标题和链接
            title_elem = question_item.find('a', class_='link-dark')
            title = title_elem.text.strip() if title_elem else "未知标题"
            question_link = title_elem['href'] if title_elem else ""
            
            # 提取用户信息
            user_elem = question_item.find('a', href=re.compile(r'/users/'))
            user = user_elem.text.strip() if user_elem else "匿名用户"
            
            # 提取声望值
            reputation_elem = question_item.find('span', title='Reputation')
            reputation = int(reputation_elem.text.strip()) if reputation_elem else 0
            
            # 提取提问时间
            time_elem = question_item.find('time')
            asked_time = time_elem.text.strip().replace('asked', '').strip() if time_elem else "未知时间"
            
            # 提取精确时间（ISO格式）
            datetime_str = ""
            if time_elem and 'datetime' in time_elem.attrs:
                datetime_str = time_elem['datetime']
            
            # 提取统计信息
            likes = self._extract_stat(question_item, 'bi-hand-thumbs-up-fill')
            answers = self._extract_stat(question_item, 'bi-chat-square-text-fill')
            views = self._extract_stat(question_item, 'bi-eye-fill')
            
            # 提取标签
            tags = self._extract_tags(question_item)
            
            # 提取问题ID
            question_id = self._extract_question_id(question_link)
            
            # 构建完整URL
            full_question_url = f"{self.base_url}{question_link}" if question_link else ""
            full_user_url = f"{self.base_url}{user_elem['href']}" if user_elem else ""
            
            return {
                '问题ID': question_id,
                '标题': title,
                '提问用户': user,
                '用户声望': reputation,
                '提问时间': asked_time,
                '精确时间': datetime_str,
                '点赞数': likes,
                '回答数': answers,
                '浏览数': views,
                '标签': tags,
                '问题链接': full_question_url,
                '用户链接': full_user_url,
                '抓取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"提取问题数据时出错: {e}")
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
    
    def _extract_tags(self, element) -> str:
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
        return ', '.join(tags)
    
    def _extract_question_id(self, question_link: str) -> str:
        """提取问题ID"""
        try:
            match = re.search(r'/questions/(\d+)', question_link)
            return match.group(1) if match else ""
        except:
            return ""
    
    def _has_next_page(self, current_page_data: List, current_page: int) -> bool:
        """检查是否有下一页"""
        # 如果当前页数据少于10个，可能没有下一页
        if len(current_page_data) < 10:
            return False
        
        # 实际应该检查HTML中的分页信息，这里简化处理
        # 最多抓取20页防止无限循环
        return current_page < 20
    
    def _save_page_content(self, content: str, filename: str):
        """保存页面内容用于调试"""
        try:
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except:
            pass

class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, data: List[Dict]):
        self.df = pd.DataFrame(data)
        self.total_records = len(self.df)
    
    def analyze(self) -> Dict:
        """执行全面分析"""
        if self.total_records == 0:
            return {"error": "没有数据可分析"}
        
        analysis = {
            "basic_stats": self._get_basic_stats(),
            "top_questions": self._get_top_questions(),
            "user_analysis": self._get_user_analysis(),
            "tag_analysis": self._get_tag_analysis(),
            "time_analysis": self._get_time_analysis(),
            "page_distribution": self._get_page_distribution()
        }
        
        return analysis
    
    def _get_basic_stats(self) -> Dict:
        """获取基础统计"""
        stats = {
            "总问题数": self.total_records,
            "总浏览数": int(self.df['浏览数'].sum()),
            "总点赞数": int(self.df['点赞数'].sum()),
            "总回答数": int(self.df['回答数'].sum()),
            "总用户声望": int(self.df['用户声望'].sum()),
            "平均浏览数": float(self.df['浏览数'].mean()),
            "平均点赞数": float(self.df['点赞数'].mean()),
            "平均回答数": float(self.df['回答数'].mean()),
            "最大浏览数": int(self.df['浏览数'].max()),
            "最小浏览数": int(self.df['浏览数'].min()),
            "问题ID范围": f"{self.df['问题ID'].min()} - {self.df['问题ID'].max()}" if '问题ID' in self.df.columns else "N/A"
        }
        return stats
    
    def _get_top_questions(self, n: int = 10) -> List[Dict]:
        """获取最热门的问题"""
        if '浏览数' not in self.df.columns:
            return []
        
        top_df = self.df.nlargest(n, '浏览数')[['标题', '浏览数', '点赞数', '回答数', '提问时间', '问题链接']]
        return top_df.to_dict('records')
    
    def _get_user_analysis(self) -> Dict:
        """用户分析"""
        if '提问用户' not in self.df.columns:
            return {}
        
        user_stats = self.df.groupby('提问用户').agg({
            '浏览数': 'sum',
            '点赞数': 'sum',
            '回答数': 'sum',
            '标题': 'count',
            '用户声望': 'max'
        }).rename(columns={'标题': '提问数'}).sort_values('提问数', ascending=False)
        
        top_users = user_stats.head(10).to_dict('index')
        
        return {
            "总用户数": len(user_stats),
            "平均每个用户提问数": float(user_stats['提问数'].mean()),
            "最多提问用户": user_stats.index[0] if len(user_stats) > 0 else "N/A",
            "最高声望用户": self.df.loc[self.df['用户声望'].idxmax(), '提问用户'] if len(self.df) > 0 else "N/A",
            "前十活跃用户": top_users
        }
    
    def _get_tag_analysis(self) -> Dict:
        """标签分析"""
        if '标签' not in self.df.columns:
            return {}
        
        # 展开所有标签
        all_tags = []
        for tags_str in self.df['标签']:
            if tags_str and isinstance(tags_str, str):
                tags = [tag.strip() for tag in tags_str.split(',')]
                all_tags.extend(tags)
        
        if not all_tags:
            return {}
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        
        return {
            "总标签数": len(tag_counts),
            "最常用标签": tag_counts.most_common(10),
            "平均每个问题标签数": len(all_tags) / self.total_records if self.total_records > 0 else 0
        }
    
    def _get_time_analysis(self) -> Dict:
        """时间分析"""
        if '提问时间' not in self.df.columns:
            return {}
        
        # 提取月份
        try:
            self.df['月份'] = self.df['提问时间'].apply(self._extract_month)
            monthly_stats = self.df.groupby('月份').agg({
                '浏览数': 'sum',
                '点赞数': 'sum',
                '标题': 'count'
            }).rename(columns={'标题': '提问数'}).sort_index(ascending=False)
            
            return {
                "月度统计": monthly_stats.head(12).to_dict('index'),
                "最活跃月份": monthly_stats['提问数'].idxmax() if len(monthly_stats) > 0 else "N/A",
                "时间范围": f"{self.df['提问时间'].min()} - {self.df['提问时间'].max()}"
            }
        except:
            return {}
    
    def _get_page_distribution(self) -> Dict:
        """页面分布分析"""
        if '来源页码' not in self.df.columns:
            return {}
        
        page_stats = self.df['来源页码'].value_counts().sort_index()
        
        return {
            "总页数": len(page_stats),
            "每页问题数统计": page_stats.to_dict(),
            "平均每页问题数": float(page_stats.mean())
        }
    
    @staticmethod
    def _extract_month(time_str: str) -> str:
        """从时间字符串提取月份"""
        try:
            # 匹配英文格式: Dec 2, 2025
            match = re.search(r'(\w+)\s+\d+,\s+(\d{4})', time_str)
            if match:
                return f"{match.group(1)} {match.group(2)}"
            
            # 匹配中文格式: 2025年12月31日
            match = re.search(r'(\d{4})年(\d{1,2})月', time_str)
            if match:
                months_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month_num = int(match.group(2))
                if 1 <= month_num <= 12:
                    return f"{months_en[month_num-1]} {match.group(1)}"
            
            return time_str[:7] if len(time_str) >= 7 else time_str
        except:
            return "未知月份"

class DataExporter:
    """数据导出器"""
    
    @staticmethod
    def export_all(df: pd.DataFrame, base_filename: str):
        """导出所有格式的数据"""
        
        # 1. 导出CSV
        csv_path = f"{base_filename}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV文件已保存: {csv_path}")
        
        # 2. 导出Excel
        try:
            excel_path = f"{base_filename}.xlsx"
            df.to_excel(excel_path, index=False)
            print(f"✅ Excel文件已保存: {excel_path}")
        except Exception as e:
            print(f"⚠️  Excel保存失败: {e}")
        
        # 3. 导出JSON
        try:
            json_path = f"{base_filename}.json"
            records = df.to_dict('records')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON文件已保存: {json_path}")
        except Exception as e:
            print(f"⚠️  JSON保存失败: {e}")
        
        # 4. 生成详细报告
        report_path = f"{base_filename}_report.txt"
        DataExporter._generate_report(df, report_path)
        print(f"✅ 分析报告已保存: {report_path}")
        
        return {
            "csv": csv_path,
            "excel": excel_path if 'excel_path' in locals() else None,
            "json": json_path if 'json_path' in locals() else None,
            "report": report_path
        }
    
    @staticmethod
    def _generate_report(df: pd.DataFrame, report_path: str):
        """生成详细分析报告"""
        analyzer = DataAnalyzer(df.to_dict('records'))
        analysis = analyzer.analyze()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("天工开物问答站完整数据分析报告\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据来源: http://localhost:3000/\n")
            f.write(f"总数据量: {len(df)} 条记录\n\n")
            
            # 基础统计
            if "basic_stats" in analysis:
                f.write("📊 基础统计信息\n")
                f.write("-" * 40 + "\n")
                stats = analysis["basic_stats"]
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
            
            # 热门问题
            if "top_questions" in analysis and analysis["top_questions"]:
                f.write("🔥 最热门问题（按浏览数）\n")
                f.write("-" * 40 + "\n")
                for i, question in enumerate(analysis["top_questions"][:10], 1):
                    f.write(f"{i}. {question['标题'][:80]}...\n")
                    f.write(f"   浏览: {question['浏览数']}, 点赞: {question['点赞数']}, 回答: {question['回答数']}\n")
                    f.write(f"   时间: {question['提问时间']}\n\n")
            
            # 用户分析
            if "user_analysis" in analysis:
                f.write("👥 用户分析\n")
                f.write("-" * 40 + "\n")
                user_info = analysis["user_analysis"]
                f.write(f"总用户数: {user_info.get('总用户数', 'N/A')}\n")
                f.write(f"最多提问用户: {user_info.get('最多提问用户', 'N/A')}\n")
                f.write(f"最高声望用户: {user_info.get('最高声望用户', 'N/A')}\n\n")
            
            # 标签分析
            if "tag_analysis" in analysis and analysis["tag_analysis"]:
                f.write("🏷️ 标签分析\n")
                f.write("-" * 40 + "\n")
                tag_info = analysis["tag_analysis"]
                f.write(f"总标签数: {tag_info.get('总标签数', 'N/A')}\n")
                if "最常用标签" in tag_info:
                    f.write("最常用标签:\n")
                    for tag, count in tag_info["最常用标签"]:
                        f.write(f"  {tag}: {count}次\n")
                f.write("\n")
            
            # 详细数据表
            f.write("📋 详细数据（前50条）\n")
            f.write("-" * 40 + "\n")
            f.write(df.head(50).to_string(index=False))

def main():
    """主函数"""
    print("=" * 70)
    print("天工开物问答站 - 完整数据抓取与分析系统")
    print("=" * 70)
    
    # 配置
    BASE_URL = "https://answer.chancefoundation.org.cn"
    OUTPUT_BASE = os.path.join(OUTPUT_DIR, 'questions_data_full')
    MAX_PAGES = 20  # 最大抓取页数，根据实际情况调整
    
    print(f"目标网站: {BASE_URL}")
    print(f"输出文件: {OUTPUT_BASE}.*")
    print(f"最大页数: {MAX_PAGES}")
    print("\n" + "=" * 70)
    
    # 1. 创建爬虫实例
    crawler = AnswerSiteCrawler(BASE_URL)
    
    # 2. 抓取所有数据
    print("开始抓取数据...")
    all_questions = crawler.fetch_all_questions(max_pages=MAX_PAGES)
    
    if not all_questions:
        print("❌ 没有抓取到任何数据，程序退出")
        return
    
    print(f"\n✅ 抓取完成！共获得 {len(all_questions)} 条数据")
    
    # 3. 转换为DataFrame
    df = pd.DataFrame(all_questions)
    
    # 4. 数据分析
    print("\n" + "=" * 70)
    print("数据分析中...")
    print("=" * 70)
    
    analyzer = DataAnalyzer(all_questions)
    analysis = analyzer.analyze()
    
    # 显示关键统计
    if "basic_stats" in analysis:
        stats = analysis["basic_stats"]
        print(f"📊 关键统计:")
        print(f"  总问题数: {stats.get('总问题数', 'N/A')}")
        print(f"  总浏览数: {stats.get('总浏览数', 'N/A'):,}")
        print(f"  总点赞数: {stats.get('总点赞数', 'N/A'):,}")
        print(f"  总回答数: {stats.get('总回答数', 'N/A'):,}")
        print(f"  平均浏览数: {stats.get('平均浏览数', 'N/A'):.1f}")
    
    if "top_questions" in analysis and analysis["top_questions"]:
        print(f"\n🔥 最热门问题:")
        for i, q in enumerate(analysis["top_questions"][:3], 1):
            print(f"  {i}. {q['标题'][:60]}...")
            print(f"     浏览: {q['浏览数']}次, 时间: {q['提问时间']}")
    
    if "user_analysis" in analysis:
        user_info = analysis["user_analysis"]
        print(f"\n👥 用户统计:")
        print(f"  总用户数: {user_info.get('总用户数', 'N/A')}")
        print(f"  最多提问用户: {user_info.get('最多提问用户', 'N/A')}")
    
    # 5. 导出数据
    print("\n" + "=" * 70)
    print("导出数据...")
    print("=" * 70)
    
    export_results = DataExporter.export_all(df, OUTPUT_BASE)
    
    # 6. 数据预览
    print("\n" + "=" * 70)
    print("数据预览")
    print("=" * 70)
    
    # 显示数据摘要
    print(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"\n列名: {', '.join(df.columns.tolist())}")
    
    print(f"\n前5条数据:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 60)
    print(df.head(5).to_string(index=False))
    
    print(f"\n{'='*70}")
    print("🎉 任务完成！")
    print(f"{'='*70}")
    
    if export_results.get("csv"):
        print(f"📁 主要数据文件: {export_results['csv']}")
    if export_results.get("report"):
        print(f"📄 详细报告文件: {export_results['report']}")
    
    print(f"\n💡 提示:")
    print(f"  - 使用 Excel 打开 .xlsx 文件进行数据分析")
    print(f"  - 使用 文本编辑器 打开 _report.txt 查看详细分析")
    print(f"  - 共抓取 {len(df)} 条完整数据")

def test_connection():
    """测试连接"""
    print("测试网站连接...")
    try:
        response = requests.get("http://localhost:3000/questions", timeout=10)
        if response.status_code == 200:
            print("✅ 网站可正常访问")
            return True
        else:
            print(f"❌ 网站访问异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    # 设置pandas显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 80)
    
    # 测试连接
    if test_connection():
        # 运行主程序
        main()
    else:
        print("请检查网络连接后重试")


# In[ ]:




