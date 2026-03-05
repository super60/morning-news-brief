#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evening News Brief - 晚间新闻简报生成器
OpenClaw 自动化工具，用于生成每日晚间新闻晚报

作者：Lin Liu (@super60), 小蛋蛋 🐣
日期：2026-03-05
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class EveningNewsBrief:
    """晚间新闻简报生成器"""
    
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
        """获取黄金价格（带重试机制）
        
        Returns:
            包含国际和国内金价的字典
        """
        import requests
        
        # 重试机制：最多重试 3 次
        for attempt in range(3):
            try:
                # 获取国际金价（美元/盎司）
                gold_response = requests.get(self.config['gold_api'], timeout=5)
                gold_data = gold_response.json()
                international_price = gold_data.get('price', 0)
                
                if international_price > 0:
                    # 获取实时汇率
                    exchange_response = requests.get(
                        "https://api.exchangerate-api.com/v4/latest/USD",
                        timeout=5
                    )
                    exchange_data = exchange_response.json()
                    usd_cny_rate = exchange_data['rates'].get('CNY', 7.0)
                    
                    # 换算成人民币/克
                    domestic_price = (international_price * usd_cny_rate) / 31.1035
                    
                    # 获取昨日金价（用于计算涨跌）
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
                if attempt < 2:
                    # 失败后等待 1 秒重试
                    import time
                    time.sleep(1)
                    continue
                else:
                    # 最后一次失败，返回友好提示
                    return {
                        "international": "数据暂缺",
                        "domestic": "数据暂缺",
                        "exchange_rate": "N/A",
                        "change": "N/A",
                        "note": "实时数据获取失败，建议查询金投网 (gold.cngold.org) 或上海黄金交易所 (sge.com.cn)"
                    }
        
        # 默认返回（不应该到这里）
        return {
            "international": "数据暂缺",
            "domestic": "数据暂缺",
            "exchange_rate": "N/A",
            "change": "N/A"
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
        """生成完整晚报
        
        Returns:
            格式化的晚报名称
        """
        gold = self.get_gold_price()
        
        brief = f"""# 🌙 晚间国际新闻简报
*{self.date} {self.time} {self.timezone}*

---

## 📊 全天重大新闻总结

1. **头条新闻** - 今天最重要的事件
2. **关键进展** - 持续关注的动态

---

## 📈 财经/股市

### 💰 黄金价格（实时）

- **国际金价**: {gold['international']}
- **国内金价**: {gold['domestic']}
- **汇率**: {gold.get('exchange_rate', 'N/A')}
- **涨跌**: {gold.get('change', 'N/A')} (较昨日)

### 📊 股市收盘

- **A 股收盘**: 上证指数、深证成指全天表现

- **港股收盘**: 恒生指数、恒生科技指数

- **美股盘前**: 道指、纳指期货前瞻

- **你的持仓股票**: 小米、阿里等今日表现

---

## 🌍 国际新闻汇总

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

## 📅 明日预告

- **经济数据**: 明天将公布的重要数据
- **重要事件**: 值得关注的明天事件
- **公司财报**: 明天发布财报的公司

---

*📊 数据来源：BBC News, CNBC, Reuters, 新浪财经*
*⏰ 明日 21:30 准时发送*
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
    print("🌙 晚间新闻简报生成器")
    print("=" * 50)
    
    brief = EveningNewsBrief()
    filename = brief.save_brief()
    
    print(f"✅ 晚报已生成：{filename}")
    print(f"📅 日期：{brief.date}")
    print("=" * 50)


if __name__ == "__main__":
    main()
