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
    
    Optimized for speed - works in 10-15 seconds like other tools.
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
            "model": "meta/llama-3.1-70b-instruct",
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

        logger.info("AI: Calling NVIDIA AI (optimized for speed like AI Tutor)...")
        
        # Same timeout as AI Tutor (which works reliably)
        response = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Match AI Tutor timeout
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
        if "issues" in ai_result:
            ai_result["critical_issues"] = ai_result["issues"]
        if "top_improvements" in ai_result:
            ai_result["top_3_improvements"] = ai_result["top_improvements"]
        if "explanation" in ai_result:
            ai_result["grade_explanation"] = ai_result["explanation"]
        
        # Add methodology transparency
        ai_result["methodology"] = {
            "analysis_type": "AI-Powered Fast Evaluation (ATS-like)",
            "model": "NVIDIA Meta Llama 3.1 70B Instruct",
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
        logger.error("AI: Analysis timed out after 30s (same as AI Tutor)")
        logger.info("AI: If AI Tutor works but this fails, check prompt complexity or API load")
        return {
            "status": "error",
            "message": "AI analysis timed out (structured output takes longer). Using fallback."
        }
    except Exception as e:
        logger.error(f"AI: Analysis error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"AI analysis failed: {str(e)}"
        }


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
