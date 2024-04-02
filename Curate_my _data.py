# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +

import streamlit as st
import pickle
import webbrowser
import requests
import time
import re
import sys
import xml.etree.ElementTree as ET
import os
import textwrap
from summarizer import Summarizer,TransformerSummarizer
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


            

           
    

# +
st.image('biocuration.png',width = 250)
pub_med_processed = False
if "button1_clicked" not in st.session_state:
    st.session_state["button1_clicked"] = False
if "button2_clicked" not in st.session_state:
    st.session_state["button2_clicked"] = False
API_URL = "https://api-inference.huggingface.co/models/Falconsai/medical_summarization"
headers = {"Authorization": "Bearer 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"}

def query(payload):
 response = requests.post(API_URL, headers=headers, json=payload, verify=False)
 time.sleep(5)
 return response.json()

def save_session_state(state):
  """Saves session state to a file."""
  with open("session.pkl", "wb") as f:
    pickle.dump(state, f)


# +
user_text = st.text_input("Enter your pubmed link:", key="pubmed")
if (st.button('Submit')):
    st.session_state["button1_clicked"] = True
    if not pub_med_processed:
        print("In herrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        text = user_text
        match = re.search(r'\d+', text)
        print(match.group())
        base_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?&ids={match.group()}"

# # Specify format (choose between BioC_xml or BioC_json)
        format = "BioC_xml"  # Replace with "BioC_json" if needed

# # Select the desired encoding (e.g., unicode or ascii)
        encoding = "unicode"

# # Construct the complete URL
        url = f"{base_url}"
        print(url)
# # Send GET request with requests library
        response = requests.get(url, verify=False)

# # Check for successful response
        if response.status_code == 200:
#   # Access the response content (text/xml or text/json)
            content = response.content
            print(content)
        else:
            print(f"Error: API request failed with status code {response.status_code}")

# # Parse the XML string
        root = ET.fromstring(response.content)

# # Find the 'record' element
        record_element = root.find('record')

# # Extract the PMCID attribute
        try:
            pmcid = record_element.attrib['pmcid']
        except:
            st.write("No Pubmed Central ID found")
            sys.exit()
# # Print the extracted PMCID
        print(pmcid)
        base_url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"

# Specify format (choose between BioC_xml or BioC_json)
        format = "BioC_xml"  # Replace with "BioC_json" if needed

# Enter the PubMed ID (PMID) you want to retrieve 
  
# Select the desired encoding (e.g., unicode or ascii)
        encoding = "unicode"

# Construct the complete URL
        url = f"{base_url}/{format}/{pmcid}/{encoding}"
        print(url)
# Send GET request with requests library
        response = requests.get(url, verify=False)

# Check for successful response
        if response.status_code == 200:
  # Access the response content (text/xml or text/json)
            content = response.content
    
        else:
            print(f"Error: API request failed with status code {response.status_code}")
  
        root = ET.fromstring(response.content)
        abstracts_paragraphs = []
        abstract = {}
        abstract['Abstract'] = []
        key_counter = 0
        abstract_title = {}
        for passage in root.findall(".//passage"):
            type = passage.find('infon[@key="type"]').text
            if type in ["abstract", "paragraph", "abstract_title_1"]:
                text = passage.find('text').text
                abstracts_paragraphs.append(text)
            if type == 'abstract_title_1':
                abstract_title = text  # Store the abstract title
            elif type == 'abstract':
                if abstract_title:
                    abstract[abstract_title] = text  # Use abstract_title as key
                    abstract_title = None
                else:
                    abstract['Abstract'].append(text)
        cleaned_list = [''.join(char for char in s.encode('latin-1').decode('unicode_escape') if char.isalnum() or char.isspace()) for s in abstracts_paragraphs]
    
        
#   
        st.write("Abstract:", abstract)
        gemini_api_key = "AIzaSyDZuPUJcr-i351-Q8Yp0N15SVQrDSLoTvA"
        genai.configure(api_key = gemini_api_key)


    
        model = genai.GenerativeModel('gemini-1.0-pro-latest')

        chat = model.start_chat(history=[])

        context= ', '.join(cleaned_list)
    
	
        #summary = query({
        #	"inputs": context,
        #})
        #print(summary)
    # Extract the summary text
        #summary_text = summary[0]['summary_text']

# Convert the summary text to a string
        #summary = str(summary_text)
        #print(summary)
        chat.send_message(context)
        
        print("Done")
        final_report = ""
        pub_med_processed = True
        
        st.session_state["Model"] = chat  # Store user_text in session state
    #st.session_state["button1_clicked"] = True  # Flag for Submit 1 click
        save_session_state(st.session_state)
if st.session_state["button1_clicked"] :
    user_question = st.text_input("Enter your question:")
    if user_question.strip() != "":
        # Validate for empty input
        chat = st.session_state["Model"]
        chat.send_message(user_question)
        last_message = chat.history[-1]
    #if st.button("Ask"):
        print(f'**{last_message.role}**: {last_message.parts[0].text}')
        st.write(last_message.parts[0].text)
        # Exit the loop if the user presses an empty Enter
       
