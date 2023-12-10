import gradio
import time


def ask(history: list[list[str, str]]):
    print("asked something")
    time.sleep(2)
    response = "this is the response"
    history[-1][1] = ""
    for token in response.split(" "):
        history[-1][1] += token + " "
        time.sleep(1)
        yield history


def user(user_message, history):
    return "", history + [[user_message, None]]


def clear_memory():
    print("cleared memory")


gradio.ChatInterface
# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as demo:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gradio.Chatbot()
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    clear_btn = gradio.ClearButton([chatbot, txt], value="Start new Conversation")

    txt.submit(user, [txt, chatbot], [txt, chatbot], queue=False).then(
        ask, chatbot, chatbot
    )
    # txt.submit(lambda x: "", txt, txt)

    clear_btn.click(clear_memory, queue=False)
    submit_btn.click(ask, inputs=[txt], outputs=[chatbot], queue=False)
    submit_btn.click(lambda x: "", [txt], [txt])


demo.queue()
demo.launch()
