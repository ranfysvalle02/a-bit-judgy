import ray
from typing import Any, Callable, Dict
import ollama
def sample_function(question=""):
        sample_call = """
**Call Transcript**

**Date:** November 20, 2024

**Time:** 10:11 AM EST

**Participants:**

- **Sales Representative:** Jane Doe
- **Prospective Client:** John Smith

**Transcript:**

**Jane Doe:** Good morning, John. Thank you for taking the time to speak with me today. How are you?

**John Smith:** Good morning, Jane. I'm doing well, thank you.

**Jane Doe:** I'm glad to hear that. I understand you're interested in our [Product/Service]. Could you share what specific challenges you're facing that led you to consider our solution?

**John Smith:** Certainly. We're currently experiencing inefficiencies in our [specific area], which is affecting our overall productivity.

**Jane Doe:** I see. Many of our clients have faced similar issues. Our [Product/Service] is designed to address these challenges by [briefly describe solution].

**John Smith:** That sounds promising. How does your solution integrate with our existing systems?

**Jane Doe:** Great question. Our solution offers seamless integration with [mention relevant systems], ensuring a smooth transition without disrupting your current operations.

**John Smith:** Integration is crucial for us. What kind of support do you provide during the implementation phase?

**Jane Doe:** We offer comprehensive support, including [mention support services], to ensure your team is fully equipped to utilize our solution effectively.

**John Smith:** That's reassuring. Could you provide some examples of how your solution has benefited other clients in our industry?

**Jane Doe:** Absolutely. For instance, [Client A] saw a [percentage]% increase in efficiency within [timeframe] of implementing our solution. Similarly, [Client B] reported significant cost savings and improved team collaboration.

**John Smith:** Impressive. What are the pricing options available?

**Jane Doe:** Our pricing is flexible and tailored to meet the specific needs of our clients. I'd be happy to provide a detailed proposal after assessing your requirements more closely.

**John Smith:** That works for me. What are the next steps?

**Jane Doe:** I'll prepare a customized proposal outlining how our solution can address your challenges, along with pricing details. We can then schedule a follow-up meeting to discuss it in detail.

**John Smith:** Sounds good. I look forward to reviewing the proposal.

**Jane Doe:** Thank you, John. I appreciate your time today and look forward to our next conversation.

**John Smith:** Thank you, Jane. Have a great day.

**Jane Doe:** You too. Goodbye.

**End of Call**
======================
"""
        response = ollama.chat(model='llama3.2:3b', messages=[
        {
            'role': 'user',
            'content': f'[call]\n{sample_call}\n[/call]\n\n\n{question} [max 5 word]',
        },
        ])
        print(response['message']['content'])
        ai_msg = response['message']['content']
        return ai_msg
def run_function_in_parallel(func: Callable, N: int, question: str) -> Dict[int, Any]:
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
        return func(question)

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
    results = run_function_in_parallel(sample_function, N, question="Is this a good conversation?")

    # Print the results
    for run_id, result in results.items():
        print(f"Run {run_id}: Result = {result}")
    # Shutdown Ray (optional)
    ray.shutdown()

"""
Run 0: Result = Conversational flow is excellent.
Run 1: Result = Yes, it's a solid conversation.
Run 2: Result = Yes, it's a good start.
Run 3: Result = Yes, it is a solid conversation.
Run 4: Result = Effective, but lacking specific data.
"""
