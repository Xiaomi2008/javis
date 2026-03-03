"""Demo of the weather skill."""

import sys
sys.path.insert(0, "..")

from javis import Javis
from javis.skills.weather_skill import WeatherSkill


def main():
    javis = Javis()
    
    # Register weather skill
    weather = WeatherSkill()
    javis.register_skill(weather)
    
    print("🌤️ Weather Skill Demo")
    print(f"Registered skills: {javis.list_skills()}")
    
    # Get weather
    locations = ["San Francisco", "Beijing", "Tokyo"]
    
    for location in locations:
        print(f"\n📍 {location}:")
        result = javis.skills.weather.get_weather(location)
        print(f"  {result}")


if __name__ == "__main__":
    main()
