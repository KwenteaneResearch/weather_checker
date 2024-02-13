
from weather_checker.params import *

import os
from os import listdir
from os.path import isfile, join

from pathlib import Path

import pandas as pd

from pypdf import PdfReader

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

#listing the files from a specific folder
def get_monthly_reports(year=2016,month="02"):
    year_folder = Path(RAW_DATA_PATH).joinpath("pdf_reports",f"{year}")
    yearly_files = [f for f in listdir(year_folder) if isfile(join(year_folder, f))]

    monthly_reports = [s for s in yearly_files if s[2] + s[3] == month]

    #extracting text from PDFs
    comments_db_monthly = []
    files_not_processed =[]

    for files in monthly_reports:
        reader = PdfReader(Path(RAW_DATA_PATH).joinpath("pdf_reports",f"{year}",f"{files}"))
        page = reader.pages[0]
        text =page.extract_text()
        comment = text.partition("COT")[2]
        comment = comment.lower()

        comment = comment.replace('\n'," ")
        comment = comment.split("         ")[-1]
        if len(comment) < 25:
            files_not_processed.append(files)
        else:
            comments_db_monthly.append(f"date of report: {files.strip('.pdf')}; report content: {comment}")
    #exporting to csv
    comments_db_monthly_df = pd.DataFrame(comments_db_monthly)
    comments_db_monthly_df.to_csv(path_or_buf=Path(RAW_DATA_PATH).joinpath("pdf_reports",f"{year}_{month}_extracted_reports.csv"),index=False)

    print(f"✅reports collected and saved")


    return comments_db_monthly,files_not_processed

def get_monthly_summary(year=2016,month="02"):

    cache_path = Path(RAW_DATA_PATH).joinpath("pdf_reports",f"{year}_{month}_extracted_reports.csv")
    if cache_path.is_file()==False:
        print(f"❌ reports for year {year} and month {month} not found, please extract monthly reports first")
        return None
    else:
        #importing the list from the existing CSV
        print(f"✅reports found and loaded")
        reports_to_summarise = pd.read_csv(Path(RAW_DATA_PATH).joinpath("pdf_reports",f"{year}_{month}_extracted_reports.csv"))
        reports_to_summarise = reports_to_summarise["0"].tolist()

    #instantiating the model
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_openai = OpenAI(model ="gpt-3.5-turbo-instruct",temperature=0, openai_api_key=openai_api_key)

    #using a complex prompt for the summarize chain using map_reduce with OpenAI
    map_prompt_template = """

                        Write a summary of this chunk of text that includes the main points and any important details about weather.
=======
                        You are a cocoa commodity market analyst
                        Write a summary of this chunk of text and include any information about weather that you find in the text.
                        Please indicate the date of the text which is indicated at the beginning in date of report

                        {text}
                        """

    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

    combine_prompt_template = """
                        Write a concise summary of the following text delimited by triple backquotes.
                        Return your response in bullet points which covers the key points of the text.
                        ```{text}```
                        BULLET POINT SUMMARY:
                        """

    combine_prompt = PromptTemplate(
        template=combine_prompt_template, input_variables=["text"]
    )

    # create LLM chain
    map_reduce_chain = load_summarize_chain(
        llm_openai,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        return_intermediate_steps=False,
        verbose=False
    )
    #splitting documents and displaying
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=300)

    docs = text_splitter.create_documents(reports_to_summarise)
    docs = text_splitter.split_documents(docs)
    num_docs = len(docs)
    for doc in range(num_docs):
        num_tokens = llm_openai.get_num_tokens(docs[doc].page_content)
        print (f"Now we have {num_docs} documents and the document{doc} has {num_tokens} tokens")

    #running the chain
    map_reduce_outputs = map_reduce_chain({"input_documents": docs})
    #printing the summary
    print(map_reduce_outputs["output_text"])
    return map_reduce_outputs["output_text"]


if __name__ == '__main__':
    reports = get_monthly_summary()
