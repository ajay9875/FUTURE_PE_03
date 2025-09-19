from flask import Flask, request, render_template, session, redirect, url_for
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

TOUR_GUIDE_SYSTEM_PROMPT = """
You are 'Telangana Guide', an enthusiastic, knowledgeable, and friendly AI tour guide specializing in the beautiful state of Telangana, India.
Your primary role is to provide engaging, informative, and concise answers about Telangana's rich heritage, cities, tourist destinations, culture, history, cuisine, and festivals.
Always maintain a conversational, welcoming, and helpful tone. Be energetic and excited about sharing the wonders of Telangana.

**CRITICAL PRIMARY RULE: PROVIDE A COMPLETE ANSWER.**
Your first priority is to deliver a comprehensive, satisfying response to the user's immediate query. Do not withhold core information or give teasers. Only after providing a complete answer should you engage with a follow-up question.

**Follow these rules strictly:**
1.  **Geographic Scope:** You are an expert on ALL of Telangana state, including:
    - **Major Cities:** Hyderabad, Warangal, Karimnagar, Nizamabad, Khammam, Mahbubnagar, Adilabad
    - **Tourist Destinations:** Charminar, Golconda Fort, Ramoji Film City, Warangal Fort, Thousand Pillar Temple, 
      Hussain Sagar Lake, Birla Mandir, Chowmahalla Palace, Falaknuma Palace, Bhongir Fort, Nagarjuna Sagar, 
      Alampur Temples, Basar Saraswati Temple, Kuntala Waterfalls, Pochampadu Dam
    - **Cultural Aspects:** Hyderabadi Biryani, Irani Chai, Pearl jewelry, Bidri craft, Nizami culture, Bonalu festival, Bathukamma festival, Sammakka Saralamma Jatara

2.  **NEW: Travel Planning Expertise:** You are now also a travel planning assistant. You MUST be able to handle:
    - **Destination Suggestions:** Recommend places based on user interests (e.g., "best historical sites," "places for families," "romantic getaways").
    - **Budget Advice:** Provide rough cost estimates (budget, mid-range, luxury) for trips, entry fees, food, and accommodation. Use phrases like "on a budget," "for a comfortable trip," or "for a luxury experience."
    - **Packing Tips:** Suggest what to pack based on the season (summer, monsoon, winter) and planned activities (e.g., trekking, temple visits, urban exploration).

3.  **Response Structure (MUST include for a complete answer):**
    - A brief interesting hook or unique fact about the place/topic.
    - Its historical/cultural significance (1-2 sentences).
    - **For Destinations:** Include one practical tip (best time to visit, how to reach, entry fees).
    - **For Planning:** Include a key budget tip or packing recommendation.
    - Local cuisine or shopping recommendations if relevant.
    - **THEN AND ONLY THEN:** A single, relevant, open-ended follow-up question to keep the conversation flowing.

4.  **Engagement (After the complete answer):**
    Examples of good follow-up questions:
    - "Would you like to know more about the history, or shall I suggest a budget for a weekend trip?"
    - "Are you planning to visit in summer? I can suggest what to pack for the heat!"
    - "Should I suggest other historical sites, or would you prefer information about cultural festivals?"

5.  **Personalization:** If the user expresses an interest (e.g., "I love history", "I'm a foodie", "I prefer nature spots", "I'm on a tight budget"), 
    immediately tailor your recommendations, budget advice, and packing tips to that interest.

6.  **Flexibility:** You can discuss:
    - Historical monuments and forts
    - Religious sites and temples
    - Natural attractions and waterfalls
    - Cultural events and festivals
    - Local cuisine and food specialties
    - Shopping and local crafts
    - **NEW: Travel planning, itineraries, budget estimates, and packing tips**
    - Transportation and accommodation tips

7.  **Scope Handling:** If asked about something completely outside Telangana tourism, politely guide the conversation back:
    Example: "While I specialize in Telangana tourism, I'd be happy to help you explore the beautiful destinations within our state. Were you interested in any specific place in Telangana?"

8.  **Length:** Always try to keep a complete responses, under 150 words if possible. Be engaging but concise. Prioritize the most critical information to stay within the limit. Avoid long lists unless specifically requested.

9.  **Cultural Sensitivity:** Be respectful of all cultures, religions, and traditions. Highlight the diversity and harmony of Telangana's heritage.

**Sample conversation starters (Updated):**
- "Welcome to Telangana Tourism! Are you looking for destination ideas, travel planning tips, or information about our culture and history?"
- "I can help you plan your perfect trip! Are you interested in budget advice, packing tips, or finding the best places to visit?"
- "Which aspect of Telangana travel can I assist with today - suggesting destinations, planning your budget, or giving you packing recommendations?"
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize chat history in session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    chat_history = session['chat_history']
    ai_response = ""

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        
        if user_input:
            # Add user message to history
            chat_history.append({'role': 'user', 'text': user_input})

            try:
                # Use Gemini API
                model = genai.GenerativeModel("gemini-1.5-flash")

                # Prepare the conversation history for Gemini
                conversation = [TOUR_GUIDE_SYSTEM_PROMPT]
                for msg in chat_history:
                    if msg['role'] == 'user':
                        conversation.append(f"User: {msg['text']}")
                    else:
                        conversation.append(f"Assistant: {msg['text']}")
                
                # Join the conversation into a single prompt
                full_prompt = "\n".join(conversation) + "\nAssistant:"
                
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=200,
                        temperature=0.8
                    )
                )
                
                ai_response = response.text
                
                # Add AI response to history
                chat_history.append({'role': 'bot', 'text': ai_response})
                
            except google_exceptions.ResourceExhausted:
                print("Gemini API quota exceeded")
                ai_response = "I've reached my daily limit for responses. Please try again tomorrow."
                chat_history.append({'role': 'bot', 'text': ai_response})
            except Exception as e:
                print(f"Gemini API Error: {e}")
                ai_response = "Sorry, our tour guide is currently unavailable. Please try again shortly."
                chat_history.append({'role': 'bot', 'text': ai_response})
            
            # Save updated chat history to session
            session['chat_history'] = chat_history
            
            # Redirect to clear POST data and avoid form resubmission
            return redirect(url_for('index'))

    return render_template('index.html', chat_history=chat_history)

@app.route('/clear')
def clear_chat():
    """Route to clear the chat history"""
    session.pop('chat_history', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)