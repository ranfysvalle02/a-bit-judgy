import ray
from typing import Any, Callable, Dict
import ollama
def sample_function(question="",max_word=5):
        sample_call = """
**Call Transcript**

**Date:** November 20, 2024

**Time:** 10:11 AM EST

**Participants:**

- **Sales Representative:** Jane Doe
- **Prospective Client:** John Smith

**Transcript:**

**Jane Doe:** Good morning, John. Thank you for taking the time to speak with me today. How are you?

**John Smith:** Good morning, Jane. I'm well, thank you.

**Jane Doe:** I'm glad to hear that. I understand you're exploring solutions to enhance your team's productivity. Could you share some of the challenges you're currently facing?

**John Smith:** We're dealing with several issues. Our current software is outdated, leading to frequent downtime. Additionally, our team struggles with collaboration across departments, which hampers efficiency.

**Jane Doe:** I see. Many organizations encounter similar obstacles. Our SaaS platform is designed to address these challenges by providing real-time collaboration tools and robust uptime guarantees.

**John Smith:** That sounds interesting. However, we've invested heavily in our existing systems. How seamless is the integration process with your solution?

**Jane Doe:** Integration is a priority for us. Our platform offers APIs and supports various plugins to ensure compatibility with your current systems, minimizing disruption during the transition.

**John Smith:** We've had issues with integrations in the past, so I'm cautious. What kind of support do you offer during the implementation phase?

**Jane Doe:** We provide comprehensive onboarding support, including dedicated account managers and 24/7 technical assistance, to ensure a smooth implementation and address any concerns promptly.

**John Smith:** That's good to know. Can you share examples of how your solution has benefited companies similar to ours?

**Jane Doe:** Certainly. For instance, [Client A], a mid-sized firm in your industry, reported a 30% increase in productivity within six months of adopting our platform. They also noted improved cross-departmental collaboration.

**John Smith:** Those are impressive numbers. However, budget constraints are a concern for us. What pricing options do you offer?

**Jane Doe:** We understand budget considerations are crucial. Our pricing is scalable, allowing you to choose a plan that aligns with your current needs and can adjust as your requirements evolve.

**John Smith:** I appreciate that flexibility. What are the next steps if we decide to proceed?

**Jane Doe:** I'd recommend scheduling a personalized demo to showcase how our platform can specifically address your challenges. Following that, we can discuss a tailored proposal that fits your budget and timeline.

**John Smith:** A demo sounds like a good idea. Let's arrange that.

**Jane Doe:** Great. I'll send over some available times for the demo. Thank you for your time today, John.

**John Smith:** Thank you, Jane. I look forward to the demo.

**Jane Doe:** Have a great day.

**John Smith:** You too.

**End of Call** 
======================
"""
        response = ollama.chat(model='llama3.2:3b', messages=[
        {
            'role': 'system', 
            'content': f'You are a helpful AI assistant who analyzes call transcripts. [important! response must always be max {max_word} words]'
        },
        {
            'role': 'user',
            'content': f'[call]\n{sample_call}\n[/call]\n\n\n{question} [important! max {max_word} words]',
        },
        ])
        print(response['message']['content'])
        ai_msg = response['message']['content']
        return ai_msg
def run_function_in_parallel(func: Callable, N: int, question: str, max_word: int) -> Dict[int, Any]:
    """
    Executes the given function `func` N times in parallel using Ray and returns a dictionary
    mapping each run index to its result.

    Parameters:
    - func: The function to execute. It should be serializable by Ray.
    - N: The number of times to run the function in parallel.
    - *args: Positional arguments to pass to `func`.
    - **kwargs: Keyword arguments to pass to `func`.

    Returns:
    - A dictionary where keys are run indices (0 to N-1) and values are the results of each run.
    """

    # Initialize Ray if it hasn't been initialized yet
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    # Define a remote version of the input function
    @ray.remote
    def remote_func():
        return func(question, max_word)

    # Launch N parallel tasks
    futures = [remote_func.remote() for _ in range(N)]

    # Wait for all tasks to complete and gather results
    results = ray.get(futures)

    # Create a dictionary mapping run indices to results
    result_dict = {i: result for i, result in enumerate(results)}

    return result_dict

# Example Usage
if __name__ == "__main__":
    # Number of parallel runs
    N = 5
    
    # Run the function in parallel
    results = run_function_in_parallel(sample_function, N, question="Based on the transcript and considering our company's focus on a consultative selling approach, identify the sales motion used, choosing from: Solution Selling, Consultative Selling, Transactional Selling, or SPIN Selling.", max_word=3)

    # Print the results
    for run_id, result in results.items():
        print(f"Run {run_id}: Result = {result}")
    # Shutdown Ray (optional)
    ray.shutdown()

"""
# TEST 1
Run 0: Result = Consultative Selling
Run 1: Result = Consultative Selling
Run 2: Result = Consultative Selling
Run 3: Result = Consultative Selling
Run 4: Result = Consultative Selling
-----------------------------
"""
