package org.qxdn.akts.service;

import java.util.Map;

public interface MailService {

    /**
     *  发送单纯文本邮件
     * @param to 接收者
     * @param subject 主题
     * @param content 内容
     */
    public void sendSimpleMail(String[] to,String subject,String content);
    
    /**
     * 
     * @param to 接收者
     * @param subject 主题
     * @param variables 模板中的变量以字典的形式
     * @param templateName 需要渲染的模板名
     */
    public void sendMimeMail(String[] to, String subject, Map<String,Object> variables,String templateName);
}
