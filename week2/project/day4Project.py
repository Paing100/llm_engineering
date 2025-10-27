import gradio as gr
import sys
from geopy.geocoders import Nominatim
import requests 
from collections import defaultdict
import os
import json 
from dotenv import load_dotenv
from api_clients import create_clients

load_dotenv(dotenv_path="C:/Users/paing/LLMProjects/llm_engineering/api_key.env",override=True)
OWM_API = os.getenv('OWM_API')
if not OWM_API:
    raise ValueError("OWM_API is not set in environment variables!")

clients = create_clients()

flights = [
    {"id": 1, "from_city": "london", "to_city": "paris", "price": 250},
    {"id": 2, "from_city": "london", "to_city": "rome", "price": 300},
    {"id": 3, "from_city": "london", "to_city": "berlin", "price": 200},
    {"id": 4, "from_city": "london", "to_city": "tokyo", "price": 850},
    {"id": 5, "from_city": "london", "to_city": "new york", "price": 700},
    {"id": 6, "from_city": "paris", "to_city": "rome", "price": 180},
    {"id": 7, "from_city": "paris", "to_city": "berlin", "price": 160},
    {"id": 8, "from_city": "berlin", "to_city": "rome", "price": 190},
    {"id": 9, "from_city": "tokyo", "to_city": "seoul", "price": 220},
    {"id": 10, "from_city": "new york", "to_city": "london", "price": 680},
    {"id": 11, "from_city": "rome", "to_city": "paris", "price": 180},
    {"id": 12, "from_city": "berlin", "to_city": "paris", "price": 160},
    {"id": 13, "from_city": "new york", "to_city": "tokyo", "price": 900},
    {"id": 14, "from_city": "paris", "to_city": "tokyo", "price": 870},
    {"id": 15, "from_city": "rome", "to_city": "berlin", "price": 190}
]

activities = [
    {"id": 1, "city": "paris", "activity_name": "Eiffel Tower Tour", "price": 50},
    {"id": 2, "city": "paris", "activity_name": "Louvre Museum", "price": 40},
    {"id": 3, "city": "paris", "activity_name": "Seine River Cruise", "price": 45},
    {"id": 4, "city": "rome", "activity_name": "Colosseum Visit", "price": 45},
    {"id": 5, "city": "rome", "activity_name": "Vatican Museums", "price": 60},
    {"id": 6, "city": "rome", "activity_name": "Pasta-Making Class", "price": 70},
    {"id": 7, "city": "berlin", "activity_name": "Brandenburg Gate Walk", "price": 0},
    {"id": 8, "city": "berlin", "activity_name": "Pergamon Museum", "price": 25},
    {"id": 9, "city": "tokyo", "activity_name": "Sushi Workshop", "price": 80},
    {"id": 10, "city": "tokyo", "activity_name": "Mount Fuji Day Trip", "price": 120},
    {"id": 11, "city": "new york", "activity_name": "Statue of Liberty Ferry", "price": 35},
    {"id": 12, "city": "new york", "activity_name": "Central Park Bike Tour", "price": 30},
    {"id": 13, "city": "seoul", "activity_name": "Gyeongbokgung Palace Tour", "price": 40},
    {"id": 14, "city": "seoul", "activity_name": "Street Food Night Market", "price": 25},
    {"id": 15, "city": "rome", "activity_name": "Trevi Fountain Visit", "price": 0},
    {"id": 16, "city": "paris", "activity_name": "Montmartre Walking Tour", "price": 20},
    {"id": 17, "city": "tokyo", "activity_name": "Akihabara Tour", "price": 15},
    {"id": 18, "city": "berlin", "activity_name": "Berlin Wall Visit", "price": 10},
    {"id": 19, "city": "new york", "activity_name": "Broadway Show", "price": 120},
    {"id": 20, "city": "seoul", "activity_name": "Han River Cruise", "price": 30}
]

system_message = f"""
You are a helpful assistant for planning travel itineraries.
You have access to functions for flights, weather, and activities.

Given the following flight data: {flights}
Given the following activities data: {activities}

Rules:
- Before calling a function, make sure you have all required parameters.
- If any parameter (like starting city, destination city, days, or budget) is missing, politely ask the user for it.
- Keep responses short and courteous (1 sentence max).
- Always be accurate; if you don’t know something, say so.
"""

def parse_budget(budget):
    if isinstance(budget, (int, float)):
        return int(budget)
    if isinstance(budget, str):
        return int(budget.split()[0])
    return 0

def get_flight_price(starting_city, destination_city, budget): 
  budget = parse_budget(budget)
  if not starting_city or not destination_city:
    return "Missing starting or destination city."
  print(f"Getting flight ticket prices from {starting_city} to {destination_city} within {budget} USD")
  for flight in flights:
    if flight.get("from_city") == starting_city.lower() and flight.get("to_city") == destination_city.lower() and flight.get("price") <= budget:
      price = flight.get("price")
      return f"The price of a ticket from {starting_city} to {destination_city} is {price}."
  return f"No flights found from {starting_city} to {destination_city} within {budget} USD."

def convert_city_to_coordinates(city):
  geolocator = Nominatim(user_agent="travel_ai")
  location = geolocator.geocode(city)
  if location is None:
    return f"Could not find coordinates for {city}."
  return location.latitude, location.longitude

def get_weather(destination_city):
  if not destination_city:
    return "Missing destination city."
  print(f"Getting the weather details from {destination_city}")
  latitude, longitude = convert_city_to_coordinates(destination_city)
  url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={OWM_API}"
  response = requests.get(url)
  if response.status_code == 200:
    daily_forecasts = defaultdict(list)
    data = response.json()
    for entry in data['list']:
      date = entry['dt_txt'].split(" ")[0]  
      daily_forecasts[date].append(entry)

    summaries = []
    for date, entries in daily_forecasts.items():
      avg_temp = sum(e['main']['temp'] for e in entries) / len(entries)
      main_condition = max(set(e['weather'][0]['description'] for e in entries),
                          key=lambda x: [e['weather'][0]['description'] for e in entries].count(x))
      summaries.append(f"{date}: Avg Temp {avg_temp:.1f}°C, Most common: {main_condition}")
    return '\n'.join(summaries)
  else:
    return(f"Error: {response.status_code}")

def get_itinerary(destination_city, days, budget): 
  print(f"Planning the activities details from {destination_city} within {budget} USD")
  result = []
  budget = parse_budget(budget)
  remaining_budget = budget
  for activity in activities:
    if activity.get("city") == destination_city.lower() and activity.get("price") <= remaining_budget:
      result.append(activity.get("activity_name"))
      remaining_budget -= activity.get("price")

  return f"The activities are {result}."

flight_price_function = {
  "name": "get_flight_price", 
  "description": "Get the price of a return ticket to the destination city.",
  "parameters": {
    "type": "object", 
    "properties": {
      "starting_city": {
        "type": "string", 
        "description": "The starting city where the user wants to fly from."
      },
      "destination_city": {
        "type": "string", 
        "description": "The destination city where the user wants to fly to."
      },
      "budget":  {
        "type": "string", 
        "description": "The amount of money that the user is able to spend."
      }
    }, 
    "required": ["starting_city", "destination_city", "budget"]
  }
}

weather_function = {
  "name": "get_weather", 
  "description": "Get the weather of the destination city.",
  "parameters": {
    "type": "object", 
    "properties": {
      "destination_city": {
        "type": "string", 
        "description": "The destination city where the user wants to fly to."
      }
    }, 
    "required": ["destination_city"]
  }
}

itinerary_function = {
  "name": "get_itinerary", 
  "description": "Plan the activities based on the days and the remaining budget from flight ticket",
  "parameters": {
    "type": "object", 
    "properties": {
      "destination_city": {
        "type": "string", 
        "description": "The destination city where the user wants to fly to."
      },
      "days": {
        "type": "integer", 
        "description": "The number of days that the user will be in the destination city"
      },
      "budget":  {
        "type": "string", 
        "description": "The amount of money that the user is able to spend."
      }
    }, 
    "required": ["destination_city", "days", "budget"]
  }
}

tools = [
  {"type": "function", "function": flight_price_function},
  {"type": "function", "function": weather_function},
  {"type": "function", "function": itinerary_function}
]

def handle_tool_call(message):
  tool_calls = message.tool_calls
  responses = []

  for tool_call in tool_calls:
    func_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    if func_name == "get_flight_price":
      starting_city = arguments.get('starting_city')
      destination_city = arguments.get('destination_city')
      budget = arguments.get('budget')
      responses = get_flight_price(starting_city, destination_city, budget)
      
    elif func_name == "get_weather":
      destination_city = arguments.get('destination_city')
      responses = get_weather(destination_city)
      
    elif func_name == "get_itinerary":
      destination_city = arguments.get('destination_city')
      days = arguments.get('days')
      budget = arguments.get('budget')
      responses = get_itinerary(destination_city, days, budget)

  return {"role": "tool", "content": responses, "name": func_name, "tool_call_id": tool_call.id}

def chat(message, history):
  history = [{"role": h["role"], "content": h["content"]}for h in history]
  messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
  response = clients["groq"].chat.completions.create(
    model=clients["models"]["GROQ_MODEL"], 
    messages=messages,
    tools=tools,
    tool_choice="auto"
  )

  message_obj = response.choices[0].message
  if hasattr(message_obj, "tool_calls") and message_obj.tool_calls:
      tool_response = handle_tool_call(message_obj)
      messages.append(tool_response)
      response = clients["groq"].chat.completions.create(
          model=clients["models"]["GROQ_MODEL"],
          messages=messages
      )
  return response.choices[0].message.content

def main():
  gr.ChatInterface(fn=chat, type="messages").launch()
main()