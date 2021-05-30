package org.qxdn.akts.util;

import org.qxdn.akts.dto.LoginUser;
import org.qxdn.akts.model.User;

public class UserUtil {

    public static User loginUser2User(LoginUser loginUser){
        User user = new User();
        user.setEmail(loginUser.getEmail());
        user.setPassword(loginUser.getPassword());
        user.setUsername(loginUser.getUsername());
        return user;
    }

    /**
     * user转loginUser
     * @param user
     * @return
     */
    public static LoginUser user2LoginUser(User user){
        LoginUser loginUser = new LoginUser();
        loginUser.setEmail(user.getEmail());
        loginUser.setRole(user.getRole());
        loginUser.setUsername(user.getPassword());
        loginUser.setId(user.getId());
        return loginUser;
    }
}
