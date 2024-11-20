import random
import string
from openai import AzureOpenAI
import ray
from typing import Any, Callable, Dict
import json

def run_function_in_parallel(func: Callable, N: int) -> Dict[int, Any]:
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
        return func()

    # Launch N parallel tasks
    futures = [remote_func.remote() for _ in range(N)]

    # Wait for all tasks to complete and gather results
    results = ray.get(futures)

    # Create a dictionary mapping run indices to results
    result_dict = {i: result for i, result in enumerate(results)}

    return result_dict


def inject_errors(text, misspell_ratio):
    """Injects errors into a string based on a given ratio.

    Args:
        text (str): The string to inject errors into.
        misspell_ratio (float): The ratio of words to misspell.

    Returns:
        str: The string with errors injected.
    """
    words = text.split()
    misspell_count = int(len(words) * misspell_ratio)
    words_to_misspell = random.sample(words, misspell_count)

    for i, word in enumerate(words):
        if word in words_to_misspell:
            if len(word) > 3:
                words[i] = _extract_random_character(word)
            else:
                words[i] = _add_random_character(word)

    return ' '.join(words)

def _extract_random_character(word):
    """Removes a random character from a word.

    Args:
        word (str): The word to remove a character from.

    Returns:
        str: The word with a character removed.
    """
    random_index = random.randint(0, len(word) - 1)
    return word[:random_index] + word[random_index + 1:]

def _add_random_character(word):
    """Adds a random character to a word.

    Args:
        word (str): The word to add a character to.

    Returns:
        str: The word with a character added.
    """
    random_char = random.choice(string.ascii_letters)
    random_index = random.randint(0, len(word))
    return word[:random_index] + random_char + word[random_index:]

# Example Usage
if __name__ == "__main__":
    # Number of parallel runs
    N = 5

    def sample_function():
        chat = inject_errors(f"""
## Conversation Snippet
                             
**Alex:** Hey Jamie, I saw the announcement about your expansion—congrats! That’s a huge milestone. How’s everything going with the new product line? I imagine it’s been quite the transition.

**Jamie:** Thanks, Alex! It’s been a whirlwind. We’ve had some incredible moments, but also some challenges. That said, since we started using your platform, we’ve noticed a 150% increase in user engagement, which has been a game changer. Though, as you can imagine, keeping up with the growth hasn’t been without its hiccups.

**Alex:** 150%? That’s fantastic to hear—growth like that doesn’t come easy! It sounds like your team has been working hard. I’d imagine scalability was one of your biggest hurdles. Is the platform holding up under the pressure, or have there been areas where it’s been more of a balancing act?

**Jamie:** It’s definitely held up, and the scalability has been crucial for keeping us afloat. But, if I’m honest, it’s not all smooth sailing. There are still areas where we’re figuring out how to optimize for the new scale. We’ve started exploring the custom analytics tools, which have helped a bit, but we’re finding that diving deeper into them comes with its own set of learning curves.

**Alex:** That’s fair—growth at your pace rarely feels straightforward. The analytics tools can definitely unlock a lot of value, but I get that the complexity might be daunting when your team’s juggling so much else. Have you found that they’re making a measurable difference yet, or is it too early to say?

**Jamie:** It’s a bit of both. We’re already seeing improvements in streamlining some workflows, and application performance has noticeably improved. But at the same time, we’re realizing there’s a whole layer of potential we haven’t fully tapped into yet. It feels like we’re just scratching the surface, which is both exciting and overwhelming.

**Alex:** I can see how that would feel like a double-edged sword—progress is clear, but there’s always that question of how much more is possible. Have you thought about prioritizing specific goals for how you use the tools? It might help to clarify which areas to double down on versus where you can afford to take a lighter touch.

**Jamie:** That’s a good point. Right now, we’re kind of experimenting in a lot of directions at once, which might not be the most focused approach. The plan is to test some of the more advanced configurations soon, but honestly, I’m wondering if we’re biting off more than we can chew.

**Alex:** It’s definitely a balancing act. Experimentation is great, but narrowing the focus might give you a clearer sense of ROI. If you’d find it helpful, I’d be happy to sit down with you and map out some potential strategies—maybe even identify which advanced features align most closely with your immediate goals.

**Jamie:** That might be a good idea. It’s tempting to dive into everything at once, but having a clearer strategy would definitely make the workload more manageable. I’ll reach out once we’ve wrapped up the current tests. Hopefully, by then, we’ll have a better sense of where to focus.

**Alex:** That sounds like a plan! Just let me know when you’re ready, and I’m happy to help however I can. Watching your team navigate this growth is inspiring—there’s so much potential here, even if it feels messy in the moment. Keep me in the loop, okay?

**Jamie:** Will do, Alex. Thanks for the support—it means a lot, especially as we’re working through all this. Fingers crossed for smoother sailing ahead!
""", 0.25)
        # Initialize the Azure OpenAI client
        az_client = AzureOpenAI(
            api_key="",  
            api_version="2024-10-21",
            azure_endpoint="https://.openai.azure.com"
        )
        response = az_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f"""
        [user input]
        ```
        {chat}
        ```
        [/user input]

        [task]
        - What is the `Sales Motion`?
        [/task]

        [response criteria]
        - JSON object with two keys: `user_input`(str) and `sales_motion`(str) [max 5 words]
        - response must be JSON 
        [/response criteria]
        """}
            ],
            response_format={ "type": "json_object" } 
        )
        ai_msg = json.loads(response.choices[0].message.content)
        return ai_msg['sales_motion']
    # Run the function in parallel
    results = run_function_in_parallel(sample_function, N)

    # Print the results
    for run_id, result in results.items():
        print(f"Run {run_id}: Result = {result}")
    # Shutdown Ray (optional)
    ray.shutdown()

"""
2024-11-20 02:07:22,845	INFO worker.py:1777 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
Run 0: Result = Platform engagement and scalability pitch
Run 1: Result = Upselling advanced features
Run 2: Result = upselling advanced analytics tools
Run 3: Result = Upselling advanced features
Run 4: Result = Upsell advanced features
"""
