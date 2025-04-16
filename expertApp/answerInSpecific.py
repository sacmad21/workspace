def answer_in_specific():
    """
    API for advance retrival information chat
    """
    # https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/#returning-sources
    try:
        # Retrieve data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        user_input = data.get("message")
        session_id = data.get("session_id")
        collection = "mp_finance_faq_csv"
        collection_lang = data.get("collection_lang")
        tts_flag = data.get("audio")
        selected_approaches = request.json.get("apprcohes", [])
        insert_data(
            data={
                "user_input": user_input,
                "session_id": session_id,
                "collection": collection,
                "collection_lang": collection_lang,
                "tts_flag": tts_flag,
            },
            collection=mongo_db[MONGO_HISTORY_COLLECTION],
        )
        print("approches:", selected_approaches)
        print("language:", collection_lang)

        if not user_input or not session_id:
            return jsonify({"error": "Missing message or session ID"}), 400

        print("Embeddings initializing started")
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=HF_INFERENCE_KEY,
            model_name="intfloat/multilingual-e5-base",
        )
        print("Embeddings initializing Completed")
        print("QDRANT_URL", QDRANT_URL)
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            prefer_grpc=False,
        )
        if qdrant_client.collection_exists(collection_name=collection):
            print(f"The selected qdrtant {collection} exists")
            retriever = Qdrant(
                client=qdrant_client,
                collection_name=collection,
                embeddings=embeddings,
            ).as_retriever()
            contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, contextualize_q_prompt
            )
            qa_system_prompt = """You are an assistant for question-answering tasks. \
                Use the following pieces of retrieved context to answer the question. \
                If you don't know the answer, just say that you don't know. \
                Use five sentences maximum and keep the answer concise.\
                Genrate the answer in {collection_lang}.\
                
                {context}"""
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

            rag_chain = create_retrieval_chain(
                history_aware_retriever, question_answer_chain
            )

            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
            print("chain initialzation started")
            result = conversational_rag_chain.invoke(
                {"input": user_input, "collection_lang": collection_lang},
                config={
                    "configurable": {"session_id": session_id},
                    "callbacks": [langfuse_handler],
                },
            )
            output_audio_path_1 = None
            print("tts flag value", tts_flag)
            if tts_flag:
                if collection_lang == "Hindi":
                    lang_code = "hi-IN"
                else:
                    lang_code = "en-IN"
                audio_count = increment_audio_count(session_id)
                print("audio_count", audio_count)
                output_audio_path = f"ui/static/audio/{session_id}{audio_count}.mp3"
                result_tts = result["answer"].replace("\n", " ")
                print("tts result:", result_tts)

                converter.convert_text_to_speech(
                    input_text=result_tts,
                    language=lang_code,
                    output_filename=output_audio_path,
                )
                output_audio_path_1 = output_audio_path.replace("ui/", "")

            references = []
            context = result["context"]

            insert_data(
                data={
                    "user_input": user_input,
                    "session_id": session_id,
                    "collection": collection,
                    "collection_lang": collection_lang,
                    "tts_flag": tts_flag,
                    "ai_response": result["answer"],
                },
                collection=mongo_db[MONGO_HISTORY_COLLECTION],
            )
            print("Result", result)
            references = []
            context = result["context"]
            for i in context:
                filename = i.metadata.get("filename", i.metadata.get("source", ""))
                if filename and "/" not in filename:
                    references.append(filename.split(".")[0])
                else:
                    references.append(filename.split("/")[-1].split(".")[0])
            return jsonify(
                {
                    "content": result["answer"],
                    "audio_path": output_audio_path_1,
                    "references": list(set(references)),
                }
            )
        else:
            return jsonify({"content": "The selected collection does not exist"})

    except Exception as e:
        print(f"Error occurred: {e}")
        print("ERROR", traceback.format_exc())
        insert_data(
            data={
                "user_input": user_input,
                "session_id": session_id,
                "collection": collection,
                "collection_lang": collection_lang,
                "tts_flag": tts_flag,
                "ai_response": "",
                "error_message": str(e),
                "traceback": traceback.format_exc(),
            },
            collection=mongo_db[MONGO_HISTORY_COLLECTION],
        )
        return (
            jsonify(
                {
                    "error": "The service is currently unavailable due to ongoing maintenance, Please contact the administrator for further details."
                }
            ),
            500,
        )