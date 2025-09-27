#!/usr/bin/env python3
"""
Keyword Analysis Service for Word Cloud Generation
"""

import re
import json
from collections import Counter
from typing import List, Dict, Tuple
from .task_service import TaskService

class KeywordService:
    """Service for analyzing keywords from tasks and generating word cloud data"""
    
    def __init__(self):
        self.task_service = TaskService()
        # Common stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'shall', 'ought', 'need', 'dare', 'used', 'get', 'got', 'getting', 'go', 'went',
            'gone', 'going', 'come', 'came', 'coming', 'see', 'saw', 'seen', 'seeing', 'know', 'knew',
            'known', 'knowing', 'think', 'thought', 'thinking', 'take', 'took', 'taken', 'taking',
            'give', 'gave', 'given', 'giving', 'make', 'made', 'making', 'find', 'found', 'finding',
            'look', 'looked', 'looking', 'use', 'used', 'using', 'work', 'worked', 'working',
            'call', 'called', 'calling', 'try', 'tried', 'trying', 'ask', 'asked', 'asking',
            'need', 'needed', 'needing', 'feel', 'felt', 'feeling', 'become', 'became', 'becoming',
            'leave', 'left', 'leaving', 'put', 'putting', 'mean', 'meant', 'meaning', 'keep', 'kept',
            'keeping', 'let', 'letting', 'begin', 'began', 'begun', 'beginning', 'seem', 'seemed',
            'seeming', 'help', 'helped', 'helping', 'talk', 'talked', 'talking', 'turn', 'turned',
            'turning', 'start', 'started', 'starting', 'show', 'showed', 'shown', 'showing',
            'hear', 'heard', 'hearing', 'play', 'played', 'playing', 'run', 'ran', 'running',
            'move', 'moved', 'moving', 'live', 'lived', 'living', 'believe', 'believed', 'believing',
            'hold', 'held', 'holding', 'bring', 'brought', 'bringing', 'happen', 'happened', 'happening',
            'write', 'wrote', 'written', 'writing', 'provide', 'provided', 'providing', 'sit', 'sat',
            'sitting', 'stand', 'stood', 'standing', 'lose', 'lost', 'losing', 'pay', 'paid', 'paying',
            'meet', 'met', 'meeting', 'include', 'included', 'including', 'continue', 'continued',
            'continuing', 'set', 'setting', 'learn', 'learned', 'learning', 'change', 'changed',
            'changing', 'lead', 'led', 'leading', 'understand', 'understood', 'understanding',
            'watch', 'watched', 'watching', 'follow', 'followed', 'following', 'stop', 'stopped',
            'stopping', 'create', 'created', 'creating', 'speak', 'spoke', 'spoken', 'speaking',
            'read', 'reading', 'allow', 'allowed', 'allowing', 'add', 'added', 'adding', 'spend',
            'spent', 'spending', 'grow', 'grew', 'grown', 'growing', 'open', 'opened', 'opening',
            'walk', 'walked', 'walking', 'win', 'won', 'winning', 'offer', 'offered', 'offering',
            'remember', 'remembered', 'remembering', 'love', 'loved', 'loving', 'consider',
            'considered', 'considering', 'appear', 'appeared', 'appearing', 'buy', 'bought', 'buying',
            'wait', 'waited', 'waiting', 'serve', 'served', 'serving', 'die', 'died', 'dying',
            'send', 'sent', 'sending', 'expect', 'expected', 'expecting', 'build', 'built', 'building',
            'stay', 'stayed', 'staying', 'fall', 'fell', 'fallen', 'falling', 'cut', 'cutting',
            'reach', 'reached', 'reaching', 'kill', 'killed', 'killing', 'remain', 'remained',
            'remaining', 'suggest', 'suggested', 'suggesting', 'raise', 'raised', 'raising',
            'pass', 'passed', 'passing', 'sell', 'sold', 'selling', 'require', 'required', 'requiring',
            'report', 'reported', 'reporting', 'decide', 'decided', 'deciding', 'pull', 'pulled',
            'pulling', 'thank', 'thanked', 'thanking', 'accept', 'accepted', 'accepting',
            'agree', 'agreed', 'agreeing', 'support', 'supported', 'supporting', 'hit', 'hitting',
            'produce', 'produced', 'producing', 'eat', 'ate', 'eaten', 'eating', 'cover', 'covered',
            'covering', 'catch', 'caught', 'catching', 'draw', 'drew', 'drawn', 'drawing',
            'choose', 'chose', 'chosen', 'choosing', 'wear', 'wore', 'worn', 'wearing',
            'break', 'broke', 'broken', 'breaking', 'prove', 'proved', 'proven', 'proving',
            'cost', 'costing', 'teach', 'taught', 'teaching', 'throw', 'threw', 'thrown', 'throwing',
            'clean', 'cleaned', 'cleaning', 'wish', 'wished', 'wishing', 'drive', 'drove', 'driven',
            'driving', 'check', 'checked', 'checking', 'fix', 'fixed', 'fixing', 'treat', 'treated',
            'treating', 'deal', 'dealt', 'dealing', 'return', 'returned', 'returning', 'arrive',
            'arrived', 'arriving', 'obtain', 'obtained', 'obtaining', 'forget', 'forgot', 'forgotten',
            'forgetting', 'prepare', 'prepared', 'preparing', 'receive', 'received', 'receiving',
            'respond', 'responded', 'responding', 'realize', 'realized', 'realizing', 'join',
            'joined', 'joining', 'reduce', 'reduced', 'reducing', 'establish', 'established',
            'establishing', 'ensure', 'ensured', 'ensuring', 'indicate', 'indicated', 'indicating',
            'manage', 'managed', 'managing', 'discover', 'discovered', 'discovering', 'enter',
            'entered', 'entering', 'consider', 'considered', 'considering', 'determine', 'determined',
            'determining', 'develop', 'developed', 'developing', 'improve', 'improved', 'improving',
            'identify', 'identified', 'identifying', 'maintain', 'maintained', 'maintaining',
            'achieve', 'achieved', 'achieving', 'assume', 'assumed', 'assuming', 'involve',
            'involved', 'involving', 'occur', 'occurred', 'occurring', 'reflect', 'reflected',
            'reflecting', 'remove', 'removed', 'removing', 'reveal', 'revealed', 'revealing',
            'contain', 'contained', 'containing', 'represent', 'represented', 'representing',
            'recognize', 'recognized', 'recognizing', 'replace', 'replaced', 'replacing',
            'require', 'required', 'requiring', 'result', 'resulted', 'resulting', 'succeed',
            'succeeded', 'succeeding', 'suffer', 'suffered', 'suffering', 'tend', 'tended',
            'tending', 'transform', 'transformed', 'transforming', 'vary', 'varied', 'varying',
            'warn', 'warned', 'warning', 'wonder', 'wondered', 'wondering', 'worry', 'worried',
            'worrying', 'yield', 'yielded', 'yielding'
        }
    
    def extract_keywords_from_text(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text, filtering out stop words"""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if len(word) >= min_length and word not in self.stop_words
        ]
        
        return keywords
    
    def get_keyword_frequencies(self, limit: int = 50) -> List[Dict[str, any]]:
        """Get keyword frequencies from all tasks for word cloud generation"""
        tasks = self.task_service.load_tasks()
        
        # Combine all text from tasks
        all_text = []
        for task in tasks:
            subject = task.get('subject', '')
            content = task.get('content', '')
            summary = task.get('summary', '')
            
            # Combine all text fields
            combined_text = f"{subject} {content} {summary}"
            all_text.append(combined_text)
        
        # Extract keywords from all text
        all_keywords = []
        for text in all_text:
            keywords = self.extract_keywords_from_text(text)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Get top keywords
        top_keywords = keyword_counts.most_common(limit)
        
        # Format for word cloud
        word_cloud_data = []
        for word, count in top_keywords:
            word_cloud_data.append({
                'text': word,
                'size': count,
                'weight': count
            })
        
        return word_cloud_data
    
    def get_keywords_by_category(self, category: str, limit: int = 30) -> List[Dict[str, any]]:
        """Get keyword frequencies for a specific category"""
        tasks = self.task_service.load_tasks()
        
        # Filter tasks by category
        category_tasks = [task for task in tasks if task.get('category') == category]
        
        if not category_tasks:
            return []
        
        # Extract keywords from category tasks
        all_text = []
        for task in category_tasks:
            subject = task.get('subject', '')
            content = task.get('content', '')
            summary = task.get('summary', '')
            
            combined_text = f"{subject} {content} {summary}"
            all_text.append(combined_text)
        
        all_keywords = []
        for text in all_text:
            keywords = self.extract_keywords_from_text(text)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(limit)
        
        # Format for word cloud
        word_cloud_data = []
        for word, count in top_keywords:
            word_cloud_data.append({
                'text': word,
                'size': count,
                'weight': count
            })
        
        return word_cloud_data
    
    def search_tasks_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Search tasks that contain any of the specified keywords"""
        tasks = self.task_service.load_tasks()
        matching_tasks = []
        
        for task in tasks:
            subject = task.get('subject', '').lower()
            content = task.get('content', '').lower()
            summary = task.get('summary', '').lower()
            
            # Check if any keyword matches
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if (keyword_lower in subject or 
                    keyword_lower in content or 
                    keyword_lower in summary):
                    matching_tasks.append(task)
                    break  # Avoid duplicates
        
        return matching_tasks
    
    def get_category_keyword_analysis(self) -> Dict[str, List[Dict[str, any]]]:
        """Get keyword analysis for each category"""
        category_stats = self.task_service.get_category_stats()
        analysis = {}
        
        for category in category_stats.keys():
            keywords = self.get_keywords_by_category(category, limit=20)
            analysis[category] = keywords
        
        return analysis
