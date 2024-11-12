import time
import json
import os
import random
from typing import List, Dict
from vertexai.generative_models._generative_models import GenerativeModel

class RocketLeagueGeminiGenerator:
    def __init__(self):
        self.MODEL_ID = "gemini-1.5-pro-001"
        self.model = GenerativeModel(self.MODEL_ID)
        #stopping generation of stories at $300 or less 
        self.BUDGET = 300
        self.COST_PER_1K_CHARS = 0.00025
        self.MAX_CHARS = int((self.BUDGET / self.COST_PER_1K_CHARS) * 1000)
        
        self.generation_config = {
            'candidate_count': 1,
            'temperature': 0.7,
            'top_p': 0.9,
            'max_output_tokens': 1024,
        }
        
        self.stories_generated = 0
        self.characters_generated = 0
        self.last_aspect_index = 0

        self.gameplay_aspects = {
            "mechanics": [
                "aerial control optimization",
                "ground dribbling mastery",
                "wall-play execution",
                "recovery techniques",
                "boost management efficiency",
                "flip reset mechanics",
                "ceiling shot execution",
                "air dribble control",
                "power shot accuracy",
                "advanced flicks"
            ],
            "strategy": [
                "rotation optimization",
                "boost control systems",
                "pressure maintenance",
                "defensive positioning",
                "offensive setups",
                "transition plays",
                "kickoff strategies",
                "possession control",
                "space creation",
                "counter-attack execution"
            ],
            "game_sense": [
                "challenge timing",
                "fake play execution",
                "demo integration",
                "boost denial tactics",
                "passing play setups",
                "shot selection",
                "save techniques",
                "aerial challenge decisions",
                "pressure application",
                "momentum management"
            ],
            "team_play": [
                "communication systems",
                "rotation synchronization",
                "boost coordination",
                "defensive coverage",
                "offensive coordination",
                "transition timing",
                "challenge coordination",
                "recovery rotations",
                "pressure maintenance",
                "position adaptations"
            ]
        }

        self.aspect_list = []
        for category, aspects in self.gameplay_aspects.items():
            for aspect in aspects:
                self.aspect_list.append((category, aspect))
        random.shuffle(self.aspect_list) 

    def create_prompt(self, category: str, aspect: str) -> str:
        return f"""As an expert Rocket League 3v3 coach, provide a focused set of advice about {aspect} in {category} gameplay.

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

    def save_progress_state(self, output_dir: str):
        state = {
            "stories_generated": self.stories_generated,
            "characters_generated": self.characters_generated,
            "last_aspect_index": self.last_aspect_index,
            "budget_used": (self.characters_generated / 1000) * self.COST_PER_1K_CHARS,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        state_file = os.path.join(output_dir, "generation_state.json")
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)
        
        print(f"Progress state saved to {state_file}")

    def load_progress_state(self, output_dir: str) -> Dict:
        state_file = os.path.join(output_dir, "generation_state.json")
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.stories_generated = state["stories_generated"]
                self.characters_generated = state["characters_generated"]
                self.last_aspect_index = state["last_aspect_index"]
                print(f"Loaded previous state from {state_file}")
                print(f"Last run statistics:")
                print(f"- Stories generated: {self.stories_generated}")
                print(f"- Characters generated: {self.characters_generated:,}")
                print(f"- Budget used: ${state['budget_used']:.2f}")
                print(f"- Last timestamp: {state['timestamp']}")
                return state
        except FileNotFoundError:
            print("No previous state found, starting fresh")
            return {}

    def save_stories(self, stories: List[str], output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        
        stories_file = os.path.join(output_dir, "stories.txt")
        with open(stories_file, 'w', encoding='utf-8') as f:
            f.write("\n\n---\n\n".join(stories))
        
        backup_file = os.path.join(output_dir, f"stories_backup_{int(time.time())}.txt")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("\n\n---\n\n".join(stories))
        
        self.save_progress_state(output_dir)
        
        print(f"\nProgress saved:")
        print(f"- Main file: {stories_file}")
        print(f"- Backup file: {backup_file}")
        print(f"- Stories: {len(stories)}")
        print(f"- Budget used: ${(self.characters_generated / 1000) * self.COST_PER_1K_CHARS:.2f} of ${self.BUDGET}")
        print(f"- Characters remaining: {self.MAX_CHARS - self.characters_generated:,}")

    def load_existing_stories(self, output_dir: str) -> List[str]:
        stories_file = os.path.join(output_dir, "stories.txt")
        try:
            with open(stories_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    stories = content.split("\n\n---\n\n")
                    return stories
        except FileNotFoundError:
            return []
        return []

    def generate_story(self) -> tuple[str, int]:
        category, aspect = self.aspect_list[self.last_aspect_index % len(self.aspect_list)]
        prompt = self.create_prompt(category, aspect)
        try:
            response = self.model.generate_content(
                [{'role': 'user', 'parts': [{'text': prompt}]}],
                generation_config=self.generation_config
            )
            story = response.text.strip()
            chars = len(story)
            return story, chars, category, aspect
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "", 0, category, aspect

    def generate_dataset(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.load_progress_state(output_dir)
        stories = self.load_existing_stories(output_dir)
        
        print(f"\nGenerating stories within ${self.BUDGET} budget...")
        print(f"Maximum characters allowed: {self.MAX_CHARS:,}")
        print(f"Starting from story #{len(stories) + 1}")
        
        try:
            while self.characters_generated < self.MAX_CHARS:
                print(f"\nGenerating story #{len(stories) + 1}")
                
                story, chars, category, aspect = self.generate_story()
                print(f"Category: {category}")
                print(f"Aspect: {aspect}")
                
                if story:
                    if self.characters_generated + chars > self.MAX_CHARS:
                        print("Would exceed budget. Stopping generation.")
                        break
                    
                    preview = story[:150] + "..." if len(story) > 150 else story
                    print(f"\nNew story preview: {preview}")
                    print(f"Characters in this story: {chars}")
                    
                    stories.append(story)
                    self.characters_generated += chars
                    self.stories_generated += 1
                    self.last_aspect_index += 1
                    
                    if self.stories_generated % 5 == 0:
                        print(f"\nSaving checkpoint at {self.stories_generated} stories...")
                        self.save_stories(stories, output_dir)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nGeneration interrupted by user. Saving progress...")
            self.save_stories(stories, output_dir)
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            print("Saving current progress...")
            self.save_stories(stories, output_dir)
            raise
        
        self.save_stories(stories, output_dir)
        
        print(f"\nFinal Statistics:")
        print(f"Stories generated: {self.stories_generated}")
        print(f"Total characters: {self.characters_generated:,}")
        print(f"Final cost: ${(self.characters_generated / 1000) * self.COST_PER_1K_CHARS:.2f}")
        print(f"Average chars/story: {self.characters_generated / self.stories_generated if self.stories_generated > 0 else 0:.2f}")

def main():
    generator = RocketLeagueGeminiGenerator()
    output_dir = "rocket_league_output_v2"
    generator.generate_dataset(output_dir)

if __name__ == "__main__":
    main()