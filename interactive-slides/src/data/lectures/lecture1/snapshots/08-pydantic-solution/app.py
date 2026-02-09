from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define structured output schema
class ExtractedData(BaseModel):
    name: str
    date_of_birth: str
    car_model: str
    car_year: str
    car_color: str
    license_plate_number: str
    address: str
    phone_number: str

# Structured extraction
response = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": """
            Extract the following details from this text and format them in a structured way.

            Text: 'Alice Smith was born on June 12, 1990.
            She recently bought a car, a red 2020 Toyota Corolla, with a license
            plate number ABC1234. Alice lives at 987 Maple Avenue, Suite 201, in
            Seattle, WA, 98101. She prefers to be contacted by phone at (206) 987-6543.'

            Details to Extract:
            - Name
            - Date of Birth
            - Car Model
            - Car Year
            - Car Color
            - License Plate Number
            - Address
            - Phone Number
            """
        }
    ],
    response_format=ExtractedData
)

# Access structured data directly
data = response.choices[0].message.parsed
print(f"Name: {data.name}")
print(f"Car: {data.car_year} {data.car_color} {data.car_model}")
print(f"Phone: {data.phone_number}")