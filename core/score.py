import os

SCORE_FILE = "assets/highscore.txt"

def load_highscore():

    if not os.path.exists(SCORE_FILE):

        with open(SCORE_FILE, "w") as f:
            f.write("0")

        return 0

    try:

        with open(SCORE_FILE, "r") as f:
            return int(f.read())

    except:

        with open(SCORE_FILE, "w") as f:
            f.write("0")

        return 0

def save_highscore(score):

    os.makedirs("assets", exist_ok=True)

    current_highscore = load_highscore()

    if score > current_highscore:

        with open(SCORE_FILE, "w") as f:
            f.write(str(score))
