import streamlit as st
import pandas as pd
import opennem_extract as oe
import altair as alt
from datetime import date as dt

###############################################################################

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
        time_option = str(dt.today().year)
    elif time_option == 'Last 7 Days':
        time_option = '7d'
    elif time_option == '30 Day Average':
        time_option = '30d'
        avg = True

with col2a:
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

data = oe.get_data(time_option, area_option)

with col3a:
    if time_option != '7d' and time_option != '30d':
        data_option = st.selectbox('Data Type:', ('Energy', 'Emissions', 
                      'Market Value'), index = 0)
    else:
        data_option = st.selectbox('Data Type:', (['Power']), index = 0)
    
    if data_option == 'Energy' or data_option == 'Power':
        data_option = 'energy'
    elif data_option == 'Emissions':
        data_option = 'emissions'
    elif data_option == 'Market Value':
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
    

if time_option == '30d' or time_option == '7d':
    x_format = 'hoursminutes(Date):O'
    frame.drop(0,inplace=True)
    
    frame = frame[frame.index % 49 != 0]
else:
    x_format = 'Date:T'


chart = alt.Chart(frame).mark_area().encode(
    x=x_format,
    y=frame.columns.values[1]+':Q',
    color=alt.Color('Source:N', scale=alt. 
                    Scale(domain=frame_cols, range=frame_colours)) 
)

st.altair_chart(chart.interactive(), theme="streamlit", use_container_width=True)


