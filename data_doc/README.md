# Data Management Specification Document
## Rocket League Gameplay Training Data

## Document Version
|
 Version 1.0 
|
 Date - Nov 13 , 2024      
|
 Ashutosh Tiwari
|
 Changes Made on Nov 13
|

## Table of Contents
1. [Project Overview](##1.-Project-Overview)
2. [Main Data Sources](##2.-Main-Data-Sources)
3. [Data format and Storage](##-3.-Data-Format-and-Storage)
4. [More on Youtube data collection](##4-More-on-Youtube-data-collection-and-post-processing-[Work-in-progress])
---

## 1. Project Overview

### 1.1 Purpose
Documentation of data collection, processing, and storage for creating a Rocket League gameplay training dataset.

### 1.2 Project Goals
- Create comprehensive training dataset of Rocket League gameplay (with focus on 3v3 gameplay setting)
- Add stopwords, tokenization and EOS tokens for efficient model training 
- Getting data into a specified format (using prompt engineering) for faster model training

## 2. Main Data Sources

### 2.1 Primary Data Source
**YouTube Data API v3** 
- Content Type - Video transcripts/captions with video titles (also collecting video_ids)
- Source Format - Raw text/captions (See file formats below for more info)
- Access Method - Using YouTube Data v3 API from GCP
- Rate Limits -  Currently we have 10,000 units per day per key due to quota restrictions (Requst submitted for increasing quota)

[More details data collection in **Youtube Datascrape Section**](#4.-More-on-Youtube-data-collection-and-post-processing)

---

### 2.2 LLM based synthetic data generation 
## Gemini Pro 
Getting synthetic data using prompt engineering from Gemini Pro - Version used - ```gemini-1.5-pro-001```
#### Type 1 : Generic Prompt 
```
"""As a Rocket League 3v3 AI coach, provide detailed technical advice about mechanics, strategies, configurations, tips, tricks, and possible mistakes and its improvements.

Focus on:
- Specific techniques and methods
- When and how to use them
- Common errors and fixes
- Training recommendations

Be direct and technical. Stay under 500 words."""
```

#### Type 2 : Story format prompt 
```
"""As a Rocket League coach, create a 3v3 match story focusing on {aspect}.

Write a brief game moment including:
1. Game situation and challenge (score, position)
2. How the team executed their {category} approach
3. What happened and why it worked/failed
4. Quick tips for improvement

Be specific about mechanics, positioning, boost usage, and team coordination.
Keep it conversational, under 250 words."""
```

#### Type 3 : Story Format with "Specific Starters..."
```
story_starters = [
            "When encountering {scenario} in competitive 3v3, pro players recommend that",
            "A common challenge in 3v3 matches is {scenario}. The best strategy here is to",
            "During high-level gameplay, if {scenario} occurs, experienced players will",
            "One critical situation in 3v3 is {scenario}. To handle this effectively, you should",
            "Many players struggle with {scenario} in 3v3. The optimal approach is to"
]

"""As a professional Rocket League 3v3 coach, provide specific tactical advice for the following scenario:

```{story_start}```...

Create a concise response (maximum 400 words) that continues the story starter above and covers:

1. Primary Strategy
- Immediate tactical response
- Key mechanical execution
- Positioning requirements

2. Team Dynamics
- Communication priorities
- Role distribution
- Support positioning

3. Technical Details
- Specific controls/inputs
- Timing considerations
- Mechanical sequences

4. Risk Management
- Common pitfalls
- Backup options
- Recovery plans

Format the response to start exactly with:
"```{story_start}...```"

Keep the advice practical and focused on high-level competitive play. Include specific mechanical inputs where relevant."""
```


## OpenAI 
Getting synthetic data using prompt engineering from OpenAI - Version used - ```gpt-4```

#### Type 1 : Generic Prompt
```
"""As an expert Rocket League 3v3 coach, provide a focused set of advice about ```{aspect}``` in ```{category}``` gameplay.

Create a concise coaching tip section (maximum 500 words) covering:

1. Technical Execution
- Core mechanics involved
- Key inputs and timing
- Critical positioning requirements

2. Implementation Guide
- When to use this technique/strategy
- How to integrate with team play
- Key decision-making points

3. Common Mistakes
- Typical errors to avoid
- Quick fixes and solutions
- Recovery options

4. Training Tips
- Specific practice methods
- Key focus points
- Progress indicators

Keep the tone direct and practical, focusing on actionable advice a player can immediately use.
Maintain technical precision while being concise and clear."""

Identified gameplay aspects (as values of dict) with categories (as keys of dict) of Rocket league gameplay to use in prompt.
```
     "mechanics": [
                "aerial control optimization",
                "ground dribbling mastery",
                .....
            ],
            "strategy": [
                "rotation optimization",
                "boost control systems",
                ..........
            ],
            "game_sense": [
                "challenge timing",
                "fake play execution",
                ............
            ],
            "team_play": [
                "communication systems",
                "rotation synchronization",
                ........
            ]
```
END
```

### Tyep 2 : Story creation prompt 
```
base_prompt = """Generate a Rocket League 3v3 gameplay analysis. Include:
1. Specific gameplay situation
2. Player actions and decisions
3. Key strengths shown
4. Main area for improvement
5. Some practice tip

Format: Start with "Here's what happened in the match:" and keep the response focused and specific.
Target length: 400-500 words maximum."""
```
or 
```
base_prompt = """Create a short Rocket League 3v3 game story focusing on {aspect}. Include:
1. What the team did
2. How they executed it
3. Why it worked (or didn't)

Keep it natural and conversational, like a replay analysis. Maximum 500 words."""
```

### 2.3 Other unreliable sources with "low quality" data 
- Reddit channel and sub-reddits data
- Twitch streaming data 
- Data from official gameplay website 

---

## 3. Data Format and Storage 

```
gs://eva-interns/ashutosh/
├── Gemini/
│   ├── <generic format data generated via Gemini-pro from prompts above - Separator used "---">
│   ├── <stories format data generated via Gemini-pro from prompts above - Separator used "---">
│   ├── <"Story starters" data generated via Gemini-pro from prompts above - Separator used "---">
├── OpenAI/
│   ├── <Generic prompt data generated via gpt-4 from prompts above - Separator used "---" >
└── Youtube/ 
│   ├── processed/
│   │   ├── <Data with only [VIDEO_TITLE] and EOS token added after end of each paragraph of text>
|   |   ├── <Data with EOS token + Ingesting it to Gemini-pro for specific formatting>
│   └── unprocessed/
|   |   ├── <Raw transcript data output - single line text with NO separators - needs tokenization>
```


---

## 4. More on Youtube data collection and post-processing [Work in progress]

Specific details on Post-processing for youtube data in ```processed``` data is below - 
### Type 1 - Transcripts ingested to Gemini-pro for conversational formatting 
Files - 
```youtube_to_gemini_processed.txt``` and ```youtube_to_gemini_processed_2.txt```

*[ VIDEO_TITLE ]* <br>
< formatting according to one of the earlier story-like prompt passed> <br>
*[ EOS ]* - used as a paragraph separator for each video transcript

### Type 2 - Raw transcripts with EOS token added after every new transcript (Not passed to gemini-pro)

All remaining files in the folder <br>

*[ VIDEO_TITLE ]* <br>
< raw pulled transcript data output by youtube api> <br>
*[ EOS ]* - used as a paragraph separator for each video transcript
