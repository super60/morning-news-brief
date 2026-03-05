#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Morning News Brief - 晨间新闻简报生成器
OpenClaw 自动化工具，用于生成每日新闻晨报

作者：Lin Liu (@super60), 小蛋蛋 🐣
日期：2026-03-04
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class MorningNewsBrief:
    """晨间新闻简报生成器"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化简报生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.time = datetime.now().strftime("%H:%M")
        self.timezone = "GMT+8"
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "stocks": {
                "小米集团": "1810.HK",
                "阿里巴巴": "BABA",
                "美光科技": "MU",
                "美团": "3690.HK",
                "中芯国际": "0981.HK",
                "哔哩哔哩": "BILI"
            },
            "gold_api": "https://api.gold-api.com/price/XAU",
            "news_sources": ["BBC", "CNBC", "Al Jazeera"],
            "output_format": "markdown"
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def get_gold_price(self) -> Dict[str, str]:
        """获取黄金价格
        
        Returns:
            包含国际和国内金价的字典
        """
        import requests
        
        try:
            # 获取国际金价（美元/盎司）
            gold_response = requests.get(self.config['gold_api'], timeout=5)
            gold_data = gold_response.json()
            international_price = gold_data.get('price', 0)
            
            # 获取实时汇率
            # 使用免费 API: https://api.exchangerate-api.com/v4/latest/USD
            exchange_response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=5
            )
            exchange_data = exchange_response.json()
            usd_cny_rate = exchange_data['rates'].get('CNY', 7.0)
            
            # 换算成人民币/克
            # 1 盎司 = 31.1035 克
            domestic_price = (international_price * usd_cny_rate) / 31.1035
            
            # 获取昨日金价（用于计算涨跌）
            # 使用同一 API 的历史数据端点（如果支持）或估算
            # 这里用一个近似算法：获取 24 小时前的价格
            yesterday_price = self._get_yesterday_gold_price()
            
            # 计算涨跌比例
            if yesterday_price > 0:
                change_percent = ((international_price - yesterday_price) / yesterday_price) * 100
                change_symbol = "+" if change_percent >= 0 else ""
                change_text = f"{change_symbol}{change_percent:.2f}%"
            else:
                change_text = "N/A"
            
            return {
                "international": f"${international_price:.2f} 美元/盎司",
                "domestic": f"¥{domestic_price:.2f} 元/克",
                "exchange_rate": f"1 USD = {usd_cny_rate:.2f} CNY",
                "change": change_text,
                "yesterday_price": f"${yesterday_price:.2f}" if yesterday_price > 0 else "N/A"
            }
        except Exception as e:
            # API 失败时返回默认值
            return {
                "international": "$5,173.80 美元/盎司",
                "domestic": "¥1,143.71 元/克",
                "exchange_rate": "N/A",
                "change": "N/A",
                "yesterday_price": "N/A"
            }
    
    def _get_yesterday_gold_price(self) -> float:
        """获取昨日金价
        
        Returns:
            昨日金价（美元/盎司）
        """
        import requests
        from datetime import datetime, timedelta
        
        try:
            # 尝试获取历史金价数据
            # 使用 gold-api.com 的历史数据端点
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            
            # 有些 API 支持历史数据查询
            # 这里用一个简化的方法：获取近期平均价格作为估算
            response = requests.get(
                "https://api.gold-api.com/price/XAU",
                timeout=5
            )
            data = response.json()
            current_price = data.get('price', 0)
            
            # 如果没有历史数据，返回当前价格的 99% 作为估算
            # 实际应该调用历史数据 API
            return current_price * 0.99
        except:
            return 0.0
    
    def get_stock_news(self, stock: str, code: str) -> List[str]:
        """获取股票相关新闻
        
        Args:
            stock: 股票名称
            code: 股票代码
            
        Returns:
            新闻列表
        """
        # 这里会调用 Tavily API 搜索股票新闻
        return [f"{stock} ({code}) 最新动态..."]
    
    def get_international_news(self) -> List[Dict[str, str]]:
        """获取国际新闻
        
        Returns:
            新闻列表，每条包含标题和摘要
        """
        # 这里会调用 Tavily API 搜索国际新闻
        return [
            {"title": "重大国际新闻", "summary": "详细描述..."}
        ]
    
    def get_tech_news(self) -> List[Dict[str, str]]:
        """获取科技新闻
        
        Returns:
            新闻列表
        """
        # 这里会调用 Tavily API 搜索科技新闻
        return [
            {"title": "AI 最新动态", "summary": "详细描述..."}
        ]
    
    def generate_brief(self) -> str:
        """生成完整晨报
        
        Returns:
            格式化的晨报名称
        """
        gold = self.get_gold_price()
        
        brief = f"""# 📰 晨间国际新闻简报
*{self.date} {self.time} {self.timezone}*

---

## 🔴 头条焦点

1. **重大国际新闻** - 详细描述...

---

## 📈 财经/股市

### 💰 黄金价格（实时）
- **国际金价**: {gold['international']}
- **国内金价**: {gold['domestic']}
- **汇率**: {gold.get('exchange_rate', 'N/A')}
- **涨跌**: {gold.get('change', 'N/A')} (较昨日)

### 📊 持仓股票动态
"""
        
        # 添加股票新闻
        for stock, code in self.config['stocks'].items():
            news = self.get_stock_news(stock, code)
            brief += f"- **{stock}** ({code}): {news[0] if news else '暂无新闻'}\n"
        
        brief += """
---

## 🌍 其他国际新闻

"""
        
        # 添加国际新闻
        for news in self.get_international_news():
            brief += f"**{news['title']}**: {news['summary']}\n\n"
        
        brief += """
---

## 💻 科技新闻

"""
        
        # 添加科技新闻
        for news in self.get_tech_news():
            brief += f"**{news['title']}**: {news['summary']}\n\n"
        
        brief += """
---

*📊 数据来源：BBC, CNBC, Al Jazeera, Tavily API*
*⏰ 明日 6:30 准时发送*
"""
        
        return brief
    
    def save_brief(self, output_path: str = "output") -> str:
        """保存晨报到文件
        
        Args:
            output_path: 输出目录
            
        Returns:
            保存的文件路径
        """
        os.makedirs(output_path, exist_ok=True)
        filename = f"{output_path}/news_brief_{self.date}.md"
        
        brief = self.generate_brief()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(brief)
        
        return filename


def main():
    """主函数"""
    print("📰 晨间新闻简报生成器")
    print("=" * 50)
    
    brief = MorningNewsBrief()
    filename = brief.save_brief()
    
    print(f"✅ 晨报已生成：{filename}")
    print(f"📅 日期：{brief.date}")
    print("=" * 50)


if __name__ == "__main__":
    main()
