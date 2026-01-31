## The Solution: Structured Output using Pydantic Models

**Pydantic** is a Python library for data validation. OpenAI's API integrates with Pydantic to support **structured outputs**—you define a schema, and the model returns data matching that exact structure.

**Step 1: Install Pydantic**
```bash
pip install pydantic
```

**Step 2: Define your schema**
```python
from pydantic import BaseModel

class ExtractedData(BaseModel):
    name: str
    date_of_birth: str
    car_model: str
    car_year: str
    car_color: str
    license_plate_number: str
    address: str
    phone_number: str
```

**Step 3: Use `.parse()` with `response_format`**
```python
response = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Extract the following details..."
    }],
    response_format=ExtractedData
)
```

**Step 4: Access structured data directly**
```python
data = response.choices[0].message.parsed
print(f"Name: {data.name}")
print(f"Car: {data.car_year} {data.car_color} {data.car_model}")
```

No parsing required—just direct attribute access.