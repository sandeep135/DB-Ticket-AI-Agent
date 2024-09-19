
from langchain.tools import  StructuredTool
from langchain.pydantic_v1 import BaseModel,Field
import httpx
from typing import List
import pandas as pd
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
import ast
from app.models import llm

load_dotenv()

class TravelQuery(BaseModel):
    query: str = Field(description="User's natural language travel query")

def parsetravelquery(query: str) -> dict:
    """LLM-based tool to extract travel details from natural language query."""     
    
     
    prompt_travel_parser = f"""
    Extract the following details from the travel query below:
    - From station
    - To station
    - Departure 1: start range of time for departure in  ISO 8601 format (YYYY-MM-DDTHH:MM)
    - Departure 2 : If the user proivde range of time then only extract end  range of time for departure in  ISO 8601 format (YYYY-MM-DDTHH:MM) other put this null.
     
    travel query: "{query}". Return formate dictionary in python
    """
    parsed_result = llm.predict(prompt_travel_parser)
    start = parsed_result.find('{')
    end = parsed_result.rfind('}') + 1

     
    dict_str = parsed_result[start:end]

 
    travel_details_dict = ast.literal_eval(dict_str)
  
    
    return {
        "from_station": travel_details_dict.get("From station", None),
        "to_station": travel_details_dict.get("To station", None),
        "departure1": travel_details_dict.get("Departure 1", None),
        "departure2": travel_details_dict.get("Departure 2", None),
        
    }



class Station(BaseModel):
    stationName: str = Field(description="Name of the station")
    

def findStationId(stationName:str) -> int:
    """Multiply two numbers."""
    url = 'https://v6.db.transport.rest/locations'

# Parameters for the request
    params = {
        'query': stationName,
        'fuzzy': 'true',
        'results': '1',
        'stops': 'true',
        'addresses': 'true',
        'poi': 'true',
        'linesOfStops': 'false',
        'language': 'en'
    }

    # Headers for the request
    headers = {
        'accept': 'application/json'
    }

# Make the GET request
    response = httpx.get(url, headers=headers, params=params)
    data = response.json()
    statioId = data[0]['id'] if isinstance(data, list) else data['id']
    return statioId



class JourneyRequest(BaseModel):
    from_station_id: int = Field(description="Station ID from where the travel begin")
    to_station_id: int = Field(description="Station ID to where the travel stops")
    departure1: str = Field(description="start range of time for departure")
    departure2: str = Field(description="end range of time for departure")
   
 
def findJourneys(from_station_id: int, to_station_id: int, departure1: str, departure2:str):
    url = 'https://v5.db.transport.rest/journeys'
    all_journeys = []
    later_ref = None

    while True:
        # Adjust query parameters to include laterRef if available
        params = {
            'from': from_station_id,
            'to': to_station_id,
            'departure': departure1 if not later_ref else None,
            'laterRef': later_ref if later_ref else None,
            'pretty': 'true',
            'tickets': 'true'  # To include price info
        }

        headers = {'accept': 'application/json'}
        response = httpx.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        print(data)
        journeys = data.get('journeys', [])

        # Collect journeys within the specified time range
        for journey in journeys:
            journey_departure_time = journey['legs'][0]['plannedDeparture']
            if journey_departure_time > departure2:
                print("-------HELLOWORLD-------")
                return all_journeys  # Exit once we've gone past the time range
            all_journeys.append(journey)

        # If there is no laterRef for pagination, stop the loop
        later_ref = data.get('laterRef')
        if not later_ref:
            break

    return all_journeys


class JourneyInfo(BaseModel):
    journeys: List[dict]

def extractJourneyInfo(journeys: List[dict]):
    journey_data = []

    for journey in journeys:
        # Extract necessary fields such as departure, arrival, and price
        departure_time = journey['legs'][0]['plannedDeparture']
        arrival_time = journey['legs'][0]['plannedArrival']
        price = journey['price']['amount']
        journey_data.append({
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'price': price
        })

    # Create DataFrame
    df = pd.DataFrame(journey_data)
    print(df.head)

    # Find the cheapest journey
    cheapest_journey = df.loc[df['price'].idxmin()]

    return cheapest_journey


journeyTool = StructuredTool.from_function(
    func=findJourneys,
    name="Journeyfinder",
    description="Find journey information between two station",
    args_schema=JourneyRequest,
    return_direct=True
)

extractTool = StructuredTool.from_function(
    func=extractJourneyInfo,
    name="JourneyExtractor",
    description="Extract relevant journey details like departure, arrival, and price and provide the cheapest option to user",
    args_schema=JourneyInfo,
    return_direct=True
)

travelQueryTool = StructuredTool.from_function(
    func=parsetravelquery,
    name="TravelQuerParser",
    description="Extract structured travel details from a natural language query",
    args_schema=TravelQuery,
    
    return_direct=True
)


stationIDTool = StructuredTool.from_function(
    func=findStationId,
    name="StationIDfinder",
    description="find integer stationId based on the station name",
    args_schema=Station,
    return_direct=True,
     
)

tools = [
     travelQueryTool,stationIDTool,journeyTool,extractTool
]
