import streamlit as st
import fitz  # PyMuPDF
import os
import tempfile
from supabase import Client
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

current_vehicle_data = st.session_state.get("current_vehicle_data")
def show_llm_analysis(supabase: Client):
    #st.set_page_config(page_title="Vehicle Manual Chatbot", page_icon="🚗", layout="wide")
    st.title("Vehicle Manual Chatbot")
    st.write("Ask your queries about your vehicle manual and get answers in real-time, powered by Large Language Models")
    st.write("------------------------------------------------------------------------")

    # Function to fetch the manual link using vehicle_id
    def fetch_manual_link(vehicle_id):
        response = supabase.table('vehicles') \
                        .select('manual_link') \
                        .eq('vehicle_id', vehicle_id) \
                        .execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['manual_link']
        return None
    # Function to download PDF from Supabase storage
    import requests

    def download_pdf(manual_link):
        if not manual_link:
            return None

        try:
            # Extract file name and remove invalid characters
            file_name = manual_link.split("/")[-1].split("?")[0]  # Remove query params if present
           # st.write(f"Cleaned File Name: {file_name}")

            temp_dir = r"D:\Projects\MainEL\mainel\manual_folder"
            temp_path = os.path.join(temp_dir, file_name)
           # st.write(f"Saving File To: {temp_path}")

            # Get the public URL
            public_link = supabase.storage.from_("manuals").get_public_url(f"manuals/{file_name}").split("?")[0]
            #st.write(f"Public URL: {public_link}")

            # Fetch the file
            response = requests.get(public_link)

            if response.status_code == 200:
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                return temp_path
            else:
                st.error(f"Failed to download file. HTTP {response.status_code}")
                return None

        except Exception as e:
            st.error(f"Error downloading manual: {e}")
            return None

    # Function to extract text from a PDF
    def extract_text_from_pdf(file_path):
        try:
            with fitz.open(file_path) as doc:
                return "\n".join([page.get_text("text") for page in doc if page.get_text("text").strip()])
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""

    # Fetch vehicle_id from session state
    vehicle_id = st.session_state.get("current_vehicle")
    vehicle_id = next(iter(vehicle_id), None)
    st.write(f"Vehicle currently being analysed : {vehicle_id}")

    if vehicle_id:
        
        #st.write(f"Fetching manual for Vehicle ID: {vehicle_id}")

        manual_link = fetch_manual_link(vehicle_id)
        if manual_link:
            pdf_path = download_pdf(manual_link)

            if pdf_path:
                st.success("Vehicle manual downloaded successfully!")

                # Extract text from the downloaded PDF
                full_manual_text = extract_text_from_pdf(pdf_path)

                if not full_manual_text:
                    st.warning("No text extracted from the PDF. Please try another file.")
                else:
                    # Load LLM model
                    MODEL = "llama2"

                    @st.cache_resource
                    def load_model():
                        return Ollama(model=MODEL, temperature=0.3, num_ctx=2048, base_url="http://localhost:11434")


                    model = load_model()

                    # Define prompt
                    template = """
                    Answer the question based on the context below. If you can't 
                    answer the question, reply "I don't know".
                    {context}

                    Question: {question}
                    """
                    prompt = PromptTemplate.from_template(template)
                    parser = StrOutputParser()

                    # User query input
                    question = st.text_input("Ask a question about your vehicle:")

                    if question:
                        response = model.invoke(prompt.format(context=full_manual_text, question=question))
                        st.write("### Answer:")
                        st.write(response)

                    # Streaming response option
                    if st.button("Stream Response"):
                        st.write_stream(model.stream(prompt.format(context=full_manual_text, question=question)))
            else:
                st.error("Failed to download the manual.")
        else:
            st.warning("No manual link found for this vehicle.")
    else:
        st.warning("No vehicle selected. Please go back to the predictions page and select a vehicle.")
