package org.qxdn.akts.service.impl;

import cn.dev33.satoken.secure.SaSecureUtil;
import org.qxdn.akts.dao.UserRepository;
import org.qxdn.akts.dto.LoginUser;
import org.qxdn.akts.model.User;
import org.qxdn.akts.service.UserService;
import org.qxdn.akts.util.UserUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Transactional
@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public LoginUser register(User user) {
        // 已存在
        if (null != userRepository.findUserByEmail(user.getEmail())) {
            return null;
        }
        if (null == user.getRole()) {
            // 普通用户
            user.setRole("user");
        }
        // sha256 加密密码
        user.setPassword(SaSecureUtil.sha256(user.getPassword()));
        return UserUtil.user2LoginUser(userRepository.save(user));
    }

    @Override
    public LoginUser doLoginByEmail(User user) {
        User user1 = userRepository.findUserByEmail(user.getEmail());
        // 密码加密
        user.setPassword(SaSecureUtil.sha256(user.getPassword()));
        // 判断email和password是否一致
        if (user1 != null && user1.getPassword().equals(user.getPassword())) {
            // 成功
            return UserUtil.user2LoginUser(user1);
        }
        return null;
    }

    @Override
    public LoginUser resetPassword(User user) {
        User user1 = userRepository.findUserByEmail(user.getEmail());
        user1.setPassword(SaSecureUtil.sha256(user.getPassword()));
        user1 = userRepository.save(user1);
        return UserUtil.user2LoginUser(user1);
    }
}
