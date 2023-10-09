from skyfield.api import load, Topos
from skyfield import almanac
from datetime import timedelta
import streamlit as st
import pandas as pd


col1,col2=st.columns([1,4])
a = col2.empty()

# Load astronomical data
ts = load.timescale()
eph = load('de421.bsp')  # Load the ephemeris file
earth = eph['earth']  # Extract earth


lat = col1.slider('Lattitude to one decimel place', max_value=60.0, min_value=20.0, value=30.0, step=0.1)
location= Topos(latitude_degrees=lat, longitude_degrees=-90)
# Geographic location: New Orleans, LA
# new_orleans = Topos(latitude_degrees=29.9511, longitude_degrees=-90.0715)


max_light_box = col1.selectbox('Choose minutes for max lightbox',[5,10,15,20,25,30,35,40,45,50],index=5)
light_box_interval = col1.selectbox('Choose an interval for light box time increase',[1,2,3,4,5],index=4)
# Days in each month for the year 2023 (which is not a leap year)
days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
df = pd.DataFrame()
# Iterate through each day of the year
for month in range(1, 13):
    for day in range(1, days_in_month[month] + 1):  # Use the number of days for each month
        t0 = ts.utc(2023, month, day, -4, 0, 0)  # Start four hours before midnight of the current day
        t1 = ts.utc(2023, month, day, 28, 0, 0)  # End four hours after midnight of the next day

        # t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, new_orleans))
        t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, location))

        # print(t)  # Debugging line to print the times array

        if len(t) >= 2:  # Both sunrise and sunset should occur
            sunrise_time = t[0] if y[0] else t[1]
            sunset_time = t[1] if y[0] else t[0]
            daylight_duration_seconds = (sunset_time.utc_datetime() - sunrise_time.utc_datetime()).seconds
            daylight_duration_minutes = int(daylight_duration_seconds/60)
            # daylight_duration = timedelta(seconds=daylight_duration)
            # st.write(daylight_duration_minutes)
            a.write(f"Calculating daylight for: {month:02d}-{day:02d}")
            df.loc[f"{month:02d}-{day:02d}",'Daylight_minutes']= daylight_duration_minutes
            # st.write(df.loc[f"{month:02d}-{day:02d}",'Daylight'])
        elif len(t) == 1:  # Only one event occurs
            # st.write(f"{month:02d}-{day:02d}: Only one event (either sunrise or sunset)")
            df[f"{month:02d}-{day:02d}",'Daylight_minutes']= None
        else:  # No sunrise or sunset
            # st.write(f"{month:02d}-{day:02d}: No sunrise or sunset")
            df[f"{month:02d}-{day:02d}",'Daylight_minutes']= None
df = df.reset_index(drop=False)
df.columns = ['Date','Daylight_minutes']
df['Date'] = pd.to_datetime('2023-' + df['Date'])
df = df.sort_values('Date')
# a.write(df)
max_daylight =df.Daylight_minutes.max()
min_daylight = df.Daylight_minutes.min()
annual_difference = max_daylight - min_daylight
col2.write(f'The difference between the maximum and minimum of daylight at your latitude is {int(annual_difference)} minutes.')
difference_to_maxbox_ratio = int(annual_difference/max_light_box)
minutes_to_interval_change = difference_to_maxbox_ratio * light_box_interval
df['Delta_from_max']=max_daylight - df.Daylight_minutes
df['Minutes_of_light'] = (light_box_interval*round(df.Delta_from_max/minutes_to_interval_change,0))-light_box_interval
# df = df.drop_duplicates('Minutes_of_light',keep='first')
display_df = df[['Date','Minutes_of_light']]
display_df = display_df.sort_values('Date')
display_df = display_df[display_df.Minutes_of_light>=0]
display_df['Change'] = (display_df['Minutes_of_light'] != display_df['Minutes_of_light'].shift()).astype(int)
display_df = display_df[display_df.Change==1]
display_df=display_df[['Date','Minutes_of_light']]
col2.write(display_df)
