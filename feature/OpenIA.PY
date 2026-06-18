import os
from openai import OpenAI
from dotenv import load_dotenv


# Le especificas el nombre exacto de tu archivo de configuración
load_dotenv("Gemini.env") 

#print(os.getenv("GEMINI_API_KEY"))  # Verifica que la variable se cargue correctamente

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)