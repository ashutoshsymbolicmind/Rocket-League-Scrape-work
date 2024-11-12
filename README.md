## Description 
1. Each of the scripts differ in How the prompts are structured 
2. 'rocket-league-gemini-master.py' contains the script that was run for previous data shared on Nov 10th 2024.

## Setup if running it on SSH browser in GCP
1. Create a SSH browser session 
2. Create a virtual env using 'python -m venv <ENVIRON_NAME>
3. Install these dependencies 

""
pip install google-cloud-aiplatform
pip install vertexai
""

Alternatively run on google colab - 
 - Run the 'rocket_league_main_script.ipynb' on Google Colab.
 - You will be asked to autheticate user sessions on GCP, confirm the login to GCP to proceed
 - In case, the GCP session stops, simply rerun the notebook, and it picks from the last 

All three files have different prompts to structure the output accordingly. 
