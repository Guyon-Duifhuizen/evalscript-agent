# 📦 evalscript-agent

## 🌟 Overview

`evalscript-agent` is a Python package designed to facilitate the generation of EvalScripts for Sentinel Hub collections. The package automates the process of listing collections, selecting a random feature, and using that context to generate EvalScripts through a query prompt. The goal is to create a loop where the Sentinel Hub processing API response image is fed back into the EvalScript generator to iteratively refine the image visualization based on the initial prompt.

## ✨ Features

- 📚 **List Collections**: Retrieve and list all available collections from Sentinel Hub.
- 🎲 **Random Feature Selection**: Select a random feature from a specified collection for processing.
- 📝 **EvalScript Generation**: Use OpenAI's GPT-4o to generate EvalScripts based on a user-defined query and the context of the selected feature.
- 🔄 **Iterative Refinement**: Loop the Sentinel Hub processing API response image back into the EvalScript generator to refine the visualization iteratively.

## 📥 Installation

To install the required dependencies, run:
```bash
python3 venv -m .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## 🚀 Usage

1. **Set Up Environment Variables**: Ensure that your environment is configured with the necessary API keys, particularly `OPENAI_API_KEY` for accessing OpenAI's services, and [SH credentials](https://sentinelhub-py.readthedocs.io/en/latest/configure.html).

2. **Run the Script**: Use the gpt_query.py script to list collections, select a feature, and generate an EvalScript—still in hacking phase.

3. **Iterative Loop**: The next steps involve creating a loop where the Sentinel Hub processing API response image is fed back into the EvalScript generator. This loop aims to refine the EvalScript until the desired visualization is achieved.
