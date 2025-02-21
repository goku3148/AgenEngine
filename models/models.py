import google
import openai
import groq
import ollama

class LLMFramework:
    def __init__(self, llm_type: str = "openai", api_key: str = None, temperature: float = 0.7, max_tokens: int = 150,
                 top_p: float = 0.8, top_k: int = 40, gen_local: callable = None):
        """
        Initialize the framework with the specified LLM type.

        Args:
            llm_type (str): Type of LLM to use ("openai", "genai", or "local").
            api_key (str): API key for the selected LLM service.
            temperature (float): Sampling temperature for randomness.
            max_tokens (int): Maximum number of tokens in the response.
            top_p (float): Cumulative probability threshold for token sampling.
            top_k (int): Limits the range of possible next tokens.
            gen_local (callable): User-defined function for handling local LLM logic.
        """
        self.llm_type = llm_type
        self.api_key = api_key
        self.user_defined_gen_local = gen_local
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k

        # Set API key based on LLM type
        if self.llm_type == "openai" and self.api_key:
            openai.api_key = self.api_key
        elif self.llm_type == "genai" and self.api_key:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

    def local_llm(self, model_name: str, prompt: str) -> str:
        """
        Default local LLM handling method. Can be overridden by user-defined function.

        Args:
            model_name (str): Name of the local LLM model.
            prompt (str): Input prompt for the local LLM.

        Returns:
            str: Generated response from the local LLM.
        """
        if self.user_defined_gen_local:
            # Use the user-defined local LLM function
            return self.user_defined_gen_local(model_name=model_name, prompt=prompt)
        else:
            # Default behavior (for demonstration or fallback)
            return f"Local LLM invoked with model '{model_name}' and prompt '{prompt}'."

    def llm_gen(self, prompt: str, model: str = "default"):
        """
        Generate output based on the selected LLM type.

        Args:
            prompt (str): The input prompt for the LLM.
            model (str): Model to use if applicable (e.g., 'gpt-4' for OpenAI or 'text-bison-001' for GenAI).

        Returns:
            str: Generated response from the selected LLM.
        """
        if self.llm_type == "genai":
            return self.llm_genai(prompt=prompt, model=model)
        elif self.llm_type == "openai":
            return self.llm_openai(model=model, prompt=prompt)
        elif self.llm_type == "ollama":
            return self.ollama(model=model, prompt=prompt)
        elif self.llm_type == "groq":
            return self.groq(model=model, prompt=prompt)
        elif self.llm_type == "local":
            return self.local_llm(model_name=model, prompt=prompt)
        else:
            return "Error: Unsupported LLM type."

    def llm_openai(self, model: str, prompt: str, temperature: float = None, max_tokens: int = None):
        """
        Generate a response using OpenAI's API.

        Args:
            model (str): The OpenAI model to use (e.g., 'gpt-4', 'gpt-3.5-turbo').
            prompt (str): The input prompt for the model.
            temperature (float): Sampling temperature for randomness.
            max_tokens (int): Maximum number of tokens for the response.

        Returns:
            str: The generated response from the model.
        """
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return f"Error: Unable to generate response from OpenAI API. Details: {e}"

    def llm_genai(self, prompt: str, model: str = "models/text-bison-001", temperature: float = None,
                  max_tokens: int = None, top_k: int = None, top_p: float = None):
        """
        Generate a response using Google GenAI.

        Args:
            prompt (str): The input prompt for the GenAI model.
            model (str): The GenAI model to use (e.g., 'models/text-bison-001').
            temperature (float): Sampling temperature for randomness.
            max_tokens (int): Maximum number of tokens for the response.
            top_k (int): Limits the range of possible next tokens.
            top_p (float): Limits the cumulative probability of token options.

        Returns:
            str: The generated response from the GenAI model.
        """
        try:
            import google.generativeai as genai
            response = genai.generate_text(
                model=model,
                prompt=prompt,
                temperature=temperature or self.temperature,
                max_output_tokens=max_tokens or self.max_tokens,
                top_k=top_k or self.top_k,
                top_p=top_p or self.top_p
            )
            return response.text
        except Exception as e:
            print(f"Google GenAI Error: {e}")
            return f"Error: Unable to generate response from Google GenAI. Details: {e}"
        
    def groq(self, prompt: str, model: str, temperature: float= None, 
             max_tokens: int = None, top_k: int = None, top_p: float = None):
        
         """
        Generate a response using Groq Api.

        Args:
            prompt (str): The input prompt for the GenAI model.
            model (str): The GenAI model to use (e.g., 'models/text-bison-001').
            temperature (float): Sampling temperature for randomness.
            max_tokens (int): Maximum number of tokens for the response.
            top_k (int): Limits the range of possible next tokens.
            top_p (float): Limits the cumulative probability of token options.

        Returns:
            str:
        """
        
        
