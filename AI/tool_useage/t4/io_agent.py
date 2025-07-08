# io_agent.py

def get_user_input():
    user_input = input("What would you like to do? (Tools include Calculator, word counter and reverse text): ")
    print(f"[DEBUG] I/O Agent: Received input → {user_input}")
    return user_input

def display_output(response):
    print(f"[DEBUG] I/O Agent: Final response to user:\n{response}")
