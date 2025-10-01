#!/usr/bin/env python3
"""
Smart Analytics for HandyConnect Phase 12
Advanced AI-powered analytics and insights
"""

import json
import logging
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import openai
import os

logger = logging.getLogger(__name__)

@dataclass
class Insight:
    """AI-generated insight"""
    id: str
    type: str  # trend, anomaly, prediction, recommendation, pattern
    title: str
    description: str
    confidence: float
    impact: str  # low, medium, high, critical
    category: str
    data_points: List[Dict[str, Any]]
    generated_at: datetime
    expires_at: Optional[datetime] = None
    action_required: bool = False
    suggested_actions: List[str] = None

@dataclass
class Prediction:
    """AI-generated prediction"""
    id: str
    metric: str
    current_value: float
    predicted_value: float
    confidence: float
    time_horizon: str  # 1h, 24h, 7d, 30d
    trend_direction: str  # increasing, decreasing, stable
    factors: List[str]
    generated_at: datetime

@dataclass
class Anomaly:
    """AI-detected anomaly"""
    id: str
    metric: str
    detected_value: float
    expected_value: float
    deviation_percentage: float
    severity: str  # minor, moderate, severe, critical
    description: str
    potential_causes: List[str]
    detected_at: datetime
    resolved_at: Optional[datetime] = None

class SmartAnalytics:
    """Advanced AI-powered analytics engine"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.insights = []
        self.predictions = []
        self.anomalies = []
        self.historical_data = []
        
        logger.info("Smart Analytics initialized")
    
    def analyze_data(self, data: Dict[str, Any]) -> List[Insight]:
        """Analyze data and generate AI-powered insights"""
        try:
            insights = []
            
            # Generate trend insights
            trend_insights = self._analyze_trends(data)
            insights.extend(trend_insights)
            
            # Generate anomaly insights
            anomaly_insights = self._detect_anomalies(data)
            insights.extend(anomaly_insights)
            
            # Generate pattern insights
            pattern_insights = self._detect_patterns(data)
            insights.extend(pattern_insights)
            
            # Generate recommendation insights
            recommendation_insights = self._generate_recommendations(data)
            insights.extend(recommendation_insights)
            
            # Store insights
            self.insights.extend(insights)
            
            logger.info(f"Generated {len(insights)} insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return []
    
    def _analyze_trends(self, data: Dict[str, Any]) -> List[Insight]:
        """Analyze trends in the data"""
        insights = []
        
        try:
            # Prepare trend analysis prompt
            prompt = f"""
            Analyze the following customer support data for trends and provide insights:
            
            Data Summary:
            {json.dumps(data, indent=2)}
            
            Please identify:
            1. Significant trends (increasing/decreasing patterns)
            2. Seasonal patterns
            3. Performance improvements or degradations
            4. Customer behavior changes
            
            For each trend identified, provide:
            - Trend type and direction
            - Confidence level (0.0-1.0)
            - Impact assessment (low/medium/high/critical)
            - Key data points supporting the trend
            - Potential implications
            
            Respond with a JSON array of trend insights.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst specializing in customer support metrics. Identify meaningful trends and provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            trend_data = json.loads(content)
            
            for trend in trend_data:
                insight = Insight(
                    id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(insights)}",
                    type="trend",
                    title=trend.get('title', 'Trend Analysis'),
                    description=trend.get('description', ''),
                    confidence=trend.get('confidence', 0.7),
                    impact=trend.get('impact', 'medium'),
                    category=trend.get('category', 'performance'),
                    data_points=trend.get('data_points', []),
                    generated_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                    action_required=trend.get('action_required', False),
                    suggested_actions=trend.get('suggested_actions', [])
                )
                insights.append(insight)
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
        
        return insights
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> List[Insight]:
        """Detect anomalies in the data"""
        insights = []
        
        try:
            # Statistical anomaly detection
            metrics = self._extract_metrics(data)
            
            for metric_name, values in metrics.items():
                if len(values) < 3:  # Need at least 3 data points
                    continue
                
                # Calculate statistical measures
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                # Detect outliers (values > 2 standard deviations from mean)
                threshold = 2 * std_val
                outliers = [v for v in values if abs(v - mean_val) > threshold]
                
                if outliers:
                    # Create anomaly insight
                    deviation = max([abs(v - mean_val) for v in outliers]) / mean_val * 100
                    
                    insight = Insight(
                        id=f"anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{metric_name}",
                        type="anomaly",
                        title=f"Anomaly Detected in {metric_name}",
                        description=f"Detected {len(outliers)} outlier(s) in {metric_name}. Maximum deviation: {deviation:.1f}%",
                        confidence=min(0.9, 0.5 + (deviation / 100)),
                        impact="high" if deviation > 50 else "medium" if deviation > 25 else "low",
                        category="performance",
                        data_points=[{"metric": metric_name, "value": v, "expected": mean_val} for v in outliers],
                        generated_at=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(days=3),
                        action_required=deviation > 50,
                        suggested_actions=[
                            f"Investigate {metric_name} anomaly",
                            "Check for system issues",
                            "Review recent changes"
                        ]
                    )
                    insights.append(insight)
                    
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return insights
    
    def _detect_patterns(self, data: Dict[str, Any]) -> List[Insight]:
        """Detect patterns in the data using AI"""
        insights = []
        
        try:
            prompt = f"""
            Analyze the following customer support data for patterns:
            
            Data:
            {json.dumps(data, indent=2)}
            
            Look for:
            1. Recurring patterns (daily, weekly, monthly)
            2. Correlation patterns between different metrics
            3. Behavioral patterns in customer interactions
            4. Efficiency patterns in task processing
            5. Quality patterns in responses
            
            For each pattern identified, provide:
            - Pattern description
            - Confidence level (0.0-1.0)
            - Business implications
            - Optimization opportunities
            
            Respond with a JSON array of pattern insights.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a pattern recognition expert. Identify meaningful patterns in customer support data that can drive business improvements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            
            content = response.choices[0].message.content.strip()
            pattern_data = json.loads(content)
            
            for pattern in pattern_data:
                insight = Insight(
                    id=f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(insights)}",
                    type="pattern",
                    title=pattern.get('title', 'Pattern Detected'),
                    description=pattern.get('description', ''),
                    confidence=pattern.get('confidence', 0.6),
                    impact=pattern.get('impact', 'medium'),
                    category=pattern.get('category', 'efficiency'),
                    data_points=pattern.get('data_points', []),
                    generated_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=14),
                    action_required=pattern.get('action_required', False),
                    suggested_actions=pattern.get('suggested_actions', [])
                )
                insights.append(insight)
                
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
        
        return insights
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[Insight]:
        """Generate AI-powered recommendations"""
        insights = []
        
        try:
            prompt = f"""
            Based on the following customer support data, generate actionable recommendations:
            
            Data:
            {json.dumps(data, indent=2)}
            
            Provide recommendations for:
            1. Performance optimization
            2. Customer experience improvements
            3. Process efficiency enhancements
            4. Resource allocation optimization
            5. Quality improvements
            
            For each recommendation:
            - Specific action to take
            - Expected impact
            - Implementation priority
            - Required resources
            - Success metrics
            
            Focus on practical, implementable recommendations that can drive measurable improvements.
            
            Respond with a JSON array of recommendations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a customer support optimization expert. Provide practical, actionable recommendations based on data analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            recommendation_data = json.loads(content)
            
            for rec in recommendation_data:
                insight = Insight(
                    id=f"recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(insights)}",
                    type="recommendation",
                    title=rec.get('title', 'Recommendation'),
                    description=rec.get('description', ''),
                    confidence=rec.get('confidence', 0.8),
                    impact=rec.get('impact', 'medium'),
                    category=rec.get('category', 'optimization'),
                    data_points=rec.get('data_points', []),
                    generated_at=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                    action_required=True,
                    suggested_actions=rec.get('suggested_actions', [])
                )
                insights.append(insight)
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return insights
    
    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Extract numeric metrics from data for analysis"""
        metrics = {}
        
        # Extract common metrics
        if 'tasks' in data:
            tasks = data['tasks']
            if isinstance(tasks, list):
                # Task count over time
                metrics['task_count'] = [len(tasks)]
                
                # Priority distribution
                priorities = [task.get('priority', 'Medium') for task in tasks]
                priority_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Urgent': 0}
                for p in priorities:
                    priority_counts[p] = priority_counts.get(p, 0) + 1
                
                metrics['urgent_tasks'] = [priority_counts.get('Urgent', 0)]
                metrics['high_priority_tasks'] = [priority_counts.get('High', 0)]
                
                # Status distribution
                statuses = [task.get('status', 'New') for task in tasks]
                status_counts = {}
                for s in statuses:
                    status_counts[s] = status_counts.get(s, 0) + 1
                
                metrics['completed_tasks'] = [status_counts.get('Completed', 0)]
                metrics['in_progress_tasks'] = [status_counts.get('In Progress', 0)]
        
        # Extract performance metrics
        if 'performance' in data:
            perf = data['performance']
            for key, value in perf.items():
                if isinstance(value, (int, float)):
                    metrics[f'perf_{key}'] = [value]
        
        # Extract analytics metrics
        if 'analytics' in data:
            analytics = data['analytics']
            for key, value in analytics.items():
                if isinstance(value, (int, float)):
                    metrics[f'analytics_{key}'] = [value]
        
        return metrics
    
    def predict_metrics(self, historical_data: List[Dict[str, Any]]) -> List[Prediction]:
        """Generate predictions based on historical data"""
        predictions = []
        
        try:
            # Prepare prediction data
            metrics_data = {}
            for data_point in historical_data:
                metrics = self._extract_metrics(data_point)
                for metric_name, values in metrics.items():
                    if metric_name not in metrics_data:
                        metrics_data[metric_name] = []
                    metrics_data[metric_name].extend(values)
            
            # Generate predictions for each metric
            for metric_name, values in metrics_data.items():
                if len(values) < 3:  # Need minimum data points
                    continue
                
                # Simple trend-based prediction
                recent_values = values[-5:]  # Last 5 data points
                trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
                current_value = recent_values[-1]
                predicted_value = current_value + trend
                
                # Calculate confidence based on data consistency
                std_dev = np.std(recent_values)
                mean_val = np.mean(recent_values)
                confidence = max(0.3, 1.0 - (std_dev / mean_val) if mean_val > 0 else 0.3)
                
                prediction = Prediction(
                    id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{metric_name}",
                    metric=metric_name,
                    current_value=current_value,
                    predicted_value=predicted_value,
                    confidence=min(0.95, confidence),
                    time_horizon="24h",
                    trend_direction="increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                    factors=["historical_trend", "recent_performance"],
                    generated_at=datetime.now(timezone.utc)
                )
                predictions.append(prediction)
            
            # Store predictions
            self.predictions.extend(predictions)
            
            logger.info(f"Generated {len(predictions)} predictions")
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
        
        return predictions
    
    def get_active_insights(self) -> List[Insight]:
        """Get active insights (not expired)"""
        now = datetime.now(timezone.utc)
        return [
            insight for insight in self.insights
            if insight.expires_at is None or insight.expires_at > now
        ]
    
    def get_insights_by_type(self, insight_type: str) -> List[Insight]:
        """Get insights by type"""
        return [insight for insight in self.get_active_insights() if insight.type == insight_type]
    
    def get_high_impact_insights(self) -> List[Insight]:
        """Get high impact insights requiring attention"""
        return [
            insight for insight in self.get_active_insights()
            if insight.impact in ['high', 'critical'] and insight.action_required
        ]
    
    def get_predictions(self, metric: str = None) -> List[Prediction]:
        """Get predictions, optionally filtered by metric"""
        if metric:
            return [pred for pred in self.predictions if pred.metric == metric]
        return self.predictions
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            active_insights = self.get_active_insights()
            high_impact_insights = self.get_high_impact_insights()
            
            report = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'total_insights': len(active_insights),
                    'high_impact_insights': len(high_impact_insights),
                    'action_required': len([i for i in active_insights if i.action_required]),
                    'insights_by_type': {
                        insight_type: len([i for i in active_insights if i.type == insight_type])
                        for insight_type in ['trend', 'anomaly', 'pattern', 'recommendation']
                    },
                    'insights_by_impact': {
                        impact: len([i for i in active_insights if i.impact == impact])
                        for impact in ['low', 'medium', 'high', 'critical']
                    }
                },
                'insights': [asdict(insight) for insight in active_insights],
                'predictions': [asdict(prediction) for prediction in self.predictions],
                'recommendations': [
                    asdict(insight) for insight in self.get_insights_by_type('recommendation')
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {'error': str(e)}
