import streamlit as st


bot_msg_container_html_template = '''
<div style='background-color: #FFFFFF; padding: 10px; border-radius: 5px; margin-bottom: 10px; display: flex'>
    <div style="width: 20%; display: flex; justify-content: center">
        <img src="https://www.svgrepo.com/show/310556/bot.svg" style="max-height: 50px; max-width: 50px; border-radius: 50%;">
    </div>
    <div style="width: 80%;">
        $MSG
    </div>
</div>
'''

user_msg_container_html_template = '''
<div style='background-color: #FFFFFF; padding: 10px; border-radius: 5px; margin-bottom: 10px; display: flex'>
    <div style="width: 78%">
        $MSG
    </div>
    <div style="width: 20%; margin-left: auto; display: flex; justify-content: center;">
        <img src="https://www.svgrepo.com/show/513868/user.svg" style="max-width: 50px; max-height: 50px; float: right; border-radius: 50%;">
    </div>    
</div>
'''

def render_chat(**kwargs):
    """
    Handles is_user 
    """
    if kwargs["is_user"]:
        st.write(
            user_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)
        
    else:
        st.write(
            bot_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)
        

    

