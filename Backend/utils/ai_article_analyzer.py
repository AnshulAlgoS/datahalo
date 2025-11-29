# AI Article Analyzer - Fast, Credible, ATS-like Scoring
# Optimized for SPEED while maintaining CREDIBILITY

import os
import re
import json
import logging
import requests
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("DataHalo")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def analyze_article_with_ai(article_text: str) -> Dict[str, Any]:
    """
    FAST AI-POWERED ARTICLE ANALYZER (ATS-like for Journalism)
    
    Like an ATS system for resumes, this analyzes articles against
    professional journalism standards FAST and gives actionable scores.
    
    Uses Qwen3 Coder 480B model - optimized for speed and accuracy.
    Typical response time: 5-15 seconds for comprehensive analysis.
    """
    
    if not NVIDIA_API_KEY:
        return {
            "status": "error",
            "message": "AI analysis requires NVIDIA API key for credible evaluation."
        }
    
    word_count = len(article_text.split())
    
    # Quick stats (objective metrics)
    sentences = [s.strip() for s in re.split(r'[.!?]+', article_text) if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    # Readability score (Flesch)
    syllables = estimate_syllables(article_text)
    syllables_per_word = syllables / max(word_count, 1)
    flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * syllables_per_word
    flesch_score = max(0, min(100, flesch_score))
    
    logger.info(f"AI ANALYSIS: Starting fast AI evaluation for {word_count} words")
    
    # SIMPLE CONVERSATIONAL PROMPT (like AI Tutor)
    prompt = f"""Grade this {word_count}-word article on journalism standards.

ARTICLE:
{article_text[:1500]}

Score 0-100 on:
- Objectivity, Sources, Accuracy, Clarity, Ethics, Context, Structure, Headline

Format (plain text):
SCORES: objectivity=X sources=X accuracy=X clarity=X ethics=X context=X structure=X headline=X
GRADE: A/B/C/D/F  
SUMMARY: brief assessment
STRENGTHS: good point 1 | good point 2
ISSUES: problem 1 | problem 2
FIXES: how to improve 1 | how to improve 2"""

    try:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen/qwen3-coder-480b-a35b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a journalism professor grading articles. Be concise and direct. Return plain text in the exact format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Balanced for quality and speed
            "top_p": 0.9,
            "max_tokens": 500,  # Enough for complete response
            "stream": False
        }

        logger.info("AI: Calling Qwen AI (optimized for speed and efficiency)...")
        
        # Qwen model timeout - faster and more reliable
        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45  # Qwen is fast but give it buffer for complex articles
        )
        response.raise_for_status()

        ai_response = response.json()
        content = ai_response["choices"][0]["message"]["content"]
        
        logger.info(f"AI: Received response ({len(content)} chars)")

        # Parse simple text format (faster than JSON parsing)
        ai_result = {}
        
        try:
            # Extract scores line
            scores_match = re.search(r'SCORES:\s*(.+)', content, re.IGNORECASE)
            if scores_match:
                scores_text = scores_match.group(1)
                scores_dict = {}
                for match in re.finditer(r'(\w+)=(\d+)', scores_text):
                    scores_dict[match.group(1)] = int(match.group(2))
                ai_result["scores"] = scores_dict
            
            # Extract grade
            grade_match = re.search(r'GRADE:\s*([A-F][+-]?)', content, re.IGNORECASE)
            if grade_match:
                ai_result["letter_grade"] = grade_match.group(1)
            
            # Extract summary
            summary_match = re.search(r'SUMMARY:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            if summary_match:
                ai_result["summary"] = summary_match.group(1).strip()
            
            # Extract strengths
            strengths_match = re.search(r'STRENGTHS:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            if strengths_match:
                ai_result["strengths"] = [s.strip() for s in strengths_match.group(1).split('|')]
            
            # Extract issues
            issues_match = re.search(r'ISSUES:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
            if issues_match:
                issues_text = issues_match.group(1).split('|')
                ai_result["issues"] = [{"issue": i.strip(), "severity": "medium", "fix": "Review and revise"} for i in issues_text]
            
            # Extract fixes
            fixes_match = re.search(r'FIXES:\s*(.+)', content, re.IGNORECASE)
            if fixes_match:
                ai_result["top_improvements"] = [f.strip() for f in fixes_match.group(1).split('|')]
            
            # Calculate overall score
            if "scores" in ai_result and ai_result["scores"]:
                scores_list = list(ai_result["scores"].values())
                ai_result["overall_score"] = round(sum(scores_list) / len(scores_list))
            else:
                raise ValueError("No scores found in AI response")
                
        except Exception as parse_error:
            logger.error(f"AI: Failed to parse response: {parse_error}")
            logger.error(f"AI: Content was: {content}")
            raise ValueError(f"Could not parse AI response: {parse_error}")

        # Add article stats
        ai_result["article_stats"] = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "readability_score": round(flesch_score, 1)
        }
        
        # Expand scores into detailed breakdown for frontend compatibility
        if "scores" in ai_result:
            ai_result["score_breakdown"] = {
                "objectivity": ai_result["scores"].get("objectivity", 0),
                "source_quality": ai_result["scores"].get("sources", 0),
                "factual_accuracy": ai_result["scores"].get("accuracy", 0),
                "writing_clarity": ai_result["scores"].get("clarity", 0),
                "ethical_standards": ai_result["scores"].get("ethics", 0),
                "context_completeness": ai_result["scores"].get("context", 0),
                "structure_flow": ai_result["scores"].get("structure", 0),
                "headline_quality": ai_result["scores"].get("headline", 0)
            }
        
        # Normalize field names for frontend
        if "summary" in ai_result:
            ai_result["one_line_summary"] = ai_result["summary"]
        
        # Transform issues into detailed_issues format (required by frontend)
        if "issues" in ai_result:
            ai_result["critical_issues"] = [issue["issue"] if isinstance(issue, dict) else str(issue) for issue in ai_result["issues"]]
            ai_result["detailed_issues"] = ai_result["issues"]  # Frontend expects this
        else:
            ai_result["critical_issues"] = []
            ai_result["detailed_issues"] = []
        
        # Transform top_improvements into improvement_actions format (required by frontend)
        if "top_improvements" in ai_result:
            ai_result["top_3_improvements"] = ai_result["top_improvements"]
            # Frontend expects improvement_actions with specific structure
            ai_result["improvement_actions"] = [
                {
                    "priority": "medium",
                    "issue": improvement,
                    "how_to_fix": improvement
                }
                for improvement in ai_result["top_improvements"]
            ]
        else:
            ai_result["improvement_actions"] = []
            
        if "explanation" in ai_result:
            ai_result["grade_explanation"] = ai_result["explanation"]
        
        # Generate comprehensive learning_recommendations with resources
        if "learning_recommendations" not in ai_result:
            ai_result["learning_recommendations"] = generate_learning_resources(ai_result, word_count)
        
        # Add methodology transparency
        ai_result["methodology"] = {
            "analysis_type": "AI-Powered Fast Evaluation (ATS-like)",
            "model": "Qwen3 Coder 480B A35B Instruct",
            "approach": "Real AI evaluation against journalism standards - optimized for speed and accuracy",
            "standards_based_on": [
                "AP Style Guide",
                "SPJ Code of Ethics",
                "Professional journalism standards"
            ],
            "speed_optimized": True,
            "accuracy_note": "This AI analyzes your article like an ATS scans resumes - fast, accurate scoring against professional standards. Use for educational guidance.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Ensure warnings field exists
        if "warnings" not in ai_result:
            ai_result["warnings"] = []
        
        # Add warnings for short articles
        if word_count < 100:
            ai_result["warnings"].append("Article is short - consider expanding for more comprehensive evaluation")
        
        logger.info(f"SUCCESS: AI analysis complete - Score: {ai_result['overall_score']}, Grade: {ai_result.get('letter_grade', 'N/A')}")
        
        return {
            "status": "success",
            "analysis": ai_result,
            "analysis_type": "ai_fast"
        }

    except json.JSONDecodeError as e:
        logger.error(f"AI: JSON parsing error: {e}")
        return {
            "status": "error",
            "message": "AI returned invalid format. Please try again."
        }
    except requests.exceptions.ReadTimeout:
        logger.error("AI: Analysis timed out after 45s (Qwen model)")
        logger.info("AI: This is rare with Qwen - check API connectivity or article length")
        return {
            "status": "error",
            "message": "AI analysis timed out. Please try again or use a shorter article."
        }
    except Exception as e:
        logger.error(f"AI: Analysis error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"AI analysis failed: {str(e)}"
        }


def generate_learning_resources(ai_result: Dict[str, Any], word_count: int) -> list:
    """Generate personalized learning recommendations with actual resources based on analysis"""
    recommendations = []
    scores = ai_result.get("score_breakdown", {})
    
    # Check each criterion and recommend resources if score is below 80
    
    # 1. Source Quality
    if scores.get("source_quality", 100) < 80:
        recommendations.append({
            "module": "Source Verification & Citation",
            "reason": f"Your source quality score is {scores.get('source_quality', 0)}/100. Strengthen your article with credible sources and proper citations.",
            "resources": [
                {
                    "type": "video",
                    "title": "How to Evaluate News Sources - Media Literacy",
                    "url": "https://youtu.be/L4aNmdL3Hr0",
                    "platform": "YouTube - TED-Ed"
                },
                {
                    "type": "article",
                    "title": "AP Style Guide: Attribution and Citations",
                    "url": "https://www.apstylebook.com/",
                    "platform": "AP Stylebook"
                },
                {
                    "type": "tool",
                    "title": "CRAAP Test for Source Evaluation",
                    "url": "https://library.csuchico.edu/help/source-or-information-good",
                    "platform": "Academic Tool"
                }
            ]
        })
    
    # 2. Objectivity
    if scores.get("objectivity", 100) < 80:
        recommendations.append({
            "module": "Objectivity & Bias Control",
            "reason": f"Your objectivity score is {scores.get('objectivity', 0)}/100. Learn to identify and eliminate bias in your writing.",
            "resources": [
                {
                    "type": "video",
                    "title": "Understanding Media Bias",
                    "url": "https://youtu.be/z7_TbTT_J3c",
                    "platform": "YouTube - Crash Course"
                },
                {
                    "type": "article",
                    "title": "SPJ Code of Ethics: Seek Truth and Report It",
                    "url": "https://www.spj.org/ethicscode.asp",
                    "platform": "Society of Professional Journalists"
                },
                {
                    "type": "course",
                    "title": "Journalism Ethics and Law",
                    "url": "https://www.coursera.org/learn/journalism-ethics",
                    "platform": "Coursera"
                }
            ]
        })
    
    # 3. Writing Clarity
    if scores.get("writing_clarity", 100) < 80:
        recommendations.append({
            "module": "Clear & Concise Writing",
            "reason": f"Your clarity score is {scores.get('writing_clarity', 0)}/100. Improve readability and eliminate jargon.",
            "resources": [
                {
                    "type": "video",
                    "title": "How to Write Clear Sentences",
                    "url": "https://youtu.be/VqU7mBBh4NY",
                    "platform": "YouTube - Writing Coach"
                },
                {
                    "type": "tool",
                    "title": "Hemingway Editor - Readability Tool",
                    "url": "https://hemingwayapp.com/",
                    "platform": "Writing Tool"
                },
                {
                    "type": "article",
                    "title": "Plain Language Guidelines",
                    "url": "https://www.plainlanguage.gov/guidelines/",
                    "platform": "PlainLanguage.gov"
                }
            ]
        })
    
    # 4. Structure & Flow
    if scores.get("structure_flow", 100) < 80:
        recommendations.append({
            "module": "Article Structure & Organization",
            "reason": f"Your structure score is {scores.get('structure_flow', 0)}/100. Learn the inverted pyramid and proper article organization.",
            "resources": [
                {
                    "type": "video",
                    "title": "The Inverted Pyramid: News Writing Structure",
                    "url": "https://youtu.be/2WY5wPX5JTE",
                    "platform": "YouTube - Journalism Course"
                },
                {
                    "type": "article",
                    "title": "How to Structure a News Story",
                    "url": "https://owl.purdue.edu/owl/subject_specific_writing/journalism_and_journalistic_writing/",
                    "platform": "Purdue OWL"
                },
                {
                    "type": "course",
                    "title": "News Writing Fundamentals",
                    "url": "https://www.edx.org/learn/journalism",
                    "platform": "edX"
                }
            ]
        })
    
    # 5. Factual Accuracy
    if scores.get("factual_accuracy", 100) < 80:
        recommendations.append({
            "module": "Fact-Checking & Verification",
            "reason": f"Your accuracy score is {scores.get('factual_accuracy', 0)}/100. Master fact-checking techniques and verification methods.",
            "resources": [
                {
                    "type": "video",
                    "title": "Fact-Checking Techniques for Journalists",
                    "url": "https://youtu.be/dEn6pS_vV2Y",
                    "platform": "YouTube - Poynter Institute"
                },
                {
                    "type": "tool",
                    "title": "Google Fact Check Explorer",
                    "url": "https://toolbox.google.com/factcheck/explorer",
                    "platform": "Google Tools"
                },
                {
                    "type": "course",
                    "title": "Verification and Fact-Checking",
                    "url": "https://www.poynter.org/fact-checking/",
                    "platform": "Poynter Institute"
                }
            ]
        })
    
    # 6. Ethical Standards
    if scores.get("ethical_standards", 100) < 80:
        recommendations.append({
            "module": "Journalism Ethics & Standards",
            "reason": f"Your ethics score is {scores.get('ethical_standards', 0)}/100. Understand ethical principles and professional standards.",
            "resources": [
                {
                    "type": "video",
                    "title": "Journalism Ethics in the Digital Age",
                    "url": "https://youtu.be/_BDdY-rI3K8",
                    "platform": "YouTube - BBC Academy"
                },
                {
                    "type": "article",
                    "title": "Reuters Handbook of Journalism",
                    "url": "http://handbook.reuters.com/",
                    "platform": "Reuters"
                },
                {
                    "type": "article",
                    "title": "SPJ Ethics Hotline Resources",
                    "url": "https://www.spj.org/ethics-hotline.asp",
                    "platform": "SPJ"
                }
            ]
        })
    
    # 7. If article is short
    if word_count < 200:
        recommendations.append({
            "module": "Comprehensive Reporting",
            "reason": "Your article is relatively short. Learn to develop stories with depth and comprehensive coverage.",
            "resources": [
                {
                    "type": "video",
                    "title": "How to Develop a News Story",
                    "url": "https://youtu.be/O5B5U3fK-KM",
                    "platform": "YouTube"
                },
                {
                    "type": "article",
                    "title": "In-Depth Reporting Techniques",
                    "url": "https://www.niemanlab.org/",
                    "platform": "Nieman Lab"
                }
            ]
        })
    
    # 8. General journalism resources if no specific issues
    if not recommendations:
        recommendations.append({
            "module": "Advanced Journalism Techniques",
            "reason": "Your article shows strong fundamentals! Continue learning advanced techniques to reach mastery.",
            "resources": [
                {
                    "type": "course",
                    "title": "Advanced Journalism Specialization",
                    "url": "https://www.coursera.org/specializations/journalism",
                    "platform": "Coursera"
                },
                {
                    "type": "video",
                    "title": "Investigative Journalism Masterclass",
                    "url": "https://youtu.be/rBdVBB7mxjY",
                    "platform": "YouTube - Masterclass"
                },
                {
                    "type": "article",
                    "title": "Pulitzer Prize Winning Stories Analysis",
                    "url": "https://www.pulitzer.org/",
                    "platform": "Pulitzer Center"
                }
            ]
        })
    
    return recommendations[:5]  # Limit to top 5 most important


def estimate_syllables(text: str) -> int:
    """Estimate syllable count for readability calculation"""
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    
    syllable_count = 0
    for word in words:
        # Basic syllable counting heuristic
        vowels = 'aeiouy'
        word_syllables = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                word_syllables += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e') and word_syllables > 1:
            word_syllables -= 1
        
        # Ensure at least one syllable per word
        if word_syllables == 0:
            word_syllables = 1
            
        syllable_count += word_syllables
    
    return max(syllable_count, len(words))  # At least one syllable per word
