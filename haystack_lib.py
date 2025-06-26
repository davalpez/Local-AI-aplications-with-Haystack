import requests 
from os import getenv
import time
import logging
import warnings
from typing import Optional, Dict, Any, List
from haystack.dataclasses import Document
from haystack import tracing
from haystack import Document, Pipeline, component
from haystack.components.generators.openai import OpenAIGenerator
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.utils import Secret
from haystack.tracing.logging_tracer import LoggingTracer
from haystack.core.component import component, InputSocket, OutputSocket

def Haystack_Logs(level="warning"):
    """
    Configures logging and tracing settings for the Haystack library.

    Args:
        level (str, optional): The logging level to set. If "warning", enables detailed logging and tracing for Haystack.
            Otherwise, sets logging to error level and disables tracing. Defaults to "warning".

    """
    if level == "warning":
        logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
        logging.getLogger("haystack").setLevel(logging.DEBUG)

        tracing.tracer.is_content_tracing_enabled = True # to enable tracing/logging content (inputs/outputs)
        tracing.enable_tracing(LoggingTracer(tags_color_strings={"haystack.component.input": "\x1b[1;31m", "haystack.component.name": "\x1b[1;34m"}))
    else:
        logging.getLogger("haystack").setLevel(logging.ERROR)
        logging.basicConfig(level=logging.ERROR)
        warnings.filterwarnings('ignore')
        tracing.tracer.is_content_tracing_enabled = False

@component
class TimedComponent:
    """
    TimedComponent is a wrapper class that measures and prints the execution time of another component's run method.
    Args:
        component: The component instance to be wrapped and timed.
    Methods:
        run(**kwargs): Executes the wrapped component's run method, timing its execution and printing the duration.
        __getattr__(attr): Delegates attribute access to the wrapped component.
    """    
    
    def __init__(self, component):
        self.component = component
        self.name = component.__class__.__name__

    def run(self, **kwargs):
        start = time.time()
        result = self.component.run(**kwargs)
        end = time.time()
        print(f"{self.name} took {end - start:.2f} seconds")
        return result

    def __getattr__(self, attr):
        return getattr(self.component, attr)


@component
class MiniPHILLM:
    """
    MiniPHILLM is a Haystack component that wraps an OpenAI-compatible language model generator, allowing for prompt-based text generation with customizable system prompts and generation parameters.
    Attributes:
        prompt (InputSocket): The main prompt to send to the language model.
        system_prompt (InputSocket): An optional system prompt to guide the model's behavior.
        generation_kwargs (InputSocket): Optional dictionary of generation parameters.
    Outputs:
        replies (OutputSocket): List of generated text replies from the model.
        meta (OutputSocket): List of metadata dictionaries associated with each reply.
    Methods:
        __init__(): Initializes the component, setting up the language model generator using environment variables for configuration.
        run(prompt, system_prompt=None, generation_kwargs=None): Executes the language model with the provided prompt and parameters, returning generated replies and metadata.
    """
    prompt: InputSocket
    system_prompt: InputSocket
    generation_kwargs: InputSocket

    replies: OutputSocket
    meta: OutputSocket

    def __init__(self):
        API_BASE_URL = getenv("API_BASE_URL").strip().rstrip(',')
        MODEL_PHI = getenv("MODEL_PHI").strip().rstrip(',')
        
        self.llm = OpenAIGenerator(
            api_base_url=API_BASE_URL,
            api_key=Secret.from_token("not-needed"),  # assuming local-only
            model=MODEL_PHI,
            timeout=100,
        )

    @component.output_types(replies=List[str], meta=List[Dict[str, Any]])
    def run(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ):
        result = self.llm.run(
            prompt=prompt,
            system_prompt=system_prompt,
            generation_kwargs=generation_kwargs or {},
        )
        return {
            "replies": result["replies"],
            "meta": result["meta"],
        }
@component
class MiniPHIChat:
    """
    MiniPHIChat is a Haystack component that wraps an OpenAI-compatible chat model for generating conversational replies.
    Attributes:
        prompt (InputSocket): The user prompt to send to the chat model.
        system_prompt (InputSocket): An optional system prompt to guide the model's behavior.
        generation_kwargs (InputSocket): Optional keyword arguments for generation settings.
        replies (OutputSocket): The generated replies from the chat model.
        meta (OutputSocket): Metadata associated with the generated replies.
    Methods:
        __init__(generation_kwargs: Optional[Dict[str, Any]] = None):
            Initializes the MiniPHIChat component with the specified generation keyword arguments.
        run(
            Runs the chat model with the given prompt, system prompt, and generation keyword arguments.
            Returns:
                dict: A dictionary containing the generated replies and associated metadata.
    """
    prompt: InputSocket
    system_prompt: InputSocket
    generation_kwargs: InputSocket

    replies: OutputSocket
    meta: OutputSocket

    def __init__(self,generation_kwargs: Optional[Dict[str, Any]] = None,):
        API_BASE_URL = getenv("API_BASE_URL").strip().rstrip(',')
        MODEL_PHI = getenv("MODEL_PHI").strip().rstrip(',')
        
        self.llm = OpenAIChatGenerator(
            api_base_url=API_BASE_URL,
            api_key=Secret.from_token("not-needed"),  # assuming local-only
            model=MODEL_PHI,
            timeout=100,
            generation_kwargs=generation_kwargs)

    @component.output_types(replies=List[str], meta=List[Dict[str, Any]])
    def run(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ):
        result = self.llm.run(
            prompt=prompt,
            system_prompt=system_prompt,
            generation_kwargs=generation_kwargs or {},
        )
        return {
            "replies": result["replies"],
            "meta": result["meta"],
        }
    
@component
class HackernewsNewestFetcher:
    """
    HackernewsNewestFetcher is a Haystack component designed for Lesson 4, which fetches the newest articles from Hacker News.
    This component retrieves the top 'k' stories from Hacker News, fetches their content and converts them into Document objects for further processing in Haystack pipelines.
    Methods:
        run(top_k: int) -> Dict[str, List[Document]]:
            Fetches the top_k newest Hacker News articles, processes their content, and returns a list of Document objects.
    """
    def __init__(self):
        fetcher = LinkContentFetcher()
        converter = HTMLToDocument()

        html_conversion_pipeline = Pipeline()
        html_conversion_pipeline.add_component("fetcher", fetcher)
        html_conversion_pipeline.add_component("converter", converter)

        html_conversion_pipeline.connect("fetcher", "converter")
        self.html_pipeline = html_conversion_pipeline
        
    @component.output_types(articles=List[Document])
    def run(self, top_k: int):
        articles = []
        trending_list = requests.get(
            url="https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
        )
        for id in trending_list.json()[0:top_k]:
            post = requests.get(
                url=f"https://hacker-news.firebaseio.com/v0/item/{id}.json?print=pretty"
            )
            if "url" in post.json():
                try:
                    article = self.html_pipeline.run(
                        {"fetcher": {"urls": [post.json()["url"]]}}
                    )
                    articles.append(article["converter"]["documents"][0])
                except:
                    print(f"Can't download {post}, skipped")
            elif "text" in post.json():
                print("text in ",id)
                try:
                    articles.append(Document(content=post.json()["text"], meta= {"title": post.json()["title"]}))
                except:
                    print(f"Can't download {post}, skipped")
        return {"articles": articles}