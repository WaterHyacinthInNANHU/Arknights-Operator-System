package org.qxdn.akts.service.impl;

import org.qxdn.akts.service.MailService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.MailException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import java.util.Map;

import javax.mail.internet.MimeMessage;

@Service
public class MailServiceImpl implements MailService {

    private static final Logger logger = LoggerFactory.getLogger(MailServiceImpl.class);

    @Autowired
    JavaMailSender javaMailSender;

    @Autowired
    TemplateEngine templateEngine;

    @Value("${spring.mail.username}")
    private String from;

    @Value("${spring.mail.nickname}")
    private String nickname;

    @Override
    public void sendSimpleMail(String[] to, String subject, String content) {
        // TODO: 可以转变为使用MQ来发送
        SimpleMailMessage simpleMailMessage = new SimpleMailMessage();
        logger.debug("send simple mail from:{}", this.from);
        // 发送者
        simpleMailMessage.setFrom(this.nickname + '<' + this.from + '>');
        // 接受者
        simpleMailMessage.setTo(to);
        // 主题
        simpleMailMessage.setSubject(subject);
        // 内容
        simpleMailMessage.setText(content);
        try {
            javaMailSender.send(simpleMailMessage);
        } catch (MailException mailException) {
            logger.error("sending simple mail to {} fail,with exception {} ", to, mailException);
        }
    }

    @Override
    public void sendMimeMail(String[] to, String subject, Map<String, Object> variables, String templateName) {
        Context ctx = new Context();
        ctx.setVariables(variables);
        //渲染html
        String html = this.templateEngine.process(templateName, ctx);
        MimeMessage mimeMessage = this.javaMailSender.createMimeMessage();
        try {
            MimeMessageHelper message = new MimeMessageHelper(mimeMessage, true, "UTF-8");
            message.setFrom(this.nickname + '<' + this.from + '>');
            message.setSubject(subject);
            message.setTo(to);
            //true 指html
            message.setText(html,true);
            this.javaMailSender.send(mimeMessage);
        } catch (Exception e) {
            logger.error("sending fail", e);
        }
    }

}
