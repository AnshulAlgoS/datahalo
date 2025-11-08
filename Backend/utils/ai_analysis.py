# utils/ai_analysis.py
from fastapi import HTTPException
from openai import OpenAI
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
USER_AGENT = "DataHaloBot/1.0"

def _get_nvidia_client():
    """
    Lazily initialize OpenAI client for NVIDIA API.
    Ensures NVIDIA_API_KEY is present before making calls.
    """
    key = os.getenv("NVIDIA_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="NVIDIA_API_KEY not set in environment variables!"
        )
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key)

def analyze_journalist(name: str, data: dict):
    """Analyze journalist data using NVIDIA's AI model."""
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=404, detail="Invalid data format")

    # Collect full dataset (articles, bio, socials, affiliations, controversies)
    articles = data.get('articles', [])
    bio = data.get('bio', '')
    socials = data.get('socials', {})
    affiliations = data.get('affiliations', [])
    awards = data.get('awards', [])
    controversies = data.get('controversies', [])

    # Build text corpus intelligently from all sections
    corpus_parts = []
    if bio: corpus_parts.append(f"BIOGRAPHY:\n{bio}")
    if articles:
        corpus_parts.append("ARTICLES:\n" + "\n".join([
            f"{a.get('title', '')} - {a.get('snippet', '')}" for a in articles if a.get('title') or a.get('snippet')
        ]))
    if socials: corpus_parts.append(f"SOCIAL MEDIA LINKS:\n{json.dumps(socials, indent=2)}")
    if affiliations: corpus_parts.append(f"MEDIA AFFILIATIONS:\n{', '.join(affiliations)}")
    if awards: corpus_parts.append(f"AWARDS & RECOGNITIONS:\n{', '.join(awards)}")
    if controversies: corpus_parts.append(f"KNOWN CONTROVERSIES:\n{json.dumps(controversies, indent=2)}")

    text_corpus = "\n\n".join(corpus_parts)[:8000]
    if not text_corpus:
        raise HTTPException(status_code=404, detail="No sufficient journalist data found")

    client = _get_nvidia_client()
    
    prompt = f"""You are DataHalo — an advanced AI journalism intelligence system.
You are tasked with generating a factual, deeply analytical, and professional profile for journalist {name}.
Use all provided data — biography, social presence, articles, awards, affiliations, and controversies — to form a nuanced credibility assessment.
Return only valid JSON with the exact structure below. Do not include explanations or markdown outside the JSON.

{{
    "name": "{name}",
    "biography": "Comprehensive factual summary (150–200 words) integrating career, focus areas, and public image.",
    "careerHighlights": ["Key milestones, publications, or achievements."],
    "mainTopics": ["Major subjects or beats covered."],
    "writingTone": "Analytical / Neutral / Persuasive / Emotional",
    "ideologicalBias": "Left-leaning / Right-leaning / Centrist / Unclear",
    "credibilityScore": {{
        "score": 0-100,
        "reasoning": "Analytical justification for score with evidence."
    }},
    "notableWorks": ["Most impactful investigations or pieces."],
    "awards": ["Awards, recognitions, or nominations."],
    "controversies": ["Summarized objectively, or 'None identified'."],
    "digitalPresence": {{
        "profileImage": "URL or placeholder",
        "verifiedLinks": ["List of active verified social profiles."],
        "mediaAffiliations": ["Publications or organizations associated."]
    }},
    "engagementInsights": {{
        "audienceSentiment": "Positive / Negative / Mixed",
        "influenceLevel": "Low / Moderate / High"
    }},
    "ethicalAssessment": "Balanced, evidence-based 2-paragraph assessment discussing integrity, bias, and credibility."
}}

Source Data:
{text_corpus}
"""

    try:
        logging.info(f"Sending request to NVIDIA API for journalist: {name}")
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-coder-32b-instruct",
            messages=[{
                "role": "system",
                "content": "Respond only with valid JSON that strictly follows user format."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.35,
            max_tokens=2500,
            stream=False
        )

        response_text = completion.choices[0].message.content.strip()

        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            result = json.loads(response_text)

            required_fields = ['name', 'biography', 'mainTopics', 'writingTone']
            missing = [f for f in required_fields if f not in result]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

            return result

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response: {response_text[:300]}...")
            raise HTTPException(
                status_code=500,
                detail="AI returned invalid JSON. Please retry."
            )

    except Exception as e:
        logging.error(f"NVIDIA API error: {str(e)}")
        if any(x in str(e) for x in ["403", "Authorization failed", "Forbidden"]):
            raise HTTPException(
                status_code=401,
                detail="NVIDIA API authorization failed - check your key or endpoint permissions."
            )
        raise HTTPException(status_code=500, detail=str(e))

    prompt = f"""
You are DataHalo — an advanced AI journalism credibility analyst.
Analyze journalist **{name}** using the full dataset below (articles, bio, controversies, awards, social presence).
Return structured JSON with the exact schema and a deep factual narrative.

{{
    "name": "{name}",
    "biography": "Concise but professional factual summary.",
    "mainTopics": ["Key areas of reporting."],
    "writingTone": "Neutral/Emotional/Persuasive/Analytical",
    "ideologicalBias": "Left/Right/Centrist/Unclear",
    "credibilityScore": "0-100 with justification",
    "notableWorks": ["Major investigations."],
    "controversies": ["Criticisms or 'None identified'."],
    "digitalPresence": {{
        "profileImage": "URL or placeholder",
        "verifiedLinks": ["Social profiles if found"],
        "mediaAffiliations": ["Known publications"]
    }},
    "engagementInsights": {{
        "audienceSentiment": "Positive/Negative/Mixed",
        "influenceLevel": "Low/Moderate/High"
    }},
    "ethicalAssessment": "Balanced one-paragraph assessment."
}}

DATA FOR ANALYSIS:
{text_corpus}
"""

    try:
        logging.info(f"Sending request to NVIDIA API for journalist: {name}")
        completion = client.chat.completions.create(
            model="qwen/qwen2.5-coder-32b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.35,
            max_tokens=2500,
            stream=False
        )

        response_text = completion.choices[0].message.content

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logging.error("Invalid JSON response from AI")
            raise HTTPException(
                status_code=500,
                detail="AI returned invalid JSON response"
            )

    except Exception as e:
        logging.error(f"NVIDIA API error: {str(e)}")
        if any(x in str(e) for x in ["403", "Authorization failed", "Forbidden"]):
            raise HTTPException(
                status_code=401,
                detail="NVIDIA API authorization failed - check key and permissions"
            )
        raise HTTPException(status_code=500, detail=str(e))
