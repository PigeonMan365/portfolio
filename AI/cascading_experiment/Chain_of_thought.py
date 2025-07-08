# chain_of_thought.py

from ollama import Client
from rich import print
from rich.console import Console
from rich.prompt import Prompt

client = Client()
console = Console()

# ---- Step-by-step reasoning prompt for the main model ----
COT_PROMPT = """You are an expert reasoning assistant. Your goal is to answer the question step-by-step, making sure each step is logical and clearly explained.

Question: {question}

Answer (let's think step by step):"""

# ---- Evaluation prompt for the critic model ----
EVALUATOR_PROMPT = """You are a logic critic assistant. The following is a step-by-step reasoning output. Your task is to check for correctness, logic flow, and completeness. Suggest corrections or approve as needed.

Step-by-step reasoning:
{cot_output}

Your evaluation:"""

def get_chain_of_thought_response(question: str, model: str = "llama2"):
    full_prompt = COT_PROMPT.format(question=question)
    response = client.chat(model=model, messages=[
        {"role": "user", "content": full_prompt}
    ])
    return response['message']['content'].strip()

def get_evaluation(cot_output: str, model: str = "deepseek-r1:1.5b"):
    eval_prompt = EVALUATOR_PROMPT.format(cot_output=cot_output)
    response = client.chat(model=model, messages=[
        {"role": "user", "content": eval_prompt}
    ])
    return response['message']['content'].strip()

def main():
    console.rule("[bold green]Chain of Thought Prompting")
    while True:
        question = Prompt.ask("\nEnter a question (or type 'exit')")
        if question.lower() in ['exit', 'quit']:
            break

        console.print("\n[bold blue]Generating step-by-step answer...")
        cot_answer = get_chain_of_thought_response(question)
        console.print(f"\n[white on black]CoT Output:\n{cot_answer}\n")

        console.print("[bold yellow]Evaluating reasoning with DeepSeek...")
        evaluation = get_evaluation(cot_answer)
        console.print(f"\n[green]Critic Evaluation:\n{evaluation}\n")

if __name__ == "__main__":
    main()
