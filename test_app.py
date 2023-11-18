import gradio


def ask(query):
    print("asked something")
    return [[query, "asdfasdf"]]


def clear_memory():
    print("cleared memory")


gradio.ChatInterface
# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gradio.Chatbot()
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    clear_btn = gradio.ClearButton([chatbot, txt], value="Start new Conversation")
    txt.submit(ask, txt, chatbot)
    txt.submit(lambda x: "", txt, txt)

    clear_btn.click(clear_memory)
    submit_btn.click(ask, inputs=[txt], outputs=[chatbot])
    submit_btn.click(lambda x: "", [txt], [txt])


ui.launch()
