import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout='wide', page_title='Startup Analysis')

@st.cache_data
def load_data():
        return pd.read_csv('dataset\\preprocess_data.csv')
df = load_data()

def load_overall_analysis():
        st.title('Overall Analysis')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
                total = round(df['amount'].sum())
                st.metric('Total', str(total)+' Cr')
        with col2:
                maximum = round(df.groupby('startup')['amount'].sum().max())
                st.metric('Max', str(maximum)+' Cr')
        with col3:
                avg = round(df.groupby('startup')['amount'].sum().mean())
                st.metric('Average', str(avg)+' Cr')
        with col4:
                total_startup = df['startup'].unique().size
                st.metric('Funded Startups', str(total_startup))

        st.header('MoM Graph')
        selected_option = st.selectbox('Select Type', ['Total', 'Count'])
        if selected_option == 'Total':
                temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
        else:
                temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()
        temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
        fig, ax = plt.subplots(figsize=(12,4))
        ax.plot(temp_df['x_axis'], temp_df['amount'])
        plt.xticks(rotation=90)
        plt.xlabel('Month over the Years')
        if selected_option == 'Total':
                plt.ylabel('Amount (in Cr)')
        else:
                plt.ylabel('Number of Investments')
        st.pyplot(fig)

        col1, col2 = st.columns(2)
        with col1:
                st.header('Top Sectors')
                st.text('On Total Amount')
                sectors_df = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head()
                fig1, ax1 = plt.subplots()
                ax1.pie(sectors_df, autopct='%0.1f%%', startangle=90, labels=sectors_df.index)
                st.pyplot(fig1)
        with col2:
                st.header('')
                st.text('On Total Number')
                sectors_df = df.groupby('vertical')['amount'].count().sort_values(ascending=False).head()
                fig2, ax2 = plt.subplots()
                ax2.pie(sectors_df, autopct='%0.1f%%', startangle=90, labels=sectors_df.index, pctdistance=0.8, labeldistance=1.05)
                st.pyplot(fig2)

def load_startup_details(startup):
        st.title(startup)

        col1, col2 = st.columns(2)
        with col1:
                vertical = df[df['startup'] == startup]['vertical'].mode().values[0]
                st.metric('Industry', str(vertical))
        with col2:
                location = df[df['startup'] == startup]['city'].mode().values[0]
                st.metric('Location', str(location))

        st.header('Investments')
        investment_df = df[df['startup'] == startup].groupby('year')['amount'].sum()
        if investment_df.sum() == 0:
                st.text('Not Disclosed')
        else:
                fig, ax = plt.subplots()
                ax.bar(investment_df.index, investment_df.values)
                plt.xlabel('Year')
                plt.ylabel('Amount (in Cr)')
                st.pyplot(fig)

def load_investor_details(investor):
        st.title(investor)

        last5_df = df[df['investors'].str.contains(investor, case=False, na=False)].sort_values('date', ascending=True).head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']].reset_index().drop(columns='index')
        st.subheader('Most Recent Investments')
        st.dataframe(last5_df)

        col1, col2 = st.columns(2)
        with col1:    
                big_series = df[df['investors'].str.contains(investor, case=False, na=False)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
                st.subheader('Biggest Investments')
                fig, ax = plt.subplots()
                ax.bar(big_series.index, big_series.values)
                plt.xticks(size=6)
                plt.xlabel('Company')
                plt.ylabel('Amount (in Cr)')
                st.pyplot(fig)
        with col2:
                vertical_series = df[df['investors'].str.contains(investor, case=False, na=False)].groupby('vertical')['amount'].sum().sort_values(ascending=False).head()
                st.subheader('Top Sectors Invested') 
                fig1, ax1 = plt.subplots()
                ax1.pie(vertical_series, autopct='%0.1f%%', startangle=90, labels=vertical_series.index)
                st.pyplot(fig1)

        col1, col2, col3 = st.columns(3)
        with col1:    
                round_series = df[df['investors'].str.contains(investor, case=False, na=False)].groupby('round')['amount'].sum().sort_values(ascending=False).head()
                st.subheader('Top Rounds') 
                fig2, ax2 = plt.subplots()
                ax2.pie(round_series, autopct='%0.1f%%', startangle=90, labels=round_series.index)
                st.pyplot(fig2)
        with col2:
                city_series = df[df['investors'].str.contains(investor, case=False, na=False)].groupby('city')['amount'].sum().sort_values(ascending=False).head()
                st.subheader('Top City Invested') 
                fig3, ax3 = plt.subplots()
                ax3.pie(city_series, autopct='%0.1f%%', startangle=90, labels=city_series.index)
                st.pyplot(fig3)
        with col3:
                YoY_series = df[df['investors'].str.contains(investor, case=False, na=False)].groupby('year')['amount'].sum()
                st.subheader('YoY Investments') 
                fig4, ax4 = plt.subplots()
                ax4.plot(YoY_series)
                plt.xticks(rotation=90)
                st.pyplot(fig4)

startup_list = df['startup'].dropna().unique().tolist()
investors_list = (
    df['investors'].dropna().str.split(',').explode().str.strip().unique())

st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('', ['Overall Analysis', 'Startup', 'Investor'])

if option == 'Overall Analysis':
        load_overall_analysis()

elif option == 'Startup':
        selected_startup = st.sidebar.selectbox('Select Startup', sorted(startup_list))
        load_startup_details(selected_startup)

else:
        selected_investor = st.sidebar.selectbox('Select Investor', sorted(investors_list))
        load_investor_details(selected_investor)
