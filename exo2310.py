# -*- coding: utf-8 -*-

import pandas as pd
import time
from datetime import date

def clean_people(df):
    # rename columns:
    df = df.rename(columns={'email address': 'email'})
    
    # remove rows which have an empty "first_name" (NA):
    #df = df[df.first_name.notna()] <- equivalent to next line:
    df = df.dropna(subset=['first_name'])
    
    # drop duplicates on ID column:
    df = df.drop_duplicates()
    
    # Normalize gender column:
    df['gender'] = df['gender'].replace({'Female': 'F', 'Male': 'M'})
    
    # Convert column "age" to number (coerce: put NaN for bad values):
    df['age'] = pd.to_numeric(df.age, errors='coerce')
    
    # Convert columns to date type:
    df['registration'] = pd.to_datetime(df.registration)
    df['last_seen'] = pd.to_datetime(df.last_seen, unit='s')
    # When missing, last seen should fallback to the registration date:
    df['last_seen'] = df.last_seen.combine_first(df.registration)
    
    # Add a "full_name" column by concatenating two other ones:
    df['full_name'] = df.first_name + " " + df.last_name
    
    # Add a "country" column by extracting it from the address, with a split:
    df['country'] = df.address.str.split(', ').str[1]
    
    # Column "money" contains values like "$50.23" or "€23,09".
    # We want to make it uniform (only dollar currency) and as number, not str.
    df['currency'] = df.money.str[0]  # extract first char ($/€) to a new "currency" column
    df['money'] = df.money.str[1:].str.replace(',', '.')  # extract remaining chars and replace , by .
    df['money'] = pd.to_numeric(df.money)  # convert to number
    # convert euros cells to dollar:
    df.loc[df.currency == '€', 'money'] = df[df.currency == '€'].money * 1.10
    del df['currency']  # remove "currency" column which is now useless
    
    # Keep only rows where email is not NA:
    df = df.dropna(subset=['email'])
    # Keep only rows where email is a good email:
    # CAUTION: in the real world you should not use dummy regexes like this to validate email addresses,
    # but instead use a dedicated tool like https://github.com/syrusakbary/validate_email.
    df = df[df.email.str.contains('.+@[0-9a-zA-Z\.\-_]+\.\w{2,}')]
    # Some users may use email alias (example: john.smith+truc@gmail.com is an alias for john.smith@gmail.com).
    # We want to drop these duplicates. To do that, we extract the 'alias' part with a regex:
    groups = df.email.str.extract('([0-9a-zA-Z\.\-_]+)(\+[0-9a-zA-Z\.\-_]+)?(@[0-9a-zA-Z\.\-_]+\.\w{2,})')
    df['email'] = groups[0] + groups[2]  # we override the email with the email without the alias part
    # Then, just use drop_duplicates, which will keep the first line by default:
    df = df.drop_duplicates(subset=['email'])
    
    
    
    df['inactive']=df['last_seen'].map(lambda x: True if(x.year-2018<1) else False)
    
    df = df[df.phone.str.contains('\w{10}', na=False)]
    
    df['mobile_phone']=df['phone'].map(lambda x: True if(x[0:2]=="06") else False) 
    
    return df


df_people = pd.read_csv('people.csv', sep=',')

df_people = clean_people(df_people)

