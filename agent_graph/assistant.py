import os
from datetime import datetime

from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

from graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, ToHotelBookingAssistant, \
    ToBookExcursion
from graph_chat.llm_tavily import tavily_tool, llm
from graph_chat.state import State
from tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.flights_tools import fetch_user_flight_information, search_flights, update_ticket_to_new_flight, \
    cancel_ticket
from tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.retriever_vector import lookup_policy
from tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion


class CtripAssistant:
    def __init__(self, runnable:Runnable):
        """
        初始化助手的实例
        :param runnable:
        """
        self.runnable = runnable

    def __call__(self, state:State, config:RunnableConfig):
        """
        调用节点，执行助手任务
        :param state:
        :param config: 里面有旅客的信息
        :return:
        """
        while True:
            # 创建了一个无限循环，它将一直执行直到：从 self.runnable 获取的结果是有效的。
            # 如果结果无效（例如，没有工具调用且内容为空或内容不符合预期格式），循环将继续执行，
            # configuration = config.get('configurable', {})
            # user_id = configuration.get('passenger_id', None) # 自定义
            # state = {**state, 'user_info': user_id} # **state: 展开state，新增一个key和value
            result = self.runnable.invoke(state)

            # 处理响应结果
            if not result.tool_calls and ( # 结果中没有工具调用
                not result.content # 内容为空
                or isinstance(result.content, list) # 内容列表第一个元素没有‘text’
                and not result.content[0].get('text') # 没有得到一个成功的输出
            ):
                message = state['message'] + [('user', '请提供一个真实的输出作为回应。')]
                state = {**state, 'message':message}
            else:
                break
        return {'message': result} # 返回状态，是一个列表，列表里面是字典

# os.environ["TAVILY_API_KEY"] = "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"
# tavily_tool = TavilySearchResults(max_results=1)
#
# safe_tools = [
#     tavily_tool,
#     fetch_user_flight_information,       # 获取用户的航班信息
#     search_flights,                      # 搜索航班
#     lookup_policy,                       # 查看公司政策
#     search_car_rentals,                  # 搜索租车选项
#     search_hotels,                       # 搜索酒店
#     search_trip_recommendations,         # 搜索旅行推荐
# ]
#
# # 定义敏感工具列表，这些工具会更改用户的预订
# sensitive_tools = [
#     update_ticket_to_new_flight,         # 更新航班票务到新航班
#     cancel_ticket,                       # 取消票务
#     book_car_rental,                     # 预订租车
#     update_car_rental,                   # 更新租车预订
#     cancel_car_rental,                   # 取消租车预订
#     book_hotel,                          # 预订酒店
#     update_hotel,                        # 更新酒店预订
#     cancel_hotel,                        # 取消酒店预订
#     book_excursion,                      # 预订短途旅行
#     update_excursion,                    # 更新短途旅行预订
#     cancel_excursion,                    # 取消短途旅行预订
# ]
#
# part_1_tools = safe_tools + sensitive_tools
# sensitive_tool_names = {t.name for t in sensitive_tools}
# def create_assistant_node()->CtripAssistant:
#     """
#     创建一个助手节点
#     :return:返回一个助手节点对象
#     """
#
#     llm = ChatOpenAI(
#         model='glm-4.5',
#         api_key='782fb7fc5b2249b4b6ca0ecf7a7c155e.INMmoIzi5BO5nEKm',
#         base_url="https://open.bigmodel.cn/api/paas/v4/",
#     )
#
#     # 提示词
#     primary_assistant_prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "您是携程瑞士航空公司的客户服务助理。优先使用提供的工具搜索航班、公司政策和其他信息来帮助用户的查询。"
#                 "搜索时，请坚持不懈。如果第一次搜索没有结果，扩大您的查询范围。"
#                 "如果搜索为空，在放弃之前扩展您的搜索。\n\n当前用户:\n<User>\n{user_info}\n</User>"
#                 "\n当前时间: {time}.",
#             ),
#             ("placeholder", "{message}"),
#         ]
#     ).partial(time=datetime.now()) # 获取当前系统时间
#
#     runnable = primary_assistant_prompt | llm.bind_tools(safe_tools + sensitive_tools)
#     return CtripAssistant(runnable) # 创建一个类的实例

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "您是携程瑞士航空公司的客户服务助理。"
            "您的主要职责是搜索航班信息和公司政策以回答客户的查询。"
            "如果客户请求更新或取消航班、预订租车、预订酒店或获取旅行推荐，请通过调用相应的工具将任务委派给合适的专门助理。您自己无法进行这些类型的更改。"
            "只有专门助理才有权限为用户执行这些操作。"
            "用户并不知道有不同的专门助理存在，因此请不要提及他们；只需通过函数调用来安静地委派任务。"
            "向客户提供详细的信息，并且在确定信息不可用之前总是复查数据库。"
            "在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。"
            "如果搜索无果，请扩大搜索范围后再放弃。"
            "\n\n当前用户的航班信息:\n<Flights>\n{user_info}\n</Fllights>"
            "\n当前时间: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# 定义主助理使用的工具
primary_assistant_tools = [
    tavily_tool,  # 假设TavilySearchResults是一个有效的搜索工具
    search_flights,  # 搜索航班的工具
    lookup_policy,  # 查找公司政策的工具
]

# 创建可运行对象，绑定主助理提示模板和工具集，包括委派给专门助理的工具
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToFlightBookingAssistant,  # 用于转交航班更新或取消的任务
        ToBookCarRental,  # 用于转交租车预订的任务
        ToHotelBookingAssistant,  # 用于转交酒店预订的任务
        ToBookExcursion,  # 用于转交旅行推荐和其他游览预订的任务
    ]
)