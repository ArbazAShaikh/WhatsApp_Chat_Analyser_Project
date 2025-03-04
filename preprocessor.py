import re
import pandas as pd

def rawToDf(text, key):
    '''Converts raw WhatsApp chat text into a DataFrame'''

    split_formats = {
        '12h': r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][mM]\s-\s',
        '24h': r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
    }
    datetime_formats = {
        '12h': '%m/%d/%y, %I:%M %p - ',  # Fixed format
        '24h': '%m/%d/%y, %H:%M - ',
        #'12h': '%d/%m/%Y, %I:%M %p - ',
        #'24h': '%d/%m/%Y, %H:%M - ',
    }

    # Convert text into a single string (handling multi-line messages)
    raw_string = ' '.join(text.split('\n'))

    # Extract messages and timestamps
    user_msg = re.split(split_formats[key], raw_string)[1:]  # Messages
    date_time = re.findall(split_formats[key], raw_string)  # Datetime strings

    # Ensure equal length for DataFrame
    if len(user_msg) != len(date_time):
        print("Warning: Mismatch in extracted messages and timestamps!")
        return pd.DataFrame()  # Return empty DataFrame if there's an issue

    df = pd.DataFrame({'date_time': date_time, 'user_msg': user_msg})

    # Convert `date_time` to actual datetime format
    df['date_time'] = pd.to_datetime(df['date_time'], format=datetime_formats[key])

    # Split user and message
    usernames = []
    msgs = []
    for i in df['user_msg']:
        a = re.split(r'([\w\W]+?):\s', i)  # Lazy pattern to match first `User: Message`
        if len(a) > 1:  # If user message
            usernames.append(a[1])
            msgs.append(a[2])
        else:  # If group notification
            usernames.append("group_notification")
            msgs.append(a[0])

    df['user'] = usernames
    df['message'] = msgs

    # Drop original user_msg column
    df.drop(columns=['user_msg'], inplace=True)

    # Extract date components
    df['year'] = df['date_time'].dt.year
    df['month_num']=df['date_time'].dt.month
    df['month'] = df['date_time'].dt.month_name()
    df['only_date'] = df['date_time'].dt.date
    df['date'] = df['date_time'].dt.day
    df['day_name'] = df['date_time'].dt.day_name()
    df['hour'] = df['date_time'].dt.hour
    df['minute'] = df['date_time'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period


    return df
