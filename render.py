import streamlit as st


bot_msg_container_html_template = '''
<div style='display: flex; margin-bottom: 10px'>
    <div style="display: flex; justify-content: center; width: 15%; padding:10px">
        <img src="https://www.svgrepo.com/show/310556/bot.svg" style="max-height: 50px; max-width: 50px; border-radius: 50%">
    </div>
    <div style="width: 85%; min-height: 70px; padding:10px; background-color: #FEFEFE; border: 0.5px solid #EFEFEF; border-radius: 5px">
        $MSG
    </div>
</div>
'''


'''
bot claro
https://www.svgrepo.com/show/310389/bot.svg

bot escuro
https://www.svgrepo.com/show/310556/bot.svg

user claro
https://www.svgrepo.com/show/513868/user.svg

user escuro
https://www.svgrepo.com/show/457826/user.svg
'''

user_msg_container_html_template = '''
<div style='display: flex; margin-bottom: 10px'>
    <div style="width: 85%; min-height: 70px; padding:10px; background-color: #FEFEFE; border: 0.5px solid #EFEFEF; border-radius: 5px">
        $MSG
    </div>
    <div style="display: flex; margin-left: auto; justify-content: center; width: 15%; padding: 10px">
        <img src="https://www.svgrepo.com/show/457826/user.svg" style="max-width: 50px; max-height: 50px; float: right; border-radius: 50%">
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
        

    

