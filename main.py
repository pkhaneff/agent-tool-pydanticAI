import streamlit as st
from agents.tool_router_agent import ToolRouterAgent
from chat_history_utils import load_chat_history, save_chat_history
from user_context_utils import load_user_context, save_user_context

# Khởi tạo agent
@st.cache_resource
def get_agent():
    return ToolRouterAgent()

tool_router_agent = get_agent()

# Sidebar: chọn user_id (giả lập)
st.sidebar.title("User Context")
user_id = st.sidebar.text_input("User ID", value="user_1")

# Nhập thông tin user context ở sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Thông tin cá nhân")
def context_form():
    name = st.sidebar.text_input("Họ tên")
    age = st.sidebar.number_input("Tuổi", min_value=0, max_value=120, value=25)
    phone = st.sidebar.text_input("Số điện thoại")
    job = st.sidebar.text_input("Nghề nghiệp")
    hobbies = st.sidebar.text_area("Sở thích (cách nhau bởi dấu phẩy)")
    return {
        "name": name,
        "age": age,
        "phone": phone,
        "job": job,
        "hobbies": [h.strip() for h in hobbies.split(",") if h.strip()]
    }

user_context = load_user_context(user_id)

with st.sidebar.form("context_form"):
    context_inputs = context_form()
    save_context = st.form_submit_button("Lưu thông tin cá nhân")
    if save_context:
        save_user_context(user_id, context_inputs)
        st.success("Đã lưu thông tin cá nhân!")
        user_context = context_inputs

# Load chat history
chat_history = load_chat_history(user_id)

st.title("Tool Router Agent Demo")
st.markdown("Nhập query của bạn, agent sẽ phân tích và chọn tool phù hợp. Lịch sử truy vấn, context và nhận xét AI sẽ hiển thị bên dưới.")

with st.form("query_form"):
    user_query = st.text_input("Nhập query:", "Tìm tài liệu về chính sách bảo mật.")
    submitted = st.form_submit_button("Gửi truy vấn")

if submitted and user_query.strip():
    # Gọi agent
    with st.spinner("Đang phân tích, vui lòng chờ..."):
        router_output = tool_router_agent.analyze(user_query, user_context, chat_history)
    st.success(f"**Tool selected:** {router_output.tool_name}")
    st.info(f"**Reasoning:** {router_output.reasoning}")

    # Lưu lại query vào chat history
    save_chat_history(user_id, user_query)
    chat_history = load_chat_history(user_id)  # reload để hiển thị mới nhất

    # Reflection
    reflection_prompt = (
        f"User query: {user_query}\n"
        f"Tool selected: {router_output.tool_name}\n"
        f"Reasoning: {router_output.reasoning}\n"
        "Hãy đánh giá xem lựa chọn tool và reasoning trên có hợp lý với query không. "
        "Nếu chưa hợp lý, hãy đề xuất tool và reasoning phù hợp hơn."
    )
    with st.spinner("Đang đánh giá lại kết quả (reflection)..."):
        reflection_result = tool_router_agent.model.chat([
            {"role": "system", "content": "Bạn là một AI reviewer, chuyên đánh giá kết quả phân luồng tool."},
            {"role": "user", "content": reflection_prompt}
        ])
    st.markdown("---")
    st.subheader("[Reflection] AI reviewer nhận xét:")
    st.write(reflection_result)

# Hiển thị context hiện tại
st.markdown("---")
st.subheader(f"Thông tin cá nhân của user: {user_id}")
st.json(user_context)

# Hiển thị lịch sử truy vấn
st.markdown("---")
st.subheader(f"Lịch sử truy vấn của user: {user_id}")
if chat_history:
    for i, q in enumerate(reversed(chat_history[-20:]), 1):
        st.markdown(f"{len(chat_history)-i+1}. {q}")
else:
    st.write("Chưa có lịch sử truy vấn.")