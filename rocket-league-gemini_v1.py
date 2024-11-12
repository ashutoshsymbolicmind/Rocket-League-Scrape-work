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
        self.BUDGET = 300
        self.COST_PER_1K_CHARS = 0.00025
        self.MAX_CHARS = int((self.BUDGET / self.COST_PER_1K_CHARS) * 1000)
        self.EOS_TOKEN = " EOS" 
        
        self.generation_config = {
            'candidate_count': 1,
            'temperature': 0.7,
            'top_p': 0.9,
            'max_output_tokens': 1024,
        }
        
        self.stories_generated = 0
        self.characters_generated = 0
        self.last_aspect_index = 0

        self.gameplay_scenarios = {
            "defensive_scenarios": [
                "opponent has possession near our goal",
                "teammate missed a save",
                "last defender facing 2v1",
                "low boost in defense",
                "defending against air dribble",
                "opponent setting up ceiling shot",
                "teammate overcommitted upfield",
                "multiple opponents attacking",
                "recovery after demo in defense",
                "backboard defense pressure"
            ],
            "offensive_scenarios": [
                "possession in opponent's corner",
                "high boost with ball control",
                "teammate centered the ball",
                "opponent double committed",
                "zero boost in offense",
                "passing play opportunity",
                "counter-attack transition",
                "opponent missed clear",
                "slow rolling ball midfield",
                "offensive demo opportunity"
            ],
            "midfield_scenarios": [
                "contested 50/50 ball",
                "rotating back post",
                "boost starved rotation",
                "challenging aerial play",
                "intercepting pass play",
                "transition after kickoff",
                "maintaining offensive pressure",
                "supporting aggressive teammate",
                "recovering from bump",
                "coordinating team rotation"
            ],
            "special_situations": [
                "overtime kickoff",
                "low boost kickoff",
                "defending 1 goal lead",
                "trailing by 2 goals",
                "teammate disconnected",
                "opponent playing passive",
                "teammate ball chasing",
                "zero second gameplay",
                "post-demo recovery",
                "boost starved endgame"
            ]
        }

        self.scenario_list = []
        for category, scenarios in self.gameplay_scenarios.items():
            for scenario in scenarios:
                self.scenario_list.append((category, scenario))
        random.shuffle(self.scenario_list)

    def create_prompt(self, category: str, scenario: str) -> str:
        return f"""As a professional Rocket League 3v3 coach, provide specific tactical advice for the following scenario:

When {scenario} in {category}, here's what you should do:

Create a concise response (maximum 400 words) following this structure:

1. Immediate Action
- What to do first
- Key mechanics to use
- Critical positioning

2. Team Coordination
- Communication needs
- Teammate expectations
- Role assignments

3. Follow-up Steps
- Next moves
- Adaptation points
- Recovery position

4. Common Mistakes
- What to avoid
- Emergency backup plans
- Risk management

Format the response to start with:
"In a 3v3 match, when {scenario}, the optimal strategy is to..." 

Keep the advice practical, specific, and focused on high-level competitive play. Include specific button inputs or mechanical techniques where relevant."""

    def generate_story(self) -> tuple[str, int, str, str]:
        category, scenario = self.scenario_list[self.last_aspect_index % len(self.scenario_list)]
        prompt = self.create_prompt(category, scenario)
        try:
            response = self.model.generate_content(
                [{'role': 'user', 'parts': [{'text': prompt}]}],
                generation_config=self.generation_config
            )
            story = response.text.strip() + self.EOS_TOKEN 
            chars = len(story)
            return story, chars, category, scenario
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "", 0, category, scenario

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
                
                story, chars, category, scenario = self.generate_story()
                print(f"Category: {category}")
                print(f"Scenario: {scenario}")
                
                if story:
                    if self.characters_generated + chars > self.MAX_CHARS:
                        print("Would exceed budget. Stopping generation.")
                        break
                    
                    preview = story[:150] + "EOS" if len(story) > 150 else story
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