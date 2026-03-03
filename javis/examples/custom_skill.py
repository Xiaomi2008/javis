"""Example of creating a custom skill."""

from javis import Javis, Skill


class CalculatorSkill(Skill):
    """A calculator skill for math operations."""
    
    name = "calculator"
    description = "Perform mathematical calculations"
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    def factorial(self, n: int) -> int:
        """Calculate factorial."""
        if n < 0:
            raise ValueError("n must be >= 0")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def get_commands(self):
        return {
            "add": self.add,
            "multiply": self.multiply,
            "factorial": self.factorial,
        }


def main():
    javis = Javis()
    
    # Register custom skill
    calc = CalculatorSkill()
    javis.register_skill(calc)
    
    print("🔢 Custom Skill Demo")
    print(f"Skills: {javis.list_skills()}")
    
    # Use via skill registry
    result = javis.skills.calculator.add(5, 3)
    print(f"5 + 3 = {result}")
    
    result = javis.skills.calculator.factorial(5)
    print(f"5! = {result}")
    
    # Or via execute
    result = javis.skills.execute("calculator.multiply", 4, 7)
    print(f"4 * 7 = {result}")


if __name__ == "__main__":
    main()
