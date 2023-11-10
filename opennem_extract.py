import requests
import json
from datetime import datetime as dt
import pandas as pd
import streamlit as st
import numpy as np
###############################################################################

"""
Function to get specific json file from OpenNEM

Inputs:
    period: 
        '20XX': given year (2006 onwards)
        '7d': previous 7 days
        'all': all available

    location:
        'AU': Australia
        'NEM': National Energy Market
        'NSW': New South Wales
        'VIC': Victoria
        'QLD': Queensland
        'TAS': Tasmania
        'SA': South Australia
        'WA': Western Australia (Wholesale Energy Market)

returns:
    Dict containing data in specified timeframe and location
"""
@st.cache_data(ttl=3600)
def get_data(period, location):
    if period == '7d' or period == '30d':
        part2 = 'power/' + period
    else:
        part2 = 'energy/'+ period
        
    if (location == 'AU' or location == 'NEM'): 
        part1 = location
    elif (location == 'NSW' or location == 'VIC' or location == 'TAS' or 
          location == 'SA' or location =='QLD'):
        part1 = 'NEM/' + location + '1'
    elif location == 'WA':
        part1 = 'WEM'
        
    # data source
    link = 'https://data.opennem.org.au/v3/stats/au/'+ part1 + '/' + part2 + '.json'
    
    # Request data from link as 'str'
    data = requests.get(link).text

    # convert 'str' to Json
    data = json.loads(data)['data']
    
    return data

"""
Function which formats desired data as arrays

Inputs:
    source: dict from get_data which contains desired data

    data_type: type of data to return
        'energy': Energy Generation / Consumption 
        'market_value': Cost in AUD/MWh
        'emissions': Emissions of power source in tCO2e
        
    fuel: fuel source to return data for
        Renewable:
            'solar_rooftop'
            'solar_utility'
            'wind'
            'hydro'
            'battery_discharging'
            'bioenergy_biogas'
            'bioenergy_biomass'
        
        Non-Renewable:
            'coal_black'
            'coal_brown'
            'distillate'
            'gas_ccgt'
            'gas_ocgt'
            'gas_recip'
            'gas_steam'
            'gas_wcmg'
            
        Loads:
            'pumps'
            'battery_charging'
        
        
Returns:
    time_list: Array of datetime values for data
    value_list: Array of values for specified data
    units: Units of values
"""

def format_data(source, data_type, fuel, avg):
    found = False
    for i in range(0,len(source)):
        
        if (source[i]['type'] == data_type) or (source[i]['type'] == 'power' 
        and data_type == 'energy'):
            
            if (source[i]['code'] == fuel):
                units = source[i]['units']
                location = source[i]['history']
                found = True
    
    if found == True:
        value_list = location['data']
        
        time_list = create_times(location, avg)
        
        return [time_list, value_list, units]
    
    else: return [[], [], []]


"""        
Function to create datetime array for data

Inputs:
    source: dict which contains 'start', 'last' and 'interval' data
    
Returns:
    time_range: Array of time values for every interval between start and end
    
"""

def create_times(source, avg):
    if avg == True:
       time_format = "%Y-%m-%dT%X+10:00"
       start_time = dt.strptime('1900-01-01T14:00:00+10:00', time_format)
       end_time = dt.strptime('1900-01-02T14:00:00+10:00', time_format)
        
    else:
        time_format = "%Y-%m-%dT%X%z"
        start_time = dt.strptime(source['start'], time_format)
        end_time = dt.strptime(source['last'], time_format)
    
    if source['interval'] == '1M':
        frequency = 'MS'
        
    elif source['interval'] == '1d':
        frequency = 'D'
    
    else:
        frequency = source['interval'] + 'in'
    
    time_range = (pd.date_range(start=start_time,end=end_time, freq = frequency).to_pydatetime().tolist())
    
    return time_range

#Handles the addition of data to the dataframe from toggles
def add_data (name, button, frame, frame_cols, frame_colours, data, data_option, avg):
    
    base_cols = ['Solar (Rooftop)',
     'Solar (Utility)',
     'Wind',
     'Hydro',
     'Pumps',
     'Battery (Discharging)',
     'Battery (Charging)',
     'Bioenergy (Biogas)',
     'Bioenergy (Biomass)',
     'Coal (Black)',
     'Coal (Brown)',
     'Distillate',
     'Gas (CCGT)',
     'Gas (OCGT)',
     'Gas (Reciprocating)',
     'Gas (Steam)',
     'Gas (Waste Coal Mine)']
    
    base_colours = ['#faf298',
     '#ffef3b',
     '#45ba41',
     '#8af3ff',
     '#4d868c',
     '#a78fff',
     '#695a9e',
     '#ec70ff',
     '#a708bf',
     '#000000',
     '#3d2f18',
     '#d4353f',
     '#ff9021',
     '#e87400',
     '#ffa74f',
     '#ffc285',
     '#826534']
    
    base_name  = ['solar_rooftop',
    'solar_utility',
    'wind',
    'hydro',
    'pumps',
    'battery_discharging',
    'battery_charging',
    'bioenergy_biogas',
    'bioenergy_biomass',
    'coal_black',
    'coal_brown',
    'distillate',
    'gas_ccgt',
    'gas_ocgt',
    'gas_recip',
    'gas_steam',
    'gas_wcmg']
    
    if button:
        
        [new_times, array_power, units] = format_data(data, data_option, name, avg)
        
        if data_option == 'market_value' and array_power != None:
            divisor = np.array(format_data(data, 'energy', name, avg)[1])
        
            for i in range(len(divisor)):
                if divisor[i] == 0 or divisor[i] == None:
                    divisor[i] = 1
            
            
            divisor *= 10**6
            
            #if type(array_power) == list or type(array_power) == np.ndarray:
               # array_power = (np.divide(array_power,divisor))
                
                
        idx = base_name.index(name)
        curr_name = base_cols[idx]
        
        
        
        if len(array_power) != 0:
            new_frame = pd.DataFrame(zip(new_times, array_power),columns=['Date',
                        frame.columns.values[1]])
            if name == 'battery_charging' or name == 'pumps':
                new_frame[frame.columns.values[1]] = new_frame[frame.columns.values[1]]*-1
            new_frame.insert(2, 'Source', curr_name)
            frame = pd.concat([frame, new_frame], 
                            ignore_index=True)  
            
        frame_cols.append(curr_name)
        frame_colours.append(base_colours[idx])
    
    return frame
###############################################################################
