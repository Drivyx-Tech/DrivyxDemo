# @title Deployment [Persist Index Cache]
import os
import base64
import streamlit as st
from PIL import Image
os.environ["OPENAI_API_KEY"] = "<your key>"
from llama_index.llms.openai import OpenAI
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)
from llama_index.core import StorageContext, load_index_from_storage


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpeg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
image = Image.open("./png_trns_logomark.png")
st.set_page_config(
     page_title = "Drivyx Matchmaking Engine",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.drivyx.com/contact',
         'Report a bug': "https://www.drivyx.com/contact",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

st.title('Drivyx®')

#add_bg_from_local('./background.jpeg')

with st.sidebar:
    add_image = st.image(image)
    add_selectbox = st.sidebar.selectbox(
        "How would you like to be contacted?",
        ("Email", "Home phone", "Mobile phone")
         )

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="./Matchmaking")

# load index
@st.cache_resource
def load_index():
    index = load_index_from_storage(storage_context)
    return index

index = load_index()
engine = index.as_query_engine(similarity_top_k=10, llm=OpenAI(model="gpt-4"))

# @title Query Engine

import nest_asyncio
nest_asyncio.apply()

from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.core.question_gen.prompts import (
    DEFAULT_SUB_QUESTION_PROMPT_TMPL,
)


question_gen = LLMQuestionGenerator.from_defaults(
    llm=llm,
    prompt_template_str="""
        Follow the example, but instead of giving a question, always prefix the question
        with: 'By first identifying and quoting the most relevant sources, '.
        """
    + DEFAULT_SUB_QUESTION_PROMPT_TMPL,
)

final_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=[
        QueryEngineTool(
            query_engine=engine,
            metadata=ToolMetadata(
                name="EGS Provider documents",
                description="ESG information on companies.",
            ),
        )
    ],
    question_gen=question_gen,
    use_async=True,
)

text = st.text_area('Start the conversation..', 'Please see documents attached for your reference')


response = final_engine.query( text )
# print(response.response)
# print(response.metadata)

st.write(response.response)
#st.json(response.metadata)
