package org.qxdn.akts;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;

import cn.dev33.satoken.secure.SaSecureUtil;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.qxdn.akts.service.MailService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class AktsApplicationTests {

	@Autowired
	MailService mailService;

	@Test
	void contextLoads() {
		mailService.sendSimpleMail(new String[]{"1464238196@qq.com"}, "简单邮件", "这是一份简单邮件，不含html");
	}

	@Test
	void htmlMailTest(){
		Map<String,Object> map = new HashMap<>();
		map.put("name", "qxdn");
		mailService.sendMimeMail(new String[]{"1464238196@qq.com"}, "简单邮件", map,"welcome");
	}

	@ParameterizedTest
	@ValueSource(strings = {"123456","59sdfsd"})
	void encoderPassword(String password){
		String password1= SaSecureUtil.sha256(password);
		String password2= SaSecureUtil.sha256(password);
		assertEquals(password1, password2);
	}
}
