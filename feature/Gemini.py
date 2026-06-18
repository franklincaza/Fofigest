import os
from google import genai
from dotenv import load_dotenv

# Le especificas el nombre exacto de tu archivo de configuración
load_dotenv("Gemini.env") 

# Ahora sí va a encontrar la variable sin problemas
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

interaction = client.interactions.create(
    model="Gemini 2 Flash Lite",
    input="dime un chiste de programadores"
)

print(interaction.output_text)