package org.qxdn.akts.controller;

import org.qxdn.akts.config.valid.LoginValid;
import org.qxdn.akts.config.valid.RegisterValid;
import org.qxdn.akts.config.valid.ResetPasswordValid;
import org.qxdn.akts.dto.AEmail;
import org.qxdn.akts.dto.LoginUser;
import org.qxdn.akts.dto.Resp;
import org.qxdn.akts.service.MailService;
import org.qxdn.akts.service.UserService;
import org.qxdn.akts.util.UserUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.BindingResult;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import cn.dev33.satoken.session.SaSession;
import cn.dev33.satoken.stp.StpUtil;

import javax.servlet.http.HttpSession;

@RestController
public class UserController {

    private static final Logger logger = LoggerFactory.getLogger(UserController.class);

    @Autowired
    MailService mailService;

    @Autowired
    UserService userService;

    @RequestMapping("/register")
    public Resp register(@Validated({ RegisterValid.class }) LoginUser user, HttpSession session) {
        // 从httpsession中取出验证码
        Integer code = (Integer) session.getAttribute("code");
        if (!code.equals(user.getCode())) {
            return Resp.bad("验证码有误", null);
        }
        LoginUser user2 = userService.register(UserUtil.loginUser2User(user));
        if (user2 == null) {
            // email已经存在或者插入失败
            return Resp.bad("注册失败", null);
        }
        return Resp.success("注册成功", null);
    }

    @RequestMapping("/sendRegisterEmail")
    public Resp sendRegisterEmail(@Validated AEmail email, HttpSession session, BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return Resp.bad("bad email format", null);
        }
        Integer code = (int) (Math.random() * (9999 - 1000) + 1000);
        session.setAttribute("code", code);
        logger.debug("valid code:{}", code);
        // TODO: 可以换成美化
        mailService.sendSimpleMail(new String[] { email.getEmail() }, "验证码", code.toString());
        return Resp.success("sending mail", null);
    }

    @RequestMapping("/login")
    public Resp doLogin(@Validated({ LoginValid.class }) LoginUser user) {
        LoginUser user1 = userService.doLoginByEmail(UserUtil.loginUser2User(user));
        if (null == user1) {
            return Resp.bad("用户名或密码错误", null);
        }
        // 登陆
        StpUtil.setLoginId(user1.getEmail());
        return Resp.success("登陆成功", user1);
    }

    @RequestMapping("/sendResetEmail")
    public Resp sendResetEmail(@Validated AEmail email){
        //生成邮件验证码
        Integer code = (int) (Math.random() * (9999 - 1000) + 1000);
        SaSession session = StpUtil.getSessionByLoginId(email.getEmail());
        session.setAttribute("resetCode", code);
        mailService.sendSimpleMail(new String[] { email.getEmail() }, "验证码", code.toString());
        return Resp.success("sending mail", null);
    }

    @RequestMapping("/resetPassword")
    public Resp resetPassword(@Validated LoginUser user){
        user = userService.resetPassword(UserUtil.loginUser2User(user));
        return Resp.success("成功", user);
    }

}
