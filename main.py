from dotenv import load_dotenv
load_dotenv()

from src.agent import Agent
def main():
    agent = Agent()
    while True:
        print("You> ", end='')
        user_input = input().strip()
        agent.loop(user_input)

if __name__ == "__main__":
    # test()
    main()
    
    
