from langchain_core.tools import tool


@tool
def greet_user(name:str):
    """ Greets the user with a welcome message for the crypto trading agent. """
    return f"Welcome {name} to the crypto trading agent!"

