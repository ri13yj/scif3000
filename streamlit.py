import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime as dt
from datetime import date as dt2
from datetime import timedelta
import requests
import json
import opennem_extract as oe
###############################################################################
st. set_page_config(layout="wide")

col1z, col2z = st.columns([1.5, 1])
with col1z:
    view = st.selectbox(
        label = "",
        options = ('Detailed',
         'Simplified'))

with col2z:
    col1a, col2a, col3a = st.columns(3)

    with col1a:
        time_option = st.selectbox(
            'Time Period:',
            ('All',
             'YTD',
             'Last 7 Days',
             '30 Day Average'))
        
        avg = False
        if time_option == 'All':
            time_option = 'all'
        elif time_option == 'YTD':
            time_option = str(dt2.today().year)
        elif time_option == 'Last 7 Days':
            time_option = '7d'
        elif time_option == '30 Day Average':
            time_option = '30d'
            avg = True
    
    with col2a:
        if time_option != '30d':
            area_option = st.selectbox(
                'State:',
                ( 'AU',
                 'NEM',
                 'NSW',
                 'VIC',
                 'QLD',
                 'TAS',
                 'SA',
                 'WA'))
        else:
            area_option = st.selectbox(
                'State:',
                (
                 'NEM',
                 'NSW',
                 'VIC',
                 'QLD',
                 'TAS',
                 'SA'))

    
    data = oe.get_data(time_option, area_option)
    
    with col3a:
        if time_option != '7d' and time_option != '30d':
            if view == 'Detailed':
                data_option = st.selectbox('Data Type:', ('Energy', 'Emissions', 
                              'Market Price'), index = 0)
            else:
                data_option = st.selectbox('Data Type:', (['Energy']), index = 0)
        else:
            data_option = st.selectbox('Data Type:', (['Power']), index = 0)
        
        if data_option == 'Energy' or data_option == 'Power':
            data_option = 'energy'
        elif data_option == 'Emissions':
            data_option = 'emissions'
        elif data_option == 'Market Price':
            data_option = 'market_value'
            
    if data_option == 'energy':
        if time_option != '7d' and time_option != '30d':
            col_name = 'Energy (GWh)'
        else:
            col_name = 'Power (MW)'
    elif data_option == 'emissions':
        col_name = 'Emissions (tCO2e)'
    else:
        col_name = 'Market Value (AUD)'
    
    
    frame = pd.DataFrame(columns = ['Date',col_name,'Source'])
    frame_cols = []
    frame_colours= []
    
    col1b, col2b, col3b = st.columns(3)
    
    with col1b:
        renew_on = st.toggle('Renewables', value = True)
        st.subheader('',divider='grey')
        
        solar_rooftop_on = st.toggle('Solar (Rooftop)', value = renew_on)
        frame = oe.add_data('solar_rooftop', solar_rooftop_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
    
        solar_utility_on = st.toggle('Solar (Utility)', value = renew_on)
        frame = oe.add_data('solar_utility', solar_utility_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
    
        wind_on = st.toggle('Wind', value = renew_on)
        frame = oe.add_data('wind', wind_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        hydro_on = st.toggle('Hydro', value = renew_on)
        frame = oe.add_data('hydro', hydro_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        battery_discharging_on = st.toggle('Battery (Discharging)', value = renew_on)
        frame = oe.add_data('battery_discharging', battery_discharging_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        bioenergy_biogas_on = st.toggle('Bioenergy (Biogas)', value = renew_on)
        frame = oe.add_data('bioenergy_biogas', bioenergy_biogas_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        bioenergy_biomass_on = st.toggle('Bioenergy (Biomass)', value = renew_on)
        frame = oe.add_data('bioenergy_biomass', bioenergy_biomass_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
    
    with col2b:
        non_on = st.toggle('Nonrenewables', value = True)
        
        st.subheader('',divider='grey')
        
        coal_black_on = st.toggle('Coal (Black)', value = non_on)
        frame = oe.add_data('coal_black', coal_black_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        coal_brown_on = st.toggle('Coal (Brown)', value = non_on)
        frame = oe.add_data('coal_brown', coal_brown_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        distillate_on = st.toggle('Distillate', value = non_on)
        frame = oe.add_data('distillate', distillate_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        gas_ccgt_on = st.toggle('Gas (CCGT)', value = non_on)
        frame = oe.add_data('gas_ccgt', gas_ccgt_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
                
        gas_ocgt_on = st.toggle('Gas (OCGT)', value = non_on)
        frame = oe.add_data('gas_ocgt', gas_ocgt_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
                
        gas_recip_on = st.toggle('Gas (Reciprocating)', value = non_on)
        frame = oe.add_data('gas_recip', gas_recip_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        gas_steam_on = st.toggle('Gas (Steam)', value = non_on)
        frame = oe.add_data('gas_steam', gas_steam_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
    
        gas_wcmg_on = st.toggle('Gas (Waste Coal Mine)', value = non_on)
        frame = oe.add_data('gas_wcmg', gas_wcmg_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
    
    with col3b:
        loads_on = st.toggle('Loads', value = True)
        st.subheader('',divider='grey')
        
        pumps_on = st.toggle('Pumps', value = loads_on)
        frame = oe.add_data('pumps', pumps_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
        
        battery_charging_on = st.toggle('Battery (Charging)', value = loads_on)
        frame = oe.add_data('battery_charging', battery_charging_on, frame, frame_cols, 
                    frame_colours, data, data_option, avg)
   
x_format = 'Date:T'
    

if time_option == '30d':
    frame['Date'] = frame['Date'] - timedelta(hours=4) 
    x_format = 'hoursminutes(Date):O'
    
    final_idx = len(frame) -1
    
    skip = True
    for i in range(final_idx):
        if frame['Date'][i].minute != 30:
            if frame['Date'][i].minute != 0:
                frame = frame.drop(i)
            else:
                if frame['Date'][i].hour == frame['Date'][0].hour and skip == True:
                   skip = False
                elif frame['Date'][i].hour == frame['Date'][0].hour and skip == False:
                    frame = frame.drop(i)
                    skip = True
   try:
        frame = frame.drop(final_idx)
    except:
        None
else:
    x_format = 'Date:T'

with col1z:
    
    if view == 'Simplified':
        
        renewables_list = ['Solar (Rooftop)',
         'Solar (Utility)',
         'Wind',
         'Hydro',
         'Battery (Discharging)',
         'Bioenergy (Biogas)',
         'Bioenergy (Biomass)',
         ]
        
        non_list = ['Coal (Black)',
         'Coal (Brown)',
         'Distillate',
         'Gas (CCGT)',
         'Gas (OCGT)',
         'Gas (Reciprocating)',
         'Gas (Steam)',
         'Gas (Waste Coal Mine)']
        
        load_list = [
         'Pumps',
         'Battery (Charging)',
        ]
        
        if time_option == 'all':
            period = 'MS'
        elif time_option == '7d':
            period = '30min'
        elif time_option == '30d':
            period = '30min'
        else:
            period = 'D'
        
        renew_on = (solar_rooftop_on or solar_utility_on or wind_on or hydro_on
                    or battery_discharging_on or bioenergy_biogas_on or
                    bioenergy_biomass_on)
        
        if renew_on:
            frame = frame.replace(renewables_list, 'Renewables')
            
            frame_renew = frame[frame['Source'] == 'Renewables']
            
            frame_renew = frame_renew.resample(period, on='Date').sum()
            
            frame_renew = frame_renew.assign(Source='Renewables')

        
        non_on = (coal_black_on or coal_brown_on or gas_ccgt_on or gas_ocgt_on
                  or gas_recip_on or gas_steam_on or gas_wcmg_on or distillate_on)
        
        if non_on:
            frame = frame.replace(non_list, 'Non-Renewables')
            
            frame_non = frame[frame['Source'] == 'Non-Renewables']
            
            frame_non = frame_non.resample(period, on='Date').sum()
            
            frame_non = frame_non.assign(Source='Non-Renewables')
        
        
        loads_on = pumps_on or battery_charging_on
        if loads_on:
            frame = frame.replace(load_list, 'Loads')
            
            frame_loads = frame[frame['Source'] == 'Loads']
            
            frame_loads = frame_loads.resample(period, on='Date').sum()
            
            frame_loads = frame_loads.assign(Source='Loads')
        
        
        if loads_on and non_on and renew_on:
            frame = pd.concat([pd.concat([frame_renew, frame_non]), frame_loads])
        
        elif loads_on == False and non_on and renew_on:
            frame = pd.concat([frame_renew, frame_non])
        
        elif loads_on == False and non_on == False and renew_on:
            frame = frame_renew
        
        elif loads_on and non_on and renew_on == False:
            frame = pd.concat([frame_loads, frame_non])
        
        elif loads_on and non_on == False and renew_on:
            frame = pd.concat([frame_loads, frame_renew])
            
        elif loads_on and non_on == False and renew_on == False:
            frame = frame_loads
            
        elif loads_on == False and non_on and renew_on == False:
            frame = frame_non
    
        else:
            frame = pd.DataFrame(columns = ['Date',col_name,'Source'])
            
            
        frame = frame.reset_index()
        
        frame_cols = ['Renewables', 'Non-Renewables', 'Loads']
        
        frame_colours = ['green', 'red', 'blue']
        

    chart = alt.Chart(frame).mark_area().encode(
        x=x_format,
        y=frame.columns.values[1]+':Q',
        color=alt.Color('Source:N', scale=alt. 
                        Scale(domain=frame_cols, range=frame_colours)) 
    )

    st.altair_chart(chart.interactive(), theme="streamlit", use_container_width=True)
