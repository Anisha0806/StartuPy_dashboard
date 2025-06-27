import openai
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# 🔑 Set OpenRouter API Key and base URL
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

# ✅ Helper: Check if query is startup-related
def is_startup_related(query):
    keywords = [
        "startup", "launch", "funding", "investor", "pitch", "MVP",
        "business model", "market", "product", "scale", "raise capital",
        "go-to-market", "growth", "idea", "bootstrapped", "accelerator"
    ]
    return any(k in query.lower() for k in keywords)

# ✅ Build contextual startup prompt
def build_prompt(user_query, selected_industry=None, selected_year=None, selected_country=None):
    # If non-startup query → polite redirection
    if not is_startup_related(user_query):
        return (
            "You are StartupGPT, a specialized assistant. If the user question is not about startups, funding, ideas, "
            "investors, or roadmaps, reply with:\n\n"
            "'I'm StartupGPT – I can only help with startup ideas, funding, roadmaps, and business planning. "
            "Please ask a question related to startups 🚀.'\n\n"
            f"User asked: {user_query}"
        )

    # Context from filters
    context = []
    if selected_industry and selected_industry.lower() in user_query.lower():
        context.append(f"• Industry: {selected_industry}")
    if selected_year:
        context.append(f"• Startup founded around: {selected_year}")
    if selected_country and selected_country.lower() in user_query.lower():
        context.append(f"• Country of interest: {selected_country}")

    startup_instruction = (
        "🧠 You are StartupGPT – a focused assistant that ONLY responds to startup-related queries:\n"
        "- Funding & investors\n"
        "- Startup ideas or MVPs\n"
        "- Roadmaps & go-to-market plans\n"
        "- City or country suggestions for launching\n"
        "- Business models or competitor analysis\n\n"
        "❗ If the question is unclear or too broad, ask a clarifying question before answering.\n"
    )

    full_prompt = "\n".join([
        startup_instruction,
        "\n📌 Context:",
        "\n".join(context) if context else "• (No specific context selected)",
        f"\n🗣️ User's question: {user_query}",
        "\n💡 Answer clearly and briefly. After answering, ask:\n"
        "'Would you like a roadmap, funding suggestions, or help identifying growth cities for this?'"
    ])

    return full_prompt

# 💬 Call OpenRouter API
def ask_ai_assistant(prompt_text):
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are StartupGPT, a specialized startup advisor chatbot. "
                        "You ONLY respond to questions related to startups, funding, roadmaps, business planning, investors, or startup locations. "
                        "If the question is NOT startup-related (e.g., politics, celebrities, news, general knowledge), say: "
                        "'I'm StartupGPT – I can only help with startup ideas, funding, roadmaps, and business planning. "
                        "Please ask a question related to startups 🚀.'"
                    )
                },
                {"role": "user", "content": prompt_text}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {e}"

# 🔁 Test it directly
if __name__ == "__main__":
    question = "How do I raise funding for an EdTech startup in India?"
    prompt = build_prompt(
        question,
        selected_industry="EdTech",
        selected_year=2025,
        selected_country="India"
    )
    print(ask_ai_assistant(prompt))

