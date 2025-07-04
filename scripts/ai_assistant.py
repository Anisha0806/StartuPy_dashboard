from openai import OpenAI
import streamlit as st

# ✅ Instantiate OpenAI client for OpenRouter
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def is_startup_related(query):
    keywords = [
        "startup", "launch", "funding", "investor", "pitch", "MVP",
        "business model", "market", "product", "scale", "raise capital",
        "go-to-market", "growth", "idea", "bootstrapped", "accelerator"
    ]
    return any(k in query.lower() for k in keywords)

def build_prompt(user_query, selected_industry=None, selected_year=None, selected_country=None):
    if not is_startup_related(user_query):
        return (
            "You are StartupGPT, a specialized assistant. If the user question is not about startups, funding, ideas, "
            "investors, or roadmaps, reply with:\n\n"
            "'I'm StartupGPT – I can only help with startup ideas, funding, roadmaps, and business planning. "
            "Please ask a question related to startups 🚀.'\n\n"
            f"User asked: {user_query}"
        )

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

def ask_ai_assistant(prompt_text):
    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct",
            messages=[
                {"role": "system", "content": "You are StartupGPT, a specialized startup advisor."},
                {"role": "user", "content": prompt_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# ▶⃣ Optional direct test (won't run on Streamlit Cloud)
if __name__ == "__main__":
    q = "How to raise seed funding for a tech startup in India?"
    p = build_prompt(q, selected_industry="Tech", selected_year=2024, selected_country="India")
    print(ask_ai_assistant(p))
