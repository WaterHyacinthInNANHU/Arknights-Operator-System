package org.qxdn.akts.service;

import org.graalvm.compiler.lir.LIRInstruction.Use;
import org.qxdn.akts.dto.LoginUser;
import org.qxdn.akts.model.User;

public interface UserService {


    /**
     * 关于save失败的方案可以参考stackoverflow 方案待测试
     * https://stackoverflow.com/questions/50364779/spring-data-repository-save-how-to-know-it-data-is-really-saved/50364891
     * @param user 用户
     * @return 保存后的user
     */
    public LoginUser register(User user);

    /**
     * 通过email来登录
     * @param user 传进来的用户
     * @return 登录成功的User否则为null
     */
    public LoginUser doLoginByEmail(User user);

    public LoginUser resetPassword(User user);
}
