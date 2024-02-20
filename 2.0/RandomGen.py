import random

def generate_matches(teams):
    matches = []

    while len(teams) >= 2:
        team1 = teams.pop(0)
        team2 = None

        # Keep generating team2 until it is different from team1 and has no common members
        while team2 is None or any(player in team1 for player in team2):
            random.shuffle(teams)
            team2 = teams.pop(0)

        match = (team1[0], team2[0], team1[1], team2[1])
        matches.append(match)

    return matches

def main():
    team_a = [("Jimit", "A"), ("Abhishek", "A"), ("Aman", "A"), ("Amey", "A")]
    team_b = [("Saurabh", "B"), ("Krishna", "B"), ("Romit", "B")]
    team_c = [("Sachin", "C"), ("Sidhant", "C"), ("Shiv", "C"), ("Sagar", "C"), ("Sumit", "C")]

    all_teams = team_a + team_b + team_c
    random.shuffle(all_teams)

    knockout_matches = generate_matches(all_teams)

    for i, match in enumerate(knockout_matches, start=1):
        print(f"Match {i}: {match[0]} ({match[2]}) vs. {match[1]} ({match[3]})")

if __name__ == "__main__":
    main()
