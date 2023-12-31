import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

files = ['chefmozaccepts',
         'chefmozcuisine',
         'chefmozhours4',
         'chefmozparking',
         'usercuisine',
         'userpayment',
         'userprofile',
         'rating_final',
         'geoplaces2']
dfs = dict()

# str1 = "C:\\Users\\LakuJayanth\\Documents\\UNCC\\DSBA_5122\\Streamlit\Data\\Resturants_streamlit\\Restaurants_around_mexico\\Data\\"
# for file in files:
#     fl= str1+file+'.csv'
#     dfs[file] = pd.read_csv(fl,encoding='ISO-8859-1')

# str1 = r'C:\Users\LakuJayanth\Documents\UNCC\DSBA_5122\Streamlit\Data\inclass_1204\Restaurant_Mexico' + '\\'

for file in files:
    fl= "Data/"+file+'.csv'
    dfs[file] = pd.read_csv(fl,encoding='ISO-8859-1')
    
st.title("Restaurants around Mexico")
st.write("Restaurants around Mexico")

alt.data_transformers.disable_max_rows()
    
# #cleaning up the resturant hourly file
# #Trim white spaces
dfs['chefmozhours4']['hours'] = dfs['chefmozhours4']['hours'].str.strip()
dfs['chefmozhours4']['days'] = dfs['chefmozhours4']['days'].str.strip()


h1 = dfs['chefmozhours4']['hours'].str.split('-',expand = True)
h1[0] = h1[0].astype('datetime64[ns]')
h1[0] = pd.to_datetime(h1[0], format='%d/%m/%y %H:%M')
h2= h1[1].str.split(';',expand = True)
h1[1]= h2[0].astype('datetime64[ns]')
h1[1] = pd.to_datetime(h1[1], format='%d/%m/%y %H:%M')
h1['openhr'] = h1[0].dt.hour
h1['openmin'] = h1[0].dt.minute
h1['clshr'] = h1[1].dt.hour
h1['clsmin'] = h1[1].dt.minute

dfs['chefmozhours4']['opentime'] =h1[0].dt.time
dfs['chefmozhours4']['openhr'] = h1['openhr']
dfs['chefmozhours4']['openmin'] = h1['openmin']
dfs['chefmozhours4']['clstime'] =h1[1].dt.time
dfs['chefmozhours4']['clshr'] = h1['clshr']
dfs['chefmozhours4']['clsmin'] = h1['clsmin']

#converting days of operation into corresponding column

d1 =dfs['chefmozhours4']['days'].str.split(';',expand = True)
d1.drop([5],axis=1,inplace=True)
d1['Mon'] = d1[0] .apply(lambda x: (x=='Mon')==True )
d1['Tue'] = d1[1] .apply(lambda x: (x=='Tue')==True )
d1['Wed'] = d1[2] .apply(lambda x: (x=='Wed')==True )
d1['Thu'] = d1[3] .apply(lambda x: (x=='Thu')==True )
d1['Fri'] = d1[4] .apply(lambda x: (x=='Fri')==True )
d1['Sat'] = d1[0] .apply(lambda x: (x=='Sat')==True )
d1['Sun'] = d1[0] .apply(lambda x: (x=='Sun')==True )
d1.replace({False: 0, True: 1}, inplace=True)
d1['days_of_operation'] = d1['Mon']+d1['Tue']+d1['Wed']+d1['Thu']+d1['Fri']+d1['Sat']+d1['Sun']

dfs['chefmozhours4']['Mon'] = d1['Mon']
dfs['chefmozhours4']['Tue'] = d1['Tue']
dfs['chefmozhours4']['Wed'] = d1['Wed']
dfs['chefmozhours4']['Thu'] = d1['Thu']
dfs['chefmozhours4']['Fri'] = d1['Fri']
dfs['chefmozhours4']['Sat'] = d1['Sat']
dfs['chefmozhours4']['Sun'] = d1['Sun']
dfs['chefmozhours4']['days_of_operation'] =  d1['days_of_operation']


#drop res_df if exists

# for col in res_df:
#     res_df.drop(col,axis=1,inplace=True)
    
#Merge the files to get the rating file
res_df = dfs['chefmozaccepts'].merge(dfs['chefmozcuisine'],on ='placeID' )
res_df = res_df.merge(dfs['chefmozhours4'],on ='placeID' )
res_df = res_df.merge(dfs['chefmozparking'],on ='placeID' )
res_df = res_df.merge(dfs['geoplaces2'],on ='placeID' )
res_rating = res_df.merge(dfs['rating_final'],on ='placeID' )
usr_df = dfs['usercuisine'].merge(dfs['userpayment'],on ='userID' )
usr_df = usr_df.merge(dfs['userprofile'],on ='userID' )
usr_rating = usr_df.merge(dfs['rating_final'],on ='userID' )

s1=["SLP","S.L.P.","s.l.p.","San Luis Potosi","slp","san luis potos","san luis potosi"]
s2 =["tamaulipas","Tamaulipas"]
s3=["morelos","Morelos"]
s4=["?","mexico"]
res_rating['state'] =  res_rating['state'].apply(lambda x: "San Luis Potosi" if x in s1 else x)
res_rating['state'] =  res_rating['state'].apply(lambda x: "Tamaulipas" if x in s2 else x)
res_rating['state'] =  res_rating['state'].apply(lambda x: "Morelos" if x in s3 else x)
res_rating['state'] =  res_rating['state'].apply(lambda x: "Not Determined" if x in s4 else x)

# creating Ranking dataframe for rating chart
filt_cols = ['placeID','name' ,'rating','food_rating','service_rating','state']
ranking = pd.DataFrame(res_rating,columns=filt_cols)
ranking['Avg_Rating'] = ranking[['rating','food_rating','service_rating']].mean(axis=1)
ranking = ranking[ranking['state'] != 'Not Determined' ]

st.write(res_rating)
bars = alt.Chart(ranking).mark_bar().encode(
    x=alt.X('mean(Avg_Rating):Q'),
    y=alt.Y('name:N',sort='x'),
    color=alt.Color('state')
    # order = alt.Order(# Sort the segments of the bars by this field
    #   'Avg_Rating',
    #   sort='descending')
)
text = alt.Chart(ranking).mark_text(dx=-15, dy=3, color='white').encode(
    x=alt.X('mean(Avg_Rating):Q', stack='zero'),
    y=alt.Y('name:N'),
    detail='state:N',
    text=alt.Text('mean(Avg_Rating):Q', format='.1f')
)

bars + text

#Top 10 rank chart
g= ranking.groupby('name', as_index=False)['rating'].mean().sort_values(by='rating', ascending=False).head(10)

bar_chart = alt.Chart(g).mark_bar().transform_filter(
            alt.FieldGTEPredicate(field='rating', gte= 1)
            ).encode(
        y=alt.Y('name',sort=alt.EncodingSortField('rating', op='min', order='descending')),
        x='rating'
    )


bar_text = bar_chart.mark_text(
    align='left',
    baseline='middle',
    dx=3
).encode(
    text=alt.Text('rating:Q', format='.1f')
)


bar_chart + bar_text

res_rat_filter  = res_rating[res_rating['rating'] > 0]
st.map(res_rat_filter)
