# Smart Data Quality Analyzer
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class QualityIssue:
    """Represents a data quality issue"""
    column: str
    issue_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_fix: str
    affected_rows: int
    confidence: float
    
    @property
    def priority(self) -> str:
        """Map severity to priority for compatibility"""
        severity_map = {
            'low': 'Low',
            'medium': 'Medium', 
            'high': 'High',
            'critical': 'Critical'
        }
        return severity_map.get(self.severity, 'Medium')

class SmartDataQualityAnalyzer:
    """
    Advanced data quality analysis with intelligent pattern detection
    and business rule validation
    """
    
    def __init__(self, df: pd.DataFrame = None):
        self.df = df
        self.issues = []
        self.quality_score = 0
        self.column_profiles = {}
    
    def analyze_quality(self, df: pd.DataFrame = None) -> Tuple[float, List[QualityIssue]]:
        """
        Analyze data quality and return score and issues
        
        Args:
            df: DataFrame to analyze (optional if passed in constructor)
            
        Returns:
            Tuple of (quality_score, list_of_issues)
        """
        if df is not None:
            self.df = df
        
        if self.df is None:
            raise ValueError("No DataFrame provided for analysis")
        
        # Run analysis
        report = self.analyze_all()
        return self.quality_score, self.issues
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run comprehensive data quality analysis"""
        self.issues = []
        
        # Run all analysis modules
        self._analyze_missing_patterns()
        self._analyze_duplicates()
        self._analyze_outliers()
        self._analyze_data_types()
        self._analyze_business_rules()
        self._analyze_consistency()
        self._analyze_completeness()
        self._calculate_quality_score()
        
        return self._generate_report()
    
    def _analyze_missing_patterns(self):
        """Detect patterns in missing data"""
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count == 0:
                continue
                
            missing_pct = (missing_count / len(self.df)) * 100
            
            # Classify missing data severity
            if missing_pct > 50:
                severity = 'critical'
                suggested_fix = f"Consider dropping column '{col}' (>{missing_pct:.1f}% missing)"
            elif missing_pct > 20:
                severity = 'high'
                suggested_fix = f"Investigate missing pattern and implement targeted imputation"
            elif missing_pct > 5:
                severity = 'medium'
                suggested_fix = f"Apply appropriate imputation (mean/mode/forward-fill)"
            else:
                severity = 'low'
                suggested_fix = f"Simple imputation or keep as-is"
            
            # Check for patterns in missing data
            if len(self.df) > 100:  # Only for larger datasets
                # Check if missing values cluster together
                missing_mask = self.df[col].isnull()
                if len(missing_mask) > 1:
                    consecutive_missing = self._find_consecutive_missing(missing_mask)
                    if consecutive_missing > 10:
                        suggested_fix += f" (Found {consecutive_missing} consecutive missing values - possible data collection issue)"
            
            self.issues.append(QualityIssue(
                column=col,
                issue_type='missing_data',
                severity=severity,
                description=f"{missing_pct:.1f}% missing values ({missing_count}/{len(self.df)})",
                suggested_fix=suggested_fix,
                affected_rows=missing_count,
                confidence=0.9
            ))
    
    def _find_consecutive_missing(self, missing_mask: pd.Series) -> int:
        """Find longest streak of consecutive missing values"""
        max_consecutive = 0
        current_consecutive = 0
        
        for is_missing in missing_mask:
            if is_missing:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
                
        return max_consecutive
    
    def _analyze_duplicates(self):
        """Analyze duplicate patterns"""
        total_dups = self.df.duplicated().sum()
        if total_dups > 0:
            dup_pct = (total_dups / len(self.df)) * 100
            
            severity = 'high' if dup_pct > 10 else 'medium' if dup_pct > 1 else 'low'
            
            # Check for partial duplicates (same values in key columns)
            potential_id_cols = [col for col in self.df.columns 
                               if 'id' in col.lower() and self.df[col].nunique() / len(self.df) > 0.8]
            
            suggested_fix = f"Remove {total_dups} duplicate rows"
            if potential_id_cols:
                for id_col in potential_id_cols:
                    id_dups = self.df[id_col].duplicated().sum()
                    if id_dups > 0:
                        suggested_fix += f" (Warning: {id_dups} duplicate IDs in '{id_col}')"
            
            self.issues.append(QualityIssue(
                column='<all>',
                issue_type='duplicates',
                severity=severity,
                description=f"{dup_pct:.1f}% duplicate rows ({total_dups}/{len(self.df)})",
                suggested_fix=suggested_fix,
                affected_rows=total_dups,
                confidence=0.95
            ))
    
    def _analyze_outliers(self):
        """Detect outliers using multiple methods"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) < 10:  # Skip small datasets
                continue
            
            # IQR method
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            # Z-score method
            z_scores = np.abs((series - series.mean()) / series.std())
            z_outliers = series[z_scores > 3]
            
            # Use the more conservative estimate
            outlier_count = len(iqr_outliers)
            outlier_pct = (outlier_count / len(series)) * 100
            
            if outlier_count > 0:
                severity = 'high' if outlier_pct > 5 else 'medium' if outlier_pct > 1 else 'low'
                
                # Check if outliers might be valid extreme values
                range_ratio = (series.max() - series.min()) / series.std()
                if range_ratio > 10:  # High variance suggests outliers might be valid
                    suggested_fix = f"Investigate {outlier_count} potential outliers (high variance detected)"
                else:
                    suggested_fix = f"Consider removing or capping {outlier_count} outliers"
                
                self.issues.append(QualityIssue(
                    column=col,
                    issue_type='outliers',
                    severity=severity,
                    description=f"{outlier_pct:.1f}% outliers ({outlier_count} values)",
                    suggested_fix=suggested_fix,
                    affected_rows=outlier_count,
                    confidence=0.8
                ))
    
    def _analyze_data_types(self):
        """Analyze data type appropriateness"""
        for col in self.df.columns:
            series = self.df[col]
            current_type = str(series.dtype)
            
            # Check if numeric data is stored as strings
            if pd.api.types.is_object_dtype(series):
                sample = series.dropna().astype(str).str.strip()
                if len(sample) > 0:
                    # Test for numeric
                    numeric_like = sample.str.match(r'^-?\d+\.?\d*$').sum()
                    if numeric_like / len(sample) > 0.8:
                        self.issues.append(QualityIssue(
                            column=col,
                            issue_type='data_type',
                            severity='medium',
                            description=f"Numeric data stored as text ({numeric_like}/{len(sample)} values)",
                            suggested_fix=f"Convert '{col}' to numeric type",
                            affected_rows=len(sample),
                            confidence=0.9
                        ))
                    
                    # Test for dates
                    date_patterns = [
                        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                        r'\d{2}-\d{2}-\d{4}'   # MM-DD-YYYY
                    ]
                    date_like = sum(sample.str.match(pattern).sum() for pattern in date_patterns)
                    if date_like / len(sample) > 0.7:
                        self.issues.append(QualityIssue(
                            column=col,
                            issue_type='data_type',
                            severity='medium',
                            description=f"Date data stored as text ({date_like}/{len(sample)} values)",
                            suggested_fix=f"Convert '{col}' to datetime type",
                            affected_rows=len(sample),
                            confidence=0.85
                        ))
    
    def _analyze_business_rules(self):
        """Validate common business rules"""
        for col in self.df.columns:
            col_lower = col.lower()
            
            # Age validation
            if 'age' in col_lower and pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_ages = self.df[(self.df[col] < 0) | (self.df[col] > 150)][col].count()
                if invalid_ages > 0:
                    self.issues.append(QualityIssue(
                        column=col,
                        issue_type='business_rule',
                        severity='high',
                        description=f"Invalid age values: {invalid_ages} ages outside 0-150 range",
                        suggested_fix=f"Review and correct invalid age values in '{col}'",
                        affected_rows=invalid_ages,
                        confidence=0.95
                    ))
            
            # Email validation
            if 'email' in col_lower and pd.api.types.is_object_dtype(self.df[col]):
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                valid_emails = self.df[col].dropna().str.match(email_pattern).sum()
                total_emails = self.df[col].dropna().count()
                if total_emails > 0 and valid_emails / total_emails < 0.8:
                    invalid_count = total_emails - valid_emails
                    self.issues.append(QualityIssue(
                        column=col,
                        issue_type='business_rule',
                        severity='medium',
                        description=f"Invalid email format: {invalid_count}/{total_emails} emails",
                        suggested_fix=f"Validate and correct email formats in '{col}'",
                        affected_rows=invalid_count,
                        confidence=0.9
                    ))
            
            # Percentage validation
            if any(word in col_lower for word in ['percent', 'rate', 'ratio']) and pd.api.types.is_numeric_dtype(self.df[col]):
                invalid_pct = self.df[(self.df[col] < 0) | (self.df[col] > 100)][col].count()
                if invalid_pct > 0:
                    self.issues.append(QualityIssue(
                        column=col,
                        issue_type='business_rule',
                        severity='medium',
                        description=f"Invalid percentage values: {invalid_pct} values outside 0-100 range",
                        suggested_fix=f"Review percentage values in '{col}' - might need scaling",
                        affected_rows=invalid_pct,
                        confidence=0.8
                    ))
    
    def _analyze_consistency(self):
        """Check for consistency issues"""
        # Check categorical column consistency
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if self.df[col].nunique() < len(self.df) * 0.5:  # Likely categorical
                values = self.df[col].dropna().astype(str)
                
                # Check for case inconsistencies
                lower_values = values.str.lower()
                unique_lower = lower_values.nunique()
                unique_original = values.nunique()
                
                if unique_original > unique_lower:
                    case_issues = unique_original - unique_lower
                    self.issues.append(QualityIssue(
                        column=col,
                        issue_type='consistency',
                        severity='low',
                        description=f"Case inconsistencies: {case_issues} variations",
                        suggested_fix=f"Standardize case in '{col}' (e.g., lowercase)",
                        affected_rows=case_issues,
                        confidence=0.9
                    ))
                
                # Check for whitespace issues
                trimmed_values = values.str.strip()
                if not values.equals(trimmed_values):
                    whitespace_issues = (values != trimmed_values).sum()
                    self.issues.append(QualityIssue(
                        column=col,
                        issue_type='consistency',
                        severity='low',
                        description=f"Leading/trailing whitespace: {whitespace_issues} values",
                        suggested_fix=f"Trim whitespace in '{col}'",
                        affected_rows=whitespace_issues,
                        confidence=0.95
                    ))
    
    def _analyze_completeness(self):
        """Analyze data completeness"""
        # Check for suspiciously uniform values
        for col in self.df.columns:
            if self.df[col].nunique() == 1 and self.df[col].count() > 1:
                self.issues.append(QualityIssue(
                    column=col,
                    issue_type='completeness',
                    severity='medium',
                    description=f"Constant column - all values are identical",
                    suggested_fix=f"Consider removing column '{col}' as it provides no information",
                    affected_rows=len(self.df),
                    confidence=0.95
                ))
            
            # Check for very low cardinality in non-boolean columns
            elif (self.df[col].nunique() <= 2 and 
                  len(self.df) > 100 and 
                  not any(word in col.lower() for word in ['is_', 'has_', 'flag', 'bool'])):
                self.issues.append(QualityIssue(
                    column=col,
                    issue_type='completeness',
                    severity='low',
                    description=f"Very low cardinality: only {self.df[col].nunique()} unique values",
                    suggested_fix=f"Verify if '{col}' should have more variety or convert to boolean",
                    affected_rows=0,
                    confidence=0.7
                ))
    
    def _calculate_quality_score(self):
        """Calculate overall data quality score"""
        total_weight = 0
        weighted_score = 0
        
        # Base score components
        base_score = 100
        
        for issue in self.issues:
            # Weight by severity
            severity_weights = {'low': 1, 'medium': 3, 'high': 5, 'critical': 10}
            weight = severity_weights[issue.severity] * issue.confidence
            
            # Penalty based on affected rows
            affected_ratio = issue.affected_rows / len(self.df) if len(self.df) > 0 else 0
            penalty = weight * affected_ratio * 10  # Scale penalty
            
            base_score -= penalty
            total_weight += weight
        
        self.quality_score = max(0, min(100, base_score))
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        # Group issues by severity
        issues_by_severity = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue)
        
        # Generate summary statistics
        summary = {
            'overall_score': round(self.quality_score, 1),
            'total_issues': len(self.issues),
            'issues_by_severity': {k: len(v) for k, v in issues_by_severity.items()},
            'columns_analyzed': len(self.df.columns),
            'rows_analyzed': len(self.df),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Prioritized recommendations
        priority_recommendations = []
        for severity in ['critical', 'high', 'medium']:
            for issue in issues_by_severity[severity]:
                priority_recommendations.append({
                    'priority': severity,
                    'column': issue.column,
                    'issue': issue.description,
                    'fix': issue.suggested_fix,
                    'confidence': issue.confidence
                })
        
        return {
            'summary': summary,
            'issues': [issue.__dict__ for issue in self.issues],
            'recommendations': priority_recommendations[:10],  # Top 10
            'quality_grade': self._get_quality_grade(self.quality_score)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Fair)'
        elif score >= 60:
            return 'D (Poor)'
        else:
            return 'F (Critical Issues)'


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Convenience function to run data quality analysis"""
    analyzer = SmartDataQualityAnalyzer(df)
    return analyzer.analyze_all()
