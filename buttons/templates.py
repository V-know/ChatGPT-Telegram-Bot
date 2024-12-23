from string import Template

say_help = {
    "en": """
If anything went wrong, just type: /start or restart the Bot to reset it.

or 

contact 👉 @AiMessagerBot 👈 for more help!
""",
    "cn": """
如遇功能异常，请输入： /start 或重启 Bot 进行重置

或
    
联系👉 @AiMessagerBot 👈获取更多帮助!
"""}

role = {
    "en": Template("""
As an AI assistant, my role is now set as🤖:

**$system_content**

Now you can send my new role directly!


In case you want to stop this setting, just reply: `cancel`‍🤝‍
"""),
    "cn": Template("""
您当前的系统AI助手身份设置为🤖：

**$system_content**

请直接回复新的AI助手身份设置！

您可以参考： [🧠ChatGPT 中文调教指南]https://github.com/PlexPt/awesome-chatgpt-prompts-zh

如需取消重置，请直接回复：`取消` 或 `取消重置` ‍🤝‍
""")}

context_info = {"en": Template("""
Each time you ask a question, the AI will provide an answer considering your most recent $context_count conversations!

Your conversation history has now been cleared, and you can start asking questions again!
"""), "cn": Template("""
每次提问AI会参考您最近 $context_count 次的对话记录为您提供答案！

现在您的会话历史已清空，可以重新开始提问了！
""")}

identity_confirmed = {"en": """
The new AI assistant identity has been confirmed.
I will answer your questions based on this new identity.
You can start asking questions now!
""", "cn": """
新的AI助手身份已确认。
我将以新身份为背景来为您解答问题。
您现在可以开始提问了！
"""}

statistics_response = {"en": Template("""
Hi $user!

Your current Token usage is as follows:

Query: $prompt_tokens Tokens
Answer: $completion_tokens Tokens
Total: $total_tokens Tokens

Have a nice day!🎉
"""), "cn": Template("""
Hi  $user!

您当前Token使用情况如下：

查询：$prompt_tokens Tokens
答案：$completion_tokens Tokens
总共：$total_tokens Tokens

祝您生活愉快！🎉
""")}

token_limit = {
    "en": Template("""
$answer

--------------------------------------

The length of the answer has exceeded your current maximum limit of $max_token tokens per answer.

Please contact @AiMessagerBot for more Tokens!✅
"""),
    "cn": Template("""
$answer

--------------------------------------

答案长度超过了您当前单条答案最大 $max_token 个Token的限制

请联系 @AiMessagerBot 获取更多权益! ✅
""")}

image = {
    "en": """
Image generator based on OpenAI DALL·E 3 model.
Please enter your prompt, I will generate an image.
""",
    "cn": """
基于 OpenAI DALL·E 3 模型的图像生成器。
请输入你的提示，我将生成一张图片。
"""}
