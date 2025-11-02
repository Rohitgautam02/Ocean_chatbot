# chatbot.py
from data_pipeline import save_conversation

def preprocess(text):
    """Simple preprocessing"""
    return text.lower().strip()

def get_response(user_input):
    """Generate response based on keywords (rule-based logic)"""
    if "temperature" in user_input:
        return "Ocean temperature varies with depth and region. Near the equator, surface temperature is usually higher."
    elif "salinity" in user_input:
        return "Salinity near the equator averages around 35 PSU, but it decreases near heavy rainfall areas."
    elif "argo" in user_input:
        return "Argo floats collect temperature and salinity data from the world’s oceans every 10 days."
    elif "data" in user_input:
        return "ARGO data is available in NetCDF format, containing ocean temperature, salinity, and other variables."
    elif "hello" in user_input:
        return "Hello! I’m FloatChat, your ocean data assistant. Ask me about ocean parameters!"
    elif "bye" in user_input:
        return "Goodbye! Your chat has been saved."
    else:
        return "Sorry, I don't have information about that yet. Try asking about salinity, temperature, or Argo floats."

def run_chatbot():
    print("🌊 FloatChat - Ocean Data Assistant 🌊")
    print("Type 'bye' to exit.\n")

    while True:
        user_input = input("You: ")
        processed_input = preprocess(user_input)
        response = get_response(processed_input)

        print("Bot:", response)
        save_conversation(user_input, response)

        if "bye" in processed_input:
            break

if __name__ == "__main__":
    run_chatbot()
