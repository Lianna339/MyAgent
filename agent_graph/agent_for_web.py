from typing import List, Dict

import gradio as gr
import uuid

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from graph_chat.assistant import CtripAssistant, assistant_runnable, primary_assistant_tools
from graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, ToHotelBookingAssistant, \
    ToBookExcursion
from graph_chat.build_child_graph import build_flight_graph, builder_hotel_graph, build_car_graph, \
    builder_excursion_graph
from tools.flights_tools import fetch_user_flight_information
from graph_chat.draw_png import draw_graph
from graph_chat.state import State
from tools.init_db import update_dates
from tools.tools_handler import create_tool_node_with_fallback, _print_event
from graph_chat.init_graph import build_graph

MAX_LENGTH = 1500
graph = build_graph()
session_id = str(uuid.uuid4())

# 配置参数，包含乘客ID和线程ID
config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": "3442 587242",
        # 检查点由session_id访问
        "thread_id": session_id,
    }
}

def excute_graph(chatbot: List[Dict])->List[Dict]:
    '''执行工作流的函数'''
    result = "" # AI助手的最后一条消息
    user_input = chatbot[-1]['content']
    if user_input.strip().lower() != 'y': # 正常的用户提问
        events = graph.stream({'messages': ('user', user_input)}, config, stream_mode='values')
    else: # 用户输入的是确认
        events = graph.stream(None, config, stream_mode='values')
    for event in events:
        messages = event.get('messages')
        if messages:
            if isinstance(messages, list):
                message = messages[-1]
            if message.__class__.__name__ == 'AI Message':
                if message.content:
                    result = message.content
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > MAX_LENGTH:
                msg_repr = msg_repr[:MAX_LENGTH] + " ... （已截断）"  
            print(msg_repr)
    current_state = graph.get_state(config)
    if current_state.next:
        result = 'AI助手马上根据你的要求，执行相关操作。您是否批准上述操作？输入‘y’继续；否则，请说明您请求的更改'
    chatbot.append({'role': 'assostant', 'content': result})
    return chatbot

def do_graph(user_input, chat_bot):
    '''
    输入框提交后，执行的函数
    '''
    if user_input:
        chat_bot.append({'role':'user', 'content':user_input})
    return '', chat_bot # 输入框置为空，聊天框显示输入内容

css = '''
#bgc {background-color: #7FFFD4}
.feedback textarea {font-size: 24px !important}
'''
with gr.Blocks(title='AI智能助手', css=css) as instatnt:
    gr.Label('AI智能助手', container=False)
    chatbot = gr.Chatbot(type='messages', height=350, label='chatbox')
    input_textbox = gr.Textbox(label='请输入你的问题', value='')
    input_textbox.submit(do_graph, [input_textbox, chatbot], [input_textbox, chatbot]).then(excute_graph, chatbot, chatbot) # 回车触发

if __name__=='__main__':
    instatnt.launch(debug=True)