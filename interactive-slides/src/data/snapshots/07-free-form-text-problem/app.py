from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example: Unstructured extraction (problematic)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": """
            Extract the following details from this text:

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
    ]
)

print(response.choices[0].message.content)