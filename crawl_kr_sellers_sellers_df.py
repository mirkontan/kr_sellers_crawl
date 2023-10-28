import pandas as pd

# # Sample DataFrame
# data = {'USERNAME': ['highsellerstore', 'kja290424'],
#         'SELLER_COMBINED': ['highsellerstore_GMARKET', 'kja290424_GMARKET'],
#         'PLATFORM': ['GMARKET', 'GMARKET'],
#         'SELLER_URL':['http://minishop.gmarket.co.kr/highsellerstore', 'http://minishop.gmarket.co.kr/kja290424'],
#         'COMPANY_VAT_N': ['736-09-02115', '-'],
#         'COMPANY_NAME': ['하이셀러', '-'],
#         'COMPANY_ADDRESS': ['전라남도순천시팔마4길40,101동1102호(연향동세영the-조은아파트)판매자개인정보처리방침', '-']     
#         }

# Define the path to your data file
data_file_path = r'/Users/mirkofontana/Desktop/Script_Python/StreamlitApps/KR_SELLERS_CRAWLING/Korean_Platforms_Sellers_Database.xlsx'
# Load data
data = pd.read_excel(data_file_path)

overall_kr_sellers_df = pd.DataFrame(data)
# Remove newlines from all columns in the DataFrame
overall_kr_sellers_df = overall_kr_sellers_df.replace('\n', '', regex=True)
overall_kr_sellers_df = overall_kr_sellers_df.drop_duplicates(subset=['SELLER_COMBINED'], keep='last')

template_overall_kr_sellers_df = pd.DataFrame(columns=overall_kr_sellers_df.columns)
print(template_overall_kr_sellers_df)