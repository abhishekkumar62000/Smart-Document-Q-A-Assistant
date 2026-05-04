from typing import List
import os
import io
from pypdf import PdfReader
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
import json

class PDFProcessor:
    @staticmethod
    def summarize_text(text: str, api_key: str) -> str:
        """
        Summarize the given text using OpenAI LLM for concise document insights.
        """
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=api_key,
            model_name='gpt-3.5-turbo',
            max_tokens=256
        )
        prompt = (
            "Summarize the following document in 3-5 bullet points, focusing on the most important insights and key information.\n"
            "Be concise and clear.\n\n"
            "Document Content:\n{text}"
        )
        # Truncate text for summarization if too long
        short_text = text[:3000] if len(text) > 3000 else text
        summary = llm.invoke(prompt.format(text=short_text)).content.strip()
        return summary

    @staticmethod
    def get_pdf_text(pdf_docs):
        # Returns a list of (filename, text) tuples for each PDF
        results = []
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            results.append((getattr(pdf, 'name', f"Document {len(results)+1}"), text))
        return results

    @staticmethod
    def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

class RAGEngine:
    @staticmethod
    def get_vectorstore(text_chunks, api_key):
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore

    @staticmethod
    def get_conversation_chain(vectorstore, api_key):
        llm = ChatOpenAI(
            temperature=0,  # Lower temperature for more focused, less verbose answers
            openai_api_key=api_key,
            model_name='gpt-3.5-turbo',
            max_tokens=512  # Limit tokens to reduce cost
        )
        memory = ConversationBufferMemory(
            memory_key='chat_history', 
            return_messages=True
        )
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory,
            combine_docs_chain_kwargs={
                'prompt': PromptTemplate(
                    template="""
                    Answer the user's question as concisely and impactfully as possible. Use only the most relevant information. Avoid unnecessary details.
                    {context}
                    Question: {question}
                    """,
                    input_variables=["context", "question"]
                )
            }
        )
        return conversation_chain

class ActionAgent:
    @staticmethod
    def analyze_for_actions(question, answer, api_key):
        """
        Analyzes the Q&A pair to suggest actions.
        Returns a JSON object with 'actions' list.
        """
        llm = ChatOpenAI(
            temperature=0,  # Most deterministic, concise
            openai_api_key=api_key,
            model_name='gpt-3.5-turbo',
            max_tokens=256  # Lower token usage for cost
        )
        prompt_template = """
        You are an intelligent Action Agent. Your goal is to analyze the following Question and Answer from a document Q&A system.
        Identify if there are any actionable items, deadlines, or follow-ups required based on the context. Be as brief and direct as possible.
        
        Question: {question}
        Answer: {answer}
        
        Return the output purely as a JSON object with the following structure:
        {{
            "actions": [
                {{
                    "type": "Calendar/Reminder/Task/Note",
                    "label": "Short action title",
                    "details": "Description of the action"
                }}
            ]
        }}
        
        If no specific action is needed, return an empty list for "actions".
        Do not output any markdown formatting, just the raw JSON string.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["question", "answer"])
        final_prompt = prompt.format(question=question, answer=answer)
        response = llm.invoke(final_prompt)
        content = response.content.strip()
        # Clean up if markdown code blocks are returned
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"actions": []}
