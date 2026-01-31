## Setting Up Python + OpenAI Environment

Before we begin, ensure you have Python 3.8+ installed on your system.

### Create a Virtual Environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

**Note:** Once the virtual environment is activated, you can use `python` (instead of `python3`) on all platforms.

### Install Required Packages

First, create a `requirements.txt` file with the following content:

```
openai
python-dotenv
```

Then install from requirements.txt:
```bash
pip install -r requirements.txt
```

Alternatively, you can install packages directly by specifying library names:
```bash
pip install openai python-dotenv
```

### Set Up Your OpenAI API Key

Create a `.env` file in your project directory:

```
OPENAI_API_KEY=sk-proj-...
```

Replace `sk-proj-...` with your actual OpenAI API key.

### Import Dependencies in Python

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```
