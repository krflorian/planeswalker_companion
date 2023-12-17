import gradio
import time
from functools import partial


def process_user_message(state):
    print(state)
    time.sleep(2)
    response = "this is the response"
    state["history"][-1][1] = ""
    for token in response.split(" "):
        state["history"][-1][1] += token + " "
        time.sleep(1)
        yield state["history"]


def update_user_message(user_message, state):
    """"""
    state["history"].append([user_message, None])
    return "", state["history"], state


def clear_memory(state):
    print("cleared memory")
    state["history"] = [[]]
    return state["history"], state


gradio.ChatInterface
# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as demo:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    state = gradio.State({"asdf": "asdf", "history": []})
    chatbot = gradio.Chatbot()

    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    clear_btn = gradio.ClearButton([txt], value="Start new Conversation")

    # text box submit
    txt.submit(
        update_user_message,
        inputs=[txt, state],
        outputs=[txt, chatbot, state],
        queue=False,
    ).then(process_user_message, inputs=[state], outputs=[chatbot])

    clear_btn.click(clear_memory, inputs=[state], outputs=[chatbot, state], queue=False)
    submit_btn.click(
        update_user_message,
        inputs=[txt, state],
        outputs=[txt, chatbot, state],
        queue=False,
    ).then(process_user_message, inputs=[state], outputs=[chatbot])


demo.queue()
demo.launch()
