"""
Article Analyzer - JournalismATS
Scores articles against professional journalism standards (like ATS for resumes)
"""

import re
from typing import Dict, List, Any
import math


class ArticleAnalyzer:
    """Analyzes articles for journalism quality and provides actionable feedback"""

    # Loaded/biased words that indicate lack of objectivity
    LOADED_WORDS = [
        "shocking", "outrageous", "devastating", "incredible", "amazing",
        "terrible", "horrible", "unbelievable", "stunning", "dramatic",
        "slammed", "blasted", "destroyed", "crushed", "demolished",
        "bombshell", "explosive", "sensational", "alarming", "disturbing"
    ]

    # Words that indicate opinion rather than fact
    OPINION_WORDS = [
        "clearly", "obviously", "undoubtedly", "certainly", "surely",
        "definitely", "absolutely", "truly", "really", "very"
    ]

    # Passive voice indicators
    PASSIVE_INDICATORS = [
        "was ", "were ", "been ", "being ", "is ", "are ",
        "has been", "have been", "had been", "will be"
    ]

    def __init__(self):
        self.article_text = ""
        self.sentences = []
        self.paragraphs = []
        self.word_count = 0
        self.sentence_count = 0

    def analyze(self, article: str) -> Dict[str, Any]:
        """Main analysis function"""
        self.article_text = article.strip()

        if not self.article_text:
            return {
                "status": "error",
                "message": "Article text is required"
            }

        # Parse article structure
        self._parse_structure()

        # Calculate all scores
        objectivity = self._calculate_objectivity()
        source_quality = self._calculate_source_quality()
        factual_accuracy = self._calculate_factual_accuracy()
        writing_clarity = self._calculate_writing_clarity()
        ethical_standards = self._calculate_ethical_standards()
        bias_control = self._calculate_bias_control()
        structure_flow = self._calculate_structure_flow()
        headline_quality = self._calculate_headline_quality()

        # Calculate weighted overall score
        overall_score = round(
            objectivity * 0.20 +
            source_quality * 0.20 +
            factual_accuracy * 0.15 +
            writing_clarity * 0.10 +
            ethical_standards * 0.15 +
            bias_control * 0.10 +
            structure_flow * 0.05 +
            headline_quality * 0.05
        )

        # Get letter grade
        letter_grade = self._get_letter_grade(overall_score)

        # Generate detailed feedback
        strengths = self._identify_strengths({
            "objectivity": objectivity,
            "source_quality": source_quality,
            "factual_accuracy": factual_accuracy,
            "writing_clarity": writing_clarity,
            "ethical_standards": ethical_standards,
            "bias_control": bias_control,
            "structure_flow": structure_flow,
            "headline_quality": headline_quality
        })

        critical_issues = self._identify_critical_issues({
            "objectivity": objectivity,
            "source_quality": source_quality,
            "factual_accuracy": factual_accuracy,
            "writing_clarity": writing_clarity,
            "ethical_standards": ethical_standards,
            "bias_control": bias_control
        })

        detailed_issues = self._generate_detailed_issues()
        improvement_actions = self._generate_improvement_actions()
        learning_recommendations = self._generate_learning_recommendations(overall_score, {
            "objectivity": objectivity,
            "source_quality": source_quality,
            "bias_control": bias_control
        })

        # Article statistics
        article_stats = self._calculate_statistics()

        return {
            "status": "success",
            "analysis": {
                "overall_score": overall_score,
                "letter_grade": letter_grade,
                "score_breakdown": {
                    "objectivity": round(objectivity),
                    "source_quality": round(source_quality),
                    "factual_accuracy": round(factual_accuracy),
                    "writing_clarity": round(writing_clarity),
                    "ethical_standards": round(ethical_standards),
                    "bias_control": round(bias_control),
                    "structure_flow": round(structure_flow),
                    "headline_quality": round(headline_quality)
                },
                "strengths": strengths,
                "critical_issues": critical_issues,
                "detailed_issues": detailed_issues,
                "improvement_actions": improvement_actions,
                "learning_recommendations": learning_recommendations,
                "article_stats": article_stats
            }
        }

    def _parse_structure(self):
        """Parse article into sentences and paragraphs"""
        # Split into paragraphs
        self.paragraphs = [p.strip() for p in self.article_text.split('\n\n') if p.strip()]

        # Split into sentences
        self.sentences = []
        for para in self.paragraphs:
            # Simple sentence split (can be improved)
            sents = re.split(r'[.!?]+', para)
            self.sentences.extend([s.strip() for s in sents if s.strip()])

        # Count words
        self.word_count = len(self.article_text.split())
        self.sentence_count = len(self.sentences)

    def _calculate_objectivity(self) -> float:
        """Score based on absence of loaded language and opinion words"""
        score = 100.0

        text_lower = self.article_text.lower()

        # Deduct for loaded words
        for word in self.LOADED_WORDS:
            count = text_lower.count(word)
            score -= count * 3  # -3 points per loaded word

        # Deduct for opinion words
        for word in self.OPINION_WORDS:
            count = text_lower.count(word)
            score -= count * 2  # -2 points per opinion word

        # Deduct for excessive exclamation marks
        exclamation_count = self.article_text.count('!')
        score -= exclamation_count * 5

        return max(0, min(100, score))

    def _calculate_source_quality(self) -> float:
        """Score based on source attribution"""
        score = 50.0  # Start at 50 (neutral)

        # Look for attribution patterns
        attribution_patterns = [
            r'according to [A-Z][a-z]+',  # "according to Smith"
            r'said [A-Z][a-z]+',  # "said Johnson"
            r'"[^"]+"[,.]?\s*[A-Z][a-z]+\s+(?:said|stated|noted|explained)',  # "quote," Smith said
            r'[A-Z][a-z]+\s+[A-Z][a-z]+,\s*[a-z\s]+(?:at|from|with)',  # Dr. Jane Smith, professor at
        ]

        attributed_sources = 0
        for pattern in attribution_patterns:
            matches = re.findall(pattern, self.article_text)
            attributed_sources += len(matches)

        # Look for anonymous sources (reduce score)
        anonymous_patterns = [
            r'sources say', r'officials said', r'sources close to',
            r'anonymous source', r'sources familiar with'
        ]

        anonymous_sources = 0
        for pattern in anonymous_patterns:
            if re.search(pattern, self.article_text.lower()):
                anonymous_sources += 1

        # Scoring logic
        if attributed_sources >= 3:
            score += 40  # Excellent sourcing
        elif attributed_sources >= 2:
            score += 25  # Good sourcing
        elif attributed_sources >= 1:
            score += 10  # Minimal sourcing
        else:
            score -= 20  # No clear sources

        # Penalty for anonymous sources
        score -= anonymous_sources * 5

        return max(0, min(100, score))

    def _calculate_factual_accuracy(self) -> float:
        """Score based on verifiable claims and fact-checking indicators"""
        score = 75.0  # Assume innocent until proven otherwise

        # Look for quantifiable data (good)
        data_patterns = [
            r'\d+%',  # percentages
            r'\$\d+',  # money
            r'\d{1,3}(?:,\d{3})*',  # numbers with commas
            r'\d+\s+(?:million|billion|thousand)',  # "5 million"
        ]

        data_points = 0
        for pattern in data_patterns:
            matches = re.findall(pattern, self.article_text)
            data_points += len(matches)

        if data_points >= 5:
            score += 15
        elif data_points >= 3:
            score += 10
        elif data_points >= 1:
            score += 5

        # Look for dates (good for context)
        date_patterns = [
            r'\d{4}',  # years
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}',
        ]

        has_dates = any(re.search(pattern, self.article_text) for pattern in date_patterns)
        if has_dates:
            score += 5

        # Check for unverifiable claims (bad)
        unverifiable_patterns = [
            r'many people', r'some say', r'it is believed', r'reportedly',
            r'allegedly', r'rumored', r'unconfirmed'
        ]

        for pattern in unverifiable_patterns:
            if re.search(pattern, self.article_text.lower()):
                score -= 5

        return max(0, min(100, score))

    def _calculate_writing_clarity(self) -> float:
        """Score based on readability metrics"""
        if self.sentence_count == 0:
            return 50.0

        # Calculate average sentence length
        avg_sentence_length = self.word_count / self.sentence_count

        # Flesch Reading Ease approximation
        # Ideal: 60-70 (acceptable), 50-60 (fairly difficult)
        avg_syllables_per_word = 1.5  # Rough estimate

        flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch = max(0, min(100, flesch))

        # Convert Flesch score to our 0-100 scale
        # 60+ is good, 30-60 is acceptable, <30 is difficult
        if flesch >= 60:
            score = 90 + (flesch - 60) / 4  # 90-100
        elif flesch >= 30:
            score = 60 + (flesch - 30)  # 60-90
        else:
            score = flesch * 2  # 0-60

        # Penalty for passive voice
        passive_count = sum(1 for indicator in self.PASSIVE_INDICATORS 
                          if indicator in self.article_text.lower())

        if passive_count > 5:
            score -= 10
        elif passive_count > 3:
            score -= 5

        return max(0, min(100, score))

    def _calculate_ethical_standards(self) -> float:
        """Score based on ethical journalism practices"""
        score = 85.0  # Start high, deduct for violations

        text_lower = self.article_text.lower()

        # Check for privacy concerns
        privacy_violations = [
            r'\d{3}-\d{2}-\d{4}',  # SSN
            r'\d{10,}',  # phone numbers (basic check)
        ]

        for pattern in privacy_violations:
            if re.search(pattern, self.article_text):
                score -= 20  # Major violation

        # Check for inflammatory language
        inflammatory_words = ['hate', 'destroy', 'kill', 'attack', 'war']
        for word in inflammatory_words:
            if word in text_lower:
                # Context matters, but flag it
                score -= 3

        # Check for balanced perspective
        # If article is long but has no opposing views, deduct
        if self.word_count > 200:
            opposing_indicators = ['however', 'but', 'on the other hand', 'critics', 'opponents']
            has_balance = any(indicator in text_lower for indicator in opposing_indicators)
            if not has_balance:
                score -= 10

        return max(0, min(100, score))

    def _calculate_bias_control(self) -> float:
        """Score based on bias indicators"""
        score = 90.0

        text_lower = self.article_text.lower()

        # Check for one-sided language
        one_sided_patterns = [
            'only', 'just', 'merely', 'simply', 'always', 'never', 'everyone', 'no one'
        ]

        for pattern in one_sided_patterns:
            count = text_lower.count(f' {pattern} ')
            score -= count * 2

        # Check for attributed vs unattributed opinions
        # Good: "Smith argues that..."
        # Bad: "It is clear that..."

        unattributed_opinions = [
            'it is clear', 'obviously', 'everyone knows', 'the truth is'
        ]

        for phrase in unattributed_opinions:
            if phrase in text_lower:
                score -= 5

        return max(0, min(100, score))

    def _calculate_structure_flow(self) -> float:
        """Score based on article structure"""
        score = 70.0

        if len(self.paragraphs) < 2:
            score -= 20  # Too short or no paragraph breaks

        if len(self.paragraphs) > 10:
            score += 10  # Well-structured

        # Check for lead paragraph (should be concise)
        if self.paragraphs:
            first_para_words = len(self.paragraphs[0].split())
            if 20 <= first_para_words <= 50:
                score += 10  # Good lead
            elif first_para_words > 80:
                score -= 10  # Lead too long

        return max(0, min(100, score))

    def _calculate_headline_quality(self) -> float:
        """Score the headline (first line if present)"""
        score = 75.0

        # For now, use first sentence as proxy for headline
        if not self.sentences:
            return 50.0

        headline = self.sentences[0]

        # Check length (ideal: 8-12 words)
        headline_words = len(headline.split())
        if 8 <= headline_words <= 12:
            score += 15
        elif 6 <= headline_words <= 15:
            score += 5
        elif headline_words > 20:
            score -= 10

        # Check for loaded language
        headline_lower = headline.lower()
        for word in self.LOADED_WORDS:
            if word in headline_lower:
                score -= 5

        # Check for clickbait patterns
        clickbait_patterns = [
            'you won\'t believe', 'shocking', 'one weird trick',
            'what happened next', 'will blow your mind'
        ]

        for pattern in clickbait_patterns:
            if pattern in headline_lower:
                score -= 15

        return max(0, min(100, score))

    def _get_letter_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify what the article does well"""
        strengths = []

        if scores["objectivity"] >= 85:
            strengths.append("Maintains strong objectivity with minimal loaded language")

        if scores["source_quality"] >= 80:
            strengths.append("Excellent source attribution with named, credible sources")

        if scores["writing_clarity"] >= 80:
            strengths.append("Clear, readable writing style with good sentence structure")

        if scores["ethical_standards"] >= 85:
            strengths.append("Adheres to ethical journalism standards")

        if scores["bias_control"] >= 85:
            strengths.append("Well-balanced perspective with controlled bias")

        if scores["factual_accuracy"] >= 80:
            strengths.append("Strong use of verifiable data and specific facts")

        if not strengths:
            strengths.append("Article shows potential with room for improvement")

        return strengths

    def _identify_critical_issues(self, scores: Dict[str, float]) -> List[str]:
        """Identify critical problems that need immediate attention"""
        issues = []

        if scores["objectivity"] < 60:
            issues.append("Excessive use of loaded language undermines objectivity")

        if scores["source_quality"] < 60:
            issues.append("Insufficient source attribution - add more named sources")

        if scores["factual_accuracy"] < 60:
            issues.append("Lacks verifiable facts and data to support claims")

        if scores["bias_control"] < 60:
            issues.append("Significant bias detected - article lacks balance")

        if scores["ethical_standards"] < 70:
            issues.append("Ethical concerns present - review journalism ethics guidelines")

        return issues

    def _generate_detailed_issues(self) -> List[Dict[str, Any]]:
        """Generate specific, actionable issues with locations"""
        issues = []

        text_lower = self.article_text.lower()

        # Check for loaded language
        found_loaded = []
        for word in self.LOADED_WORDS:
            if word in text_lower:
                found_loaded.append(word)

        if found_loaded:
            issues.append({
                "category": "Objectivity",
                "severity": "high" if len(found_loaded) > 3 else "medium",
                "issue": f"Loaded language detected: {', '.join(found_loaded[:5])}",
                "suggestion": "Replace with neutral, factual language",
                "example": f'Instead of "shocking," use "unexpected" or "significant"'
            })

        # Check for source quality
        has_sources = bool(re.search(r'according to|said [A-Z]', self.article_text))
        if not has_sources:
            issues.append({
                "category": "Source Quality",
                "severity": "high",
                "issue": "No clear source attribution found",
                "suggestion": 'Add named sources with credentials (e.g., "According to Dr. Jane Smith, MIT economist...")',
            })

        # Check for passive voice
        passive_count = sum(1 for indicator in self.PASSIVE_INDICATORS 
                          if indicator in text_lower)
        if passive_count > 3:
            issues.append({
                "category": "Writing Clarity",
                "severity": "medium",
                "issue": f"Excessive passive voice detected ({passive_count} instances)",
                "suggestion": "Convert to active voice for stronger, clearer writing",
                "example": 'Instead of "The report was released by the agency," write "The agency released the report"'
            })

        # Check average sentence length
        if self.sentence_count > 0:
            avg_length = self.word_count / self.sentence_count
            if avg_length > 25:
                issues.append({
                    "category": "Writing Clarity",
                    "severity": "medium",
                    "issue": f"Average sentence length is high ({avg_length:.1f} words)",
                    "suggestion": "Break long sentences into shorter ones (aim for 15-20 words)",
                })

        return issues

    def _generate_improvement_actions(self) -> List[Dict[str, Any]]:
        """Generate prioritized improvement actions"""
        actions = []

        # Analyze current state
        text_lower = self.article_text.lower()

        # Source attribution
        has_sources = bool(re.search(r'according to|said [A-Z]', self.article_text))
        if not has_sources:
            actions.append({
                "priority": "high",
                "issue": "Insufficient source attribution",
                "how_to_fix": "Add 2-3 named sources with credentials throughout the article",
                "before": '"The economy is improving."',
                "after": '"The economy is improving," according to Dr. Sarah Johnson, chief economist at the Federal Reserve Bank.'
            })

        # Loaded language
        loaded_found = [w for w in self.LOADED_WORDS if w in text_lower]
        if loaded_found:
            actions.append({
                "priority": "high",
                "issue": f"Loaded language: {', '.join(loaded_found[:3])}",
                "how_to_fix": "Replace emotional words with neutral, factual alternatives",
                "before": "The shocking report reveals devastating consequences",
                "after": "The new report details significant consequences"
            })

        # Passive voice
        if sum(1 for ind in self.PASSIVE_INDICATORS if ind in text_lower) > 3:
            actions.append({
                "priority": "medium",
                "issue": "Excessive passive voice",
                "how_to_fix": "Rewrite sentences in active voice for clarity and impact",
                "before": "The bill was passed by Congress yesterday",
                "after": "Congress passed the bill yesterday"
            })

        # Paragraph structure
        if len(self.paragraphs) < 3:
            actions.append({
                "priority": "low",
                "issue": "Article lacks proper paragraph structure",
                "how_to_fix": "Break content into logical paragraphs (one main idea per paragraph)",
            })

        return actions

    def _generate_learning_recommendations(self, overall_score: int, 
                                          scores: Dict[str, float]) -> List[Dict[str, str]]:
        """Recommend learning modules based on performance"""
        recommendations = []

        if overall_score < 70:
            recommendations.append({
                "module": "Journalism Fundamentals",
                "reason": "Overall score indicates need for foundational skills review"
            })

        if scores["objectivity"] < 70:
            recommendations.append({
                "module": "Understanding Media Bias",
                "reason": "Improve objectivity by learning to identify and eliminate bias"
            })

        if scores["source_quality"] < 70:
            recommendations.append({
                "module": "Source Quality & Attribution 101",
                "reason": "Learn proper sourcing techniques and when to use different types of sources"
            })

        if scores["bias_control"] < 70:
            recommendations.append({
                "module": "Writing Without Bias",
                "reason": "Master techniques for balanced, fair reporting"
            })

        # Always recommend something
        if not recommendations:
            recommendations.append({
                "module": "Advanced Journalism Techniques",
                "reason": "Continue improving your already strong foundation"
            })

        return recommendations

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate article statistics"""
        avg_sentence_length = self.word_count / self.sentence_count if self.sentence_count > 0 else 0

        # Flesch Reading Ease (simplified)
        avg_syllables = 1.5  # Approximation
        flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        flesch = max(0, min(100, flesch))

        return {
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "paragraph_count": len(self.paragraphs),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "readability_score": round(flesch, 1)
        }


def analyze_article(article_text: str) -> Dict[str, Any]:
    """
    Main function to analyze an article
    
    Args:
        article_text: The article content to analyze
        
    Returns:
        Dict containing analysis results with scores and feedback
    """
    analyzer = ArticleAnalyzer()
    return analyzer.analyze(article_text)
