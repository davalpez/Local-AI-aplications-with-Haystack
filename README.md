# Local AI Applications with Haystack


## Acknowledgements

- This project is based on the *Local AI Applications with Haystack* course by **DeepLearning.AI**, and the objective of this repository is solely to
    explore its model agnostic capabilities.
- This project uses the [Haystack 2](https://github.com/deepset-ai/haystack) AI open‑source framework.



> Hands‑on notebooks that show how to build  Retrieval‑Augmented Generation (RAG) and agent pipelines with [Haystack 2](https://docs.haystack.deepset.ai/).\
> All models run on your own hardware—no API keys required. Some other API services with free trial keys are used, but are optional.

## List of content

| Folder                               | Highlights                                               |
| ------------------------------------ | -------------------------------------------------------- |
| **1‑Basic Components in Haystack**   | Minimal example: `DocumentStore → Retriever → Generator` |
| **2‑Customized RAG**                 | Prompt engineering, rerankers, hybrid retrieval          |
| **3‑Creating Custom Components**     | Write & register your own Haystack Component             |
| **4‑Branching Pipelines**            | Conditional routers, parallel document stores            |
| **5‑Self‑Reflecting Agent Pipeline** | Autonomous agent that iteratively refines its answers    |

How to run the

##  How to run this notebook

First, you will need to have VS code installed in your WSL 2.

Then, you will need to have installed LM studio on your computer, load an LLM model and start a server.
You will need to copy the server URL.

In your WSL : 

```bash

# 1. Clone & enter
git clone https://github.com/davalpez/Local-AI-aplications-with-Haystack.git
cd Local-AI-aplications-with-Haystack

# 2. Create an isolated environment (Python ≥ 3.10)
python -m venv .venv
source .venv/bin/activate  

# 3. Install requirements
pip install -r requirements.txt \

```


## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.


