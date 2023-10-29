import streamlit as st
import pandas as pd
import requests
import re
import bs4
from bs4 import BeautifulSoup
import googletrans
from googletrans import Translator
import base64
import io
from io import BytesIO
import xlsxwriter
import numpy as np
from crawl_kr_sellers_sellers_df import overall_kr_sellers_df, template_overall_kr_sellers_df


# URL di prova
# https://minishop.gmarket.co.kr/victorydelivery
# https://minishop.gmarket.co.kr/issgmbh782
# https://shopping.interpark.com/product/productInfo.do?prdNo=7544796724&dispNo=016001&bizCd=P01397&NaPm=ct%3Dlo1a55mw%7Cci%3D3aa05c9dcff051c8d603072ebc2c6d478d4839eb%7Ctr%3Dslsl%7Csn%3D3%7Chk%3Df02003da051ce3ada457d016f746535b44961b7a&utm_medium=affiliate&utm_source=naver&utm_campaign=shop_20211015_navershopping_p01397_cps&utm_content=conversion_47
# https://smartstore.naver.com/illyheaven
# http://smartstore.naver.com/euroheim?NaPm=ct%3Dlo19fg76%7Cci%3Dshopn%7Ctr%3Dslsl%7Chk%3D0e5159ac915fd3cbeb337563189932b24301a0d9%7Ctrx%3Dundefined


# Streamlit App
st.title('KR Sellers Crawling')

#-----------------------------INPUT-----------------------------------------
excel_data = io.BytesIO()
# Define menu options
menu_options = ["Analyze Sellers", "Overall Database"]
# Create a widget to select a menu option
selected_option = st.sidebar.radio('Select Option', menu_options)


password = 'SecretConvey!?'
entered_password = st.text_input("Enter Password: ", type="password")

if entered_password == password:
    st.write('Correct Password')
    # Create content for each menu option
    if selected_option == "Overall Database":
        st.sidebar.header('   ')
        st.write(overall_kr_sellers_df)
        st.sidebar.title('SellersInfo Overall Database')
        with pd.ExcelWriter(excel_data, engine='xlsxwriter', mode='xlsx') as writer:
            overall_kr_sellers_df.to_excel(writer, index=False, sheet_name='SellersInfo')
        excel_data.seek(0)
        st.sidebar.markdown(f'### [Download SellersInfo Database](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_data.read()).decode()})')
        
        st.sidebar.header('___________________________________________________')
        st.sidebar.header('Update SellersInfo Database')
        update_sellers_database_file = st.sidebar.file_uploader('Provide XLSX file to Update SellersInfo Database', type=['xlsx'])
        # Create a Streamlit link to download the template as an XLSX file
        
        with pd.ExcelWriter(excel_data, engine='xlsxwriter', mode='xlsx') as writer:
            template_overall_kr_sellers_df.to_excel(writer, index=False, sheet_name='SellersInfo')
        excel_data.seek(0)
        st.sidebar.markdown(f'### [Download Template (XLSX) for Updating SellersInfo](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_data.read()).decode()})')
        
        if update_sellers_database_file:
            # Read the uploaded file
            new_data = pd.read_excel(update_sellers_database_file)
            # Append the new data to the existing data
            new_sellers_to_upload_df = pd.DataFrame(new_data)
            st.write(new_sellers_to_upload_df)
            # Append the new data to the existing data using pd.concat()
            updated_data = pd.concat([overall_kr_sellers_df, new_sellers_to_upload_df], ignore_index=True)
            updated_data = updated_data.dropna(how='all')
            st.header('DOWNLOAD THE UPDATED OVERALL SELLERS INFO DATABASE AND UPDATE THE DATABASE LOCALLY')
    
            # Save the updated data back to the data file
            updated_data.to_excel('Korean_Platforms_Sellers_Database.xlsx', index=False)
            
            with pd.ExcelWriter(excel_data, engine='xlsxwriter', mode='xlsx') as writer:
                updated_data.to_excel(writer, index=False, sheet_name='SellersInfoDatabase')
            excel_data.seek(0)
            st.markdown(f'### [Download updated Overall Database (XLSX)](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_data.read()).decode()})')

    elif selected_option == "Analyze Sellers":
        st.sidebar.header('___________________________________________________')
        # Upload XLSX file
        st.sidebar.header('Upload an XLSX File with sellers to analyze')
        uploaded_file = st.sidebar.file_uploader("Upload XLSX file", type=["xlsx"])
        # Input for typing URLs
        st.sidebar.header('OR')
    
        st.sidebar.header('Type URLs for sellers to analyze')
        user_input = st.sidebar.text_area("Enter URLs (one per line)")
        # Allow the user to upload an Excel file
    
    
    
    
    
    
    # Initialize a sellers urls DataFrame
    df_sellers_urls = pd.DataFrame({'SELLER_URL': [], 'SELLER_USERNAME': [], 'PLATFORM': [], 'SELLER_URL_original': [], 'SELLER_COMBINED': []})
    
    def clean_url(url):
        cleaned_url = re.sub('http://smart', 'https://smart', url)
        cleaned_url = re.sub(r'^https?://cr.shopping.naver.com', 'https://smartstore.naver.com', cleaned_url)
        cleaned_url = re.sub(r'\?NaP.*', '', cleaned_url)
        username = re.sub(r'^.*\/', '', cleaned_url)
        # Set the platform based on the cleaned URL
        if 'smartstore.naver' in cleaned_url:
            platform = 'NAVER'
        elif 'interpark' in cleaned_url:
            platform = 'INTERPARK'
        elif 'gmarket' in cleaned_url:
            platform = 'GMARKET'  # You can set a default value if the condition is not met
        elif 'shopping.naver.com' in cleaned_url:
            platform = 'SHOPPING NAVER'
        
        seller_combined = username + '_' + platform
        return cleaned_url, username, platform, seller_combined
    
    if selected_option == "Analyze Sellers":
        if uploaded_file is not None:
            uploaded_df = pd.read_excel(uploaded_file)    
            # Remove rows with empty cells
            uploaded_df.dropna(inplace=True)
            if 'Seller Url' in uploaded_df.columns:
                uploaded_df.rename(columns={'Seller Url': 'SELLER_URL_original'}, inplace=True)
            if 'Seller URL' in uploaded_df.columns:
                uploaded_df.rename(columns={'Seller URL': 'SELLER_URL_original'}, inplace=True)
            if 'SELLER_URL' in uploaded_df.columns:
                uploaded_df.rename(columns={'SELLER_URL': 'SELLER_URL_original'}, inplace=True)
            # st.write(df_urls)
            # Assign an index to each row
            uploaded_df['INDEX'] = range(len(uploaded_df))
            # Count occurrences of in LISTING_URL_xlsx
            urls_count = len(uploaded_df['SELLER_URL_original'])
            # Identify duplicates and drop them
            urls_duplicates = uploaded_df['SELLER_URL_original'].duplicated().sum()
            uploaded_df = uploaded_df.drop_duplicates(subset=['SELLER_URL_original'])
            # Concatenate the two DataFrames vertically
            df_sellers_urls = pd.concat([df_sellers_urls, uploaded_df], ignore_index=True)
            # Apply 'clean_url' function to every URL in 'SELLER_URL_original' column
            df_sellers_urls[['SELLER_URL', 'SELLER_USERNAME', 'PLATFORM', 'SELLER_COMBINED']] = uploaded_df['SELLER_URL_original'].apply(clean_url).apply(pd.Series)
    
    
            # Count the number of non-empty URLs
            num_urls = len([url for url in uploaded_df['SELLER_URL_original'] if isinstance(url, str) and url.strip() != ""])
            st.sidebar.write(f"Total number of URLs in the DataFrame: {num_urls}")
            
            st.header('SELLER URLs UPLOADED with XLSX')
            st.write(df_sellers_urls)
    
        if user_input:
            urls_imported = user_input.split('\n')
            # Remove duplicates from urls_imported
            urls_imported = list(set(urls_imported))
    
            cleaned_urls = [clean_url(url)[0] for url in urls_imported]
            usernames = [clean_url(url)[1] for url in urls_imported]
            platforms = [clean_url(url)[2] for url in urls_imported]
            seller_combineds = [clean_url(url)[3] for url in urls_imported]
    
            # Create a DataFrame from the cleaned URLs
            df_sellers_urls['SELLER_URL'] = cleaned_urls
            df_sellers_urls['SELLER_USERNAME'] = usernames
            df_sellers_urls['PLATFORM'] = platforms
            df_sellers_urls['SELLER_COMBINED'] = seller_combineds
            df_sellers_urls['SELLER_URL_original'] = urls_imported
            df_sellers_urls = df_sellers_urls.drop_duplicates(subset=['SELLER_COMBINED'])
         
            st.header('SELLER URLs PROVIDED in the BOX')
            st.write(df_sellers_urls)
            # urls_modified = [url.replace(r'https?://cr.shopping.naver.com', 'https://smartstore.naver.com', regex=True) for url in urls_inputed]
            # urls = urls_modified
    
    # Filter overall_kr_sellers_df based on the 'SELLER_COMBINED' values
    sellers_in_database_df = overall_kr_sellers_df[overall_kr_sellers_df['SELLER_COMBINED'].isin(df_sellers_urls['SELLER_COMBINED'])]
    # Reset the index of the resulting DataFrame
    sellers_in_database_df = sellers_in_database_df.reset_index(drop=True)
    if not sellers_in_database_df.empty:
        st.header('SELLERS ALREADY IN DATABASE')
        st.write(sellers_in_database_df)
    
    # Filter overall_kr_sellers_df based on the 'SELLER_COMBINED' values
    df_new_sellers_urls = df_sellers_urls[~df_sellers_urls['SELLER_COMBINED'].isin(overall_kr_sellers_df['SELLER_COMBINED'])]
    # Reset the index of the resulting DataFrame
    df_new_sellers_urls = df_new_sellers_urls.reset_index(drop=True)
    if not df_new_sellers_urls.empty:
        st.header('NEW SELLERS TO CRAWL')
        st.write(df_new_sellers_urls)
        start_crawl_button = st.button('CRAWL NEW SELLERS')
    #-----------------------------/INPUT----------------------------------------
    
    
    #--------------------------CRAWLING DATA------------------------------------
    
    
    # Function to extract content inside '<script>window.__PRELOADED_STATE__=' element
    def extract_minishop(url):
        try:
            response = requests.get(url)
            source_code = response.text
            # st.write(source_code)
            # Parse the HTML
            soup = BeautifulSoup(source_code, 'html.parser')
            # Find the <div class="seller_info"> element
            seller_info_div = soup.find('div', class_='seller_info')
            if seller_info_div:
                content = seller_info_div.get_text()
                return content
            else:
                return "No 'div sellers info' class found in the source code."
        except Exception as e:
            return str(e)
    
    
    def extract_interpark(url):
        try:
            response = requests.get(url)
            source_code = response.text
            # st.write(source_code)
            # Regular expression pattern with capturing group
            pattern = r'<script type="text/javascript">(.*?)</script>'
            # Use re.findall to find all matches
            matches = re.findall(pattern, source_code, re.DOTALL)
            if len(matches) > 1:
                # Extract the content from the second match (index 1)
                javascript_content = matches[1]
                return javascript_content
            else:
                return "Not enough matches found."
        except Exception as e:
            return str(e)
    
    
    def extract_preloaded_state(url):
        try:
            response = requests.get(url)
            source_code = response.text
            # st.write(source_code)
            preloaded_state_match = re.search(r'<script>window.__PRELOADED_STATE__=(.*?)</script>', source_code)
            if preloaded_state_match:
                preloaded_state_content = preloaded_state_match.group(1)
                return preloaded_state_content
            else:
                return "No '<script>window.__PRELOADED_STATE__=' element found in the source code."
        except Exception as e:
            return str(e)
    
    
    
    
    
    # Create a DataFrame to store the extracted content
    # df_content = pd.DataFrame(columns=['SELLER_URL', 'COMPANY_VAT_N', 'COMPANY_NAME', 'COMPANY_REPRESENTATIVE', 'COMPANY_TEL_N', 'COMPANY_E-MAIL', 'CONTENT_EXTRACTED'])
    df_content = df_new_sellers_urls.copy()
    urls = df_content['SELLER_URL']
    
    
    
    # Initialize counts for each type
    count_gmarket = 0
    count_store_naver = 0
    count_interpark = 0
    
    
    
    
    
    
    # Display content for the provided URLs
    if start_crawl_button:
        data = {'SELLER_URL': urls, 'CONTENT_EXTRACTED': [], 'PLATFORM': []}
        for url in urls:
            if isinstance(url, str):
                st.subheader(f'Content for {url}')
                if 'minishop.gmarket' in url:
                    content_extracted = extract_minishop(url)
                    data['CONTENT_EXTRACTED'].append(content_extracted)
                    data['PLATFORM'].append('GMARKET')
                    count_gmarket += 1
                    st.sidebar.text(f"GMARKET Sellers Count: {count_gmarket}")
    
                elif 'smartstore.naver' in url:
                    content_extracted = extract_preloaded_state(url)
                    data['CONTENT_EXTRACTED'].append(content_extracted)
                    data['PLATFORM'].append('NAVER')
                    count_store_naver += 1
                    st.sidebar.text(f"NAVER Sellers Count: {count_store_naver}")
    
                elif 'interpark' in url:
                    content_extracted = extract_interpark(url)
                    data['CONTENT_EXTRACTED'].append(content_extracted)
                    data['PLATFORM'].append('INTERPARK')
                    count_interpark += 1
                    st.sidebar.text(f"INTERPARK Sellers Count: {count_interpark}")
                else:
                    data['CONTENT_EXTRACTED'].append('PLATFORM NOT SET YET')
                    data['PLATFORM'].append('UNKNOWN')
                
    
    
    
        # Ensure all arrays are the same length
        max_length = max(len(data['SELLER_URL']), len(data['CONTENT_EXTRACTED']), len(data['PLATFORM']))
        data['SELLER_URL'] = data['SELLER_URL'].tolist() + [None] * (max_length - len(data['SELLER_URL']))
        data['CONTENT_EXTRACTED'] += [None] * (max_length - len(data['CONTENT_EXTRACTED']))
        data['PLATFORM'] += [None] * (max_length - len(data['PLATFORM']))
    
        df_content = pd.DataFrame(data)
    
    
    
        minishop_df = df_content[df_content['PLATFORM'].isin(['GMARKET', None])]
        minishop_df['SELLER_USERNAME'] = minishop_df['SELLER_URL'].str.split(r'.com/').str[1]
        minishop_df['SELLER_USERNAME'] = minishop_df['SELLER_URL'].str.split(r'.kr/').str[1]
    
        storenaver_df = df_content[df_content['PLATFORM'].isin(['NAVER'])]
        storenaver_df['SELLER_USERNAME'] = storenaver_df['SELLER_URL'].str.split(r'/').str[1]
        
        interpark_df = df_content[df_content['PLATFORM'].isin(['INTERPARK'])]
        interpark_df['SELLER_USERNAME'] = interpark_df['SELLER_URL'].str.split(r'.com/').str[1]
        interpark_df['SELLER_USERNAME'] = interpark_df['SELLER_URL'].str.split(r'/').str[1]
        interpark_df['SELLER_USERNAME'] = interpark_df['SELLER_URL'].str.split(r'.kr/').str[1]
    
       # Process the 'CONTENT_EXTRACTED' column to extract relevant information
       
        minishop_df['COMPANY_VAT_N'] = minishop_df['CONTENT_EXTRACTED'].str.split('사업자번호').str[1]
        minishop_df['COMPANY_VAT_N'] = minishop_df['COMPANY_VAT_N'].str.split('영업소재지').str[0]
        
        minishop_df['COMPANY_NAME'] = minishop_df['CONTENT_EXTRACTED'].str.split('상호').str[1]
        minishop_df['COMPANY_NAME'] = minishop_df['COMPANY_NAME'].str.split('대표자').str[0] 
        
        minishop_df['COMPANY_ADDRESS'] = minishop_df['CONTENT_EXTRACTED'].str.split('영업소재지').str[1]
        minishop_df['COMPANY_ADDRESS'] = minishop_df['COMPANY_ADDRESS'].str.replace(' ', '', regex=True)
       
        minishop_df['COMPANY_REPRESENTATIVE'] = minishop_df['CONTENT_EXTRACTED'].str.split('대표자').str[1]
        minishop_df['COMPANY_REPRESENTATIVE'] = minishop_df['COMPANY_REPRESENTATIVE'].str.split('전화번호').str[0]
    
        minishop_df['COMPANY_TEL_N'] = minishop_df['CONTENT_EXTRACTED'].str.split('전화번호').str[1]
        minishop_df['COMPANY_TEL_N'] = minishop_df['COMPANY_TEL_N'].str.split('응대시간').str[0]
        minishop_df['COMPANY_TEL_N'] = minishop_df['COMPANY_TEL_N'].str.split('이메일').str[0]
        minishop_df['COMPANY_TEL_N'] = minishop_df['COMPANY_TEL_N'].str.replace('팩스번호', '; Fax: ', regex=False)
    
        minishop_df['COMPANY_E-MAIL'] = minishop_df['CONTENT_EXTRACTED'].str.split('이메일').str[1]
        minishop_df['COMPANY_E-MAIL'] = minishop_df['COMPANY_E-MAIL'].str.split('사업자번호').str[0]
        minishop_df['USERNAME_MATCH'] = ""
    
    
    
    
        storenaver_df['SELLER_USERNAME'] = storenaver_df['SELLER_URL'].str.split(r'.com/').str[1]
    
        storenaver_df['COMPANY_NAME'] = storenaver_df['CONTENT_EXTRACTED'].str.split('"contactInfo"').str[1]
        storenaver_df['COMPANY_NAME'] = storenaver_df['CONTENT_EXTRACTED'].str.split('representName"').str[1]
        storenaver_df['COMPANY_NAME'] = storenaver_df['COMPANY_NAME'].str.replace(r':"', '', regex=False)
        storenaver_df['COMPANY_NAME'] = storenaver_df['COMPANY_NAME'].str.split('"').str[0]
    
        storenaver_df['COMPANY_REPRESENTATIVE'] = storenaver_df['CONTENT_EXTRACTED'].str.split('representativeName"').str[1]
        storenaver_df['COMPANY_REPRESENTATIVE'] = storenaver_df['COMPANY_REPRESENTATIVE'].str.replace(r':"', '', regex=False)
        storenaver_df['COMPANY_REPRESENTATIVE'] = storenaver_df['COMPANY_REPRESENTATIVE'].str.split('"').str[0]
        storenaver_df['COMPANY_VAT_N'] = 'NOT AVAILABLE'
        storenaver_df['COMPANY_TEL_N'] = 'NOT AVAILABLE'
        storenaver_df['COMPANY_E-MAIL'] = 'NOT AVAILABLE'
        storenaver_df['COMPANY_ADDRESS'] = 'NOT AVAILABLE'
        storenaver_df['USERNAME_MATCH'] = ""
    
    
    
        interpark_df['COMPANY_NAME'] = interpark_df['CONTENT_EXTRACTED'].str.split('entrNm":"').str[1]
        interpark_df['COMPANY_NAME'] = interpark_df['COMPANY_NAME'].astype(str)
        interpark_df['COMPANY_NAME'] = interpark_df['COMPANY_NAME'].str.split('","').str[0]
        
        interpark_df['COMPANY_VAT_N'] = interpark_df['CONTENT_EXTRACTED'].str.split('bizRegNo":"').str[1]
        interpark_df['COMPANY_VAT_N'] = interpark_df['COMPANY_VAT_N'].astype(str)
        interpark_df['COMPANY_VAT_N'] = interpark_df['COMPANY_VAT_N'].str.split('","').str[0]
    
        interpark_df['COMPANY_TEL_N'] = interpark_df['CONTENT_EXTRACTED'].str.split('AdminTelno":"').str[1]
        interpark_df['COMPANY_TEL_N'] = interpark_df['COMPANY_TEL_N'].astype(str)
        interpark_df['COMPANY_TEL_N'] = interpark_df['COMPANY_TEL_N'].str.split('","').str[0]
    
        interpark_df['COMPANY_E-MAIL'] = interpark_df['CONTENT_EXTRACTED'].str.split('AdminEmail":"').str[1]
        interpark_df['COMPANY_E-MAIL'] = interpark_df['COMPANY_E-MAIL'].astype(str)
        interpark_df['COMPANY_E-MAIL'] = interpark_df['COMPANY_E-MAIL'].str.split('","').str[0]
    
        interpark_df['COMPANY_ADDRESS'] = interpark_df['CONTENT_EXTRACTED'].str.split('addr":"').str[1]
        interpark_df['COMPANY_ADDRESS'] = interpark_df['COMPANY_ADDRESS'].astype(str)
        interpark_df['COMPANY_ADDRESS'] = interpark_df['COMPANY_ADDRESS'].str.split('","').str[0]
    
        interpark_df['COMPANY_REPRESENTATIVE'] = interpark_df['CONTENT_EXTRACTED'].str.split('mainNm":"').str[1]
        interpark_df['COMPANY_REPRESENTATIVE'] = interpark_df['COMPANY_REPRESENTATIVE'].astype(str)
        interpark_df['COMPANY_REPRESENTATIVE'] = interpark_df['COMPANY_REPRESENTATIVE'].str.split('","').str[0]
    
        interpark_df['USERNAME_MATCH'] = ""
    
        def fill_empty_values(store_df, minishop_df, column_name):
            for index, row in store_df.iterrows():
                if pd.isna(row[column_name]) or row[column_name].strip() == "" or row[column_name].strip() == "NOT AVAILABLE":
                    username = row['SELLER_USERNAME']
                    matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
                    if not matching_minishop_row.empty:
                        store_df.at[index, column_name] = matching_minishop_row.iloc[0][column_name]
                        store_df.at[index, 'USERNAME_MATCH'] = 'Username match with minishop.gmarket'
    
        # Usage
        columns_to_fill = ['COMPANY_NAME', 'COMPANY_ADDRESS', 'COMPANY_VAT_N', 'COMPANY_REPRESENTATIVE', 'COMPANY_TEL_N', 'COMPANY_E-MAIL']
        for column in columns_to_fill:
            fill_empty_values(storenaver_df, minishop_df, column)
    
    
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_NAME']) or row['COMPANY_NAME'].strip() == "" or row['COMPANY_NAME'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_NAME'] = matching_minishop_row.iloc[0]['COMPANY_NAME']
        
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_ADDRESS']) or row['COMPANY_ADDRESS'].strip() == "" or row['COMPANY_ADDRESS'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_ADDRESS'] = matching_minishop_row.iloc[0]['COMPANY_ADDRESS']
        
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_VAT_N']) or row['COMPANY_VAT_N'].strip() == "" or row['COMPANY_VAT_N'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_VAT_N'] = matching_minishop_row.iloc[0]['COMPANY_VAT_N']
        
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_REPRESENTATIVE']) or row['COMPANY_REPRESENTATIVE'].strip() == "" or row['COMPANY_REPRESENTATIVE'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_REPRESENTATIVE'] = matching_minishop_row.iloc[0]['COMPANY_REPRESENTATIVE']
        
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_VAT_N']) or row['COMPANY_VAT_N'].strip() == "" or row['COMPANY_VAT_N'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_VAT_N'] = matching_minishop_row.iloc[0]['COMPANY_VAT_N']
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_VAT_N']) or row['COMPANY_VAT_N'].strip() == "" or row['COMPANY_VAT_N'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_VAT_N'] = matching_minishop_row.iloc[0]['COMPANY_VAT_N']
        # for index, row in storenaver_df.iterrows():
        #     if pd.isna(row['COMPANY_VAT_N']) or row['COMPANY_VAT_N'].strip() == "" or row['COMPANY_VAT_N'].strip() == "NOT AVAILABLE":
        #         username = row['SELLER_USERNAME']
        #         matching_minishop_row = minishop_df[minishop_df['SELLER_USERNAME'] == username]
        #         if not matching_minishop_row.empty:
        #             storenaver_df.at[index, 'COMPANY_VAT_N'] = matching_minishop_row.iloc[0]['COMPANY_VAT_N']
    
        df_content = pd.concat([minishop_df, storenaver_df, interpark_df], ignore_index=True)
        
        # Create a translator instance
        from googletrans import Translator
    
        translator = Translator()
    
        # Define a function to translate if the input is not None or NaN
        def translate_text(text):
            if pd.notna(text):
                try:
                    translations = translator.translate(text, src='ko', dest='en')
                    if hasattr(translations, 'text'):
                        return translations.text
                    else:
                        return text
                except Exception as e:
                    print(f"Translation error: {e}")
                    return text
            return text
    
    
        # Translate the 'COMPANY_NAME' column from Korean to English
        df_content['COMPANY_NAME_EN'] = df_content['COMPANY_NAME'].apply(translate_text)
        df_content['COMPANY_ADDRESS_EN'] = df_content['COMPANY_ADDRESS'].apply(translate_text)
        df_content['COMPANY_REPRESENTATIVE_EN'] = df_content['COMPANY_REPRESENTATIVE'].apply(translate_text)
        df_content['SELLER_COMBINED'] = df_content['SELLER_USERNAME'] + '_' + df_content['PLATFORM']
    
        df_content = df_content[['SELLER_USERNAME', 'SELLER_COMBINED', 'USERNAME_MATCH', 'SELLER_URL', 'PLATFORM', 'COMPANY_VAT_N', 'COMPANY_NAME', 'COMPANY_ADDRESS', 'COMPANY_NAME_EN', 'COMPANY_ADDRESS_EN',  'COMPANY_REPRESENTATIVE', 'COMPANY_REPRESENTATIVE_EN', 'COMPANY_TEL_N', 'COMPANY_E-MAIL', 'CONTENT_EXTRACTED']]
    
        #   newlines from all columns in the DataFrame
        df_content = df_content.replace('\n', '', regex=True)
        st.write('DF CONTENT')    
        st.dataframe(df_content)
    
        df_sellers_urls = pd.concat([df_content, sellers_in_database_df], ignore_index=True)
    
        # Convert the DataFrame to XLSX format
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_sellers_urls.to_excel(writer, sheet_name='SellersInfo', index=False)
    
        # Set up the download link
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Korean_Platforms_SellersInfo.xlsx">Download df_content as XLSX</a>'
    
        # Display the download link
        st.markdown(href, unsafe_allow_html=True)
else:
    st.write('Incorrect Password. Try again!')
