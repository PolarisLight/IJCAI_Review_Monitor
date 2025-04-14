import requests
import time
import json
import datetime
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class ReviewerMonitor:
    def __init__(self, reviewer_id,index):
        self.reviewer_id = reviewer_id
        self.api_url = f"https://cmt3.research.microsoft.com/api/odata/IJCAI2025/ReviewViews({reviewer_id})"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.cookies = {
            '.AspNetCore.Cookies': 'your_cookie_here',
            '.TRACK': '1',
            '.ROLE': 'Author'
        }
        self.index = index
        self.last_score = None
        self.from_email = "your_email1" # 填写您的邮件地址
        self.from_password = "your_email1_password"  # 填写您的邮件密码或生成的应用密码
        self.to_email = "your_email2"  # 填写接收通知的邮件地址
        self.init_flag = False

    def send_email(self,subject, body, to_email):
        
        # 构建邮件内容
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            # 使用 SSL 端口 465 连接 QQ SMTP 服务器
            server = smtplib.SMTP_SSL('smtp.qq.com', 465) # 以QQ邮箱为例
            server.login(self.from_email, self.from_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            print("邮件已发送成功")
        except Exception as e:
            print("邮件发送失败:", e)


    def check_feedback(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()  # 如果响应失败会抛出异常
            data = response.json()
            
            # 解析 "Questions" 数组中的内容，找到 "Overall Assessment" 部分
            overall_assessment = None
            for question in data.get('Questions', []):
                if question['Details'] == "Overall Assessment":
                    overall_assessment = question['Answers'][0].get('Text', '')
                    break
            
            if overall_assessment:
                score = overall_assessment.split(".")[0]
                if self.last_score != score:
                    if not self.init_flag:
                        self.last_score = score
                        self.init_flag = True
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f"Reviewer #{self.index} (ID:{self.reviewer_id}) : 初始评分",score)
                    else:
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f"Reviewer #{self.index} (ID:{self.reviewer_id}) : 评分已更新",score)
                        self.last_score = score
                        # 发送邮件通知
                        subject = f"[IJCAI2025] Reviewer #{self.index} (ID:{self.reviewer_id}) 评分更新通知！！！"
                        body = f"Reviewer #{self.index} (ID:{self.reviewer_id}) 的评分从 {self.last_score} 更新为 {score}"
                        self.send_email(subject, body, self.to_email)
                else:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f"Reviewer #{self.index} (ID:{self.reviewer_id}) : 评分无更新")
                    
            else:
                print("没有找到整体评估")
                
        except requests.exceptions.RequestException as e:
            print("请求失败:", e)

ReviewerIDList = [] # 查询Review号的方法见小红书文章

# 监控函数，每隔60秒检查一次
def monitor_reviews(interval=60):
    print("开始监控评审反馈...")
    Monitor_list = [ReviewerMonitor(reviewer_id, i+1) for i,reviewer_id in enumerate(ReviewerIDList)]
    while True:
        for monitor in Monitor_list:
            monitor.check_feedback()
        time.sleep(interval)

# 开始监控
monitor_reviews()
